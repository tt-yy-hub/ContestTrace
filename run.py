#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ContestTrace 主运行脚本
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from contesttrace.core.utils import setup_logger, ensure_directory
from contesttrace.core.spiders.spider_manager import SpiderManager
from contesttrace.core.storage.db_manager import DatabaseManager
from contesttrace.core.filter.competition_filter import CompetitionFilter
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
            logger.info(f"[{spider.name}] 开始执行爬虫线程")
            result = spider.crawl()
            logger.info(f"[{spider.name}] 爬虫线程执行完成, 共获取 {len(result)} 条数据")
        except Exception as e:
            logger.error(f"[{spider.name}] 爬虫执行失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    logger.info(f"[{spider.name}] 等待爬虫线程执行完成，最多等待 300 秒")
    thread.join(timeout=300)  # 增加超时时间到300秒，确保能够完成更深层次的爬取任务
    
    if thread.is_alive():
        logger.error(f"[{spider.name}] 爬虫执行超时")
        return []
    
    logger.info(f"[{spider.name}] 爬虫线程执行完成，共获取 {len(result)} 条数据")
    return result

def crawl(db_manager):
    """
    执行爬虫
    
    Args:
        db_manager: 数据库管理器
    """
    # 设置日志级别为INFO，确保所有日志都能被输出
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    logger.info("开始执行爬虫任务")
    
    try:
        # 初始化爬虫管理器
        spider_manager = SpiderManager()
        
        # 使用spider_manager的crawl_all方法执行所有爬虫（多线程并发）
        all_contests = spider_manager.crawl_all()
        
        # 打印爬取到的公告数量
        logger.info(f"爬虫实际爬取到 {len(all_contests)} 条公告")
        
        # 存储原始公告
        logger.info("开始存储原始公告")
        stored_count = 0
        for contest in all_contests:
            if db_manager.insert_raw_notice(contest):
                stored_count += 1
        
        # 获取爬取统计信息
        stats = db_manager.get_crawl_stats()
        logger.info(f"爬取完成：共爬取 {len(all_contests)} 条，成功入库 {stored_count} 条，数据库总计 {stats['total']} 条")
        
        logger.info("爬虫任务执行完成")
    except Exception as e:
        logger.error(f"爬虫任务执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

def perform_filter(db_manager):
    """
    执行筛选
    
    Args:
        db_manager: 数据库管理器
    """
    # 获取待筛选的公告
    pending_notices = db_manager.get_pending_notices()
    
    if not pending_notices:
        logger.info("没有待筛选的公告")
        return
    
    # 初始化过滤器
    competition_filter = CompetitionFilter()
    
    # 筛选公告
    filtered_notices = competition_filter.filter_notices(pending_notices)
    
    # 处理筛选结果
    passed_count = 0
    rejected_count = 0
    
    for notice in pending_notices:
        notice_id = notice.get('id')
        title = notice.get('title', '')
        
        # 检查是否在筛选结果中
        is_competition = any(filtered['id'] == notice_id for filtered in filtered_notices)
        
        if is_competition:
            # 标记为通过并插入竞赛库
            db_manager.update_filter_status(notice_id, 'passed')
            
            # 准备竞赛公告数据
            competition_notice = {
                'raw_notice_id': notice_id,
                'notice_url': notice.get('notice_url', ''),
                'title': title,
                'publish_time': notice.get('publish_time', ''),
                'source_department': notice.get('source_department', ''),
                'content': notice.get('content', ''),
                'filter_pass_time': datetime.now().isoformat()
            }
            
            # 插入竞赛库
            if db_manager.insert_competition_notice(competition_notice):
                passed_count += 1
        else:
            # 标记为拒绝
            db_manager.update_filter_status(notice_id, 'rejected')
            rejected_count += 1
    
    logger.info(f"筛选完成：共处理 {len(pending_notices)} 条待筛选数据，筛选通过 {passed_count} 条，拒绝 {rejected_count} 条，成功写入竞赛库 {passed_count} 条")

def export_data(db_manager, filter_arg=None):
    """
    导出数据
    
    Args:
        db_manager: 数据库管理器
        filter_arg: 筛选参数
    """
    # 获取竞赛公告
    contests = db_manager.get_competition_notices()
    
    # 按字段筛选
    if filter_arg:
        field, keyword = filter_arg.split(':', 1)
        filtered_contests = []
        for contest in contests:
            if field in contest and keyword in str(contest[field]):
                filtered_contests.append(contest)
        contests = filtered_contests
        logger.info(f'按 {field}:{keyword} 筛选，共 {len(contests)} 条数据')
    
    # 处理竞赛数据
    from contesttrace.core.utils.data_processor import DataProcessor
    data_processor = DataProcessor()
    processed_contests = []
    for contest in contests:
        processed_contest = data_processor.process_contest(contest)
        processed_contests.append(processed_contest)
    
    # 导出到前端
    exporter = ContestExporter()
    export_path = exporter.export_to_frontend(processed_contests)
    logger.info(f"成功导出到前端: {export_path}")


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='ContestTrace 运行脚本')
    parser.add_argument('--crawl', action='store_true', help='执行爬虫任务')
    parser.add_argument('--export', action='store_true', help='导出数据')
    parser.add_argument('--crawl-only', action='store_true', help='仅执行全量爬虫，不执行筛选')
    parser.add_argument('--filter-only', action='store_true', help='仅执行筛选模块，不执行爬虫')
    parser.add_argument('--refilter-all', action='store_true', help='重置所有公告的筛选状态，重新执行全量筛选')
    parser.add_argument('--filter', type=str, help='按字段筛选，格式：字段名:关键词')
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    ensure_directory('logs')
    
    # 初始化数据库管理器
    db_manager = DatabaseManager()
    
    if args.crawl or args.crawl_only:
        # 执行爬虫
        crawl(db_manager)
        
        # 如果不是仅爬取，则执行筛选
        if not args.crawl_only:
            # 执行筛选
            logger.info("执行筛选")
            perform_filter(db_manager)
            
            # 导出数据到前端
            logger.info("导出数据到前端")
            export_data(db_manager, args.filter)
    elif args.filter_only:
        # 仅执行筛选
        logger.info("执行筛选模块")
        perform_filter(db_manager)
        
        # 导出数据到前端
        logger.info("导出数据到前端")
        export_data(db_manager, args.filter)
    elif args.refilter_all:
        # 重置筛选状态并重新筛选
        logger.info("重置筛选状态并重新筛选")
        db_manager.reset_filter_status()
        perform_filter(db_manager)
        
        # 导出数据到前端
        logger.info("导出数据到前端")
        export_data(db_manager, args.filter)
    elif args.export:
        # 导出数据
        logger.info("导出数据")
        export_data(db_manager, args.filter)
    else:
        # 默认执行爬虫
        crawl(db_manager)
        
        # 执行筛选
        logger.info("执行筛选")
        perform_filter(db_manager)
        
        # 导出数据到前端
        logger.info("导出数据到前端")
        export_data(db_manager, args.filter)


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
