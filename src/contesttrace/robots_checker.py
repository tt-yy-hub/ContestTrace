# -*- coding: utf-8 -*-
"""
robots.txt 合规检查（urllib.robotparser）。

说明：
- 若 robots.txt 无法获取，默认记录警告并放行（避免个别站点阻断导致全站不可用）
- 生产环境建议 respect_robots_txt=true
"""

from __future__ import annotations

import logging
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser


def robots_url_for_base(base_url: str) -> str:
    """由站点根域名拼接 robots.txt 地址。"""

    p = urlparse(base_url)
    if not p.scheme or not p.netloc:
        return ""
    return f"{p.scheme}://{p.netloc}/robots.txt"


def can_fetch_url(user_agent: str, base_url: str, target_url: str, logger: logging.Logger) -> bool:
    """
    判断 user_agent 是否允许抓取 target_url（相对站点 base_url 的 robots 规则）。
    """

    robots = robots_url_for_base(base_url)
    if not robots:
        return True
    rp = RobotFileParser()
    try:
        rp.set_url(robots)
        rp.read()
    except Exception as e:
        logger.warning(f"robots.txt 读取失败，默认允许继续：{robots} | {type(e).__name__}: {e}")
        return True
    try:
        ua = user_agent or "*"
        return rp.can_fetch(ua, target_url)
    except Exception as e:
        logger.warning(f"robots can_fetch 异常，默认允许：{type(e).__name__}: {e}")
        return True
