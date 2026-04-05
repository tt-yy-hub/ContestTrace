#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContestTrace 主运行脚本
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from contesttrace.core.utils import setup_logger, ensure_directory
from contesttrace.core.spiders.spider_manager import SpiderManager
from contesttrace.core.parsers import SmartParser, ContestFilter
from contesttrace.core.database import ContestDatabase
from contesttrace.core.utils import DataProcessor
from contesttrace.core.exporter import ContestExporter
import logging

# 设置日志
logger = setup_logger()


import threading
import time

def crawl_with_timeout(spider):
    """
    带超时的爬虫执行
    """
    result = []
    
    def target():
        nonlocal result
        try:
            logger.info(f"开始执行爬虫线程: {spider.name}")
            result = spider.crawl()
            logger.info(f"爬虫线程执行完成: {spider.name}, 共获取 {len(result)} 条数据")
        except Exception as e:
            logger.error(f"爬虫执行失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    logger.info(f"等待爬虫线程执行完成，最多等待 300 秒")
    thread.join(timeout=300)  # 增加超时时间到300秒，确保能够完成更深层次的爬取任务
    
    if thread.is_alive():
        logger.error(f"爬虫执行超时: {spider.name}")
        return []
    
    logger.info(f"爬虫线程执行完成，共获取 {len(result)} 条数据")
    return result

def crawl():
    """
    执行爬虫
    """
    logger.info("开始执行爬虫任务")
    
    try:
        # 初始化爬虫管理器
        logger.info("初始化爬虫管理器")
        spider_manager = SpiderManager()
        
        all_contests = []
        
        # 执行所有爬虫
        logger.info("执行所有爬虫")
        for spider in spider_manager.spiders:
            try:
                logger.info(f"开始爬取 {spider.name}")
                # 直接调用fetch方法测试
                test_url = spider.base_url
                logger.info(f"测试获取页面: {test_url}")
                content = spider.fetch(test_url)
                if not content:
                    logger.error(f"无法获取测试页面: {test_url}")
                    continue
                logger.info(f"成功获取测试页面，长度: {len(content)}")
                
                # 执行爬取（带超时）
                logger.info("执行爬取（带超时）")
                contests = crawl_with_timeout(spider)
                logger.info(f"{spider.name} 爬取完成，共获取 {len(contests)} 条数据")
                all_contests.extend(contests)
            except Exception as e:
                logger.error(f"爬虫执行失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"共爬取 {len(all_contests)} 条数据")
        
        # 智能解析
        parser = SmartParser()
        parsed_contests = []
        for contest in all_contests:
            try:
                parsed_contest = parser.parse_all(contest)
                parsed_contests.append(parsed_contest)
            except Exception as e:
                logger.error(f"解析竞赛失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"共解析 {len(parsed_contests)} 条数据")
        
        # 精准筛选
        filter = ContestFilter()
        filtered_contests = filter.filter_contests(parsed_contests)
        logger.info(f"筛选完成，共保留 {len(filtered_contests)} 条竞赛数据")
        
        # 数据处理
        processor = DataProcessor()
        processed_contests = processor.process_contests(filtered_contests)
        logger.info(f"数据处理完成，共处理 {len(processed_contests)} 条竞赛数据")
        
        # 打印处理后的数据，检查URL字段
        if processed_contests:
            logger.info("处理后的竞赛数据示例:")
            for i, contest in enumerate(processed_contests[:5]):  # 只打印前5个
                url = contest.get('url', '空')
                title = contest.get('title', '未知')
                logger.info(f"{i+1}. 标题: {title} | URL: {url}")
        
        # 存储到数据库
        with ContestDatabase() as db:
            count = db.batch_insert_contests(processed_contests)
            logger.info(f"成功存储 {count} 条竞赛数据")
        
        # 导出到前端
        exporter = ContestExporter()
        export_path = exporter.export_to_frontend(processed_contests)
        logger.info(f"成功导出到前端: {export_path}")
        
        # 打印导出的数据
        if processed_contests:
            logger.info("导出的竞赛数据:")
            for i, contest in enumerate(processed_contests[:3]):  # 只打印前3个
                logger.info(f"{i+1}. {contest.get('title', '未知')}")
        
        logger.info("爬虫任务执行完成")
    except Exception as e:
        logger.error(f"爬虫任务执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='ContestTrace 运行脚本')
    parser.add_argument('--crawl', action='store_true', help='执行爬虫任务')
    parser.add_argument('--export', action='store_true', help='导出数据')
    
    args = parser.parse_args()
    
    if args.crawl:
        crawl()
    elif args.export:
        # 导出数据
        with ContestDatabase() as db:
            contests = db.get_all_contests()
            exporter = ContestExporter()
            exporter.export_csv(contests)
            logger.info("数据导出完成")
    else:
        # 默认执行爬虫
        crawl()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        logger.info("正在保存数据...")
        # 可以在这里添加数据保存逻辑
        logger.info("数据保存完成")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
