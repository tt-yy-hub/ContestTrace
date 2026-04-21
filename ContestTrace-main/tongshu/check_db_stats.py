from __future__ import annotations

import sqlite3
from pathlib import Path


def main() -> None:
    db_path = Path(__file__).resolve().parent / "data" / "notices.db"
    if not db_path.is_file():
        raise SystemExit(f"DB not found: {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        max_pub, total = conn.execute(
            """
            SELECT MAX(publish_time), COUNT(*)
            FROM notices
            WHERE spider_name = 'hbue_tsxy_notice_spider'
              AND publish_time != ''
            """
        ).fetchone()

        in_window = conn.execute(
            """
            SELECT COUNT(*)
            FROM notices
            WHERE spider_name = 'hbue_tsxy_notice_spider'
              AND publish_time >= '2025-01-01'
              AND publish_time <= '2026-04-09'
            """
        ).fetchone()[0]

        print({"max_publish_time": max_pub, "count_non_empty_publish_time": total, "count_in_window": in_window})
    finally:
        conn.close()


if __name__ == "__main__":
    main()

