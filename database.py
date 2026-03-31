"""
兼容入口（保留旧文件名）：
- 初始化数据库并输出统计信息
"""

import sys
from pathlib import Path


def _bootstrap_src_path() -> None:
    root = Path(__file__).resolve().parent
    src = root / "src"
    if src.exists() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def init_db() -> None:
    _bootstrap_src_path()
    from contesttrace.config_center import load_config
    from contesttrace.db import SQLiteDB
    from contesttrace.utils import setup_logger

    cfg = load_config()
    logger = setup_logger(cfg.paths.logs_dir)
    db = SQLiteDB(cfg.paths.db_path, cfg.database.get("table_name") or "contest_announcements")
    db.init_db(logger)
    st = db.stats()
    logger.info(f"数据库统计：总数={st.get('total')}，未处理={st.get('unprocessed')}")


if __name__ == "__main__":
    init_db()