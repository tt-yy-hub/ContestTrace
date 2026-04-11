# -*- coding: utf-8 -*-
"""
仅更新 notices 表的 content 字段：按 url 重新请求详情页，用当前正文提取规则生成纯文本后写回。
正文规则与爬虫一致：整段可读文本 + 表格制表符 + 文档类链接（.jpg/.pdf/.doc/.docx/.xls/.xlsx）
在行内以「文本 绝对URL」出现，遗漏的链接在文末「【文档链接】」区按行列出（文本与 URL 以制表符分隔）。
同时更新 updated_at；其余字段不变。

用法：
  python update_content_only.py
  python update_content_only.py --db d:\\path\\to\\notices.db
  python update_content_only.py --id 3
  python update_content_only.py --limit 5
  python update_content_only.py --spider hbue_jrxy_notice_spider
"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from hbue_jrxy_notice_spider import (
    DEFAULT_DB_PATH,
    DETAIL_DELAY_SEC,
    DETAIL_RETRIES,
    DETAIL_RETRY_SLEEP_SEC,
    SPIDER_NAME,
    extract_content_from_html,
    fetch_html,
    session_factory,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("update_content_only")


def main() -> None:
    ap = argparse.ArgumentParser(description="仅更新数据库中的 content 字段")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="SQLite 数据库路径")
    ap.add_argument(
        "--spider",
        default=SPIDER_NAME,
        help="只处理 spider_name 等于该值的记录（默认与爬虫一致）",
    )
    ap.add_argument("--id", type=int, default=None, help="只更新指定主键 id")
    ap.add_argument("--limit", type=int, default=None, help="最多处理条数（调试用）")
    ap.add_argument(
        "--delay",
        type=float,
        default=DETAIL_DELAY_SEC,
        help="每条详情请求之间的间隔（秒）",
    )
    args = ap.parse_args()

    if not args.db.is_file():
        log.error("数据库不存在: %s", args.db)
        raise SystemExit(1)

    conn = sqlite3.connect(str(args.db))
    cur = conn.cursor()

    sql = "SELECT id, url FROM notices WHERE 1=1"
    params: list = []
    if args.spider:
        sql += " AND spider_name = ?"
        params.append(args.spider)
    if args.id is not None:
        sql += " AND id = ?"
        params.append(args.id)
    sql += " ORDER BY id"
    if args.limit is not None:
        sql += " LIMIT ?"
        params.append(args.limit)

    rows = cur.execute(sql, params).fetchall()
    if not rows:
        log.warning("没有匹配的记录")
        conn.close()
        return

    log.info("待更新 %s 条", len(rows))
    session = session_factory()
    ok = 0
    fail: list[tuple[int, str]] = []

    for i, (row_id, url) in enumerate(rows):
        if i > 0:
            time.sleep(args.delay)

        html = fetch_html(session, url, retries=DETAIL_RETRIES, retry_sleep=DETAIL_RETRY_SLEEP_SEC)
        if not html:
            fail.append((row_id, url))
            continue

        content = extract_content_from_html(html)
        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        cur.execute(
            "UPDATE notices SET content = ?, updated_at = ? WHERE id = ?",
            (content, now, row_id),
        )
        conn.commit()
        ok += 1
        log.info("已更新 id=%s len(content)=%s", row_id, len(content))

    log.info("完成: 成功 %s, 失败 %s", ok, len(fail))
    for row_id, url in fail:
        log.warning("失败 id=%s url=%s", row_id, url)

    conn.close()


if __name__ == "__main__":
    main()
