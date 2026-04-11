#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查指定数据库是否包含 confidence 字段
"""

import sqlite3
import os

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_confidence_field(db_path):
    """
    检查指定数据库是否包含 confidence 字段
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取数据库中的表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        logger.info(f"检查数据库：{db_path}")
        
        for table in tables:
            table_name = table[0]
            # 检查表是否已包含 confidence 字段
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'confidence' in column_names:
                logger.info(f"  ✓ {table_name} 表包含 confidence 字段")
            else:
                logger.warning(f"  ✗ {table_name} 表缺少 confidence 字段")
        
        conn.close()
    except Exception as e:
        logger.error(f"处理 {db_path} 时出错：{str(e)}")

def main():
    """
    检查指定数据库是否包含 confidence 字段
    """
    # 要检查的数据库列表
    db_files = [
        'data/contest_trace_competition_新闻与传播学院.db',
        'data/contest_trace_raw_金融学院.db',
        'data/contest_trace_competition_会计学院.db',
        'data/contest_trace_raw_实验教学中心.db'
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            check_confidence_field(db_file)
        else:
            logger.error(f"数据库文件不存在：{db_file}")

if __name__ == '__main__':
    main()
