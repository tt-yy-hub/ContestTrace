import argparse
import json
import logging
import random
import re
import sqlite3
import sys
import time
from dataclasses import dataclass
from datetime import datetime, date
from typing import Iterable, Optional, Tuple, List, Dict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


SPIDER_NAME = "hbue_xwcb_notice_spider"
BASE = "https://xwcb.hbue.edu.cn/"
LIST_ENTRY = "https://xwcb.hbue.edu.cn/183/list.htm"
CATEGORY = "通知公告"
DEFAULT_SOURCE = "新闻与传播学院"

TIME_WINDOW_START = date(2025, 1, 1)
TIME_WINDOW_END = date(2026, 4, 9)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def utc_now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_yyyy_mm_dd(s: str) -> Optional[date]:
    s = (s or "").strip()
    m = re.search(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        return date(y, mo, d)
    except ValueError:
        return None


def date_to_str(d: Optional[date]) -> Optional[str]:
    if not d:
        return None
    return d.strftime("%Y-%m-%d")


def is_doc_like(url: str) -> bool:
    path = (urlparse(url).path or "").lower()
    return any(
        path.endswith(ext)
        for ext in (".jpg", ".jpeg", ".pdf", ".doc", ".docx", ".xls", ".xlsx")
    )


def is_image(url: str) -> bool:
    path = (urlparse(url).path or "").lower()
    return any(path.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"))


@dataclass
class HttpConfig:
    list_delay_s: float = 1.0
    detail_delay_s: float = 1.0
    detail_retry: int = 3
    detail_retry_delay_s: float = 2.0
    timeout_s: float = 20.0


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.6",
            "Connection": "keep-alive",
        }
    )
    return s


def sleep_jitter(base_s: float) -> None:
    base_s = max(0.0, float(base_s))
    jitter = random.uniform(-0.15, 0.15) * base_s
    time.sleep(max(0.0, base_s + jitter))


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notices (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT,
          url TEXT UNIQUE,
          source TEXT DEFAULT '新闻与传播学院',
          publish_time TEXT,
          crawl_time TEXT,
          deadline TEXT,
          category TEXT,
          organizer TEXT,
          participants TEXT,
          prize TEXT,
          requirement TEXT,
          contact TEXT,
          content TEXT,
          keywords TEXT NOT NULL DEFAULT '[]',
          tags TEXT NOT NULL DEFAULT '[]',
          spider_name TEXT,
          created_at TEXT,
          updated_at TEXT
        );
        """
    )
    conn.commit()


def get_max_publish_time(conn: sqlite3.Connection) -> Optional[date]:
    row = conn.execute(
        "SELECT MAX(publish_time) FROM notices WHERE publish_time IS NOT NULL AND publish_time != ''"
    ).fetchone()
    if not row or not row[0]:
        return None
    return parse_yyyy_mm_dd(str(row[0]))


def within_window(d: date) -> bool:
    return TIME_WINDOW_START <= d <= TIME_WINDOW_END


def normalize_abs_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return u
    return urljoin(BASE, u)


def clean_text(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def tag_is_block(tag: Tag) -> bool:
    return tag.name in {
        "p",
        "div",
        "section",
        "article",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "table",
        "thead",
        "tbody",
        "tfoot",
        "tr",
        "blockquote",
        "pre",
    }


def iter_text_nodes_in_order(node: Tag) -> Iterable[Tag | NavigableString]:
    for child in node.children:
        if isinstance(child, NavigableString):
            yield child
        elif isinstance(child, Tag):
            yield child


def extract_anchor_text(a: Tag) -> str:
    txt = a.get_text(strip=True) or ""
    if txt:
        return txt
    img = a.find("img")
    if img:
        return (img.get("alt") or "").strip() or "[图片]"
    return ""


def extract_document_and_image_mentions(container: Tag) -> Tuple[str, List[Tuple[str, str]]]:
    """
    返回：
    - content（按规则生成纯文本）
    - doc_urls_seen_in_content：[(display, abs_url)] 仅记录“文档类链接/图片”中出现过的 url
    """
    doc_seen: List[Tuple[str, str]] = []

    def render_inline(el: Tag | NavigableString) -> str:
        nonlocal doc_seen
        if isinstance(el, NavigableString):
            return str(el)

        if not isinstance(el, Tag):
            return ""

        if el.name == "br":
            return "\n"

        if el.name == "a":
            href = normalize_abs_url(el.get("href") or "")
            text = extract_anchor_text(el)
            if href and is_doc_like(href):
                doc_seen.append((text or href, href))
                if text:
                    return f"{text} {href}"
                return href
            return el.get_text(strip=False)

        if el.name == "img":
            src = normalize_abs_url(el.get("src") or "")
            alt = (el.get("alt") or "").strip()
            if src:
                if is_doc_like(src) or is_image(src):
                    doc_seen.append((alt or "[图片]", src))
                return f"{alt or '[图片]'} {src}".strip()
            return alt or "[图片]"

        if el.name == "table":
            rows_out: List[str] = []
            for tr in el.find_all("tr"):
                cells = tr.find_all(["th", "td"])
                row_cells: List[str] = []
                for c in cells:
                    row_cells.append(clean_text(render_block(c)))
                row = "\t".join([c for c in row_cells if c is not None])
                rows_out.append(row.rstrip())
            return "\n".join([r for r in rows_out if r.strip()])

        return render_block(el)

    def render_block(el: Tag | NavigableString) -> str:
        if isinstance(el, NavigableString):
            return str(el)
        if not isinstance(el, Tag):
            return ""

        if el.name in {"script", "style", "noscript"}:
            return ""

        if el.name == "table":
            return render_inline(el)

        parts: List[str] = []
        for child in iter_text_nodes_in_order(el):
            parts.append(render_inline(child))
        return "".join(parts)

    blocks: List[str] = []
    for child in iter_text_nodes_in_order(container):
        if isinstance(child, NavigableString):
            text = str(child)
            if text.strip():
                blocks.append(text)
            continue
        if isinstance(child, Tag):
            if child.name in {"script", "style", "noscript"}:
                continue
            txt = render_inline(child)
            txt = txt.replace("\xa0", " ")
            txt = clean_text(txt)
            if txt:
                blocks.append(txt)

    content = "\n\n".join(blocks)
    content = clean_text(content)
    return content, doc_seen


def find_detail_container(soup: BeautifulSoup) -> Optional[Tag]:
    selectors = [
        "div.wp_articlecontent",
        "#vsb_content",
        ".article-content",
        "div.read",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el and isinstance(el, Tag):
            return el
    return None


def parse_deadline(text: str) -> Optional[str]:
    """
    仅做尽力解析：匹配 “截止/报名截止/提交截止/截至 2025-xx-xx”
    """
    if not text:
        return None
    m = re.search(r"(截止|截至|报名截止|提交截止)[^0-9]{0,10}(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})", text)
    if not m:
        return None
    d = parse_yyyy_mm_dd(m.group(2))
    return date_to_str(d)


def collect_all_doc_links(container: Tag) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for a in container.find_all("a"):
        href = normalize_abs_url(a.get("href") or "")
        if not href or not is_doc_like(href):
            continue
        text = extract_anchor_text(a) or href
        out.append((text, href))
    for img in container.find_all("img"):
        src = normalize_abs_url(img.get("src") or "")
        if not src:
            continue
        if is_doc_like(src) or is_image(src):
            out.append(((img.get("alt") or "").strip() or "[图片]", src))
    # 去重（保序）
    seen = set()
    dedup: List[Tuple[str, str]] = []
    for t, u in out:
        key = (t, u)
        if key in seen:
            continue
        seen.add(key)
        dedup.append((t, u))
    return dedup


def append_doc_link_block_if_missing(content: str, all_links: List[Tuple[str, str]]) -> str:
    if not all_links:
        return content
    present_urls = set(re.findall(r"https?://\S+", content or ""))
    missing = [(t, u) for (t, u) in all_links if u and u not in present_urls]
    if not missing:
        return content
    lines = ["【文档链接】"]
    for t, u in missing:
        lines.append(f"{t}\t{u}")
    extra = "\n".join(lines)
    if content.strip():
        return content.rstrip() + "\n\n" + extra
    return extra


def fetch_html(session: requests.Session, url: str, timeout_s: float) -> str:
    r = session.get(url, timeout=timeout_s)
    r.raise_for_status()
    raw = r.content or b""

    COMMON_HITS = ["新闻", "传播", "学院", "通知", "公告", "学生", "关于", "工作", "活动"]

    def metrics(t: str) -> Tuple[int, int, int]:
        repl = t.count("\ufffd")
        cjk = sum(1 for ch in t if "\u4e00" <= ch <= "\u9fff")
        hits = sum(t.count(w) for w in COMMON_HITS)
        return hits, cjk, repl

    # 站点可能未正确声明编码；避免把 ISO-8859-1 这种“零替换但乱码”的编码当成最优
    candidates: List[str] = []
    apparent = (r.apparent_encoding or "").strip().lower()
    if apparent and apparent not in candidates:
        candidates.append(apparent)
    for enc in ["utf-8", "gb18030"]:
        if enc not in candidates:
            candidates.append(enc)
    header_enc = (r.encoding or "").strip().lower()
    if header_enc and header_enc not in {"iso-8859-1", "latin-1"} and header_enc not in candidates:
        candidates.append(header_enc)

    best_text = None
    best_hits = -1
    best_cjk = -1
    best_repl = 10**18
    for enc in candidates:
        try:
            t = raw.decode(enc, errors="replace")
        except Exception:
            continue
        hits, cjk, repl = metrics(t)
        if (hits > best_hits) or (hits == best_hits and cjk > best_cjk) or (
            hits == best_hits and cjk == best_cjk and repl < best_repl
        ):
            best_text = t
            best_hits = hits
            best_cjk = cjk
            best_repl = repl

    return best_text or raw.decode("utf-8", errors="replace")


def parse_list_page(html: str) -> Tuple[List[Tuple[str, str, Optional[date]]], Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    items: List[Tuple[str, str, Optional[date]]] = []
    # 兼容两类结构：
    # 1) ul.news_list / li.news / span.news_title a + span.news_meta
    # 2) .wp_article_list / li.list_item / .Article_Title a + .Article_PublishDate
    ul = soup.select_one("ul.news_list")
    if ul:
        for li in ul.select("li.news"):
            a = li.select_one("span.news_title a")
            meta = li.select_one("span.news_meta")
            if not a:
                continue
            title = a.get_text(strip=True)
            href = normalize_abs_url(a.get("href") or "")
            d = parse_yyyy_mm_dd(meta.get_text(" ", strip=True) if meta else "")
            if title and href:
                items.append((title, href, d))
    else:
        for li in soup.select(".wp_article_list li"):
            a = li.select_one(".Article_Title a") or li.find("a")
            d_el = li.select_one(".Article_PublishDate")
            if not a:
                continue
            title = a.get_text(strip=True)
            href = normalize_abs_url(a.get("href") or "")
            d = parse_yyyy_mm_dd(d_el.get_text(" ", strip=True) if d_el else "")
            if title and href:
                items.append((title, href, d))
    next_url = None
    next_a = soup.select_one("a.next")
    if next_a:
        href = (next_a.get("href") or "").strip()
        # 有些页最后一页会是 javascript:void(0) 或空链接
        if href and not href.lower().startswith("javascript:"):
            abs_u = normalize_abs_url(href)
            # 仅接受列表分页链接，避免抓到无关导航
            if re.search(r"/183/list(\d*)?\.htm$", abs_u):
                next_url = abs_u
    return items, next_url


def parse_detail(html: str, url: str, list_date: Optional[date], logger: logging.Logger) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.select_one("h1.arti_title")
    title = title_el.get_text(strip=True) if title_el else None

    publish_time = None
    # 优先从详情元数据里抓取日期
    meta_candidates = []
    for sel in ["span.arti_update", "span.arti_publisher", "div.arti_metas", "div.arti_info"]:
        el = soup.select_one(sel)
        if el:
            meta_candidates.append(el.get_text(" ", strip=True))
    meta_text = " ".join(meta_candidates)
    publish_d = parse_yyyy_mm_dd(meta_text) if meta_text else None
    if publish_d:
        publish_time = date_to_str(publish_d)
    elif list_date:
        publish_time = date_to_str(list_date)
        logger.warning("publish_time fallback to list date for %s", url)
    else:
        logger.warning("publish_time missing for %s", url)

    container = find_detail_container(soup)
    content = ""
    deadline = None
    if container:
        content, _seen = extract_document_and_image_mentions(container)
        all_links = collect_all_doc_links(container)
        content = append_doc_link_block_if_missing(content, all_links)
        deadline = parse_deadline(content)
    else:
        logger.warning("detail container not found for %s", url)

    return {
        "title": title,
        "publish_time": publish_time,
        "deadline": deadline,
        "content": content,
    }


def upsert_notice_ignore(
    conn: sqlite3.Connection,
    *,
    title: str,
    url: str,
    publish_time: Optional[str],
    deadline: Optional[str],
    content: str,
    source: str,
) -> bool:
    now = utc_now_iso()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO notices (
          title, url, source, publish_time, crawl_time, deadline, category,
          content, keywords, tags, spider_name, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            url,
            source or DEFAULT_SOURCE,
            publish_time,
            now,
            deadline,
            CATEGORY,
            content,
            "[]",
            "[]",
            SPIDER_NAME,
            now,
            now,
        ),
    )
    inserted = cur.rowcount > 0
    conn.commit()
    return inserted


def crawl(
    *,
    mode: str,
    db_path: str,
    max_pages: Optional[int],
    source: str,
    http: HttpConfig,
) -> None:
    logger = logging.getLogger(SPIDER_NAME)
    session = make_session()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_db(conn)

    max_db_date = get_max_publish_time(conn) if mode == "incremental" else None
    if mode == "incremental":
        logger.info("incremental mode: max publish_time in db = %s", date_to_str(max_db_date))

    next_url = LIST_ENTRY
    page = 0
    inserted_cnt = 0
    scanned_cnt = 0
    stop_by_incremental = False

    while next_url:
        page += 1
        if max_pages and page > max_pages:
            break

        sleep_jitter(http.list_delay_s)
        html = fetch_html(session, next_url, http.timeout_s)
        items, parsed_next = parse_list_page(html)

        if not items:
            logger.warning("no items parsed on %s", next_url)

        for list_title, detail_url, list_d in items:
            scanned_cnt += 1

            # 增量：若列表日期已不晚于库最大时间，则可停止（但仅当列表日期可靠）
            if mode == "incremental" and max_db_date and list_d and list_d <= max_db_date:
                stop_by_incremental = True
                break

            # 全量：按时间窗口过滤（用列表日期作粗筛；详情页最终判定）
            if mode == "full" and list_d and not within_window(list_d):
                continue

            # 抓详情（带重试）
            detail_html = None
            for attempt in range(http.detail_retry):
                try:
                    sleep_jitter(http.detail_delay_s)
                    detail_html = fetch_html(session, detail_url, http.timeout_s)
                    break
                except Exception as e:
                    logger.warning("detail fetch failed (%s/%s) %s: %s", attempt + 1, http.detail_retry, detail_url, e)
                    if attempt + 1 < http.detail_retry:
                        sleep_jitter(http.detail_retry_delay_s)
            if not detail_html:
                continue

            detail = parse_detail(detail_html, detail_url, list_d, logger)
            title = (detail.get("title") or list_title or "").strip()
            publish_time_str = (detail.get("publish_time") or "").strip() or None
            publish_d = parse_yyyy_mm_dd(publish_time_str) if publish_time_str else None

            # 最终按时间窗口过滤
            if not publish_d:
                # 没有日期：全量不入库；增量也不入库（避免污染 max）
                logger.warning("skip due to missing publish_time: %s", detail_url)
                continue
            if not within_window(publish_d):
                continue
            if mode == "incremental" and max_db_date and publish_d <= max_db_date:
                # 严格执行“只抓晚于库最大 publish_time”
                continue

            inserted = upsert_notice_ignore(
                conn,
                title=title,
                url=detail_url,
                publish_time=date_to_str(publish_d),
                deadline=detail.get("deadline"),
                content=detail.get("content") or "",
                source=source or DEFAULT_SOURCE,
            )
            if inserted:
                inserted_cnt += 1

        if stop_by_incremental:
            logger.info("incremental stop: reached items not newer than db max publish_time")
            break

        next_url = parsed_next

    logger.info("done. scanned=%s inserted=%s pages=%s", scanned_cnt, inserted_cnt, page)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="HBUE xwcb notices spider (list+detail).")
    p.add_argument("--mode", choices=["full", "incremental"], required=True)
    p.add_argument("--db", default="notices.db", help="sqlite db path")
    p.add_argument("--max-pages", type=int, default=None, help="limit pages for debug")
    p.add_argument("--source", default=DEFAULT_SOURCE)
    p.add_argument("--list-delay", type=float, default=1.0)
    p.add_argument("--detail-delay", type=float, default=1.0)
    p.add_argument("--detail-retry", type=int, default=3)
    p.add_argument("--detail-retry-delay", type=float, default=2.0)
    p.add_argument("--log", default="spider.log")
    return p


def setup_logging(log_path: str) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.handlers.clear()
    logger.addHandler(sh)
    logger.addHandler(fh)


def main() -> None:
    args = build_arg_parser().parse_args()
    setup_logging(args.log)
    http = HttpConfig(
        list_delay_s=args.list_delay,
        detail_delay_s=args.detail_delay,
        detail_retry=args.detail_retry,
        detail_retry_delay_s=args.detail_retry_delay,
    )
    crawl(
        mode=args.mode,
        db_path=args.db,
        max_pages=args.max_pages,
        source=args.source,
        http=http,
    )


if __name__ == "__main__":
    main()
