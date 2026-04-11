#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比独立竞赛数据库和主竞赛数据库的记录数
"""

import os
import sqlite3
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_competition_count(db_path):
    """
    获取指定数据库中的竞赛公告数量
    
    Args:
        db_path: 数据库文件路径
    
    Returns:
        竞赛公告数量
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM competition_notices')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        logger.error(f"获取数据库 {db_path} 记录数失败: {e}")
        return 0

def compare_counts():
    """
    对比独立库和主库的记录数
    """
    data_dir = "data"
    if not os.path.exists(data_dir):
        logger.error("数据目录不存在: %s", data_dir)
        return
    
    # 统计所有独立竞赛数据库中的唯一记录
    independent_dbs = []
    total_independent_count = 0
    unique_records = set()
    
    for filename in os.listdir(data_dir):
        if filename.startswith("contest_trace_competition_") and filename != "contest_trace_competition.db":
            db_path = os.path.join(data_dir, filename)
            
            # 获取该数据库中的记录数
            count = get_competition_count(db_path)
            independent_dbs.append((filename, count))
            total_independent_count += count
            logger.info(f"{filename}: {count} 条")
            
            # 获取该数据库中的唯一记录
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT notice_url FROM competition_notices')
                rows = cursor.fetchall()
                for row in rows:
                    unique_records.add(row[0])
                conn.close()
            except Exception as e:
                logger.error(f"获取数据库 {filename} 中的记录失败: {e}")
    
    # 统计主竞赛数据库
    main_db_path = os.path.join(data_dir, "contest_trace_competition.db")
    main_count = get_competition_count(main_db_path)
    
    # 输出统计结果
    logger.info(f"\n独立竞赛数据库总数: {total_independent_count} 条")
    logger.info(f"独立竞赛数据库唯一记录数: {len(unique_records)} 条")
    logger.info(f"主竞赛数据库数量: {main_count} 条")
    
    if len(unique_records) == main_count:
        logger.info("✅ 独立库唯一记录数与主库数量一致，数据没有丢失")
    else:
        logger.error(f"❌ 数据丢失: 独立库唯一记录数 {len(unique_records)}，主库数量 {main_count}，相差 {abs(len(unique_records) - main_count)} 条")
    
    # 详细列出每个独立库的情况
    logger.info("\n详细统计:")
    for filename, count in independent_dbs:
        logger.info(f"  - {filename}: {count} 条")

if __name__ == "__main__":
    compare_counts()
