#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复原始数据库中的字段顺序问题
"""

import os
import sqlite3
from datetime import datetime

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_raw_db():
    """
    修复原始数据库中的字段顺序问题
    """
    # 原始数据库路径
    raw_db_path = os.path.join('data', 'contest_trace_raw.db')
    # 临时数据库路径
    temp_db_path = os.path.join('data', 'contest_trace_raw_temp.db')
    
    # 检查原始数据库是否存在
    if not os.path.exists(raw_db_path):
        logger.error(f"原始数据库不存在: {raw_db_path}")
        return
    
    # 连接原始数据库
    raw_conn = sqlite3.connect(raw_db_path)
    raw_cursor = raw_conn.cursor()
    
    # 创建临时数据库
    temp_conn = sqlite3.connect(temp_db_path)
    temp_cursor = temp_conn.cursor()
    
    # 创建正确的表结构
    temp_cursor.execute('''
    CREATE TABLE raw_notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT,
        source TEXT,
        publish_time TEXT,
        crawl_time TEXT,
        deadline TEXT,
        category TEXT,
        organizer TEXT,
        participants TEXT,
        prize TEXT,
        requirement TEXT,
        contact TEXT,
        content TEXT,
        keywords TEXT,
        tags TEXT,
        spider_name TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    # 获取所有记录
    raw_cursor.execute('SELECT * FROM raw_notices')
    all_records = raw_cursor.fetchall()
    
    logger.info(f"从原始数据库获取到 {len(all_records)} 条记录")
    
    # 修复字段顺序并插入到临时数据库
    for record in all_records:
        # 对于 id 为 402, 403, 404 的记录，修复字段顺序
        if record[0] in [402, 403, 404]:
            # 原始记录的字段顺序是错误的，需要修复
            # 原始顺序: id, title, url, source, publish_time, crawl_time, deadline, category, organizer, participants, prize, requirement, contact, content, keywords, tags, spider_name, created_at, updated_at
            # 但实际值是: id, url, title, publish_time, source, tags, deadline, category, organizer, participants, prize, requirement, contact, content, keywords, crawl_time, spider_name, created_at, updated_at
            fixed_record = (
                record[0],  # id
                record[2],  # title (从原始的 url 字段获取)
                record[1],  # url (从原始的 title 字段获取)
                record[4],  # source (从原始的 publish_time 字段获取)
                record[3],  # publish_time (从原始的 source 字段获取)
                record[16], # crawl_time (从原始的 spider_name 字段获取)
                record[6],  # deadline
                record[7],  # category
                record[8],  # organizer
                record[9],  # participants
                record[10], # prize
                record[11], # requirement
                record[12], # contact
                record[13], # content
                record[14], # keywords
                record[5],  # tags (从原始的 crawl_time 字段获取)
                record[16], # spider_name
                record[17], # created_at
                record[18]  # updated_at
            )
        else:
            # 其他记录字段顺序正确，直接使用
            fixed_record = record
        
        # 插入到临时数据库
        temp_cursor.execute('''
        INSERT INTO raw_notices (
            id, title, url, source, publish_time, crawl_time, deadline, category, 
            organizer, participants, prize, requirement, contact, content, keywords, 
            tags, spider_name, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', fixed_record)
    
    # 提交事务
    temp_conn.commit()
    
    # 关闭连接
    raw_conn.close()
    temp_conn.close()
    
    # 替换原始数据库
    os.remove(raw_db_path)
    os.rename(temp_db_path, raw_db_path)
    
    logger.info(f"修复完成，共修复 {len(all_records)} 条记录")

if __name__ == '__main__':
    fix_raw_db()
