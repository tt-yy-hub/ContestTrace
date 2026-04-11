#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫管理器
管理多个爬虫的执行
"""

import logging
from typing import List, Dict, Any
from .base_spider import BaseSpider
from .hbufe_spider import HbufeSpider
from .xgxy_spider import XgxySpider
from .etc_spider import EtcSpider
from .tsxy_spider import TsxySpider
from .gsxy_spider import GsxySpider
from .jwc_spider import JwcSpider
from .ysxy_spider import YsxySpider
from .jmxy_spider import JmxySpider
from .jrxy_spider import JrxySpider
from .kjxy_spider import KjxySpider
from .lyxy_spider import LyxySpider
from .wyxy_spider import WyxySpider
from .iexy_spider import IexySpider
from .xgc_spider import XgcSpider
from .xwcb_spider import XwcbSpider

logger = logging.getLogger(__name__)


class SpiderManager:
    """
    爬虫管理器
    """
    
    def __init__(self):
        """
        初始化爬虫管理器
        """
        self.spiders: List[BaseSpider] = []
        self._init_spiders()
    
    def _init_spiders(self):
        """
        初始化所有爬虫
        """
        # 校团委爬虫
        self.spiders.append(HbufeSpider())
        # 信息管理学院爬虫
        self.spiders.append(XgxySpider())
        # 创新创业学院爬虫
        self.spiders.append(EtcSpider())
        # 统计与数学学院爬虫
        self.spiders.append(TsxySpider())
        # 工商管理学院爬虫
        self.spiders.append(GsxySpider())
        # 教务处爬虫
        self.spiders.append(JwcSpider())
        # 艺术学院爬虫
        self.spiders.append(YsxySpider())
        # 经济与贸易学院爬虫
        self.spiders.append(JmxySpider())
        # 金融学院爬虫
        self.spiders.append(JrxySpider())
        # 会计学院爬虫
        self.spiders.append(KjxySpider())
        # 旅游与酒店管理学院爬虫
        self.spiders.append(LyxySpider())
        # 外国语学院爬虫
        self.spiders.append(WyxySpider())
        # 信息工程学院爬虫
        self.spiders.append(IexySpider())
        # 学生工作处爬虫
        self.spiders.append(XgcSpider())
        # 新闻与传播学院爬虫
        self.spiders.append(XwcbSpider())
        
        logger.info(f"初始化完成，共 {len(self.spiders)} 个爬虫")
    
    def crawl_all(self, exclude_spiders: list = None) -> List[Dict[str, Any]]:
        """
        执行所有爬虫
        
        Args:
            exclude_spiders: 要排除的爬虫名称列表
        
        Returns:
            所有爬虫获取的竞赛信息列表
        """
        all_contests = []
        
        # 确保 exclude_spiders 是列表
        if exclude_spiders is None:
            exclude_spiders = []
        
        # 过滤掉要排除的爬虫
        filtered_spiders = [spider for spider in self.spiders if spider.name not in exclude_spiders]
        
        print("开始执行所有爬虫")
        print(f"共 {len(filtered_spiders)} 个爬虫")
        
        # 逐个执行爬虫，避免多线程导致的问题
        for i, spider in enumerate(filtered_spiders):
            print(f"执行第 {i+1} 个爬虫: {spider.name}...")
            try:
                contests = spider.crawl()
                print(f"{spider.name} 爬虫实际爬取到 {len(contests)} 条公告")
                all_contests.extend(contests)
            except Exception as e:
                print(f"[{spider.name}] 执行失败: {e}")
                import traceback
                print(traceback.format_exc())
        
        print(f"所有爬虫执行完成，共获取 {len(all_contests)} 条2025年后的公告")
        return all_contests
    
    def get_spider_by_name(self, name: str) -> BaseSpider:
        """
        根据名称获取爬虫
        
        Args:
            name: 爬虫名称
        
        Returns:
            爬虫实例
        """
        for spider in self.spiders:
            if spider.name == name:
                return spider
        return None
