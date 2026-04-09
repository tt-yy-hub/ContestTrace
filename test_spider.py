#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫是否能正常运行
"""

from contesttrace.core.spiders.spider_manager import SpiderManager

if __name__ == "__main__":
    # 初始化爬虫管理器
    manager = SpiderManager()
    
    # 打印爬虫数量
    print('爬虫数量:', len(manager.spiders))
    
    # 打印爬虫名称列表
    print('爬虫名称列表:')
    for spider in manager.spiders:
        print('-', spider.name)
