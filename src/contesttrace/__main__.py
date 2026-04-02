from __future__ import annotations

"""
主入口（新手友好）：
- 提供一个统一菜单：爬取 / 查询 / 导出 / 环境检查
"""


def main() -> None:
    while True:
        print("\nContestTrace 2.0 - 主菜单")
        print("1) 运行爬虫（多源抓取并入库）")
        print("2) 数据查询（菜单式）")
        print("3) 一键导出（Excel/CSV）")
        print("4) 环境检查")
        print("5) Web 前端说明（Streamlit）")
        print("0) 退出")

        choice = input("请输入数字选择：").strip()

        if choice == "0":
            print("已退出。")
            return

        if choice == "1":
            from .scraper import main as crawl_main

            crawl_main()
            continue

        if choice == "2":
            from .query_cli import main as query_main

            query_main()
            continue

        if choice == "3":
            from .config_center import load_config
            from .db import SQLiteDB
            from .exporter import export_data
            from .utils import setup_logger

            cfg = load_config()
            logger = setup_logger(cfg.paths.logs_dir)
            db = SQLiteDB(cfg.paths.db_path, cfg.database.get("table_name") or "contest_announcements")
            db.init_db(logger)

            print("导出格式：1) Excel(.xlsx)  2) CSV(.csv)")
            fmt_choice = input("请选择：").strip()
            fmt = "xlsx" if fmt_choice != "2" else "csv"

            print("导出范围：1) 全量  2) 时间范围  3) 未处理数据")
            scope_choice = input("请选择：").strip()
            if scope_choice == "2":
                start = input("开始日期（YYYY-MM-DD）：").strip()
                end = input("结束日期（YYYY-MM-DD）：").strip()
                export_data(db, cfg.paths.exports_dir, logger, fmt=fmt, scope="date_range", start_date=start, end_date=end)
            elif scope_choice == "3":
                export_data(db, cfg.paths.exports_dir, logger, fmt=fmt, scope="unprocessed")
            else:
                export_data(db, cfg.paths.exports_dir, logger, fmt=fmt, scope="all")
            continue

        if choice == "4":
            from .env_check import main as env_main

            env_main()
            continue

        if choice == "5":
            print("请在新终端运行：python run_web.py")
            print("或：python -m streamlit run src/contesttrace/web/app.py")
            continue

        print("无效选择，请重新输入。")


if __name__ == "__main__":
    main()

