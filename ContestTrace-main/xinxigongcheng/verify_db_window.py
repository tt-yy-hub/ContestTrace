from __future__ import annotations

import sqlite3
from pathlib import Path


def main() -> None:
    db = Path(__file__).resolve().parent / "data" / "notices.db"
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    spider = "hbue_ie_notice_spider"

    count, min_pt, max_pt = cur.execute(
        "SELECT COUNT(*), MIN(publish_time), MAX(publish_time) FROM notices WHERE spider_name=?",
        (spider,),
    ).fetchone()
    print("count,min,max=", (count, min_pt, max_pt))

    (out_of_window,) = cur.execute(
        "SELECT COUNT(*) FROM notices WHERE spider_name=? AND (publish_time < ? OR publish_time > ?)",
        (spider, "2025-01-01", "2026-04-09"),
    ).fetchone()
    print("out_of_window=", out_of_window)

    rows = cur.execute(
        "SELECT publish_time, title, url FROM notices WHERE spider_name=? ORDER BY publish_time DESC, id DESC LIMIT 5",
        (spider,),
    ).fetchall()
    print("newest5:")
    for pt, title, url in rows:
        print(pt, (title or "")[:50], url)

    conn.close()


if __name__ == "__main__":
    main()

