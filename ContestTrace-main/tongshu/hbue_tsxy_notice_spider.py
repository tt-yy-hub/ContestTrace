# -*- coding: utf-8 -*-
"""
湖北经济学院统计与数学学院 · 通知公告爬虫

列表：https://tsxy.hbue.edu.cn/xkjs/list.htm

调度示例：
  python d:\\xiangmu\\ConTest11\\tongshu\\hbue_tsxy_notice_spider.py --mode incremental

全量：
  python hbue_tsxy_notice_spider.py --mode full

环境变量（可选）：
  FIRECRAWL_API_KEY — 若需通过 Firecrawl 拉取正文，可扩展本脚本；默认使用 requests + BeautifulSoup。

robots.txt：站点根路径返回 404，无公开 robots 规则；请控制频率、仅作合规采集。
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sqlite3
import time
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

BASE_URL = "https://tsxy.hbue.edu.cn"
LIST_PREFIX = "/xkjs/list"
SOURCE_DEFAULT = "统计与数学学院"
CATEGORY = "通知公告"
SPIDER_NAME = "hbue_tsxy_notice_spider"

DATE_START = date(2025, 1, 1)
DATE_END = date.today()

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

LIST_DELAY_SEC = 1.0
DETAIL_DELAY_SEC = 1.0
DETAIL_RETRIES = 3
DETAIL_RETRY_SLEEP_SEC = 2.0

# 正文中需保留为「文档超链接」的文件扩展名（不区分大小写）
_DOCUMENT_EXTENSIONS = frozenset({".jpg", ".jpeg", ".pdf", ".doc", ".docx", ".xls", ".xlsx"})

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = SCRIPT_DIR / "data" / "notices.db"

# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------

LOG_DIR = SCRIPT_DIR / "logs"
_logger: Optional[logging.Logger] = None


def setup_logging() -> logging.Logger:
    global _logger
    if _logger:
        return _logger
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"spider_{datetime.now():%Y%m%d_%H%M%S}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    _logger = logging.getLogger(SPIDER_NAME)
    logging.getLogger("jieba").setLevel(logging.WARNING)
    return _logger


log = setup_logging()


# ---------------------------------------------------------------------------
# 日期解析
# ---------------------------------------------------------------------------

_RE_YMD_DASH = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")
_RE_YMD_CN = re.compile(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")
_RE_PUB_LINE = re.compile(
    r"(?:发布时间|发布日期)[：:]\s*"
    r"(?:(\d{4}-\d{1,2}-\d{1,2})|(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日)"
)
_RE_SOURCE_PUB = re.compile(r"(?:发布单位|来源)[：:]\s*(.+?)(?:\n|$)")


def _to_date(y: str, m: str, d: str) -> Optional[date]:
    try:
        return date(int(y), int(m), int(d))
    except ValueError:
        return None


def parse_list_date(text: str) -> Optional[date]:
    text = (text or "").strip()
    m = _RE_YMD_DASH.search(text)
    if m:
        return _to_date(m.group(1), m.group(2), m.group(3))
    m = _RE_YMD_CN.search(text)
    if m:
        return _to_date(m.group(1), m.group(2), m.group(3))
    return None


def parse_publish_time_from_detail_html(soup: BeautifulSoup, plain_text: str, list_fallback: Optional[date]) -> tuple[str, bool]:
    """
    返回 (yyyy-mm-dd, 是否使用了列表页降级日期)。
    """
    # 结构化元数据
    arti = soup.select_one("span.arti_update")
    if arti:
        t = arti.get_text(strip=True)
        m = _RE_PUB_LINE.search(t)
        if m:
            if m.group(1):
                parts = m.group(1).split("-")
                d = _to_date(parts[0], parts[1], parts[2])
            else:
                d = _to_date(m.group(2), m.group(3), m.group(4))
            if d:
                return d.isoformat(), False

    m = _RE_PUB_LINE.search(plain_text)
    if m:
        if m.group(1):
            parts = m.group(1).split("-")
            d = _to_date(parts[0], parts[1], parts[2])
        else:
            d = _to_date(m.group(2), m.group(3), m.group(4))
        if d:
            return d.isoformat(), False

    for m in _RE_YMD_DASH.finditer(plain_text[:800]):
        d = _to_date(m.group(1), m.group(2), m.group(3))
        if d:
            return d.isoformat(), False

    for m in _RE_YMD_CN.finditer(plain_text[:800]):
        d = _to_date(m.group(1), m.group(2), m.group(3))
        if d:
            return d.isoformat(), False

    if list_fallback:
        log.warning("详情页未解析到发布时间，使用列表日期降级: %s", list_fallback.isoformat())
        return list_fallback.isoformat(), True

    log.warning("详情页未解析到发布时间且无列表降级，使用空字符串")
    return "", True


def parse_source(soup: BeautifulSoup, plain_text: str) -> str:
    pub = soup.select_one("span.arti_publisher")
    if pub:
        t = pub.get_text(strip=True)
        m = re.match(r"发布者[：:]\s*(.+)", t)
        if m and m.group(1).strip():
            return m.group(1).strip()

    m = _RE_SOURCE_PUB.search(plain_text[:2000])
    if m:
        return m.group(1).strip()
    return SOURCE_DEFAULT


# ---------------------------------------------------------------------------
# 正文提取（块之间 \n\n；块内合并行内标签为连贯句子，仅 <br> 换行；表格 \t / \n）
# 附件：.jpg/.pdf/.doc 等链接与图片 src 作为文档超链接写入正文
# ---------------------------------------------------------------------------

def _is_document_href(href: str) -> bool:
    if not href:
        return False
    h = href.strip()
    if h.startswith("#") or h.lower().startswith("javascript"):
        return False
    path = h.split("?", 1)[0].split("#", 1)[0]
    return Path(path).suffix.lower() in _DOCUMENT_EXTENSIONS


def _abs_asset_url(href: str) -> str:
    return urljoin(BASE_URL + "/", href.strip())


def _normalize_text_lines(raw: str, *, collapse_soft_breaks: bool = False) -> str:
    """按行压缩空白；collapse_soft_breaks 为 True 时把行内换行收成空格（用于表格单元格）。"""
    if collapse_soft_breaks:
        raw = re.sub(r"[\s\u00a0]*\n[\s\u00a0]*", " ", raw)
    lines: list[str] = []
    for line in raw.split("\n"):
        lines.append(re.sub(r"[\s\u00a0]+", " ", line).strip())
    out = "\n".join(L for L in lines if L)
    return out


def _inline_merged_text(el: Tag, *, collapse_soft_breaks: bool = False) -> str:
    """
    提取块级元素内全部可读文本：行内标签（span/font 等）不插入换行，与网页连续阅读一致；
    仅显式 <br> 产生换行。文档类 <a href>、<img src> 输出「锚文本 + 空格 + 绝对 URL」。
    """
    parts: list[str] = []

    def walk(n: Tag) -> None:
        for c in n.children:
            if isinstance(c, NavigableString):
                if isinstance(c, Comment):
                    continue
                parts.append(str(c))
            elif isinstance(c, Tag):
                low = c.name.lower()
                if low == "br":
                    parts.append("\n")
                elif low == "a":
                    href = (c.get("href") or "").strip()
                    if href and _is_document_href(href):
                        abs_u = _abs_asset_url(href)
                        label = re.sub(r"\s+", " ", c.get_text(separator=" ", strip=True)).strip()
                        if not label:
                            inner_img = c.find("img")
                            if inner_img and (inner_img.get("alt") or "").strip():
                                label = inner_img.get("alt", "").strip()
                        parts.append(f"{label} {abs_u}" if label else abs_u)
                        parts.append(" ")
                    else:
                        walk(c)
                elif low == "img":
                    src = (c.get("src") or "").strip()
                    if src and _is_document_href(src):
                        abs_u = _abs_asset_url(src)
                        alt = (c.get("alt") or "").strip()
                        lab = alt if alt else "[图片]"
                        parts.append(f"{lab} {abs_u}")
                        parts.append(" ")
                elif low == "table":
                    t = _table_to_text(c)
                    if t:
                        parts.append("\n" + t + "\n")
                elif low in ("script", "style"):
                    continue
                else:
                    walk(c)

    walk(el)
    raw = "".join(parts)
    return _normalize_text_lines(raw, collapse_soft_breaks=collapse_soft_breaks).strip()


def _table_to_text(table: Tag) -> str:
    lines: list[str] = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"], recursive=False)
        if not cells:
            continue
        row = [_inline_merged_text(c, collapse_soft_breaks=True) for c in cells]
        lines.append("\t".join(row))
    return "\n".join(L for L in lines if any(L.split("\t")))


def _process_block_node(el: Tag, blocks: list[str]) -> None:
    low = el.name.lower()
    if low in ("script", "style"):
        return
    if low == "table":
        txt = _table_to_text(el)
        if txt:
            blocks.append(txt)
        return
    if low in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre"):
        txt = _inline_merged_text(el)
        if txt:
            blocks.append(txt)
        return
    if low == "ul":
        for li in el.find_all("li", recursive=False):
            txt = _inline_merged_text(li)
            if txt:
                blocks.append(txt)
        return
    if low == "ol":
        for i, li in enumerate(el.find_all("li", recursive=False), 1):
            txt = _inline_merged_text(li)
            if txt:
                blocks.append(f"{i}. {txt}")
        return
    if low == "div":
        has_struct = bool(
            el.find(
                ["p", "table", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "div"],
                recursive=False,
            )
        )
        if has_struct:
            for c in el.children:
                if isinstance(c, Tag):
                    _process_block_node(c, blocks)
        else:
            txt = _inline_merged_text(el)
            if txt:
                blocks.append(txt)
        return

    if el.find(["p", "table", "ul", "ol", "div"], recursive=False):
        for c in el.children:
            if isinstance(c, Tag):
                _process_block_node(c, blocks)
    else:
        txt = _inline_merged_text(el)
        if txt:
            blocks.append(txt)


def _append_document_link_section(plain: str, container: Tag) -> str:
    """DOM 顺序收集文档类 a/img，若 URL 尚未出现在正文中则追加【文档链接】区块。"""
    seen_urls: set[str] = set()
    lines: list[str] = []
    for el in container.find_all(["a", "img"]):
        if el.name == "a":
            href = (el.get("href") or "").strip()
            if not href or not _is_document_href(href):
                continue
            abs_u = _abs_asset_url(href)
        else:
            src = (el.get("src") or "").strip()
            if not src or not _is_document_href(src):
                continue
            abs_u = _abs_asset_url(src)
        if abs_u in seen_urls:
            continue
        seen_urls.add(abs_u)
        if abs_u in plain:
            continue
        if el.name == "a":
            label = re.sub(r"\s+", " ", el.get_text(separator=" ", strip=True)).strip()
            if not label:
                im = el.find("img")
                if im and (im.get("alt") or "").strip():
                    label = im.get("alt", "").strip()
            if not label:
                label = abs_u
        else:
            label = (el.get("alt") or "").strip() or "[图片]"
        lines.append(f"{label}\t{abs_u}")
    if not lines:
        return plain
    return plain + "\n\n【文档链接】\n" + "\n".join(lines)


def extract_article_plain(container: Tag) -> str:
    if not container:
        return ""
    for s in container.find_all(["script", "style"]):
        s.decompose()

    blocks: list[str] = []
    for child in container.children:
        if isinstance(child, Tag):
            _process_block_node(child, blocks)
    merged = "\n\n".join(b for b in blocks if b)
    merged = merged.strip()
    return _append_document_link_section(merged, container)


# ---------------------------------------------------------------------------
# 关键词（jieba 可选）
# ---------------------------------------------------------------------------

def extract_keywords(title: str, content: str, top_n: int = 5) -> str:
    try:
        import jieba
    except ImportError:
        return "[]"

    text = f"{title}\n{content}"
    if not text.strip():
        return "[]"

    words = jieba.cut(text)
    stop = set(
        "的 了 和 与 或 在 是 为 有 等 及 对 中 其 将 由 可 请 各 本 院 学院 通知 公告 关于 开展 进行"
        .split()
    )
    filtered = [
        w.strip()
        for w in words
        if len(w.strip()) > 1
        and w.strip() not in stop
        and not w.strip().isdigit()
        and not re.fullmatch(r"\d{4}年", w.strip())
    ]
    if not filtered:
        return "[]"
    cnt = Counter(filtered)
    top = [w for w, _ in cnt.most_common(top_n)]
    return json.dumps(top, ensure_ascii=False)


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

@dataclass
class ListItem:
    url: str
    list_date: date
    list_title: str


def session_factory() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9"})
    return s


def fetch_html(session: requests.Session, url: str, retries: int = 1, retry_sleep: float = 2.0) -> Optional[str]:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, timeout=45)
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception as e:
            last_err = e
            log.warning("请求失败 %s (%s/%s): %s", url, attempt, retries, e)
            if attempt < retries:
                time.sleep(retry_sleep)
    log.error("放弃 URL: %s, 错误: %s", url, last_err)
    return None


def list_page_url(page: int) -> str:
    if page <= 1:
        return f"{BASE_URL}{LIST_PREFIX}.htm"
    return f"{BASE_URL}{LIST_PREFIX}{page}.htm"


def parse_list_page(html: str) -> tuple[list[ListItem], Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    items: list[ListItem] = []
    ul = soup.select_one("ul.news_list.list2") or soup.select_one("ul.news_list")
    if not ul:
        log.error("列表页未找到 ul.news_list")
        return items, None

    for li in ul.select("li.news"):
        a = li.select_one("span.news_title a")
        meta = li.select_one("span.news_meta")
        if not a or not a.get("href"):
            continue
        href = a["href"].strip()
        abs_url = urljoin(BASE_URL + "/", href)
        if urlparse(abs_url).netloc and urlparse(abs_url).netloc != urlparse(BASE_URL).netloc:
            continue
        d = parse_list_date(meta.get_text() if meta else "")
        if not d:
            continue
        title = a.get("title") or a.get_text(strip=True)
        items.append(ListItem(url=abs_url, list_date=d, list_title=title))

    next_href: Optional[str] = None
    nxt = soup.select_one("a.next")
    if nxt and nxt.get("href"):
        h = nxt["href"].strip()
        if h and not h.startswith("javascript"):
            next_href = urljoin(BASE_URL + "/", h)
    return items, next_href


def should_stop_full_page(items: list[ListItem]) -> bool:
    if not items:
        return True
    return all(it.list_date < DATE_START for it in items)


def should_stop_incremental_page(items: list[ListItem], max_pub: str) -> bool:
    if not items:
        return True
    return all(it.list_date.isoformat() <= max_pub for it in items)


def filter_items_full(items: list[ListItem]) -> list[ListItem]:
    return [it for it in items if DATE_START <= it.list_date <= DATE_END]


def filter_items_incremental(items: list[ListItem], max_pub: str) -> list[ListItem]:
    out = []
    for it in items:
        if it.list_date.isoformat() <= max_pub:
            continue
        if it.list_date > DATE_END or it.list_date < DATE_START:
            continue
        out.append(it)
    return out


# ---------------------------------------------------------------------------
# 数据库
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source TEXT,
    publish_time TEXT,
    crawl_time TIMESTAMP,
    deadline TEXT,
    category TEXT,
    organizer TEXT,
    participants TEXT,
    prize TEXT,
    requirement TEXT,
    contact TEXT,
    content TEXT,
    keywords TEXT,
    tags TEXT,
    spider_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_notices_publish_time ON notices(publish_time);
"""


def init_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def max_publish_time(conn: sqlite3.Connection) -> Optional[str]:
    row = conn.execute(
        "SELECT MAX(publish_time) FROM notices WHERE spider_name = ? AND publish_time != ''",
        (SPIDER_NAME,),
    ).fetchone()
    return row[0] if row and row[0] else None


INSERT_SQL = """
INSERT OR IGNORE INTO notices (
    title, url, source, publish_time, crawl_time, deadline, category,
    organizer, participants, prize, requirement, contact, content,
    keywords, tags, spider_name, updated_at
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""


def insert_notice(conn: sqlite3.Connection, row: tuple) -> bool:
    cur = conn.execute(INSERT_SQL, row)
    conn.commit()
    return cur.rowcount > 0


# ---------------------------------------------------------------------------
# 详情解析与入库
# ---------------------------------------------------------------------------

def extract_content_from_soup(soup: BeautifulSoup) -> str:
    container = (
        soup.select_one("div.wp_articlecontent")
        or soup.select_one("#vsb_content")
        or soup.select_one(".article-content")
        or soup.select_one("div.read")
    )
    return extract_article_plain(container) if container else ""


def extract_content_from_html(html: str) -> str:
    return extract_content_from_soup(BeautifulSoup(html, "lxml"))


def parse_detail(html: str, list_item: ListItem) -> Optional[dict]:
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.select_one("h1.arti_title")
    title = (h1.get_text(strip=True) if h1 else "") or ""
    if not title:
        t = soup.find("title")
        title = t.get_text(strip=True) if t else ""
    title = re.sub(r"\s+", " ", title).strip()

    content = extract_content_from_soup(soup)

    plain_for_meta = soup.get_text("\n", strip=True)
    publish_time, used_fallback = parse_publish_time_from_detail_html(
        soup, plain_for_meta, list_item.list_date
    )
    if used_fallback and publish_time:
        log.info("发布时间降级记录 url=%s publish_time=%s", list_item.url, publish_time)

    source = parse_source(soup, plain_for_meta)

    keywords = extract_keywords(title, content)
    tags = "[]"

    return {
        "title": title,
        "publish_time": publish_time,
        "source": source,
        "content": content,
        "keywords": keywords,
        "tags": tags,
    }


def crawl(
    mode: str,
    db_path: Path,
    max_pages: Optional[int] = None,
) -> None:
    conn = init_db(db_path)
    session = session_factory()
    max_pub = max_publish_time(conn) if mode == "incremental" else None

    if mode == "incremental" and not max_pub:
        log.info("增量模式但库中无 publish_time，按全量日期窗口抓取")
        mode = "full"
        max_pub = None

    queue: list[ListItem] = []
    page = 1
    next_url: Optional[str] = None

    while True:
        if max_pages is not None and page > max_pages:
            log.info("已达 max_pages=%s，停止列表遍历", max_pages)
            break

        url = next_url or list_page_url(page)
        log.info("列表页 %s", url)
        html = fetch_html(session, url, retries=3, retry_sleep=2.0)
        if not html:
            log.error("列表页获取失败，停止遍历: %s", url)
            break

        items, next_href = parse_list_page(html)
        log.info("本页条目数: %s", len(items))

        if mode == "full":
            if should_stop_full_page(items):
                log.info("本页所有条目早于 %s，停止翻页", DATE_START.isoformat())
                queue.extend(filter_items_full(items))
                break
            queue.extend(filter_items_full(items))
        else:
            assert max_pub is not None
            if should_stop_incremental_page(items, max_pub):
                log.info("本页无新条目（列表日期均 <= %s），停止翻页", max_pub)
                queue.extend(filter_items_incremental(items, max_pub))
                break
            queue.extend(filter_items_incremental(items, max_pub))

        if not next_href:
            log.info("无下一页链接，结束")
            break

        next_url = next_href
        page += 1
        time.sleep(LIST_DELAY_SEC)

    # 按 URL 去重，保持顺序
    seen: set[str] = set()
    unique_queue: list[ListItem] = []
    for it in queue:
        if it.url in seen:
            continue
        seen.add(it.url)
        unique_queue.append(it)

    log.info("待抓取详情数: %s", len(unique_queue))

    # 优化：先获取数据库中已存在的所有URL，避免逐一检查
    existing_urls = set()
    if mode == "incremental":
        cursor = conn.execute("SELECT url FROM notices WHERE spider_name = ?", (SPIDER_NAME,))
        for row in cursor:
            existing_urls.add(row[0])
        log.info("数据库中已存在 %s 个URL，将直接跳过", len(existing_urls))

        # 过滤掉已存在的URL
        unique_queue = [it for it in unique_queue if it.url not in existing_urls]
        log.info("过滤后待抓取详情数: %s", len(unique_queue))

        if len(unique_queue) == 0:
            log.info("所有URL均已存在，无需抓取，结束")
            conn.close()
            return

    inserted = 0
    skipped_dup = 0
    skipped_date_detail = 0
    failed: list[str] = []

    for it in unique_queue:
        time.sleep(DETAIL_DELAY_SEC)
        html = fetch_html(session, it.url, retries=DETAIL_RETRIES, retry_sleep=DETAIL_RETRY_SLEEP_SEC)
        if not html:
            failed.append(it.url)
            continue

        data = parse_detail(html, it)
        if not data:
            failed.append(it.url)
            continue

        pt = data["publish_time"]
        if pt:
            try:
                ptd = date.fromisoformat(pt)
                if ptd < DATE_START or ptd > DATE_END:
                    skipped_date_detail += 1
                    log.info("详情发布时间不在窗口内，跳过: %s %s", pt, it.url)
                    continue
            except ValueError:
                log.warning("发布时间格式异常，跳过: %s", pt)
                continue
        else:
            log.warning("无发布时间，跳过: %s", it.url)
            continue

        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        row = (
            data["title"],
            it.url,
            data["source"],
            data["publish_time"],
            now,
            None,
            CATEGORY,
            None,
            None,
            None,
            None,
            None,
            data["content"],
            data["keywords"],
            data["tags"],
            SPIDER_NAME,
            now,
        )
        if insert_notice(conn, row):
            inserted += 1
            log.info("已入库: %s", data["title"][:60])
        else:
            skipped_dup += 1
            log.info("已存在跳过(URL 重复): %s", it.url)

    log.info(
        "完成: 新插入 %s 条, 因 URL 已存在跳过 %s 条, 因详情日期不在窗口跳过 %s 条, 失败 %s 条",
        inserted,
        skipped_dup,
        skipped_date_detail,
        len(failed),
    )
    if failed:
        log.warning("失败 URL 列表:\n%s", "\n".join(failed))
    conn.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="湖北经济学院统计与数学学院通知公告爬虫")
    ap.add_argument("--mode", choices=("full", "incremental"), default="full")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--max-pages", type=int, default=None, help="调试用：最多翻页数")
    args = ap.parse_args()
    crawl(args.mode, args.db, args.max_pages)


if __name__ == "__main__":
    main()
