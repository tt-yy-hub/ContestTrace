# -*- coding: utf-8 -*-
"""
仅更新 notices 表中结构化元数据字段（不请求网络，基于已有 title + content 解析）：

- organizer / participants / prize / requirement / contact：正文正则提取，无匹配存 NULL
- keywords：标题 + 正文前 500 字分词，词频 Top5 → JSON 数组；失败或无词存 "[]"
- tags：按下方 TAG_RULES 主题词命中打标签 → JSON 数组；无命中存 "[]"

同时更新 updated_at。

用法：
  python update_notice_meta_fields.py
  python update_notice_meta_fields.py --db d:\\path\\to\\notices.db --limit 10
  python update_notice_meta_fields.py --id 5
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

from hbue_jrxy_notice_spider import DEFAULT_DB_PATH, SPIDER_NAME

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("update_notice_meta_fields")
logging.getLogger("jieba").setLevel(logging.WARNING)

# ---------------------------------------------------------------------------
# 主题标签： (标签名, 触发词列表) — 标题或全文中任一触发词出现则打上该标签（可改规则）
# ---------------------------------------------------------------------------

TAG_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("研究生招生", ("硕士研究生", "硕士", "研究生", "复试", "拟录取", "调剂", "一志愿", "招生")),
    ("人才招聘", ("招聘", "专任教师", "博士后", "聘用")),
    ("奖学金资助", ("奖学金", "助学金", "励志奖学金", "国家奖学金")),
    ("评选公示", ("公示", "拟推荐", "初评", "评审结果", "评选结果")),
    ("荣誉称号", ("十佳", "五四", "优秀个人", "先进集体", "先进个人", "优秀团员")),
    ("竞赛活动", ("竞赛", "大赛", "挑战赛", "比赛")),
    ("教学教务", ("教学", "课程", "学业", "选课", "考试", "培养方案")),
    ("党建思政", ("党建", "清廉", "思政", "团支部")),
    ("材料申报", ("申报", "提交材料", "报名表", "申请材料")),
    ("联系方式可见", ("联系电话", "咨询邮箱", "办公地点")),
]

# 用于多行字段截断：遇到下列「下一小节」标题则停止（不含 prize 的短词「奖励」避免误切）
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
    if not parts:
        return ""
    return "(?:" + "|".join(parts) + ")"


def _extract_block_after_labels(text: str, labels: tuple[str, ...], exclude_stops: frozenset[str]) -> Optional[str]:
    """匹配 标签[：:] 后的内容；优先取到下一小节标题前的多行，否则取单行。"""
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
    if not s or len(s) < 1:
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
    # 「奖励」「奖金」较短，单行提取减少误匹配
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
    """合并正文中出现的联系方式 / 联系人 / 咨询电话 各行内容（去重）。"""
    labels = ("联系方式", "联系人", "咨询电话")
    alt = "|".join(re.escape(x) for x in sorted(labels, key=len, reverse=True))
    seen: set[str] = set()
    parts: list[str] = []
    for m in re.finditer(rf"(?:{alt})\s*[：:]\s*([^\n\r]+)", text):
        v = m.group(1).strip()
        v = re.sub(r" +", " ", v)
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
        log.warning("未安装 jieba，keywords 将存 []")
        return "[]"

    body = (content or "")[:head_chars]
    piece = f"{title or ''}\n{body}"
    if not piece.strip():
        return "[]"

    words = jieba.cut(piece)
    stop = set(
        "的 了 和 与 或 在 是 为 有 等 及 对 中 其 将 由 可 请 各 本 院 学院 通知 公告 关于 开展 进行 根据 现将 以下 有关"
        .split()
    )
    filtered = [
        w.strip()
        for w in words
        if len(w.strip()) > 1
        and w.strip() not in stop
        and not w.strip().isdigit()
        and not re.fullmatch(r"\d{4}年", w.strip())
    ]
    if not filtered:
        return "[]"
    cnt = Counter(filtered)
    top = [w for w, _ in cnt.most_common(5)]
    return json.dumps(top, ensure_ascii=False)


def extract_tags(title: str, content: str) -> str:
    hay = f"{title or ''}\n{content or ''}"
    if not hay.strip():
        return "[]"
    tags: list[str] = []
    for tag_name, triggers in TAG_RULES:
        if any(t in hay for t in triggers):
            tags.append(tag_name)
    return json.dumps(tags, ensure_ascii=False)


def compute_row(title: str, content: Optional[str]) -> tuple:
    text = content or ""
    org = extract_organizer(text)
    part = extract_participants(text)
    prize = extract_prize(text)
    req = extract_requirement(text)
    cont = extract_contact(text)
    kw = extract_keywords_top5(title or "", text)
    tg = extract_tags(title or "", text)
    return org, part, prize, req, cont, kw, tg


UPDATE_SQL = """
UPDATE notices SET
    organizer = ?,
    participants = ?,
    prize = ?,
    requirement = ?,
    contact = ?,
    keywords = ?,
    tags = ?,
    updated_at = ?
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
    n = 0
    for row_id, title, content in rows:
        org, part, prize, req, cont, kw, tg = compute_row(title, content)
        cur.execute(
            UPDATE_SQL,
            (org, part, prize, req, cont, kw, tg, now, row_id),
        )
        n += 1
        log.info("已更新 id=%s", row_id)

    conn.commit()
    conn.close()
    log.info("完成，共 %s 条", n)


if __name__ == "__main__":
    main()
