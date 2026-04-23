#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 推荐重排后端服务（OpenAI 兼容接口）
默认用于本地 Ollama：
  OPENAI_BASE_URL=http://127.0.0.1:11434/v1
  OPENAI_MODEL=qwen2.5:1.5b
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

import requests
from flask import Flask, jsonify, request


def load_dotenv(dotenv_path: str = ".env") -> None:
    """轻量加载 .env，避免额外依赖。"""
    path = Path(dotenv_path)
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_dotenv()

app = Flask(__name__)


def corsify(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.after_request
def after_request(response):
    return corsify(response)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "ai-rerank"})


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "ok": True,
            "message": "AI rerank service is running.",
            "health": "/health",
            "rerank_api": "/api/ai/rerank",
        }
    )


@app.route("/api/ai/rerank", methods=["OPTIONS", "POST"])
def rerank():
    if request.method == "OPTIONS":
        return corsify(jsonify({"ok": True}))

    payload = request.get_json(silent=True) or {}
    query = str(payload.get("query", "")).strip()
    candidates = payload.get("candidates") or []
    if not isinstance(candidates, list):
        candidates = []

    normalized = normalize_candidates(candidates)
    if not normalized:
        return jsonify([])

    # 先尝试大模型重排，失败自动规则兜底
    model_ids = rerank_by_llm(query, normalized)
    if model_ids:
        resp = jsonify(model_ids)
        resp.headers["X-Rerank-Source"] = "llm"
        resp.headers["X-Rerank-Model"] = os.getenv("OPENAI_MODEL", "qwen2.5:1.5b")
        print(
            f"[rerank] source=llm model={resp.headers['X-Rerank-Model']} "
            f"query_len={len(query)} candidates={len(normalized)}"
        )
        return resp

    fallback_ids = rerank_by_rules(query, normalized)
    resp = jsonify(fallback_ids)
    resp.headers["X-Rerank-Source"] = "fallback"
    resp.headers["X-Rerank-Model"] = os.getenv("OPENAI_MODEL", "qwen2.5:1.5b")
    print(
        f"[rerank] source=fallback model={resp.headers['X-Rerank-Model']} "
        f"query_len={len(query)} candidates={len(normalized)}"
    )
    return resp


def normalize_candidates(candidates: List[Dict]) -> List[Dict]:
    result: List[Dict] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        cid = str(item.get("id", "")).strip()
        if not cid:
            continue
        result.append(
            {
                "id": cid,
                "title": str(item.get("title", "")),
                "category": str(item.get("category", "")),
                "level": str(item.get("level", "")),
                "summary": str(item.get("summary", "")),
                "score": float(item.get("score", 0) or 0),
            }
        )
    return result


def rerank_by_llm(query: str, candidates: List[Dict]) -> List[str]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    # 若未配置，默认直连本地 Ollama OpenAI 兼容接口，便于开箱即用
    base_url = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:11434/v1").strip().rstrip("/")
    model = os.getenv("OPENAI_MODEL", "qwen2.5:1.5b").strip()
    timeout_s = int(os.getenv("OPENAI_TIMEOUT", "30") or "30")

    if not base_url:
        return []

    endpoint = f"{base_url}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    prompt = build_rerank_prompt(query, candidates)
    body = {
        "model": model,
        "temperature": 0.1,
        "max_tokens": 256,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是竞赛推荐重排器。只返回 JSON 数组，数组元素必须是候选 id。"
                    "不得返回解释文字。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }

    try:
        resp = requests.post(endpoint, headers=headers, json=body, timeout=timeout_s)
        if resp.status_code != 200:
            print(f"[rerank-llm] http_status={resp.status_code} endpoint={endpoint}")
            print(f"[rerank-llm] response_preview={resp.text[:300]}")
            return []
        data = resp.json()
        text = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        print(
            f"[rerank-llm] http_status=200 model={model} endpoint={endpoint} "
            f"content_preview={text[:180]}"
        )
        return parse_llm_ids(text, candidates)
    except Exception as exc:
        print(f"[rerank-llm] exception={type(exc).__name__}: {exc}")
        return []


def build_rerank_prompt(query: str, candidates: List[Dict]) -> str:
    rows = []
    for c in candidates:
        rows.append(
            {
                "id": c["id"],
                "title": c["title"],
                "category": c["category"],
                "level": c["level"],
                "summary": c["summary"][:160],
                "base_score": c["score"],
            }
        )
    return (
        "请基于用户意图对候选赛事排序，优先考虑语义相关性、用户目标匹配、可执行性。\n"
        f"用户输入: {query}\n"
        f"候选: {json.dumps(rows, ensure_ascii=False)}\n"
        "输出格式示例: [\"12\",\"8\",\"31\"]\n"
        "只输出 JSON 数组。"
    )


def parse_llm_ids(raw: str, candidates: List[Dict]) -> List[str]:
    if not raw:
        return []
    text = raw.strip()
    if "```" in text:
        text = text.replace("```json", "").replace("```", "").strip()
    # 容错：有些模型会在 JSON 前后输出解释文本，尝试截取首个数组
    if "[" in text and "]" in text and not text.strip().startswith("["):
        start = text.find("[")
        end = text.rfind("]")
        if end > start:
            text = text[start : end + 1]
    try:
        arr = json.loads(text)
        if not isinstance(arr, list):
            print(f"[rerank-llm] parse_failed=not_list raw_preview={raw[:200]}")
            return []
        valid = {c["id"] for c in candidates}
        result = []
        for item in arr:
            sid = str(item)
            if sid in valid and sid not in result:
                result.append(sid)
        if not result:
            print(f"[rerank-llm] parse_failed=no_valid_id raw_preview={raw[:200]}")
            return []
        # 补齐未返回候选，保证稳定
        for c in candidates:
            if c["id"] not in result:
                result.append(c["id"])
        return result
    except Exception as exc:
        print(f"[rerank-llm] parse_exception={type(exc).__name__}: {exc} raw_preview={raw[:200]}")
        return []


def rerank_by_rules(query: str, candidates: List[Dict]) -> List[str]:
    tokens = [t.strip().lower() for t in split_tokens(query) if len(t.strip()) >= 2]
    scored: List[Tuple[str, float]] = []
    for c in candidates:
        text = " ".join([c["title"], c["category"], c["summary"]]).lower()
        bonus = 0.0
        for tk in tokens:
            if tk in text:
                bonus += 1.8
        if c["level"] == "A+":
            bonus += 0.8
        elif c["level"] == "A":
            bonus += 0.5
        scored.append((c["id"], c["score"] + bonus))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [sid for sid, _ in scored]


def split_tokens(text: str) -> List[str]:
    seps = [" ", ",", "，", "。", "；", ";", "、", "\n", "\t"]
    result = [text]
    for sep in seps:
        temp = []
        for item in result:
            temp.extend(item.split(sep))
        result = temp
    return result


if __name__ == "__main__":
    host = os.getenv("AI_API_HOST", "127.0.0.1")
    port = int(os.getenv("AI_API_PORT", "8001") or "8001")
    app.run(host=host, port=port, debug=False)

