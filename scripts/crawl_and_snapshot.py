# -*- coding: utf-8 -*-
"""
CI/本地：运行爬虫并导出 CSV 快照到 data/reports（供 GitHub Actions 提交）。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from contesttrace.config_center import load_config  # noqa: E402
from contesttrace.db import SQLiteDB  # noqa: E402
from contesttrace.exporter import export_data  # noqa: E402
from contesttrace.scraper import run_crawl  # noqa: E402
from contesttrace.utils import ensure_dir, setup_logger  # noqa: E402


def main() -> None:
    cfg = load_config()
    logger = setup_logger(cfg.paths.logs_dir)
    ensure_dir(cfg.paths.reports_dir)
    summary = run_crawl(cfg)
    db = SQLiteDB(cfg.paths.db_path, cfg.database.get("table_name") or "contest_announcements")
    db.init_db(logger)
    out = cfg.paths.reports_dir / "latest_snapshot.csv"
    # 直接写 CSV 到固定文件名便于 Git 跟踪
    p = export_data(db, cfg.paths.reports_dir, logger, fmt="csv", scope="all")
    if p:
        try:
            import shutil

            shutil.copy(p, out)
        except Exception:
            pass
    else:
        try:
            out.write_text("id,title,publish_date,detail_url\n", encoding="utf-8-sig")
        except Exception:
            pass
    logger.info(f"快照完成 inserted={summary.inserted} path={out}")


if __name__ == "__main__":
    main()
