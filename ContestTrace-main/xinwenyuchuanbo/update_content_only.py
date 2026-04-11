import argparse
import logging
import random
import re
import sqlite3
import sys
import time
from datetime import datetime
from typing import Optional, Tuple, List
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


BASE = "https://xwcb.hbue.edu.cn/"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def utc_now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalize_abs_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return u
    return urljoin(BASE, u)


def is_doc_like(url: str) -> bool:
    path = (urlparse(url).path or "").lower()
    return any(
        path.endswith(ext)
        for ext in (".jpg", ".jpeg", ".pdf", ".doc", ".docx", ".xls", ".xlsx")
    )


def is_image(url: str) -> bool:
    path = (urlparse(url).path or "").lower()
    return any(path.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"))


def clean_text(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def sleep_jitter(base_s: float) -> None:
    base_s = max(0.0, float(base_s))
    jitter = random.uniform(-0.15, 0.15) * base_s
    time.sleep(max(0.0, base_s + jitter))


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


def fetch_html(session: requests.Session, url: str, timeout_s: float) -> str:
    r = session.get(url, timeout=timeout_s)
    r.raise_for_status()
    raw = r.content or b""

    COMMON_HITS = ["新闻", "传播", "学院", "通知", "公告", "学生", "关于", "工作", "活动"]

    def metrics(t: str):
        repl = t.count("\ufffd")
        cjk = sum(1 for ch in t if "\u4e00" <= ch <= "\u9fff")
        hits = sum(t.count(w) for w in COMMON_HITS)
        return hits, cjk, repl

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


def iter_text_nodes_in_order(node: Tag):
    for child in node.children:
        if isinstance(child, (NavigableString, Tag)):
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
    doc_seen: List[Tuple[str, str]] = []

    def render_inline(el):
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
                rows_out.append("\t".join([c for c in row_cells if c is not None]).rstrip())
            return "\n".join([r for r in rows_out if r.strip()])
        return render_block(el)

    def render_block(el):
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

    content = clean_text("\n\n".join(blocks))
    return content, doc_seen


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
            out.append(((img.get("alt") or "").strip() or "[图片]"), src)
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


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Update content only (+updated_at) by refetching detail pages.")
    p.add_argument("--db", default="notices.db")
    p.add_argument("--delay", type=float, default=1.0)
    p.add_argument("--retry", type=int, default=3)
    p.add_argument("--retry-delay", type=float, default=2.0)
    p.add_argument("--timeout", type=float, default=20.0)
    p.add_argument("--where-like", default=None, help="only update urls matching LIKE pattern")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--log", default="update_content_only.log")
    return p


def setup_logging(log_path: str) -> logging.Logger:
    logger = logging.getLogger("update_content_only")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.handlers.clear()
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger


def main() -> None:
    args = build_arg_parser().parse_args()
    logger = setup_logging(args.log)
    session = make_session()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    sql = "SELECT url FROM notices"
    params = []
    if args.where_like:
        sql += " WHERE url LIKE ?"
        params.append(args.where_like)
    sql += " ORDER BY id ASC"
    if args.limit:
        sql += " LIMIT ?"
        params.append(args.limit)

    urls = [r["url"] for r in conn.execute(sql, params).fetchall()]
    logger.info("loaded urls: %s", len(urls))

    updated = 0
    for url in urls:
        html = None
        for attempt in range(args.retry):
            try:
                sleep_jitter(args.delay)
                html = fetch_html(session, url, args.timeout)
                break
            except Exception as e:
                logger.warning("fetch failed (%s/%s) %s: %s", attempt + 1, args.retry, url, e)
                if attempt + 1 < args.retry:
                    sleep_jitter(args.retry_delay)
        if not html:
            continue

        soup = BeautifulSoup(html, "lxml")
        container = find_detail_container(soup)
        if not container:
            logger.warning("container not found: %s", url)
            continue

        content, _seen = extract_document_and_image_mentions(container)
        all_links = collect_all_doc_links(container)
        content = append_doc_link_block_if_missing(content, all_links)

        now = utc_now_iso()
        conn.execute(
            "UPDATE notices SET content = ?, updated_at = ? WHERE url = ?",
            (content, now, url),
        )
        conn.commit()
        updated += 1

    logger.info("done. updated=%s", updated)


if __name__ == "__main__":
    main()
