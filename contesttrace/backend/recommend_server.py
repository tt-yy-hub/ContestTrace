#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContestTrace 推荐服务：
- 规则召回
- Ollama llama3.1 语义重排
- 解析失败兜底
"""

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.1"
MAX_RECALL = 50
ALLOWED_ORIGINS = {
    "http://localhost:8000",
    "http://127.0.0.1:8000",
}

TAXONOMY_PATH = Path(__file__).resolve().parents[2] / "config" / "competition_taxonomy.json"


def load_taxonomy() -> list:
    if not TAXONOMY_PATH.exists():
        return []
    try:
        with TAXONOMY_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        categories = data.get("categories", [])
        return categories if isinstance(categories, list) else []
    except Exception:
        return []


TAXONOMY = load_taxonomy()


def _category_match(text: str, category: dict) -> tuple[float, list]:
    include = [str(x).lower() for x in category.get("include", [])]
    exclude = [str(x).lower() for x in category.get("exclude", [])]
    matched_keywords = [kw for kw in include if kw and kw in text]
    exclude_hits = sum(1 for kw in exclude if kw and kw in text)
    if not matched_keywords:
        return 0.0, []
    score = max(0.0, len(matched_keywords) * 2.0 - exclude_hits * 1.5)
    return score, matched_keywords[:5]


def _interest_match_score(text: str, interest: str) -> tuple[float, str, list]:
    interest_l = str(interest).strip().lower()
    best_score = 0.0
    best_category = ""
    best_keywords = []
    for category in TAXONOMY:
        cat_name = str(category.get("name", ""))
        aliases = [str(x).lower() for x in category.get("aliases", [])]
        if interest_l not in cat_name.lower() and interest_l not in aliases:
            continue
        score, kws = _category_match(text, category)
        if score > best_score:
            best_score = score
            best_category = cat_name
            best_keywords = kws
    return best_score, best_category, best_keywords


def infer_primary_category(contest: dict) -> tuple[str, list]:
    text = " ".join(
        [
            str(contest.get("title", "")),
            str(contest.get("summary", "")),
            str(contest.get("content", "")),
            str(contest.get("category", "")),
        ]
    ).lower()
    best = ("未分类", 0.0, [])
    for category in TAXONOMY:
        score, kws = _category_match(text, category)
        if score > best[1]:
            best = (str(category.get("name", "未分类")), score, kws)
    return best[0], best[2]


def load_contests() -> list:
    data_path = Path(__file__).resolve().parents[1] / "frontend" / "data" / "contests.json"
    if not data_path.exists():
        return []
    try:
        with data_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def calc_rule_score(contest: dict, interests: list, profile: dict) -> tuple[float, dict]:
    text = " ".join(
        [
            str(contest.get("title", "")),
            str(contest.get("summary", "")),
            str(contest.get("content", "")),
            str(contest.get("tags", "")),
            str(contest.get("keywords", "")),
            str(contest.get("category", "")),
        ]
    ).lower()
    score = 0.0
    matched_categories = []
    matched_keywords = []

    for interest in interests:
        s, cat_name, kws = _interest_match_score(text, str(interest).strip())
        score += s
        if cat_name and cat_name not in matched_categories:
            matched_categories.append(cat_name)
        for kw in kws:
            if kw not in matched_keywords:
                matched_keywords.append(kw)

    weights = profile.get("keyword_weights", {})
    if isinstance(weights, dict):
        for kw, weight in weights.items():
            kw_text = str(kw).strip().lower()
            if kw_text and kw_text in text:
                try:
                    score += float(weight) * 0.3
                except Exception:
                    pass
    inferred, inferred_kws = infer_primary_category(contest)
    if inferred != "未分类" and inferred not in matched_categories:
        matched_categories.append(inferred)
    for kw in inferred_kws:
        if kw not in matched_keywords:
            matched_keywords.append(kw)

    return score, {
        "matched_categories": matched_categories[:3],
        "matched_keywords": matched_keywords[:8],
    }


def rule_recall(contests: list, interests: list, profile: dict) -> tuple[list, dict]:
    scored = []
    meta_map = {}
    for c in contests:
        score, meta = calc_rule_score(c, interests, profile)
        scored.append((c, score))
        cid = str(c.get("id") or c.get("raw_notice_id") or "")
        if cid:
            meta_map[cid] = meta
    scored.sort(key=lambda x: x[1], reverse=True)
    recalled = [c for c, _ in scored[:MAX_RECALL]]
    fallback = recalled if recalled else contests[:MAX_RECALL]
    return fallback, meta_map


def build_prompt(interests: list, candidates: list) -> str:
    compact = []
    for c in candidates[:MAX_RECALL]:
        compact.append(
            {
                "id": c.get("id") or c.get("raw_notice_id"),
                "title": c.get("title", ""),
                "summary": c.get("summary", ""),
                "content": c.get("content", ""),
                "category": c.get("category", ""),
            }
        )
    return (
        "你是竞赛推荐助手。请依据用户兴趣对候选竞赛做个性化推荐。\n"
        "严格要求：\n"
        "1. 只能返回 JSON，不要返回额外文本。\n"
        "2. JSON 格式: {\"recommended_ids\":[...],\"reason\":\"...\"}\n"
        "3. recommended_ids 只能从候选 id 中选择，最多 6 个。\n\n"
        f"用户兴趣: {'、'.join(interests) if interests else '无'}\n"
        f"候选竞赛: {json.dumps(compact, ensure_ascii=False)}"
    )


def parse_model_output(raw_text: str) -> dict:
    text = (raw_text or "").strip()
    if not text:
        return {"recommended_ids": [], "reason": "模型未返回内容"}

    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    for m in re.finditer(r"\{[\s\S]*?\}", text):
        candidate = m.group(0)
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    ids = []
    block = re.search(r"recommended_ids\s*[:=]\s*\[([^\]]*)\]", text, re.IGNORECASE)
    if block:
        ids = [int(x) for x in re.findall(r"\d+", block.group(1))]
    return {"recommended_ids": ids[:6], "reason": "模型返回非标准 JSON，已宽松解析"}


def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }
    req = urllib_request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib_request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("response", "")


class Handler(BaseHTTPRequestHandler):
    def _origin(self) -> str:
        origin = self.headers.get("Origin", "")
        return origin if origin in ALLOWED_ORIGINS else "http://127.0.0.1:8000"

    def _json(self, status: int, payload: dict):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", self._origin())
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self._json(200, {"ok": True})

    def do_POST(self):
        if self.path != "/api/recommend":
            self._json(404, {"error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            req_data = json.loads(body)
        except Exception:
            self._json(400, {"error": "请求 JSON 格式错误"})
            return

        interests = req_data.get("interests", [])
        profile = req_data.get("user_profile", {})
        if not isinstance(interests, list):
            self._json(400, {"error": "interests 必须为数组"})
            return
        if not isinstance(profile, dict):
            profile = {}

        contests = load_contests()
        if not contests:
            self._json(500, {"error": "竞赛数据为空，请先导出 contests.json"})
            return

        recalled, meta_map = rule_recall(contests, interests, profile)
        reason = "规则推荐"
        recommended = recalled[:6]

        try:
            model_text = call_ollama(build_prompt(interests, recalled))
            parsed = parse_model_output(model_text)
            ids = parsed.get("recommended_ids", [])
            if not isinstance(ids, list):
                ids = []
            id_set = {str(x) for x in ids[:6]}
            hit = [c for c in contests if str(c.get("id") or c.get("raw_notice_id")) in id_set]
            if hit:
                recommended = hit[:6]
            reason = parsed.get("reason", reason) or reason
        except (HTTPError, URLError, TimeoutError):
            reason = "大模型不可用，已回退规则推荐"
        except Exception:
            reason = "解析失败，已回退规则推荐"

        enhanced = []
        for c in recommended:
            item = dict(c)
            cid = str(c.get("id") or c.get("raw_notice_id") or "")
            meta = meta_map.get(cid, {})
            item["ai_match_categories"] = meta.get("matched_categories", [])
            item["ai_match_keywords"] = meta.get("matched_keywords", [])
            enhanced.append(item)

        self._json(
            200,
            {
                "recommended": enhanced,
                "reason": reason,
                "model": MODEL_NAME,
                "recall_size": len(recalled),
            },
        )


def main():
    server = HTTPServer(("0.0.0.0", 8001), Handler)
    print("Recommendation API running at http://localhost:8001")
    print("Using model:", MODEL_NAME)
    server.serve_forever()


if __name__ == "__main__":
    main()
