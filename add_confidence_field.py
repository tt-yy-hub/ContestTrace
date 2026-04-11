#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有数据库添加 confidence 字段
"""

import os
import sqlite3

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_confidence_field(db_path):
    """
    为指定数据库添加 confidence 字段
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取数据库中的表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            # 跳过 sqlite_sequence 系统表
            if table_name == 'sqlite_sequence':
                continue
            
            # 检查表是否已包含 confidence 字段
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'confidence' not in column_names:
                # 添加 confidence 字段
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN confidence REAL DEFAULT 0.0;")
                logger.info(f"已为 {db_path} 中的 {table_name} 表添加 confidence 字段")
            else:
                logger.info(f"{db_path} 中的 {table_name} 表已包含 confidence 字段，跳过")
        
        # 提交事务
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"处理 {db_path} 时出错：{str(e)}")
        return False

def main():
    """
    为所有数据库添加 confidence 字段
    """
    data_dir = 'data'
    db_files = [f for f in os.listdir(data_dir) if f.endswith('.db')]
    
    logger.info(f"找到 {len(db_files)} 个数据库文件")
    
    for db_file in db_files:
        db_path = os.path.join(data_dir, db_file)
        logger.info(f"处理数据库：{db_file}")
        add_confidence_field(db_path)
    
    logger.info("所有数据库处理完成")

if __name__ == '__main__':
    main()
