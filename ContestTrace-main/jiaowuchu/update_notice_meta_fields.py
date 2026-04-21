# -*- coding: utf-8 -*-
"""
针对湖北经济学院教务处 · 通知公告（已入库 title + content）提取并回写字段，不请求网络。
默认 spider_name = hbue_jwc_notice_spider。

用法：
  cd jiaowuchu
  python update_notice_meta_fields.py
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sqlite3
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

from hbue_jwc_notice_spider import DEFAULT_DB_PATH, SPIDER_NAME

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("update_notice_meta_fields")
logging.getLogger("jieba").setLevel(logging.WARNING)

TAG_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("选课排课", ("选课", "退选", "补选", "停开", "课表")),
    ("考试考务", ("考试", "考场", "缓考", "补考", "四六级", "学位英语")),
    ("学籍学位", ("学籍", "学位", "毕业", "结业", "肄业", "转学")),
    ("双学位辅修", ("双学位", "辅修", "微专业")),
    ("教学质量", ("教学评估", "督导", "评教", "教改")),
    ("竞赛项目", ("竞赛", "大创", "创新训练", "项目立项")),
    ("规章制度", ("管理办法", "规定", "细则", "制度")),
    ("材料申报", ("申报", "提交材料", "报名表")),
    ("联系方式可见", ("联系电话", "咨询邮箱", "办公地点")),
)

_SECTION_STOP_FOR_MULTILINE = (
    "主办单位",
    "主办方",
    "组织单位",
    "参赛对象",
    "参与人员",
    "申报范围",
    "奖项设置",
    "参赛要求",
    "申报条件",
    "需提交材料",
    "联系方式",
    "联系人",
    "咨询电话",
    "公示时间",
    "报名时间",
    "报名地点",
    "发布时间",
    "发布单位",
    "来源",
)


def _build_stop_pattern(exclude: frozenset[str]) -> str:
    parts = [re.escape(h) for h in _SECTION_STOP_FOR_MULTILINE if h not in exclude]
    return "(?:" + "|".join(parts) + ")" if parts else ""


def _extract_block_after_labels(text: str, labels: tuple[str, ...], exclude_stops: frozenset[str]) -> Optional[str]:
    if not text or not labels:
        return None
    labels_sorted = sorted(labels, key=len, reverse=True)
    alt = "|".join(re.escape(x) for x in labels_sorted)
    stop_pat = _build_stop_pattern(exclude_stops)
    if stop_pat:
        multi = re.compile(
            rf"(?:{alt})\s*[：:]\s*([\s\S]+?)(?=\n\s*{stop_pat}\s*[：:]|$)",
            re.MULTILINE,
        )
        m = multi.search(text)
        if m:
            val = re.sub(r"[\n\r\t]+", " ", m.group(1)).strip()
            val = re.sub(r" +", " ", val).strip()
            if _meaningful(val):
                return val
    line = re.compile(rf"(?:{alt})\s*[：:]\s*([^\n\r]+)")
    m = line.search(text)
    if m:
        val = m.group(1).strip()
        if _meaningful(val):
            return val
    return None


def _meaningful(s: str) -> bool:
    if not s:
        return False
    if s in ("无", "无。", "详见附件", "详见通知", "/", "——", "-"):
        return False
    return True


def extract_organizer(text: str) -> Optional[str]:
    return _extract_block_after_labels(
        text,
        ("主办单位", "主办方", "组织单位"),
        frozenset({"主办单位", "主办方", "组织单位"}),
    )


def extract_participants(text: str) -> Optional[str]:
    return _extract_block_after_labels(
        text,
        ("参赛对象", "参与人员", "申报范围"),
        frozenset({"参赛对象", "参与人员", "申报范围"}),
    )


def extract_prize(text: str) -> Optional[str]:
    for labels in (("奖项设置",), ("奖励",), ("奖金",)):
        v = _extract_block_after_labels(text, labels, frozenset(labels))
        if v:
            return v
    return None


def extract_requirement(text: str) -> Optional[str]:
    return _extract_block_after_labels(
        text,
        ("参赛要求", "申报条件", "需提交材料"),
        frozenset({"参赛要求", "申报条件", "需提交材料"}),
    )


def extract_contact(text: str) -> Optional[str]:
    labels = ("联系方式", "联系人", "咨询电话")
    alt = "|".join(re.escape(x) for x in sorted(labels, key=len, reverse=True))
    seen: set[str] = set()
    parts: list[str] = []
    for m in re.finditer(rf"(?:{alt})\s*[：:]\s*([^\n\r]+)", text):
        v = re.sub(r" +", " ", m.group(1).strip())
        if not _meaningful(v) or v in seen:
            continue
        seen.add(v)
        parts.append(v)
    if parts:
        return "；".join(parts)
    return _extract_block_after_labels(text, labels, frozenset(labels))


def extract_keywords_top5(title: str, content: str, head_chars: int = 500) -> str:
    try:
        import jieba
    except ImportError:
        return "[]"
    piece = f"{title or ''}\n{(content or '')[:head_chars]}"
    if not piece.strip():
        return "[]"
    stop = set(
        "的 了 和 与 或 在 是 为 有 等 及 对 中 其 将 由 可 请 各 本 院 学院 通知 公告 关于 开展 进行 根据 现将 以下 有关"
        .split()
    )
    filtered = [
        w.strip()
        for w in jieba.cut(piece)
        if len(w.strip()) > 1
        and w.strip() not in stop
        and not w.strip().isdigit()
        and not re.fullmatch(r"\d{4}年", w.strip())
    ]
    if not filtered:
        return "[]"
    cnt = Counter(filtered)
    return json.dumps([w for w, _ in cnt.most_common(5)], ensure_ascii=False)


def extract_tags(title: str, content: str) -> str:
    hay = f"{title or ''}\n{content or ''}"
    if not hay.strip():
        return "[]"
    tags = [name for name, triggers in TAG_RULES if any(t in hay for t in triggers)]
    return json.dumps(tags, ensure_ascii=False)


def compute_row(title: str, content: Optional[str]) -> tuple:
    text = content or ""
    return (
        extract_organizer(text),
        extract_participants(text),
        extract_prize(text),
        extract_requirement(text),
        extract_contact(text),
        extract_keywords_top5(title or "", text),
        extract_tags(title or "", text),
    )


UPDATE_SQL = """
UPDATE notices SET
    organizer = ?, participants = ?, prize = ?, requirement = ?, contact = ?,
    keywords = ?, tags = ?, updated_at = ?
WHERE id = ?
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="仅更新 organizer 等元数据与 keywords/tags")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--spider", default=SPIDER_NAME)
    ap.add_argument("--id", type=int, default=None)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    if not args.db.is_file():
        log.error("数据库不存在: %s", args.db)
        raise SystemExit(1)
    conn = sqlite3.connect(str(args.db))
    cur = conn.cursor()
    sql = "SELECT id, title, content FROM notices WHERE 1=1"
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
    now = datetime.now().isoformat(sep=" ", timespec="seconds")
    for row_id, title, content in rows:
        cur.execute(UPDATE_SQL, (*compute_row(title, content), now, row_id))
        log.info("已更新 id=%s", row_id)
    conn.commit()
    conn.close()
    log.info("完成，共 %s 条", len(rows))


if __name__ == "__main__":
    main()
