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
from contesttrace.core.storage.db_manager import DatabaseManager
from contesttrace.core.filter.competition_filter import CompetitionFilter
from contesttrace.core.exporter import ContestExporter
import logging

# 设置日志
logger = setup_logger()




def crawl(db_manager):
    """
    执行爬虫
    
    Args:
        db_manager: 数据库管理器
    """
    logger.info("开始执行爬虫任务")
    
    try:
        # 执行爬虫
        from contesttrace.core.spiders.spider_manager import SpiderManager
        spider_manager = SpiderManager()
        contests = spider_manager.crawl_all()
        
        # 保存爬取的数据
        for contest in contests:
            db_manager.insert_raw_notice(contest)
        
        logger.info(f"爬虫任务执行完成，共获取 {len(contests)} 条公告")
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
    
    # 初始化竞赛指南解析器并加载指南数据
    from contesttrace.core.utils.contest_guide_parser import contest_guide_parser
    guide_competitions = contest_guide_parser.load_guide_competitions()
    
    # 初始化过滤器，传入指南数据
    competition_filter = CompetitionFilter(guide_competitions=guide_competitions)
    
    # 筛选公告
    filtered_notices = competition_filter.filter_notices(pending_notices)
    
    # 处理筛选结果
    passed_count = 0
    rejected_count = 0
    
    for notice in pending_notices:
        notice_id = notice.get('id')
        title = notice.get('title', '')
        
        # 检查是否在筛选结果中
        filtered_notice = next((filtered for filtered in filtered_notices if filtered['id'] == notice_id), None)
        is_competition = filtered_notice is not None
        
        if is_competition:
            # 标记为通过并插入竞赛库
            db_manager.update_filter_status(notice_id, 'passed')
            
            # 准备竞赛公告数据
            competition_notice = {
                'raw_notice_id': notice_id,
                'notice_url': notice.get('notice_url', ''),
                'title': title,
                'publish_time': notice.get('publish_time', ''),
                'publisher': notice.get('publisher', '') or notice.get('source_department', ''),
                'content': notice.get('content', ''),
                'source': notice.get('spider_name', ''),
                'filter_pass_time': datetime.now().isoformat(),
                'confidence': filtered_notice.get('filter_confidence', 0.0)
            }
            
            # 插入竞赛库
            if db_manager.insert_competition_notice(competition_notice):
                passed_count += 1
        else:
            # 标记为拒绝
            db_manager.update_filter_status(notice_id, 'rejected')
            rejected_count += 1
    
    logger.info(f"筛选完成：共处理 {len(pending_notices)} 条待筛选数据，筛选通过 {passed_count} 条，拒绝 {rejected_count} 条，成功写入竞赛库 {passed_count} 条")

def perform_filter_all():
    """
    执行所有数据库的筛选，并汇总到主竞赛数据库
    """
    import os
    
    # 主数据库管理器
    main_db_manager = DatabaseManager()
    
    # 初始化竞赛指南解析器并加载指南数据
    from contesttrace.core.utils.contest_guide_parser import contest_guide_parser
    guide_competitions = contest_guide_parser.load_guide_competitions()
    
    # 初始化过滤器，传入指南数据
    competition_filter = CompetitionFilter(guide_competitions=guide_competitions)
    
    # 处理其他爬虫的数据库
    data_dir = "data"
    spider_dbs = []
    
    # 直接从竞赛数据库中读取数据，而不是从原始数据库中重新筛选
    for filename in os.listdir(data_dir):
        if filename.startswith("contest_trace_competition_") and filename != "contest_trace_competition.db":
            # 提取爬虫名称
            spider_name = filename.replace("contest_trace_competition_", "").replace(".db", "")
            spider_dbs.append((spider_name, filename))
    
    # 汇总到主竞赛数据库的公告
    all_competition_notices = []
    
    # 处理每个爬虫的竞赛数据库
    for spider_name, comp_db_filename in spider_dbs:
        logger.info(f"\n开始处理 {spider_name} 的竞赛数据库")
        
        # 初始化数据库管理器
        spider_db_manager = DatabaseManager(data_dir=data_dir, spider_name=spider_name)
        
        # 获取筛选后的竞赛公告
        comp_notices = spider_db_manager.get_competition_notices()
        logger.info(f"{spider_name} 竞赛数据库中有 {len(comp_notices)} 条竞赛公告")
        
        # 直接添加所有记录，不移除重复
        all_competition_notices.extend(comp_notices)
    
    logger.info(f"\n汇总后，共 {len(all_competition_notices)} 条竞赛公告")
    
    # 汇总到主竞赛数据库
    if all_competition_notices:
        logger.info(f"\n将 {len(all_competition_notices)} 条竞赛公告汇总到主竞赛数据库")
        
        # 清空主竞赛数据库
        main_db_manager.clear_competition_notices()
        
        # 插入汇总的竞赛公告
        inserted_count = 0
        skipped_count = 0
        for notice in all_competition_notices:
            # 计算置信度
            title = notice.get('title', '')
            content = notice.get('content', '')
            _, confidence = competition_filter.is_contest(title, content)
            
            # 准备竞赛公告数据，不使用独立数据库中的竞赛名称和级别，让 insert_competition_notice 重新计算
            competition_notice = {
                'raw_notice_id': notice.get('raw_notice_id', notice.get('id', 0)),
                'notice_url': notice.get('notice_url', ''),
                'title': title,
                'publish_time': notice.get('publish_time', ''),
                'publisher': notice.get('publisher', '') or notice.get('source_department', ''),
                'content': content,
                'source': notice.get('source', spider_name),
                'filter_pass_time': notice.get('filter_pass_time', datetime.now().isoformat()),
                'confidence': confidence
                # 不设置 competition_name 和 competition_level，让 insert_competition_notice 重新计算
            }
            
            if main_db_manager.insert_competition_notice(competition_notice):
                inserted_count += 1
                logger.debug(f"插入成功: {title[:50]}..., 置信度: {confidence:.2f}")
            else:
                skipped_count += 1
                logger.debug(f"跳过: {title[:50]}...")
        
        logger.info(f"汇总完成：共插入 {inserted_count} 条竞赛公告到主竞赛数据库，跳过 {skipped_count} 条")
    
    # 导出数据到前端
    export_data(main_db_manager)
    logger.info("所有数据库筛选和汇总完成")

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
    parser.add_argument('--filter-all', action='store_true', help='执行所有数据库的筛选，并汇总到主竞赛数据库')
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
    elif args.filter_all:
        # 执行所有数据库的筛选，并汇总到主竞赛数据库
        logger.info("执行所有数据库的筛选，并汇总到主竞赛数据库")
        perform_filter_all()
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
