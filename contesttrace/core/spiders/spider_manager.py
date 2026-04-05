#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫管理器
管理多个爬虫的执行
"""

import logging
from typing import List, Dict, Any
from .base_spider import BaseSpider
from .hbufe_spider import HBUFESpider
from .xgxy_spider import XGXySpider
from .etc_spider import ETCSpider
from .tsxy_spider import TSXySpider
from .gsxy_spider import GsxSpider
from .jwc_spider import JWCSpider
from .ysxy_spider import YSXySpider

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
        self.spiders.append(HBUFESpider())
        # 信息管理学院爬虫
        self.spiders.append(XGXySpider())
        # 创新创业学院爬虫
        self.spiders.append(ETCSpider())
        # 统计与数学学院爬虫
        self.spiders.append(TSXySpider())
        # 工商管理学院爬虫
        self.spiders.append(GsxSpider())
        # 教务处爬虫
        self.spiders.append(JWCSpider())
        # 艺术学院爬虫
        self.spiders.append(YSXySpider())
        
        logger.info(f"初始化完成，共 {len(self.spiders)} 个爬虫")
    
    def crawl_all(self) -> List[Dict[str, Any]]:
        """
        执行所有爬虫
        
        Returns:
            所有爬虫获取的竞赛信息列表
        """
        all_contests = []
        
        logger.info("开始执行所有爬虫")
        
        for spider in self.spiders:
            try:
                logger.info(f"开始执行爬虫: {spider.name}")
                contests = spider.crawl()
                logger.info(f"爬虫 {spider.name} 执行完成，获取 {len(contests)} 条数据")
                all_contests.extend(contests)
            except Exception as e:
                logger.error(f"爬虫 {spider.name} 执行失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info(f"所有爬虫执行完成，共获取 {len(all_contests)} 条数据")
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
