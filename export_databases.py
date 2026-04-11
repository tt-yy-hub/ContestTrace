#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出 data\competiton.db 和 data\contest_trace_raw.db 数据库到 CSV 文件
"""

import sqlite3
import os
import csv

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def export_database_to_csv(db_path):
    """
    导出指定数据库中的所有表到 CSV 文件
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取数据库中的表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # 确保导出目录存在
        export_dir = 'exports'
        os.makedirs(export_dir, exist_ok=True)
        
        # 提取数据库名称
        db_name = os.path.basename(db_path).replace('.db', '')
        
        logger.info(f"导出数据库：{db_path}")
        
        for table in tables:
            table_name = table[0]
            # 跳过 sqlite_sequence 系统表
            if table_name == 'sqlite_sequence':
                continue
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # 获取表数据
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            if rows:
                # 构建导出文件路径
                csv_file_path = os.path.join(export_dir, f"{db_name}_{table_name}.csv")
                
                logger.info(f"  导出表 {table_name} 到 {csv_file_path}")
                
                # 写入 CSV 文件
                with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    # 写入表头
                    writer.writerow(column_names)
                    # 写入数据
                    for row in rows:
                        writer.writerow(row)
                
                logger.info(f"  表 {table_name} 导出完成，共 {len(rows)} 条记录")
            else:
                logger.info(f"  表 {table_name} 无记录，跳过")
        
        conn.close()
        logger.info(f"数据库 {db_path} 导出完成")
        
    except Exception as e:
        logger.error(f"导出数据库 {db_path} 失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """
    主函数
    """
    # 要导出的数据库
    db_files = [
        'data/competiton.db',
        'data/contest_trace_raw.db'
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            export_database_to_csv(db_file)
        else:
            logger.error(f"数据库文件不存在：{db_file}")
    
    logger.info("所有数据库导出完成")

if __name__ == '__main__':
    main()
