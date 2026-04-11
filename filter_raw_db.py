#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对 data\contest_trace_raw.db 进行筛选，将筛选后的公告放到 data\competiton.db 中
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

# 原始数据库路径
RAW_DB = DATA_DIR / "contest_trace_raw.db"

# 竞赛数据库路径
COMP_DB = DATA_DIR / "competiton.db"

def filter_raw_db():
    """
    对 data\contest_trace_raw.db 进行筛选，将筛选后的公告放到 data\competiton.db 中
    """
    logger.info("开始筛选原始数据库...")
    
    # 确保数据目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 检查原始数据库是否存在
    if not RAW_DB.exists():
        logger.error(f"原始数据库 {RAW_DB} 不存在")
        return
    
    # 删除已存在的竞赛数据库
    if COMP_DB.exists():
        logger.info(f"删除已存在的 {COMP_DB}")
        COMP_DB.unlink()
    
    # 创建新的竞赛数据库
    create_competition_db()
    
    # 读取原始数据库中的所有记录
    raw_notices = get_raw_notices()
    logger.info(f"获取到 {len(raw_notices)} 条原始公告")
    
    # 使用现有的筛选逻辑进行筛选
    filtered_notices = filter_notices(raw_notices)
    logger.info(f"筛选出 {len(filtered_notices)} 条竞赛公告")
    
    # 将筛选后的记录插入到竞赛数据库中
    insert_competition_notices(filtered_notices)
    
    logger.info(f"筛选完成！共筛选出 {len(filtered_notices)} 条竞赛公告到 {COMP_DB}")

def create_competition_db():
    """
    创建新的竞赛数据库
    """
    try:
        conn = sqlite3.connect(COMP_DB)
        cursor = conn.cursor()
        
        # 创建竞赛公告表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS competition_notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_notice_id INTEGER,
            notice_url TEXT,
            title TEXT NOT NULL,
            publish_time TEXT NOT NULL,
            source_department TEXT NOT NULL,
            content TEXT NOT NULL,
            summary TEXT,
            tags TEXT,
            sign_up_deadline TEXT,
            filter_pass_time TEXT NOT NULL,
            deadline TEXT,
            organizer TEXT,
            participants TEXT,
            prize TEXT,
            requirement TEXT,
            contact TEXT,
            competition_name TEXT,
            competition_level TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"竞赛数据库 {COMP_DB} 创建成功")
    except Exception as e:
        logger.error(f"创建竞赛数据库失败: {e}")
        raise

def get_raw_notices():
    """
    读取原始数据库中的所有记录
    
    Returns:
        原始公告列表
    """
    try:
        conn = sqlite3.connect(RAW_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询所有原始公告
        cursor.execute('SELECT * FROM raw_notices')
        rows = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        notices = []
        for row in rows:
            notice = dict(row)
            notices.append(notice)
        
        return notices
    except Exception as e:
        logger.error(f"读取原始数据库失败: {e}")
        return []

def filter_notices(notices):
    """
    使用现有的筛选逻辑对公告进行筛选
    
    Args:
        notices: 原始公告列表
    
    Returns:
        筛选后的竞赛公告列表
    """
    try:
        # 导入现有的筛选器
        from contesttrace.core.filter.competition_filter import CompetitionFilter
        
        # 初始化筛选器
        competition_filter = CompetitionFilter()
        
        # 对公告进行筛选
        filtered_notices = competition_filter.filter_notices(notices)
        
        return filtered_notices
    except Exception as e:
        logger.error(f"筛选公告失败: {e}")
        return []

def insert_competition_notices(notices):
    """
    将筛选后的记录插入到竞赛数据库中
    
    Args:
        notices: 筛选后的竞赛公告列表
    """
    try:
        conn = sqlite3.connect(COMP_DB)
        cursor = conn.cursor()
        
        # 导入数据处理器
        from contesttrace.core.utils.data_processor import DataProcessor
        data_processor = DataProcessor()
        
        # 插入每条记录
        inserted_count = 0
        for notice in notices:
            try:
                # 准备插入数据
                raw_notice_id = notice.get('id')
                notice_url = notice.get('url', '')
                title = notice.get('title', '')
                publish_time = notice.get('publish_time', '')
                source_department = notice.get('source', '')
                content = notice.get('content', '')
                filter_pass_time = datetime.now().isoformat()
                
                # 处理竞赛公告，提取详细字段
                contest = {
                    'id': raw_notice_id,
                    'title': title,
                    'content': content
                }
                processed_contest = data_processor.process_contest(contest)
                
                # 获取竞赛名称和级别
                competition_name = processed_contest.get('competition_name')
                competition_level = processed_contest.get('competition_level')
                
                # 执行插入
                cursor.execute('''
                INSERT INTO competition_notices 
                (raw_notice_id, notice_url, title, publish_time, source_department, 
                 content, summary, tags, sign_up_deadline, filter_pass_time, 
                 deadline, organizer, participants, prize, requirement, contact, 
                 competition_name, competition_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (raw_notice_id, notice_url, title, publish_time, source_department, 
                      content, '', '', '', filter_pass_time, 
                      processed_contest.get('deadline', ''),
                      processed_contest.get('organizer', ''),
                      processed_contest.get('participants', ''),
                      processed_contest.get('prize', ''),
                      processed_contest.get('requirement', ''),
                      processed_contest.get('contact', ''),
                      competition_name,
                      competition_level))
                
                inserted_count += 1
            except Exception as e:
                logger.error(f"插入竞赛公告失败: {e}")
                continue
        
        # 提交事务
        conn.commit()
        conn.close()
        
        logger.info(f"成功插入 {inserted_count} 条竞赛公告")
    except Exception as e:
        logger.error(f"插入竞赛公告失败: {e}")

if __name__ == "__main__":
    filter_raw_db()
