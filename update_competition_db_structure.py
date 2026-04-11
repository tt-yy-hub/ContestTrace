#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新竞赛数据库的表结构，使其使用新的字段结构
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

def update_competition_db_structure():
    """
    更新竞赛数据库的表结构
    """
    logger.info("开始更新竞赛数据库表结构...")
    
    # 确保数据目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 找到所有竞赛数据库文件
    comp_dbs = []
    for filename in os.listdir(DATA_DIR):
        if filename.startswith("contest_trace_competition") and filename.endswith(".db"):
            comp_dbs.append(filename)
    
    logger.info(f"找到 {len(comp_dbs)} 个竞赛数据库文件")
    
    # 更新每个竞赛数据库
    for db_filename in comp_dbs:
        db_path = DATA_DIR / db_filename
        logger.info(f"更新数据库: {db_filename}")
        update_single_db(db_path)
    
    logger.info("所有竞赛数据库表结构更新完成！")

def update_single_db(db_path):
    """
    更新单个竞赛数据库的表结构
    
    Args:
        db_path: 数据库文件路径
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查是否已经是新结构
        cursor.execute('PRAGMA table_info(competition_notices)')
        columns = [row[1] for row in cursor.fetchall()]
        
        # 如果已经有 publisher 字段，说明已经是新结构
        if 'publisher' in columns:
            logger.info(f"数据库 {db_path.name} 已经是新结构，跳过")
            conn.close()
            return
        
        # 创建临时表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS competition_notices_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_notice_id INTEGER,                -- 对应 notices.id
            notice_url TEXT,                      -- 对应 notices.url
            title TEXT,                           -- 对应 notices.title
            publish_time DATE,                    -- 对应 notices.publish_time
            publisher TEXT,                       -- 对应 notices.source（发布部门）
            content TEXT,                         -- 对应 notices.content
            source TEXT,                          -- 爬虫来源，可从 spider_name 或文件名获取
            filter_pass_time DATETIME,            -- 筛选通过时间
            competition_name TEXT,                -- 识别出的竞赛名称
            competition_level TEXT,               -- 识别出的级别 (A+/A/B/C)
            -- 以下字段为可选的扩展信息，如果原始数据中有则映射，没有则留空
            deadline TEXT,                        -- 对应 notices.deadline
            organizer TEXT,                       -- 对应 notices.organizer
            participants TEXT,                    -- 对应 notices.participants
            prize TEXT,                           -- 对应 notices.prize
            requirement TEXT,                     -- 对应 notices.requirement
            contact TEXT                          -- 对应 notices.contact
        )
        ''')
        
        # 从旧表中读取数据
        cursor.execute('SELECT * FROM competition_notices')
        rows = cursor.fetchall()
        
        # 插入数据到新表
        inserted_count = 0
        for row in rows:
            try:
                # 旧表结构: id, raw_notice_id, notice_url, title, publish_time, source_department, content, summary, tags, sign_up_deadline, filter_pass_time, deadline, organizer, participants, prize, requirement, contact, competition_name, competition_level
                # 新表结构: id, raw_notice_id, notice_url, title, publish_time, publisher, content, source, filter_pass_time, competition_name, competition_level, deadline, organizer, participants, prize, requirement, contact
                
                # 提取旧表字段
                old_id = row[0]
                raw_notice_id = row[1]
                notice_url = row[2]
                title = row[3]
                publish_time = row[4]
                source_department = row[5]
                content = row[6]
                filter_pass_time = row[10]
                deadline = row[11]
                organizer = row[12]
                participants = row[13]
                prize = row[14]
                requirement = row[15]
                contact = row[16]
                competition_name = row[17]
                competition_level = row[18]
                
                # 转换字段
                publisher = source_department
                source = db_path.name.replace("contest_trace_competition_", "").replace(".db", "")
                
                # 执行插入
                cursor.execute('''
                INSERT INTO competition_notices_new 
                (raw_notice_id, notice_url, title, publish_time, publisher, 
                 content, source, filter_pass_time, competition_name, competition_level, 
                 deadline, organizer, participants, prize, requirement, contact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (raw_notice_id, notice_url, title, publish_time, publisher, 
                      content, source, filter_pass_time, competition_name, competition_level, 
                      deadline, organizer, participants, prize, requirement, contact))
                
                inserted_count += 1
            except Exception as e:
                logger.error(f"插入记录失败: {e}")
                continue
        
        # 删除旧表
        cursor.execute('DROP TABLE IF EXISTS competition_notices')
        
        # 重命名新表
        cursor.execute('ALTER TABLE competition_notices_new RENAME TO competition_notices')
        
        # 提交事务
        conn.commit()
        conn.close()
        
        logger.info(f"数据库 {db_path.name} 更新成功，共插入 {inserted_count} 条记录")
    except Exception as e:
        logger.error(f"更新数据库 {db_path.name} 失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    update_competition_db_structure()
