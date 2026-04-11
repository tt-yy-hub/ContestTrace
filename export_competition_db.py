#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出data\competiton.db数据库内容到CSV文件
"""

import os
import sqlite3
import csv
from datetime import datetime

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def export_competition_db():
    """
    导出competiton.db数据库内容到CSV文件
    """
    # 数据库路径
    db_path = os.path.join('data', 'competiton.db')
    
    # 检查数据库是否存在
    if not os.path.exists(db_path):
        logger.error(f"数据库不存在: {db_path}")
        return
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询所有竞赛通知
    cursor.execute('SELECT * FROM competition_notices')
    rows = cursor.fetchall()
    
    # 获取列名
    column_names = [description[0] for description in cursor.description]
    
    # 创建导出目录
    export_dir = os.path.join('data', 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    # 生成导出文件名
    export_filename = f"competiton_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    export_path = os.path.join(export_dir, export_filename)
    
    # 写入CSV文件
    with open(export_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        # 写入列名
        writer.writerow(column_names)
        # 写入数据
        for row in rows:
            writer.writerow(row)
    
    # 关闭连接
    conn.close()
    
    logger.info(f"导出完成，共导出 {len(rows)} 条记录到 {export_path}")
    return export_path

if __name__ == '__main__':
    export_competition_db()
