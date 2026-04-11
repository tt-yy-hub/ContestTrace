#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新建 data\contest_trace_raw.db，汇总 15 个原始数据库的公告
"""

import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 数据目录
DATA_DIR = Path("data")

# 主原始数据库路径
MAIN_RAW_DB = DATA_DIR / "contest_trace_raw.db"

# 15个原始数据库文件
RAW_DBS = [
    "contest_trace_raw_会计学院.db",
    "contest_trace_raw_信息工程学院.db",
    "contest_trace_raw_信息管理学院.db",
    "contest_trace_raw_外国语学院.db",
    "contest_trace_raw_学生工作处.db",
    "contest_trace_raw_实验教学中心.db",
    "contest_trace_raw_工商管理学院.db",
    "contest_trace_raw_教务处.db",
    "contest_trace_raw_新闻与传播学院.db",
    "contest_trace_raw_旅游与酒店管理学院.db",
    "contest_trace_raw_湖北经济学院团委.db",
    "contest_trace_raw_经济与贸易学院.db",
    "contest_trace_raw_统计与数学学院.db",
    "contest_trace_raw_艺术学院.db",
    "contest_trace_raw_金融学院.db"
]

def create_raw_db():
    """
    新建 data\contest_trace_raw.db，汇总 15 个原始数据库的公告
    """
    logger.info("开始创建并汇总原始数据库...")
    
    # 确保数据目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 删除已存在的文件
    if MAIN_RAW_DB.exists():
        logger.info(f"删除已存在的 {MAIN_RAW_DB}")
        MAIN_RAW_DB.unlink()
    
    # 创建新的主原始数据库
    create_main_db()
    
    # 合并每个原始数据库
    total_records = 0
    for db_name in RAW_DBS:
        db_file = DATA_DIR / db_name
        if not db_file.exists():
            logger.warning(f"数据库文件 {db_name} 不存在，跳过")
            continue
        
        logger.info(f"合并 {db_name}...")
        records_count = merge_db(db_file, db_name)
        total_records += records_count
        logger.info(f"成功合并 {records_count} 条记录")
    
    logger.info(f"合并完成！共合并 {total_records} 条记录到 {MAIN_RAW_DB}")

def create_main_db():
    """
    创建新的主原始数据库
    """
    try:
        conn = sqlite3.connect(MAIN_RAW_DB)
        cursor = conn.cursor()
        
        # 创建原始公告表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            publish_time TEXT NOT NULL,
            crawl_time TEXT NOT NULL,
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
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(url)
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"主原始数据库 {MAIN_RAW_DB} 创建成功")
    except Exception as e:
        logger.error(f"创建主原始数据库失败: {e}")
        raise

def merge_db(db_file, db_name):
    """
    合并单个原始数据库到主数据库
    
    Args:
        db_file: 原始数据库文件路径
        db_name: 原始数据库名称
    
    Returns:
        合并的记录数
    """
    try:
        # 连接源数据库
        src_conn = sqlite3.connect(db_file)
        src_cursor = src_conn.cursor()
        
        # 连接目标数据库
        dest_conn = sqlite3.connect(MAIN_RAW_DB)
        dest_cursor = dest_conn.cursor()
        
        # 查询源数据库中的所有记录
        src_cursor.execute('SELECT * FROM raw_notices')
        rows = src_cursor.fetchall()
        
        # 插入记录到目标数据库
        inserted_count = 0
        for row in rows:
            try:
                # 从源记录中提取字段
                # 源表结构: id, notice_url, title, publish_time, publisher, content, crawl_time, filter_status, filter_time, review_status, review_time, review_result, review_notes, filter_confidence
                notice_id = row[0]
                notice_url = row[1]
                title = row[2]
                publish_time = row[3]
                publisher = row[4]
                content = row[5]
                crawl_time = row[6]
                
                # 准备插入数据
                url = notice_url
                source = publisher
                spider_name = db_name.replace("contest_trace_raw_", "").replace(".db", "")
                created_at = datetime.now().isoformat()
                updated_at = datetime.now().isoformat()
                
                # 执行插入
                dest_cursor.execute('''
                INSERT OR IGNORE INTO raw_notices 
                (title, url, source, publish_time, crawl_time, 
                 deadline, category, organizer, participants, prize, 
                 requirement, contact, content, keywords, tags, 
                 spider_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (title, url, source, publish_time, crawl_time, 
                      None, None, None, None, None, 
                      None, None, content, None, None, 
                      spider_name, created_at, updated_at))
                
                if dest_cursor.rowcount > 0:
                    inserted_count += 1
            except Exception as e:
                logger.error(f"插入记录失败: {e}")
                continue
        
        # 提交事务
        dest_conn.commit()
        
        # 关闭连接
        src_conn.close()
        dest_conn.close()
        
        return inserted_count
    except Exception as e:
        logger.error(f"合并数据库 {db_name} 失败: {e}")
        return 0

if __name__ == "__main__":
    create_raw_db()
