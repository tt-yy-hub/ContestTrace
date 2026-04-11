#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 data\contest_trace_raw.db 导出为 CSV 文件
"""

import os
import sqlite3
import csv
from datetime import datetime

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def export_raw_to_csv():
    """
    将 data\contest_trace_raw.db 导出为 CSV 文件
    """
    # 数据库路径
    db_path = os.path.join('data', 'contest_trace_raw.db')
    # 导出文件路径
    csv_path = os.path.join('data', 'contest_trace_raw.csv')
    
    # 检查数据库是否存在
    if not os.path.exists(db_path):
        logger.error(f"数据库不存在: {db_path}")
        return
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取表结构
    cursor.execute("PRAGMA table_info(raw_notices)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    logger.info(f"表结构: {column_names}")
    
    # 获取所有数据
    cursor.execute("SELECT * FROM raw_notices")
    rows = cursor.fetchall()
    
    logger.info(f"从数据库获取到 {len(rows)} 条记录")
    
    # 导出到 CSV
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        # 写入表头
        writer.writerow(column_names)
        # 写入数据
        for row in rows:
            writer.writerow(row)
    
    # 关闭连接
    conn.close()
    
    logger.info(f"成功导出 {len(rows)} 条记录到 {csv_path}")

if __name__ == '__main__':
    export_raw_to_csv()
