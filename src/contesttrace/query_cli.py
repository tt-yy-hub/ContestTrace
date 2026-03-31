from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .db import SQLiteDB
from .utils import setup_logger


def _print_table(rows: List[Dict[str, Any]], limit: int = 50) -> None:
    """
    纯控制台表格输出（不依赖额外库，新手环境更稳）。
    """

    if not rows:
        print("（无数据）")
        return

    show = rows[:limit]
    headers = ["id", "publish_date", "title", "status"]
    widths = {h: len(h) for h in headers}
    for r in show:
        widths["id"] = max(widths["id"], len(str(r.get("id", ""))))
        widths["publish_date"] = max(widths["publish_date"], len(str(r.get("publish_date", ""))))
        widths["title"] = max(widths["title"], min(40, len(str(r.get("title", "")))))
        widths["status"] = max(widths["status"], len(str(r.get("status", ""))))

    def cut(s: str, n: int) -> str:
        return s if len(s) <= n else s[: n - 1] + "…"

    line = "+".join(["-" * (widths[h] + 2) for h in headers])
    print(line)
    print(
        " | ".join(
            [
                str(h).ljust(widths[h])
                for h in headers
            ]
        )
    )
    print(line)
    for r in show:
        print(
            " | ".join(
                [
                    str(r.get("id", "")).ljust(widths["id"]),
                    str(r.get("publish_date", "")).ljust(widths["publish_date"]),
                    cut(str(r.get("title", "")), 40).ljust(widths["title"]),
                    str(r.get("status", "")).ljust(widths["status"]),
                ]
            )
        )
    print(line)
    if len(rows) > limit:
        print(f"（已显示前 {limit} 条，共 {len(rows)} 条）")


def _print_detail(row: Dict[str, Any]) -> None:
    """按ID查看完整详情（新手友好）。"""

    if not row:
        print("未找到该ID对应的数据。")
        return

    fields = [
        ("ID", row.get("id")),
        ("通知标题", row.get("title")),
        ("发布时间", row.get("publish_date")),
        ("详情链接", row.get("detail_url")),
        ("主办单位", row.get("organizer")),
        ("赛事级别", row.get("competition_level")),
        ("参赛对象", row.get("target_audience")),
        ("报名截止时间", row.get("signup_deadline")),
        ("作品提交截止时间", row.get("submission_deadline")),
        ("比赛时间", row.get("competition_time")),
        ("核心参赛要求", row.get("requirements")),
        ("奖项设置", row.get("awards")),
        ("联系方式", row.get("contact")),
        ("发布人/来源", row.get("publisher")),
        ("更新时间", row.get("update_time")),
        ("处理状态", row.get("status")),
        ("爬取时间", row.get("crawled_at")),
    ]

    print("=" * 80)
    for k, v in fields:
        if v is None or str(v).strip() == "":
            continue
        print(f"{k}：{v}")
    print("-" * 80)
    print("通知全文：")
    print(row.get("full_text") or "（空）")
    print("=" * 80)


def run_query_cli(db: SQLiteDB) -> None:
    """
    控制台菜单式交互：
    - 查看列表
    - 标题关键词搜索
    - 按ID查看详情
    - 数据统计
    - 更新处理状态
    """

    while True:
        print("\n湖北经济学院团委竞赛信息追踪系统 - 查询菜单")
        print("1) 查看最近公告列表（默认前200条）")
        print("2) 按标题关键词搜索")
        print("3) 按ID查看公告完整详情")
        print("4) 查看数据统计")
        print("5) 更新处理状态（new -> done 等）")
        print("0) 退出")

        choice = input("请输入数字选择：").strip()

        if choice == "0":
            print("已退出。")
            return

        if choice == "1":
            rows = db.query_all(limit=200)
            _print_table(rows, limit=50)
            continue

        if choice == "2":
            kw = input("请输入关键词：").strip()
            if not kw:
                print("关键词不能为空。")
                continue
            rows = db.query_by_keyword(kw, limit=200)
            _print_table(rows, limit=50)
            continue

        if choice == "3":
            sid = input("请输入ID：").strip()
            if not sid.isdigit():
                print("ID必须是数字。")
                continue
            with db.connect() as conn:
                row = conn.execute(f"SELECT * FROM {db.table_name} WHERE id = ?;", (int(sid),)).fetchone()
                _print_detail(dict(row) if row else {})
            continue

        if choice == "4":
            st = db.stats()
            print(f"总数：{st.get('total')}")
            print(f"未处理：{st.get('unprocessed')}")
            print("按月统计（近24个月）：")
            for x in st.get("by_month") or []:
                print(f"- {x.get('month')}: {x.get('count')}")
            continue

        if choice == "5":
            sid = input("请输入要更新的ID：").strip()
            if not sid.isdigit():
                print("ID必须是数字。")
                continue
            status = input("请输入新的状态（例如 new / done / ignored）：").strip()
            if not status:
                print("状态不能为空。")
                continue
            ok = db.update_status(int(sid), status)
            print("更新成功。" if ok else "更新失败（ID不存在或数据库异常）。")
            continue

        print("无效选择，请重新输入。")


def main() -> None:
    """脚本入口：新手直接运行即可打开菜单。"""

    from .config_center import load_config

    cfg = load_config()
    logger = setup_logger(cfg.paths.logs_dir)
    db = SQLiteDB(cfg.paths.db_path, cfg.database.get("table_name") or "contest_announcements")
    db.init_db(logger)

    run_query_cli(db)


if __name__ == "__main__":
    main()

