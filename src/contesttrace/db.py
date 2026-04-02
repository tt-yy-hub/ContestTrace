# -*- coding: utf-8 -*-
"""
SQLite 数据库模块：竞赛主表 + 用户画像/收藏/订阅/推荐反馈。

特性：
- 启动时自动建表、自动迁移新增列（ALTER TABLE）
- URL 唯一去重（detail_url）
- 上下文管理器管理连接，单条失败不影响批量
"""

from __future__ import annotations

import datetime as dt
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .utils import ensure_dir


@dataclass(frozen=True)
class DbStats:
    """入库统计。"""

    inserted: int = 0
    skipped: int = 0
    failed: int = 0


# 竞赛表新增列（老库自动 ALTER）
MIGRATION_COLUMNS: Dict[str, str] = {
    "source_site_id": "TEXT DEFAULT ''",
    "event_name": "TEXT",
    "undertaker": "TEXT",
    "competition_category": "TEXT",
    "attachments_json": "TEXT",
    "content_hash": "TEXT",
    "tags": "TEXT",
    "ml_is_competition": "TEXT",
    "ml_category_abc": "TEXT",
}


class SQLiteDB:
    """SQLite 封装。"""

    def __init__(self, db_path: Path, table_name: str = "contest_announcements") -> None:
        self.db_path = Path(db_path)
        self.table_name = table_name

    @contextmanager
    def connect(self) -> Iterable[sqlite3.Connection]:
        """打开连接，用完关闭。"""

        ensure_dir(self.db_path.parent)
        conn = sqlite3.connect(str(self.db_path), timeout=60)
        try:
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            conn.close()

    def _migrate_table(self, conn: sqlite3.Connection, logger) -> None:
        """为竞赛主表补齐缺失列。"""

        try:
            rows = conn.execute(f"PRAGMA table_info({self.table_name});").fetchall()
            existing = {r[1] for r in rows}
            for col, decl in MIGRATION_COLUMNS.items():
                if col not in existing:
                    try:
                        conn.execute(f"ALTER TABLE {self.table_name} ADD COLUMN {col} {decl};")
                        logger.info(f"数据库迁移：已添加列 {col}")
                    except Exception as e:
                        logger.warning(f"迁移列失败 {col}：{e}")
        except Exception as e:
            logger.warning(f"迁移检查失败：{e}")

    def init_db(self, logger) -> None:
        """建表 + 迁移 + 辅助表。"""

        create_main = f"""
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
        create_users = """
        CREATE TABLE IF NOT EXISTS app_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            profile_json TEXT,
            created_at TEXT NOT NULL
        );
        """
        create_fav = """
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            contest_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, contest_id)
        );
        """
        create_sub = """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            email TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            last_notified_at TEXT,
            created_at TEXT NOT NULL
        );
        """
        create_fb = """
        CREATE TABLE IF NOT EXISTS recommend_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            contest_id INTEGER NOT NULL,
            vote INTEGER NOT NULL,
            nl_query TEXT,
            created_at TEXT NOT NULL
        );
        """

        with self.connect() as conn:
            try:
                conn.execute(create_main)
                conn.execute(
                    f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_publish_date ON {self.table_name}(publish_date);"
                )
                conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_name}_status ON {self.table_name}(status);")
                self._migrate_table(conn, logger)
                conn.execute(create_users)
                conn.execute(create_fav)
                conn.execute(create_sub)
                conn.execute(create_fb)
                conn.execute("INSERT OR IGNORE INTO app_users (id, username, profile_json, created_at) VALUES (1, 'default', '{}', datetime('now'));")
                conn.commit()
                logger.info(f"数据库初始化完成：{self.db_path}")
            except Exception as e:
                conn.rollback()
                logger.error(f"数据库初始化失败：{type(e).__name__}: {e}")
                raise

    def exists_by_url(self, detail_url: str) -> bool:
        """URL 去重。"""

        sql = f"SELECT 1 FROM {self.table_name} WHERE detail_url = ? LIMIT 1;"
        with self.connect() as conn:
            cur = conn.execute(sql, (detail_url,))
            return cur.fetchone() is not None

    def find_by_content_hash(self, h: str) -> Optional[int]:
        """内容哈希去重辅助：若已存在相同正文哈希则返回行 id。"""

        if not h:
            return None
        sql = f"SELECT id FROM {self.table_name} WHERE content_hash = ? LIMIT 1;"
        with self.connect() as conn:
            row = conn.execute(sql, (h,)).fetchone()
            return int(row["id"]) if row else None

    def insert_one(self, item: Dict[str, Any], logger) -> bool:
        """插入一条竞赛记录（字段齐全时写入扩展列）。"""

        if not item.get("detail_url"):
            logger.warning("跳过写入：detail_url为空")
            return False
        if self.exists_by_url(item["detail_url"]):
            return False

        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload: Dict[str, Any] = {
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
            "source_site_id": item.get("source_site_id") or "",
            "event_name": item.get("event_name"),
            "undertaker": item.get("undertaker"),
            "competition_category": item.get("competition_category"),
            "attachments_json": item.get("attachments_json"),
            "content_hash": item.get("content_hash"),
            "tags": item.get("tags"),
            "ml_is_competition": item.get("ml_is_competition"),
            "ml_category_abc": item.get("ml_category_abc"),
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
        """批量插入，逐条容错统计。"""

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

    def update_row(self, row_id: int, fields: Dict[str, Any], logger) -> bool:
        """按 id 更新部分字段（数据处理/ML 回写）。"""

        if not fields:
            return False
        sets = ", ".join([f"{k} = ?" for k in fields.keys()])
        vals = list(fields.values()) + [row_id]
        sql = f"UPDATE {self.table_name} SET {sets} WHERE id = ?;"
        with self.connect() as conn:
            try:
                conn.execute("BEGIN;")
                cur = conn.execute(sql, vals)
                conn.commit()
                return cur.rowcount > 0
            except Exception as e:
                conn.rollback()
                logger.warning(f"更新失败 id={row_id}：{e}")
                return False

    def get_by_id(self, row_id: int) -> Optional[Dict[str, Any]]:
        """按主键取一条。"""

        sql = f"SELECT * FROM {self.table_name} WHERE id = ?;"
        with self.connect() as conn:
            row = conn.execute(sql, (int(row_id),)).fetchone()
            return dict(row) if row else None

    def query_all(self, limit: int = 200) -> List[Dict[str, Any]]:
        sql = f"SELECT * FROM {self.table_name} ORDER BY publish_date DESC, id DESC LIMIT ?;"
        with self.connect() as conn:
            rows = conn.execute(sql, (int(limit),)).fetchall()
            return [dict(r) for r in rows]

    def query_filtered(
        self,
        *,
        keyword: str = "",
        level: str = "",
        category: str = "",
        start_date: str = "",
        end_date: str = "",
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """多条件筛选（供 Streamlit）。"""

        where: List[str] = ["1=1"]
        args: List[Any] = []
        if keyword.strip():
            where.append("(title LIKE ? OR full_text LIKE ?)")
            k = f"%{keyword.strip()}%"
            args.extend([k, k])
        if level.strip():
            where.append("competition_level LIKE ?")
            args.append(f"%{level.strip()}%")
        if category.strip():
            where.append("competition_category LIKE ?")
            args.append(f"%{category.strip()}%")
        if start_date.strip():
            where.append("publish_date >= ?")
            args.append(start_date.strip())
        if end_date.strip():
            where.append("publish_date <= ?")
            args.append(end_date.strip())
        sql = f"""
        SELECT * FROM {self.table_name}
        WHERE {' AND '.join(where)}
        ORDER BY publish_date DESC, id DESC
        LIMIT ?;
        """
        args.append(int(limit))
        with self.connect() as conn:
            rows = conn.execute(sql, args).fetchall()
            return [dict(r) for r in rows]

    def query_by_keyword(self, keyword: str, limit: int = 200) -> List[Dict[str, Any]]:
        kw = f"%{keyword.strip()}%"
        sql = f"SELECT * FROM {self.table_name} WHERE title LIKE ? ORDER BY publish_date DESC, id DESC LIMIT ?;"
        with self.connect() as conn:
            rows = conn.execute(sql, (kw, int(limit))).fetchall()
            return [dict(r) for r in rows]

    def query_by_date_range(self, start_date: str, end_date: str, limit: int = 2000) -> List[Dict[str, Any]]:
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
        sql = f"SELECT * FROM {self.table_name} WHERE status != 'done' ORDER BY publish_date DESC, id DESC LIMIT ?;"
        with self.connect() as conn:
            rows = conn.execute(sql, (int(limit),)).fetchall()
            return [dict(r) for r in rows]

    def update_status(self, item_id: int, status: str) -> bool:
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

    # ---------- 用户 / 收藏 / 订阅 / 反馈 ----------

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        sql = "SELECT * FROM app_users WHERE id = ?;"
        with self.connect() as conn:
            row = conn.execute(sql, (int(user_id),)).fetchone()
            if not row:
                return {}
            d = dict(row)
            try:
                d["profile"] = json.loads(d.get("profile_json") or "{}")
            except Exception:
                d["profile"] = {}
            return d

    def save_user_profile(self, user_id: int, profile: Dict[str, Any], logger) -> bool:
        sql = "UPDATE app_users SET profile_json = ? WHERE id = ?;"
        try:
            pj = json.dumps(profile, ensure_ascii=False)
            with self.connect() as conn:
                conn.execute("BEGIN;")
                conn.execute(sql, (pj, int(user_id)))
                conn.commit()
            return True
        except Exception as e:
            logger.warning(f"保存用户画像失败：{e}")
            return False

    def list_favorites(self, user_id: int) -> List[int]:
        sql = "SELECT contest_id FROM favorites WHERE user_id = ? ORDER BY id DESC;"
        with self.connect() as conn:
            rows = conn.execute(sql, (int(user_id),)).fetchall()
            return [int(r["contest_id"]) for r in rows]

    def add_favorite(self, user_id: int, contest_id: int, logger) -> bool:
        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT OR IGNORE INTO favorites (user_id, contest_id, created_at) VALUES (?,?,?);"
        try:
            with self.connect() as conn:
                conn.execute(sql, (int(user_id), int(contest_id), now))
                conn.commit()
            return True
        except Exception as e:
            logger.warning(f"收藏失败：{e}")
            return False

    def remove_favorite(self, user_id: int, contest_id: int, logger) -> bool:
        sql = "DELETE FROM favorites WHERE user_id = ? AND contest_id = ?;"
        try:
            with self.connect() as conn:
                conn.execute(sql, (int(user_id), int(contest_id)))
                conn.commit()
            return True
        except Exception as e:
            logger.warning(f"取消收藏失败：{e}")
            return False

    def list_subscriptions(self, user_id: int) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM subscriptions WHERE user_id = ? AND active = 1;"
        with self.connect() as conn:
            rows = conn.execute(sql, (int(user_id),)).fetchall()
            return [dict(r) for r in rows]

    def add_subscription(self, user_id: int, keyword: str, email: str, logger) -> bool:
        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """
        INSERT INTO subscriptions (user_id, keyword, email, active, created_at)
        VALUES (?,?,?,1,?);
        """
        try:
            with self.connect() as conn:
                conn.execute(sql, (int(user_id), keyword.strip(), (email or "").strip(), now))
                conn.commit()
            return True
        except Exception as e:
            logger.warning(f"订阅失败：{e}")
            return False

    def add_recommend_feedback(
        self, user_id: int, contest_id: int, vote: int, nl_query: str, logger
    ) -> bool:
        """vote: 1 赞 -1 踩。"""

        now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """
        INSERT INTO recommend_feedback (user_id, contest_id, vote, nl_query, created_at)
        VALUES (?,?,?,?,?);
        """
        try:
            with self.connect() as conn:
                conn.execute(sql, (int(user_id), int(contest_id), int(vote), nl_query or "", now))
                conn.commit()
            return True
        except Exception as e:
            logger.warning(f"反馈记录失败：{e}")
            return False
