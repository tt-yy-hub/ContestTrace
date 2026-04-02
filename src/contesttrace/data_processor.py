# -*- coding: utf-8 -*-
"""
智能数据处理：时间归一化、赛事级别/类别映射、正文相似度去重辅助、缺失值简单填充。

参考文献思路：
- 字符串相似度：Python difflib.SequenceMatcher（Ratcliff/Obershelp 启发式，标准库文档）
- 文本分类：scikit-learn 朴素贝叶斯（教材常见基线）
"""

from __future__ import annotations

import difflib
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from .db import SQLiteDB
from .utils import normalize_datetime


def normalize_competition_level(raw: Optional[str]) -> Optional[str]:
    """将常见写法映射为 国家级/省级/校级。"""

    if not raw:
        return None
    s = str(raw).strip()
    mapping = [
        (r"国赛|国家级|全国", "国家级"),
        (r"省赛|省级|湖北省|全省", "省级"),
        (r"校赛|校级|校内|学校", "校级"),
    ]
    for pat, lab in mapping:
        if re.search(pat, s):
            return lab
    return s[:40] if s else None


def normalize_category_abc(raw: Optional[str]) -> Optional[str]:
    """提取 A/B/C 类标识。"""

    if not raw:
        return None
    s = str(raw).strip().upper()
    m = re.search(r"\b([ABC])\b", s)
    if m:
        return f"{m.group(1)}类"
    if "A类" in s:
        return "A类"
    if "B类" in s:
        return "B类"
    if "C类" in s:
        return "C类"
    return None


def text_similarity(a: str, b: str) -> float:
    """正文相似度 0~1。"""

    if not a or not b:
        return 0.0
    try:
        return difflib.SequenceMatcher(None, a[:8000], b[:8000]).ratio()
    except Exception:
        return 0.0


def process_row_fields(row: Dict[str, Any]) -> Dict[str, Any]:
    """单条记录清洗（不写库，仅返回待更新字段）。"""

    updates: Dict[str, Any] = {}
    try:
        lvl = normalize_competition_level(row.get("competition_level"))
        if lvl and lvl != row.get("competition_level"):
            updates["competition_level"] = lvl
        cat = normalize_category_abc(row.get("competition_category"))
        if cat:
            updates["competition_category"] = cat
        for key in ("signup_deadline", "submission_deadline", "competition_time", "publish_date"):
            v = row.get(key)
            if v:
                n = normalize_datetime(str(v))
                if n and n != v:
                    updates[key] = n
    except Exception:
        pass
    return updates


def run_batch_clean(db: SQLiteDB, logger: logging.Logger, limit: int = 500) -> int:
    """批量清洗并回写数据库。"""

    rows = db.query_all(limit=limit)
    n = 0
    for r in rows:
        try:
            uid = int(r["id"])
            upd = process_row_fields(r)
            if upd and db.update_row(uid, upd, logger):
                n += 1
        except Exception:
            continue
    logger.info(f"数据处理：批量清洗完成，更新 {n} 条")
    return n


def extract_tags_jieba(text: str, top_k: int = 8) -> str:
    """
    使用 jieba TF-IDF 提取关键词，返回逗号分隔标签字符串。
    失败时返回空字符串（不抛异常）。
    """

    if not text or not text.strip():
        return ""
    try:
        import jieba.analyse

        tags = jieba.analyse.extract_tags(text, topK=int(top_k))
        return ",".join(tags)
    except Exception:
        return ""


def run_jieba_tagging(db: SQLiteDB, logger: logging.Logger, limit: int = 200) -> int:
    """为无 tags 的记录补充关键词标签。"""

    rows = db.query_all(limit=limit)
    n = 0
    for r in rows:
        try:
            if r.get("tags"):
                continue
            tid = int(r["id"])
            tags = extract_tags_jieba(r.get("full_text") or r.get("title") or "")
            if tags and db.update_row(tid, {"tags": tags}, logger):
                n += 1
        except Exception:
            continue
    logger.info(f"Jieba 标签：更新 {n} 条")
    return n


def find_near_duplicate_pairs(
    rows: List[Dict[str, Any]], threshold: float = 0.92
) -> List[Tuple[int, int, float]]:
    """
    基于正文相似度找疑似重复对（O(n^2) 简化版，仅适合中小数据量）。
    返回 (id_a, id_b, score)。
    """

    pairs: List[Tuple[int, int, float]] = []
    n = len(rows)
    for i in range(n):
        for j in range(i + 1, n):
            try:
                ta = rows[i].get("full_text") or ""
                tb = rows[j].get("full_text") or ""
                sc = text_similarity(ta, tb)
                if sc >= threshold:
                    pairs.append((int(rows[i]["id"]), int(rows[j]["id"]), sc))
            except Exception:
                continue
    return pairs
