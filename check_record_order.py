#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 data\contest_trace_raw.db 中 id 为 402,403,404 的三条公告的字段顺序
以及 data\competiton.db 中对应的记录
"""

import os
import sqlite3

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_record_order():
    """
    检查记录的字段顺序
    """
    # 原始数据库路径
    raw_db_path = os.path.join('data', 'contest_trace_raw.db')
    # 竞赛数据库路径
    competition_db_path = os.path.join('data', 'competiton.db')
    
    # 检查原始数据库
    if os.path.exists(raw_db_path):
        logger.info("检查原始数据库: data\contest_trace_raw.db")
        raw_conn = sqlite3.connect(raw_db_path)
        raw_cursor = raw_conn.cursor()
        
        # 获取表结构
        raw_cursor.execute("PRAGMA table_info(raw_notices)")
        raw_columns = raw_cursor.fetchall()
        raw_column_names = [col[1] for col in raw_columns]
        logger.info(f"原始数据库表结构: {raw_column_names}")
        
        # 检查指定记录
        for notice_id in [402, 403, 404]:
            raw_cursor.execute("SELECT * FROM raw_notices WHERE id = ?", (notice_id,))
            row = raw_cursor.fetchone()
            if row:
                logger.info(f"\n原始数据库记录 ID {notice_id}:")
                for i, (col_name, value) in enumerate(zip(raw_column_names, row)):
                    logger.info(f"  {i+1}. {col_name}: {value}")
            else:
                logger.warning(f"原始数据库中未找到 ID {notice_id} 的记录")
        
        raw_conn.close()
    else:
        logger.error(f"原始数据库不存在: {raw_db_path}")
    
    # 检查竞赛数据库
    if os.path.exists(competition_db_path):
        logger.info("\n检查竞赛数据库: data\competiton.db")
        competition_conn = sqlite3.connect(competition_db_path)
        competition_cursor = competition_conn.cursor()
        
        # 获取表结构
        competition_cursor.execute("PRAGMA table_info(competition_notices)")
        competition_columns = competition_cursor.fetchall()
        competition_column_names = [col[1] for col in competition_columns]
        logger.info(f"竞赛数据库表结构: {competition_column_names}")
        
        # 检查指定记录
        for raw_notice_id in [402, 403, 404]:
            competition_cursor.execute("SELECT * FROM competition_notices WHERE raw_notice_id = ?", (raw_notice_id,))
            row = competition_cursor.fetchone()
            if row:
                logger.info(f"\n竞赛数据库记录 raw_notice_id {raw_notice_id}:")
                for i, (col_name, value) in enumerate(zip(competition_column_names, row)):
                    logger.info(f"  {i+1}. {col_name}: {value}")
            else:
                logger.warning(f"竞赛数据库中未找到 raw_notice_id {raw_notice_id} 的记录")
        
        competition_conn.close()
    else:
        logger.error(f"竞赛数据库不存在: {competition_db_path}")

if __name__ == '__main__':
    check_record_order()
