#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从原始数据库筛选数据到竞赛数据库
- 处理独立原始数据库到对应独立竞赛数据库
- 处理汇总原始数据库到汇总竞赛数据库
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

def create_competition_table(cursor):
    """
    创建竞赛数据库表
    """
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS competition_notices (
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
        contact TEXT,
        confidence REAL DEFAULT 0.0
    )
    ''')

def process_database(raw_db_path, competition_db_path, competition_filter, data_processor):
    """
    处理单个数据库的筛选
    """
    # 检查原始数据库是否存在
    if not os.path.exists(raw_db_path):
        logger.error(f"原始数据库不存在: {raw_db_path}")
        return 0
    
    # 连接原始数据库
    raw_conn = sqlite3.connect(raw_db_path)
    raw_cursor = raw_conn.cursor()
    
    # 连接或创建竞赛数据库
    competition_conn = sqlite3.connect(competition_db_path)
    competition_cursor = competition_conn.cursor()
    
    # 创建竞赛数据库表
    create_competition_table(competition_cursor)
    
    # 检查raw_notices表的列结构
    raw_cursor.execute('PRAGMA table_info(raw_notices)')
    columns = [column[1] for column in raw_cursor.fetchall()]
    
    # 确定URL列名
    url_col = 'url' if 'url' in columns else 'notice_url' if 'notice_url' in columns else 'link'
    # 确定来源列名
    source_col = 'source' if 'source' in columns else 'publisher' if 'publisher' in columns else 'org'
    # 确定是否有spider_name列
    has_spider_name = 'spider_name' in columns
    # 确定是否有crawl_time列
    has_crawl_time = 'crawl_time' in columns
    
    # 构建查询语句
    select_columns = ['id', 'title', url_col, source_col, 'publish_time']
    if has_crawl_time:
        select_columns.append('crawl_time')
    select_columns.append('content')
    if has_spider_name:
        select_columns.append('spider_name')
    
    query = f'SELECT {", ".join(select_columns)} FROM raw_notices'
    
    # 确定索引位置
    url_idx = 2
    source_idx = 3
    publish_time_idx = 4
    crawl_time_idx = 5 if has_crawl_time else None
    content_idx = 6 if has_crawl_time else 5
    spider_name_idx = 7 if (has_crawl_time and has_spider_name) else 6 if has_spider_name else None
    
    # 执行查询
    try:
        raw_cursor.execute(query)
        raw_notices = raw_cursor.fetchall()
    except sqlite3.OperationalError as e:
        logger.error(f"执行查询失败: {e}")
        logger.error(f"数据库结构可能不同，尝试使用默认表结构")
        # 尝试使用默认表结构
        try:
            raw_cursor.execute('SELECT id, title, url, source, publish_time, crawl_time, content, spider_name FROM notices')
            raw_notices = raw_cursor.fetchall()
            # 调整索引位置
            url_idx = 2
            source_idx = 3
            publish_time_idx = 4
            crawl_time_idx = 5
            content_idx = 6
            spider_name_idx = 7
            has_spider_name = True
            has_crawl_time = True
            logger.info(f"使用默认表结构成功，获取到 {len(raw_notices)} 条记录")
        except Exception as e2:
            logger.error(f"使用默认表结构也失败: {e2}")
            raw_notices = []
    
    logger.info(f"从 {os.path.basename(raw_db_path)} 获取到 {len(raw_notices)} 条记录")
    
    # 准备待筛选的通知
    notices_to_filter = []
    for notice in raw_notices:
        notice_dict = {
            'id': notice[0],
            'title': notice[1],
            'notice_url': notice[url_idx],
            'source': notice[source_idx],
            'publish_time': notice[publish_time_idx],
            'crawl_time': notice[crawl_time_idx] if crawl_time_idx is not None else '',
            'content': notice[content_idx],
            'spider_name': notice[spider_name_idx] if spider_name_idx is not None else ''
        }
        notices_to_filter.append(notice_dict)
    
    # 筛选通知
    filtered_notices = competition_filter.filter_notices(notices_to_filter)
    
    logger.info(f"从 {os.path.basename(raw_db_path)} 筛选出 {len(filtered_notices)} 条竞赛通知")
    
    # 处理筛选结果
    inserted_count = 0
    for notice in filtered_notices:
        # 检查是否已存在相同的记录
        competition_cursor.execute('''
        SELECT id FROM competition_notices WHERE raw_notice_id = ? OR notice_url = ?
        ''', (notice.get('id'), notice.get('notice_url', '')))
        existing_record = competition_cursor.fetchone()
        
        if existing_record:
            logger.debug(f"记录已存在，跳过: {notice.get('title')}")
            continue
        
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
        
        # 处理竞赛数据，识别竞赛名称和级别
        processed_contest = data_processor.process_contest(competition_notice)
        
        # 插入到竞赛数据库
        competition_cursor.execute('''
        INSERT INTO competition_notices (
            raw_notice_id, notice_url, title, publish_time, publisher, content, source, 
            filter_pass_time, competition_name, competition_level, deadline, organizer, 
            participants, prize, requirement, contact, confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            processed_contest.get('contact'),
            notice.get('filter_confidence', 0.0)
        ))
        inserted_count += 1
    
    # 提交事务
    competition_conn.commit()
    
    # 关闭连接
    raw_conn.close()
    competition_conn.close()
    
    logger.info(f"筛选完成，共插入 {inserted_count} 条竞赛公告到 {competition_db_path}")
    return inserted_count

def filter_raw_to_competition():
    """
    从原始数据库筛选数据到竞赛数据库
    - 只处理汇总原始数据库到汇总竞赛数据库
    """
    # 初始化竞赛指南解析器并加载指南数据
    from contesttrace.core.utils.contest_guide_parser import contest_guide_parser
    guide_competitions = contest_guide_parser.load_guide_competitions()
    
    # 初始化过滤器，传入指南数据
    competition_filter = CompetitionFilter(guide_competitions=guide_competitions)
    # 初始化数据处理器
    data_processor = DataProcessor()
    
    # 处理汇总的原始数据库
    logger.info("开始处理汇总原始数据库...")
    raw_db_path = os.path.join('data', 'contest_trace_raw.db')
    competition_db_path = os.path.join('data', 'competiton.db')
    process_database(raw_db_path, competition_db_path, competition_filter, data_processor)
    
    logger.info("数据库处理完成")
    
    # 导出数据到前端
    logger.info("开始导出数据到前端...")
    try:
        import subprocess
        subprocess.run(['python', 'export_to_frontend.py'], check=True)
        logger.info("前端数据更新完成")
    except Exception as e:
        logger.error(f"导出到前端失败: {e}")

if __name__ == '__main__':
    filter_raw_to_competition()
