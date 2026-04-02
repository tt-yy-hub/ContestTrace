# -*- coding: utf-8 -*-
"""
断点续爬状态：读写 JSON 状态文件（每站点记录下一待爬页码等）。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

from .utils import ensure_dir, safe_write_text
from .encoding_fixer import read_text_file


def load_state(path: Path, logger: logging.Logger) -> Dict[str, Any]:
    """加载状态；文件不存在返回空字典。"""

    try:
        if not path.exists():
            return {}
        text, _enc = read_text_file(path, logger=logging.getLogger("contesttrace.encoding"))
        return json.loads(text) if text.strip() else {}
    except Exception as e:
        logger.warning(f"状态文件读取失败，将重新开始：{type(e).__name__}: {e}")
        return {}


def save_state(path: Path, data: Dict[str, Any], logger: logging.Logger) -> None:
    """原子写入状态（UTF-8 JSON）。"""

    try:
        ensure_dir(path.parent)
        safe_write_text(path, json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        logger.warning(f"状态保存失败：{type(e).__name__}: {e}")


def get_next_page(state: Dict[str, Any], site_id: str, default_start: int) -> int:
    """读取某站点下一页；无记录则 default_start。"""

    try:
        sites = state.get("sites") or {}
        cur = sites.get(site_id) or {}
        return int(cur.get("next_page", default_start))
    except Exception:
        return int(default_start)


def set_next_page(state: Dict[str, Any], site_id: str, next_page: int) -> None:
    """更新某站点下一页。"""

    if "sites" not in state or not isinstance(state["sites"], dict):
        state["sites"] = {}
    state["sites"][site_id] = {"next_page": int(next_page)}
