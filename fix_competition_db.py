#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 data\competiton.db 中的字段顺序问题
"""

import os
import sqlite3
from datetime import datetime
from contesttrace.core.filter.competition_filter import CompetitionFilter
from contesttrace.core.utils.data_processor import DataProcessor

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_competition_db():
    """
    修复 data\competiton.db 中的字段顺序问题
    """
    # 原始数据库路径
    raw_db_path = os.path.join('data', 'contest_trace_raw.db')
    # 目标竞赛数据库路径
    competition_db_path = os.path.join('data', 'competiton.db')
    
    # 检查原始数据库是否存在
    if not os.path.exists(raw_db_path):
        logger.error(f"原始数据库不存在: {raw_db_path}")
        return
    
    # 删除已存在的竞赛数据库
    if os.path.exists(competition_db_path):
        os.remove(competition_db_path)
        logger.info(f"已删除旧的竞赛数据库: {competition_db_path}")
    
    # 连接原始数据库
    raw_conn = sqlite3.connect(raw_db_path)
    raw_cursor = raw_conn.cursor()
    
    # 创建竞赛数据库
    competition_conn = sqlite3.connect(competition_db_path)
    competition_cursor = competition_conn.cursor()
    
    # 创建竞赛表
    competition_cursor.execute('''
    CREATE TABLE competition_notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_notice_id INTEGER,
        notice_url TEXT,
        title TEXT,
        publish_time DATE,
        publisher TEXT,
        content TEXT,
        source TEXT,
        filter_pass_time DATETIME,
        competition_name TEXT,
        competition_level TEXT,
        deadline TEXT,
        organizer TEXT,
        participants TEXT,
        prize TEXT,
        requirement TEXT,
        contact TEXT
    )
    ''')
    
    # 从原始数据库获取所有记录
    raw_cursor.execute('SELECT id, title, url, source, publish_time, crawl_time, content, spider_name FROM raw_notices')
    raw_notices = raw_cursor.fetchall()
    
    logger.info(f"从原始数据库获取到 {len(raw_notices)} 条记录")
    
    # 初始化过滤器
    competition_filter = CompetitionFilter()
    # 初始化数据处理器
    data_processor = DataProcessor()
    
    # 准备待筛选的通知
    notices_to_filter = []
    for notice in raw_notices:
        # 确保字段顺序正确
        notice_dict = {
            'id': notice[0],
            'title': notice[1],
            'notice_url': notice[2],
            'source': notice[3],
            'publish_time': notice[4],
            'crawl_time': notice[5],
            'content': notice[6],
            'spider_name': notice[7]
        }
        notices_to_filter.append(notice_dict)
    
    # 筛选通知
    filtered_notices = competition_filter.filter_notices(notices_to_filter)
    
    logger.info(f"筛选出 {len(filtered_notices)} 条竞赛通知")
    
    # 处理筛选结果
    for notice in filtered_notices:
        # 准备竞赛公告数据
        competition_notice = {
            'raw_notice_id': notice.get('id'),
            'notice_url': notice.get('notice_url', ''),
            'title': notice.get('title', ''),
            'publish_time': notice.get('publish_time', ''),
            'publisher': notice.get('source', ''),
            'content': notice.get('content', ''),
            'source': notice.get('spider_name', ''),
            'filter_pass_time': datetime.now().isoformat()
        }
        
        # 打印调试信息
        logger.debug(f"Processing notice ID {notice.get('id')}:")
        logger.debug(f"  Title: {notice.get('title')}")
        logger.debug(f"  URL: {notice.get('notice_url')}")
        logger.debug(f"  Publish time: {notice.get('publish_time')}")
        logger.debug(f"  Source: {notice.get('source')}")
        
        # 处理竞赛数据，识别竞赛名称和级别
        processed_contest = data_processor.process_contest(competition_notice)
        
        # 插入到竞赛数据库
        competition_cursor.execute('''
        INSERT INTO competition_notices (
            raw_notice_id, notice_url, title, publish_time, publisher, content, source, 
            filter_pass_time, competition_name, competition_level, deadline, organizer, 
            participants, prize, requirement, contact
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            processed_contest.get('raw_notice_id'),
            processed_contest.get('notice_url'),
            processed_contest.get('title'),
            processed_contest.get('publish_time'),
            processed_contest.get('publisher'),
            processed_contest.get('content'),
            processed_contest.get('source'),
            processed_contest.get('filter_pass_time'),
            processed_contest.get('competition_name'),
            processed_contest.get('competition_level'),
            processed_contest.get('deadline'),
            processed_contest.get('organizer'),
            processed_contest.get('participants'),
            processed_contest.get('prize'),
            processed_contest.get('requirement'),
            processed_contest.get('contact')
        ))
    
    # 提交事务
    competition_conn.commit()
    
    # 关闭连接
    raw_conn.close()
    competition_conn.close()
    
    logger.info(f"修复完成，共插入 {len(filtered_notices)} 条竞赛公告到 {competition_db_path}")

if __name__ == '__main__':
    fix_competition_db()
