#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将各学院原始数据库中当日新爬取的公告汇总到主原始数据库
- 不删除旧数据库，只追加当日新数据
- 避免重复插入
"""

import os
import sqlite3
import logging
from pathlib import Path
from datetime import date, datetime

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
    将各学院原始数据库中当日新爬取的公告汇总到主原始数据库
    - 不删除旧数据库，只追加当日新数据
    """
    logger.info("开始汇总当日新公告到原始数据库...")
    
    # 确保数据目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 确保主原始数据库和表存在
    ensure_main_db_exists()
    
    # 获取今天的日期
    today = date.today().isoformat()
    logger.info(f"只汇总 {today} 当日新爬取的公告")
    
    # 合并每个原始数据库中当日新增的公告
    total_records = 0
    for db_name in RAW_DBS:
        db_file = DATA_DIR / db_name
        if not db_file.exists():
            logger.warning(f"数据库文件 {db_name} 不存在，跳过")
            continue
        
        logger.info(f"处理 {db_name} 中当日新公告...")
        records_count = merge_db(db_file, db_name, today)
        total_records += records_count
        if records_count > 0:
            logger.info(f"成功汇总 {records_count} 条新公告")
    
    logger.info(f"汇总完成！共汇总 {total_records} 条当日新公告到 {MAIN_RAW_DB}")

def ensure_main_db_exists():
    """
    确保主原始数据库和表存在
    """
    try:
        conn = sqlite3.connect(MAIN_RAW_DB)
        cursor = conn.cursor()
        
        # 创建原始公告表（如果不存在）
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
        logger.info(f"主原始数据库 {MAIN_RAW_DB} 检查完成")
    except Exception as e:
        logger.error(f"检查主原始数据库失败: {e}")
        raise

def merge_db(db_file, db_name, today):
    """
    合并单个原始数据库中当日新增的公告到主数据库

    Args:
        db_file: 原始数据库文件路径
        db_name: 原始数据库名称
        today: 当日日期字符串 (YYYY-MM-DD)

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

        # 检查源数据库的表结构
        try:
            # 优先从notices表中读取数据
            src_cursor.execute('SELECT * FROM notices LIMIT 1')
            src_columns = [description[0] for description in src_cursor.description]
            logger.info(f"从notices表读取，列: {src_columns}")
        except sqlite3.OperationalError as e:
            logger.error(f"从notices表读取失败: {e}")
            src_conn.close()
            dest_conn.close()
            return 0

        # 检查是否有 crawl_time 列
        has_crawl_time = 'crawl_time' in src_columns

        if has_crawl_time:
            # 只查询当日新爬取的公告（根据 crawl_time 判断）
            query = 'SELECT * FROM notices WHERE DATE(crawl_time) = ?'
            src_cursor.execute(query, (today,))
            rows = src_cursor.fetchall()
            logger.info(f"从notices表中获取到 {len(rows)} 条当日新增记录")
        else:
            # 如果没有 crawl_time 列，则跳过（当日新增应该在爬虫层已经判断过）
            logger.info(f"该数据库没有 crawl_time 列，跳过")
            src_conn.close()
            dest_conn.close()
            return 0

        if len(rows) == 0:
            logger.info(f"当日没有新公告需要汇总")
            src_conn.close()
            dest_conn.close()
            return 0

        # 获取源表的列索引
        col_indices = {col: idx for idx, col in enumerate(src_columns)}

        # 插入记录到目标数据库
        inserted_count = 0
        for row in rows:
            try:
                # 根据列名获取对应索引的值
                notice_id = row[col_indices.get('id', 0)]
                title = row[col_indices.get('title', 1)]
                notice_url = row[col_indices.get('url', 2)]
                publisher = row[col_indices.get('publisher', 3)]
                publish_time = row[col_indices.get('publish_time', 4)]
                crawl_time = row[col_indices.get('crawl_time', 5)] if has_crawl_time else ''
                deadline = row[col_indices.get('deadline', 6)] if 'deadline' in col_indices else None
                category = row[col_indices.get('category', 7)] if 'category' in col_indices else None
                organizer = row[col_indices.get('organizer', 8)] if 'organizer' in col_indices else None
                participants = row[col_indices.get('participants', 9)] if 'participants' in col_indices else None
                prize = row[col_indices.get('prize', 10)] if 'prize' in col_indices else None
                requirement = row[col_indices.get('requirement', 11)] if 'requirement' in col_indices else None
                contact = row[col_indices.get('contact', 12)] if 'contact' in col_indices else None
                content = row[col_indices.get('content', 13)] if 'content' in col_indices else ''
                keywords = row[col_indices.get('keywords', 14)] if 'keywords' in col_indices else None
                tags = row[col_indices.get('tags', 15)] if 'tags' in col_indices else None
                spider_name = row[col_indices.get('spider_name', 16)] if 'spider_name' in col_indices else db_name.replace("contest_trace_raw_", "").replace(".db", "")
                created_at = row[col_indices.get('created_at', 17)] if 'created_at' in col_indices else datetime.now().isoformat()
                updated_at = row[col_indices.get('updated_at', 18)] if 'updated_at' in col_indices else datetime.now().isoformat()

                # 准备插入数据
                url = notice_url
                source = publisher

                # 执行插入（使用 INSERT OR IGNORE，URL 冲突时忽略）
                dest_cursor.execute('''
                INSERT OR IGNORE INTO raw_notices
                (title, url, source, publish_time, crawl_time,
                 deadline, category, organizer, participants, prize,
                 requirement, contact, content, keywords, tags,
                 spider_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (title, url, source, publish_time, crawl_time,
                      deadline, category, organizer, participants, prize,
                      requirement, contact, content, keywords, tags,
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
