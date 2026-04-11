#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清空主竞赛数据库并汇总 15 个独立的竞赛数据库
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from contesttrace.core.storage.db_manager import DatabaseManager
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reset_and_aggregate():
    """
    清空主竞赛数据库并汇总 15 个独立的竞赛数据库
    """
    logger.info("开始清空主竞赛数据库并汇总 15 个独立的竞赛数据库...")
    
    # 初始化主数据库管理器
    main_db_manager = DatabaseManager()
    
    # 清空主竞赛数据库
    logger.info("清空主竞赛数据库...")
    main_db_manager.clear_competition_notices()
    logger.info("主竞赛数据库清空成功")
    
    # 汇总 15 个独立的竞赛数据库
    logger.info("开始汇总 15 个独立的竞赛数据库...")
    
    # 处理其他爬虫的数据库
    data_dir = "data"
    spider_dbs = []
    
    # 直接从竞赛数据库中读取数据，而不是从原始数据库中重新筛选
    for filename in os.listdir(data_dir):
        if filename.startswith("contest_trace_competition_") and filename != "contest_trace_competition.db":
            # 提取爬虫名称
            spider_name = filename.replace("contest_trace_competition_", "").replace(".db", "")
            spider_dbs.append((spider_name, filename))
    
    logger.info(f"找到 {len(spider_dbs)} 个独立的竞赛数据库")
    
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
        
        # 插入汇总的竞赛公告
        inserted_count = 0
        skipped_count = 0
        for notice in all_competition_notices:
            # 准备竞赛公告数据，不使用独立数据库中的竞赛名称和级别，让 insert_competition_notice 重新计算
            competition_notice = {
                'raw_notice_id': notice.get('raw_notice_id', notice.get('id', 0)),
                'notice_url': notice.get('notice_url', ''),
                'title': notice.get('title', ''),
                'publish_time': notice.get('publish_time', ''),
                'publisher': notice.get('publisher', '') or notice.get('source_department', ''),
                'content': notice.get('content', ''),
                'source': notice.get('source', spider_name),
                'filter_pass_time': notice.get('filter_pass_time', '')
                # 不设置 competition_name 和 competition_level，让 insert_competition_notice 重新计算
            }
            
            if main_db_manager.insert_competition_notice(competition_notice):
                inserted_count += 1
                logger.debug(f"插入成功: {notice.get('title', '')[:50]}...")
            else:
                skipped_count += 1
                logger.debug(f"跳过: {notice.get('title', '')[:50]}...")
        
        logger.info(f"汇总完成：共插入 {inserted_count} 条竞赛公告到主竞赛数据库，跳过 {skipped_count} 条")
    
    logger.info("所有操作完成！")

if __name__ == "__main__":
    reset_and_aggregate()
