# -*- coding: utf-8 -*-
"""
竞赛推荐：无 API Key 时采用规则打分；配置 OPENAI_API_KEY 时可调用 OpenAI 兼容接口做语义推荐。

敏感信息仅从环境变量读取，绝不硬编码。
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


def _rule_score(profile: Dict[str, Any], contest: Dict[str, Any]) -> float:
    """简单规则匹配度 0~100。"""

    score = 40.0
    interests = " ".join(profile.get("interests") or [])
    major = str(profile.get("major") or "")
    grade = str(profile.get("grade") or "")
    blob = f"{contest.get('title','')} {contest.get('full_text','')[:2000]}"
    for tok in re.split(r"[\s,，、]+", interests):
        t = tok.strip()
        if len(t) >= 2 and t in blob:
            score += 8.0
    if major and major in blob:
        score += 12.0
    if grade and grade in blob:
        score += 5.0
    for kw in ("省级", "校级", "国赛", "挑战杯", "互联网+", "数学建模"):
        if kw in blob:
            score += 3.0
    return max(0.0, min(100.0, score))


def _rule_reason(profile: Dict[str, Any], contest: Dict[str, Any], score: float) -> str:
    """规则版推荐理由与备赛建议。"""

    parts = [
        f"匹配度（规则引擎）约 {score:.1f} 分。",
        "建议：对照通知中的报名时间与作品提交截止日，提前组队与分工。",
    ]
    if profile.get("major"):
        parts.append(f"结合你的专业「{profile.get('major')}」，可重点阅读正文中与专业相关的赛道说明。")
    return " ".join(parts)


def recommend_with_llm(
    profile: Dict[str, Any],
    contests: List[Dict[str, Any]],
    model_cfg: Dict[str, Any],
    logger: logging.Logger,
) -> Optional[str]:
    """
    调用 OpenAI 兼容接口生成自然语言推荐结果（纯文本）。
    需环境变量：OPENAI_API_KEY；可选 OPENAI_BASE_URL、OPENAI_MODEL。
    """

    if OpenAI is None:
        logger.info("openai 包未安装，跳过 LLM 推荐")
        return None
    try:
        llm = model_cfg.get("llm") or {}
        env_key_name = str(llm.get("env_api_key", "OPENAI_API_KEY"))
        env_base_name = str(llm.get("env_base_url", "OPENAI_BASE_URL"))
        env_model_name = str(llm.get("env_model", "OPENAI_MODEL"))
        key = os.environ.get(env_key_name, "").strip()
        if not key:
            return None
        base_url = os.environ.get(env_base_name, "").strip() or None
        model = os.environ.get(env_model_name, "").strip() or str(llm.get("default_model", "gpt-4o-mini"))
        client = OpenAI(api_key=key, base_url=base_url)
        brief = [
            {
                "id": c.get("id"),
                "title": c.get("title"),
                "level": c.get("competition_level"),
                "category": c.get("competition_category"),
            }
            for c in contests[:20]
        ]
        prompt = (
            "你是高校竞赛指导助手。根据用户画像与竞赛列表，输出 JSON 数组，"
            "每项含 contest_id, match_score(0-100), reason, study_tips。\n"
            f"用户画像：{json.dumps(profile, ensure_ascii=False)}\n"
            f"竞赛列表：{json.dumps(brief, ensure_ascii=False)}"
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1200,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        logger.warning(f"LLM 推荐失败，将降级规则：{type(e).__name__}: {e}")
        return None


def recommend_contests(
    profile: Dict[str, Any],
    contests: List[Dict[str, Any]],
    model_cfg: Dict[str, Any],
    logger: logging.Logger,
    nl_query: str = "",
) -> List[Dict[str, Any]]:
    """
    返回带 match_score、reason、study_tips 的竞赛列表（按分数降序）。
    """

    llm_out = recommend_with_llm(profile, contests, model_cfg, logger)
    if llm_out:
        try:
            # 尝试解析 JSON
            arr = json.loads(llm_out)
            if isinstance(arr, list):
                return arr[:30]
        except Exception:
            return [{"raw_llm": llm_out}]

    ranked: List[Dict[str, Any]] = []
    for c in contests:
        try:
            sc = _rule_score(profile, c)
            ranked.append(
                {
                    "contest_id": c.get("id"),
                    "match_score": round(sc, 2),
                    "reason": _rule_reason(profile, c, sc),
                    "study_tips": "分解赛题、预留润色与答辩时间；保存好报名表与作品提交截图。",
                    "nl_query": nl_query,
                }
            )
        except Exception:
            continue
    ranked.sort(key=lambda x: float(x.get("match_score") or 0), reverse=True)
    return ranked[:30]
