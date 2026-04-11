#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查原始数据库中 id 为 402, 403, 404 的记录
"""

import os
import sqlite3

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_raw_records():
    """
    检查原始数据库中 id 为 402, 403, 404 的记录
    """
    # 原始数据库路径
    raw_db_path = os.path.join('data', 'contest_trace_raw.db')
    
    # 检查原始数据库是否存在
    if not os.path.exists(raw_db_path):
        logger.error(f"原始数据库不存在: {raw_db_path}")
        return
    
    # 连接原始数据库
    raw_conn = sqlite3.connect(raw_db_path)
    raw_cursor = raw_conn.cursor()
    
    # 获取表结构
    raw_cursor.execute("PRAGMA table_info(raw_notices)")
    raw_columns = raw_cursor.fetchall()
    raw_column_names = [col[1] for col in raw_columns]
    logger.info(f"原始数据库表结构: {raw_column_names}")
    
    # 检查指定记录
    for notice_id in [402, 403, 404]:
        raw_cursor.execute("SELECT id, title, url, source, publish_time, crawl_time, content, spider_name FROM raw_notices WHERE id = ?", (notice_id,))
        row = raw_cursor.fetchone()
        if row:
            logger.info(f"\n原始数据库记录 ID {notice_id}:")
            logger.info(f"  id: {row[0]}")
            logger.info(f"  title: {row[1]}")
            logger.info(f"  url: {row[2]}")
            logger.info(f"  source: {row[3]}")
            logger.info(f"  publish_time: {row[4]}")
            logger.info(f"  crawl_time: {row[5]}")
            logger.info(f"  content: {row[6][:100]}...")
            logger.info(f"  spider_name: {row[7]}")
        else:
            logger.warning(f"原始数据库中未找到 ID {notice_id} 的记录")
    
    # 关闭连接
    raw_conn.close()

if __name__ == '__main__':
    check_raw_records()
