from __future__ import annotations

import datetime as dt
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .utils import ensure_dir


@dataclass(frozen=True)
class DbStats:
    """入库统计（新手可直接看懂）。"""

    inserted: int = 0
    skipped: int = 0
    failed: int = 0


class SQLiteDB:
    """
    SQLite数据库操作模块：
    - 自动初始化（启动检测，不存在则创建）
    - 上下文管理器（连接自动关闭）
    - 事务提交/回滚
    - 单条数据错误不影响整体运行
    """

    def __init__(self, db_path: Path, table_name: str = "contest_announcements") -> None:
        self.db_path = Path(db_path)
        self.table_name = table_name

    @contextmanager
    def connect(self) -> Iterable[sqlite3.Connection]:
        """上下文管理器：自动打开/关闭连接。"""

        ensure_dir(self.db_path.parent)
        conn = sqlite3.connect(str(self.db_path), timeout=30)
        try:
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            conn.close()

    def init_db(self, logger) -> None:
        """自动初始化：检测并创建表与索引。"""

        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,
            publish_date TEXT,
            detail_url TEXT NOT NULL UNIQUE,

            organizer TEXT,
            competition_level TEXT,
            target_audience TEXT,
            signup_deadline TEXT,
            submission_deadline TEXT,
            competition_time TEXT,
            requirements TEXT,
            awards TEXT,
            contact TEXT,

            publisher TEXT,
            update_time TEXT,
            full_text TEXT,

            crawled_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new'
        );
        """
        with self.connect() as conn:
            try:
                conn.execute(create_sql)
                conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_publish_date ON {self.table_name}(publish_date);")
                conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_status ON {self.table_name}(status);")
                conn.commit()
                logger.info(f"数据库初始化完成：{self.db_path}")
            except Exception as e:
                conn.rollback()
                logger.error(f"数据库初始化失败：{type(e).__name__}: {e}")
                raise

    def exists_by_url(self, detail_url: str) -> bool:
        """以详情URL为唯一键严格去重。"""

        sql = f"SELECT 1 FROM {self.table_name} WHERE detail_url = ? LIMIT 1;"
        with self.connect() as conn:
            cur = conn.execute(sql, (detail_url,))
            return cur.fetchone() is not None

    def insert_one(self, item: Dict[str, Any], logger) -> bool:
        """
        去重写入（单条）：
        - URL重复 -> 返回 False
        - 写入成功 -> True
        - 写入失败 -> False（并记录日志）
        """

        if not item.get("detail_url"):
            logger.warning("跳过写入：detail_url为空")
            return False

        if self.exists_by_url(item["detail_url"]):
            return False

        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "title": item.get("title"),
            "publish_date": item.get("publish_date"),
            "detail_url": item.get("detail_url"),
            "organizer": item.get("organizer"),
            "competition_level": item.get("competition_level"),
            "target_audience": item.get("target_audience"),
            "signup_deadline": item.get("signup_deadline"),
            "submission_deadline": item.get("submission_deadline"),
            "competition_time": item.get("competition_time"),
            "requirements": item.get("requirements"),
            "awards": item.get("awards"),
            "contact": item.get("contact"),
            "publisher": item.get("publisher"),
            "update_time": item.get("update_time"),
            "full_text": item.get("full_text"),
            "crawled_at": now,
            "status": item.get("status") or "new",
        }

        cols = ", ".join(payload.keys())
        placeholders = ", ".join(["?"] * len(payload))
        sql = f"INSERT INTO {self.table_name} ({cols}) VALUES ({placeholders});"

        with self.connect() as conn:
            try:
                conn.execute("BEGIN;")
                conn.execute(sql, tuple(payload.values()))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                conn.rollback()
                return False
            except Exception as e:
                conn.rollback()
                logger.error(f"写入失败：{payload.get('title')} | {type(e).__name__}: {e}")
                return False

    def insert_many(self, items: List[Dict[str, Any]], logger) -> DbStats:
        """批量写入：逐条容错统计，单条错误不影响整体。"""

        stats = DbStats()
        for item in items:
            try:
                ok = self.insert_one(item, logger)
                if ok:
                    stats = DbStats(inserted=stats.inserted + 1, skipped=stats.skipped, failed=stats.failed)
                else:
                    stats = DbStats(inserted=stats.inserted, skipped=stats.skipped + 1, failed=stats.failed)
            except Exception:
                stats = DbStats(inserted=stats.inserted, skipped=stats.skipped, failed=stats.failed + 1)
        return stats

    def query_all(self, limit: int = 200) -> List[Dict[str, Any]]:
        """全量查询（默认只取前200条防止刷屏）。"""

        sql = f"SELECT * FROM {self.table_name} ORDER BY publish_date DESC, id DESC LIMIT ?;"
        with self.connect() as conn:
            rows = conn.execute(sql, (int(limit),)).fetchall()
            return [dict(r) for r in rows]

    def query_by_keyword(self, keyword: str, limit: int = 200) -> List[Dict[str, Any]]:
        """条件查询：标题关键词。"""

        kw = f"%{keyword.strip()}%"
        sql = f"SELECT * FROM {self.table_name} WHERE title LIKE ? ORDER BY publish_date DESC, id DESC LIMIT ?;"
        with self.connect() as conn:
            rows = conn.execute(sql, (kw, int(limit))).fetchall()
            return [dict(r) for r in rows]

    def query_by_date_range(self, start_date: str, end_date: str, limit: int = 2000) -> List[Dict[str, Any]]:
        """条件查询：时间范围（YYYY-MM-DD）。"""

        sql = f"""
        SELECT * FROM {self.table_name}
        WHERE publish_date >= ? AND publish_date <= ?
        ORDER BY publish_date DESC, id DESC
        LIMIT ?;
        """
        with self.connect() as conn:
            rows = conn.execute(sql, (start_date, end_date, int(limit))).fetchall()
            return [dict(r) for r in rows]

    def query_unprocessed(self, limit: int = 2000) -> List[Dict[str, Any]]:
        """未处理数据查询（status != done）。"""

        sql = f"SELECT * FROM {self.table_name} WHERE status != 'done' ORDER BY publish_date DESC, id DESC LIMIT ?;"
        with self.connect() as conn:
            rows = conn.execute(sql, (int(limit),)).fetchall()
            return [dict(r) for r in rows]

    def update_status(self, item_id: int, status: str) -> bool:
        """更新处理状态。"""

        sql = f"UPDATE {self.table_name} SET status = ? WHERE id = ?;"
        with self.connect() as conn:
            try:
                conn.execute("BEGIN;")
                cur = conn.execute(sql, (status, int(item_id)))
                conn.commit()
                return cur.rowcount > 0
            except Exception:
                conn.rollback()
                return False

    def stats(self) -> Dict[str, Any]:
        """数据统计：总数、未处理数、按月份统计。"""

        with self.connect() as conn:
            total = conn.execute(f"SELECT COUNT(1) AS c FROM {self.table_name};").fetchone()["c"]
            unprocessed = conn.execute(
                f"SELECT COUNT(1) AS c FROM {self.table_name} WHERE status != 'done';"
            ).fetchone()["c"]
            by_month = conn.execute(
                f"""
                SELECT SUBSTR(COALESCE(publish_date,''), 1, 7) AS ym, COUNT(1) AS c
                FROM {self.table_name}
                GROUP BY ym
                ORDER BY ym DESC
                LIMIT 24;
                """
            ).fetchall()
            return {
                "total": int(total or 0),
                "unprocessed": int(unprocessed or 0),
                "by_month": [{"month": r["ym"] or "未知", "count": int(r["c"] or 0)} for r in by_month],
            }

