#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查原始数据库中的筛选状态
"""

import sqlite3
import os

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_filter_status(db_path):
    """
    检查指定数据库中的筛选状态
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 统计筛选状态
        cursor.execute("SELECT filter_status, COUNT(*) FROM raw_notices GROUP BY filter_status;")
        status_counts = cursor.fetchall()
        
        logger.info(f"检查数据库：{db_path}")
        logger.info("筛选状态统计：")
        for status, count in status_counts:
            logger.info(f"  {status}: {count} 条")
        
        # 检查待筛选的公告
        cursor.execute("SELECT id, title, publish_time FROM raw_notices WHERE filter_status = 'pending' LIMIT 5;")
        pending_notices = cursor.fetchall()
        
        if pending_notices:
            logger.info("\n待筛选的公告（前 5 条）：")
            for notice in pending_notices:
                logger.info(f"  ID: {notice[0]}, 标题: {notice[1][:50]}..., 发布时间: {notice[2]}")
        else:
            logger.info("\n没有待筛选的公告")
        
        conn.close()
    except Exception as e:
        logger.error(f"处理 {db_path} 时出错：{str(e)}")

def main():
    """
    检查原始数据库中的筛选状态
    """
    # 检查主原始数据库
    db_file = 'data/contest_trace_raw.db'
    if os.path.exists(db_file):
        check_filter_status(db_file)
    else:
        logger.error(f"数据库文件不存在：{db_file}")

if __name__ == '__main__':
    main()
