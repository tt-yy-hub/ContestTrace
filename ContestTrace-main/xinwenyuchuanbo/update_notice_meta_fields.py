import argparse
import json
import re
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import jieba


def utc_now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 可编辑：主题词命中规则（按需扩展）
TAG_RULES: List[Tuple[str, List[str]]] = [
    ("奖学金", ["奖学金", "助学金", "奖贷补助", "教育基金"]),
    ("竞赛", ["比赛", "竞赛", "大赛", "征集", "作品征集", "评选"]),
    ("实践", ["社会实践", "实践", "志愿", "调研", "走访"]),
    ("讲座", ["讲座", "报告", "论坛", "座谈"]),
    ("普通话", ["普通话", "测试", "报名", "培训"]),
    ("安全", ["安全", "防诈", "反诈", "消防", "宿舍", "寝室"]),
    ("考试", ["考试", "诚信考试", "考风考纪"]),
    ("评优", ["评优", "先进个人", "先进班集体", "文明寝室"]),
]


FIELD_PATTERNS = {
    "organizer": [r"(主办单位|主办方|组织单位)\s*[:：]?\s*(.+)"],
    "participants": [r"(参赛对象|参与人员|申报范围)\s*[:：]?\s*(.+)"],
    "prize": [r"(奖项设置|奖励|奖金)\s*[:：]?\s*(.+)"],
    "requirement": [r"(参赛要求|申报条件|需提交材料)\s*[:：]?\s*(.+)"],
    "contact": [r"(联系方式|联系人|咨询电话)\s*[:：]?\s*(.+)"],
}


def normalize_spaces(s: str) -> str:
    s = (s or "").replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def extract_field(text: str, patterns: List[str], *, merge_multiline: bool = False) -> Optional[str]:
    """
    尽力抽取：从“标题: 内容”到下一行空行/下一字段前。
    这里用简化策略：命中后取该行剩余内容，并向后最多再拼接 2 行（避免漏掉换行后的补充）。
    """
    if not text:
        return None
    lines = [ln.strip() for ln in text.split("\n")]

    for i, ln in enumerate(lines):
        for pat in patterns:
            m = re.search(pat, ln)
            if not m:
                continue
            val = (m.group(2) or "").strip()
            extra: List[str] = []
            # 往后拼接两行（若不是明显的新字段行）
            for j in range(1, 3):
                if i + j >= len(lines):
                    break
                nxt = lines[i + j].strip()
                if not nxt:
                    break
                if re.search(r"^(主办单位|主办方|组织单位|参赛对象|参与人员|申报范围|奖项设置|奖励|奖金|参赛要求|申报条件|需提交材料|联系方式|联系人|咨询电话)\s*[:：]?", nxt):
                    break
                extra.append(nxt)

            if merge_multiline and extra:
                parts = [val] + extra
                # 联系方式要求：多行合并，用中文分号；
                return "；".join([p for p in parts if p])
            if val:
                return val
            if extra:
                return extra[0]
    return None


def extract_keywords(title: str, content: str, topn: int = 5) -> List[str]:
    base = (title or "").strip() + "\n" + (content or "")[:500]
    base = normalize_spaces(base)
    # 去掉 URL / 标点
    base = re.sub(r"https?://\S+", " ", base)
    base = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]+", " ", base)
    words = [w.strip() for w in jieba.lcut(base) if w.strip()]
    # 简单停用：长度<2 丢弃；纯数字丢弃
    words = [w for w in words if len(w) >= 2 and not re.fullmatch(r"\d+", w)]
    freq: Dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    return [w for w, _ in ranked[:topn]]


def extract_tags(text: str) -> List[str]:
    text = text or ""
    tags: List[str] = []
    for tag, kws in TAG_RULES:
        for kw in kws:
            if kw and kw in text:
                tags.append(tag)
                break
    # 去重保序
    seen = set()
    out: List[str] = []
    for t in tags:
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Update meta fields (offline) based on existing title+content.")
    ap.add_argument("--db", default="notices.db")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--where-like", default=None)
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    sql = "SELECT id, title, content FROM notices"
    params = []
    if args.where_like:
        sql += " WHERE url LIKE ?"
        params.append(args.where_like)
    sql += " ORDER BY id ASC"
    if args.limit:
        sql += " LIMIT ?"
        params.append(args.limit)

    rows = conn.execute(sql, params).fetchall()
    now = utc_now_iso()

    for r in rows:
        title = r["title"] or ""
        content = r["content"] or ""
        text = normalize_spaces(title + "\n" + content)

        organizer = extract_field(text, FIELD_PATTERNS["organizer"])
        participants = extract_field(text, FIELD_PATTERNS["participants"])
        prize = extract_field(text, FIELD_PATTERNS["prize"])
        requirement = extract_field(text, FIELD_PATTERNS["requirement"])
        contact = extract_field(text, FIELD_PATTERNS["contact"], merge_multiline=True)

        keywords = extract_keywords(title, content, topn=5)
        tags = extract_tags(text)

        conn.execute(
            """
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
            """,
            (
                organizer,
                participants,
                prize,
                requirement,
                contact,
                json.dumps(keywords, ensure_ascii=False),
                json.dumps(tags, ensure_ascii=False),
                now,
                r["id"],
            ),
        )

    conn.commit()
    print(f"updated rows: {len(rows)}")


if __name__ == "__main__":
    main()

