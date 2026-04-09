#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试教务处爬虫
"""

from contesttrace.core.spiders.jwc_spider import JwcSpider
import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # 创建爬虫实例
    spider = JwcSpider()
    
    # 执行爬取
    start_time = time.time()
    contests = spider.crawl()
    end_time = time.time()
    
    # 打印爬取结果
    print(f"爬取完成，共获取 {len(contests)} 条2025年后的公告")
    print(f"爬取耗时: {end_time - start_time:.2f} 秒")
    
    # 打印前5条公告的标题和发布时间
    print("\n前5条公告:")
    for i, contest in enumerate(contests[:5]):
        print(f"{i+1}. {contest.get('title', '无标题')} - {contest.get('publish_time', '无发布时间')}")
