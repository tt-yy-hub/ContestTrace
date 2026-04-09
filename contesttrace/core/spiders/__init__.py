#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫模块初始化文件
"""

from .base_spider import BaseSpider
from .hbufe_spider import HbufeSpider

__all__ = [
    'BaseSpider',
    'HbufeSpider'
]
