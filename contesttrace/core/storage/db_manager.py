#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块
管理原始公告库和竞赛结果库
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    数据库管理器
    """
    
    def __init__(self, data_dir: str = "data", spider_name: str = None):
        """
        初始化数据库管理器
        
        Args:
            data_dir: 数据目录
            spider_name: 爬虫名称，用于创建独立的数据库
        """
        # 确保数据目录存在
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 数据库文件路径
        if spider_name:
            # 为每个爬虫创建独立的数据库
            self.raw_db_path = os.path.join(self.data_dir, f"contest_trace_raw_{spider_name}.db")
            self.comp_db_path = os.path.join(self.data_dir, f"contest_trace_competition_{spider_name}.db")
        else:
            # 默认数据库
            self.raw_db_path = os.path.join(self.data_dir, "contest_trace_raw.db")
            self.comp_db_path = os.path.join(self.data_dir, "contest_trace_competition.db")
        
        # 初始化数据库
        self._init_databases()
    
    def _init_databases(self):
        """
        初始化数据库表结构
        """
        # 初始化原始公告库
        self._init_raw_database()
        # 初始化竞赛结果库
        self._init_competition_database()
    
    def _init_raw_database(self):
        """
        初始化原始公告库
        """
        try:
            conn = sqlite3.connect(self.raw_db_path)
            cursor = conn.cursor()
            
            # 创建原始公告表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_notices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notice_url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                publish_time TEXT NOT NULL,
                publisher TEXT NOT NULL,
                content TEXT,
                crawl_time TEXT NOT NULL,
                filter_status TEXT DEFAULT 'pending',
                filter_time TEXT,
                review_status TEXT DEFAULT 'unreviewed',
                review_time TEXT,
                review_result TEXT,
                review_notes TEXT,
                filter_confidence REAL,
                UNIQUE(notice_url)
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("原始公告库初始化成功")
        except Exception as e:
            logger.error(f"初始化原始公告库失败: {e}")
            raise
    
    def _init_competition_database(self):
        """
        初始化竞赛结果库
        """
        try:
            conn = sqlite3.connect(self.comp_db_path)
            cursor = conn.cursor()
            
            # 创建竞赛结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS competition_notices (
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
                contact TEXT,                         -- 对应 notices.contact
                confidence REAL DEFAULT 0.0           -- 筛选置信度
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("竞赛结果库初始化成功")
        except Exception as e:
            logger.error(f"初始化竞赛结果库失败: {e}")
            raise
    
    def insert_raw_notice(self, notice: Dict[str, Any]) -> bool:
        """
        插入原始公告
        
        Args:
            notice: 公告信息
        
        Returns:
            是否插入成功
        """
        try:
            conn = sqlite3.connect(self.raw_db_path)
            cursor = conn.cursor()
            
            # 检查发布时间是否在2025-01-01及以后
            publish_time = notice.get('publish_time')
            if not publish_time:
                logger.info("公告缺少发布时间，使用默认值")
                publish_time = '2025-01-01'  # 使用默认值
            
            # 解析发布时间
            try:
                publish_date = datetime.strptime(publish_time, '%Y-%m-%d')
                if publish_date < datetime(2025, 1, 1):
                    logger.info(f"公告发布时间 {publish_time} 在2025-01-01之前，跳过")
                    return False
            except Exception as e:
                logger.info(f"解析发布时间失败: {e}，使用默认值")
                publish_time = '2025-01-01'  # 使用默认值
            
            # 准备插入数据
            notice_url = notice.get('url', '')
            title = notice.get('title', '无标题')
            publisher = notice.get('source', '未知来源')
            content = notice.get('content', '无内容')
            crawl_time = notice.get('crawl_time', datetime.now().isoformat())
            
            # 执行插入
            cursor.execute('''
            INSERT OR IGNORE INTO raw_notices 
            (notice_url, title, publish_time, publisher, content, crawl_time, filter_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (notice_url, title, publish_time, publisher, content, crawl_time, notice.get('filter_confidence', 0.0)))
            
            inserted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if inserted:
                logger.info(f"原始公告插入成功: {title}")
            else:
                logger.info(f"原始公告已存在，跳过: {title}")
            
            return inserted
        except Exception as e:
            logger.error(f"插入原始公告失败: {e}")
            return False
    
    def get_pending_notices(self) -> List[Dict[str, Any]]:
        """
        获取待筛选的公告
        
        Returns:
            待筛选的公告列表
        """
        try:
            conn = sqlite3.connect(self.raw_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询待筛选的公告
            cursor.execute('''
            SELECT * FROM raw_notices 
            WHERE filter_status = 'pending' 
            AND publish_time >= '2025-01-01'
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典列表
            notices = []
            for row in rows:
                notice = dict(row)
                notices.append(notice)
            
            logger.info(f"获取到 {len(notices)} 条待筛选公告")
            return notices
        except Exception as e:
            logger.error(f"获取待筛选公告失败: {e}")
            return []
    
    def update_filter_status(self, notice_id: int, status: str, filter_time: Optional[str] = None):
        """
        更新筛选状态
        
        Args:
            notice_id: 公告ID
            status: 筛选状态
            filter_time: 筛选时间
        """
        try:
            conn = sqlite3.connect(self.raw_db_path)
            cursor = conn.cursor()
            
            if not filter_time:
                filter_time = datetime.now().isoformat()
            
            cursor.execute('''
            UPDATE raw_notices 
            SET filter_status = ?, filter_time = ? 
            WHERE id = ?
            ''', (status, filter_time, notice_id))
            
            conn.commit()
            conn.close()
            logger.info(f"更新公告筛选状态成功: {notice_id}, 状态: {status}")
        except Exception as e:
            logger.error(f"更新筛选状态失败: {e}")
    
    def insert_competition_notice(self, notice: Dict[str, Any]) -> bool:
        """
        插入竞赛公告
        
        Args:
            notice: 竞赛公告信息
        
        Returns:
            是否插入成功
        """
        try:
            from contesttrace.core.utils.data_processor import DataProcessor
            
            conn = sqlite3.connect(self.comp_db_path)
            cursor = conn.cursor()
            
            # 准备插入数据
            raw_notice_id = notice.get('raw_notice_id')
            notice_url = notice.get('notice_url', '')
            title = notice.get('title', '')
            publish_time = notice.get('publish_time', '')
            publisher = notice.get('publisher', '') or notice.get('source_department', '')
            content = notice.get('content', '')
            source = notice.get('source', '')
            filter_pass_time = notice.get('filter_pass_time', datetime.now().isoformat())
            
            # 处理竞赛公告，提取详细字段
            data_processor = DataProcessor()
            contest = {
                'id': raw_notice_id,
                'title': title,
                'content': content
            }
            processed_contest = data_processor.process_contest(contest)
            
            # 获取竞赛名称和级别，如果notice中已有则使用，否则使用处理后的
            competition_name = notice.get('competition_name') or processed_contest.get('competition_name')
            competition_level = notice.get('competition_level') or processed_contest.get('competition_level')
            
            # 执行插入
            cursor.execute('''
            INSERT INTO competition_notices 
            (raw_notice_id, notice_url, title, publish_time, publisher, 
             content, source, filter_pass_time, competition_name, competition_level, 
             deadline, organizer, participants, prize, requirement, contact, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (raw_notice_id, notice_url, title, publish_time, publisher, 
                 content, source, filter_pass_time, competition_name, competition_level, 
                 processed_contest.get('deadline', ''),
                 processed_contest.get('organizer', ''),
                 processed_contest.get('participants', ''),
                 processed_contest.get('prize', ''),
                 processed_contest.get('requirement', ''),
                 processed_contest.get('contact', ''),
                 notice.get('confidence', 0.0)))
            
            inserted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if inserted:
                logger.info(f"竞赛公告插入/更新成功: {title}")
            else:
                logger.info(f"竞赛公告操作失败: {title}")
            
            return inserted
        except Exception as e:
            logger.error(f"插入竞赛公告失败: {e}")
            return False
    
    def get_competition_notices(self) -> List[Dict[str, Any]]:
        """
        获取竞赛公告
        
        Returns:
            竞赛公告列表
        """
        try:
            conn = sqlite3.connect(self.comp_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询所有竞赛公告
            cursor.execute('''
            SELECT * FROM competition_notices 
            ORDER BY publish_time DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典列表
            notices = []
            for row in rows:
                notice = dict(row)
                notices.append(notice)
            
            return notices
        except Exception as e:
            logger.error(f"获取竞赛公告失败: {e}")
            return []
    
    def clear_competition_notices(self):
        """
        清空竞赛公告表
        """
        try:
            conn = sqlite3.connect(self.comp_db_path)
            cursor = conn.cursor()
            
            # 清空竞赛公告表
            cursor.execute('DELETE FROM competition_notices')
            conn.commit()
            conn.close()
            
            logger.info("竞赛公告表已清空")
        except Exception as e:
            logger.error(f"清空竞赛公告表失败: {e}")
    
    def reset_filter_status(self):
        """
        重置所有公告的筛选状态为pending，并清空竞赛公告表
        """
        try:
            # 重置原始公告的筛选状态
            conn = sqlite3.connect(self.raw_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE raw_notices 
            SET filter_status = 'pending', filter_time = NULL
            ''')
            
            updated = cursor.rowcount
            conn.commit()
            conn.close()
            
            # 清空竞赛公告表
            conn = sqlite3.connect(self.comp_db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM competition_notices')
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"重置筛选状态成功，共 {updated} 条公告，清空竞赛公告表 {deleted} 条记录")
        except Exception as e:
            logger.error(f"重置筛选状态失败: {e}")
    
    def get_crawl_stats(self) -> Dict[str, int]:
        """
        获取爬取统计信息
        
        Returns:
            统计信息
        """
        try:
            conn = sqlite3.connect(self.raw_db_path)
            cursor = conn.cursor()
            
            # 总公告数
            cursor.execute('SELECT COUNT(*) FROM raw_notices')
            total = cursor.fetchone()[0]
            
            # 时间符合的公告数
            cursor.execute('SELECT COUNT(*) FROM raw_notices WHERE publish_time >= "2025-01-01"')
            time_valid = cursor.fetchone()[0]
            
            # 重复的公告数（通过unique约束判断）
            # 这里简化处理，假设所有插入的都是时间有效的
            duplicate = total - time_valid
            
            conn.close()
            
            return {
                'total': total,
                'time_valid': time_valid,
                'duplicate': duplicate
            }
        except Exception as e:
            logger.error(f"获取爬取统计信息失败: {e}")
            return {
                'total': 0,
                'time_valid': 0,
                'duplicate': 0
            }
    
    def is_notice_exist(self, notice_url: str) -> bool:
        """
        检查公告是否已存在
        
        Args:
            notice_url: 公告URL
        
        Returns:
            是否存在
        """
        try:
            conn = sqlite3.connect(self.raw_db_path)
            cursor = conn.cursor()
            
            # 检查公告是否存在
            cursor.execute('''
            SELECT COUNT(*) FROM raw_notices 
            WHERE notice_url = ?
            ''', (notice_url,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
        except Exception as e:
            logger.error(f"检查公告是否存在失败: {e}")
            return False
    
    def update_review_status(self, notice_id: int, status: str, result: str = None, notes: str = None):
        """
        更新审核状态
        
        Args:
            notice_id: 公告ID
            status: 审核状态 (unreviewed, reviewing, reviewed)
            result: 审核结果 (approve, reject)
            notes: 审核备注
        """
        try:
            conn = sqlite3.connect(self.raw_db_path)
            cursor = conn.cursor()
            
            review_time = datetime.now().isoformat()
            
            cursor.execute('''
            UPDATE raw_notices 
            SET review_status = ?, review_time = ?, review_result = ?, review_notes = ? 
            WHERE id = ?
            ''', (status, review_time, result, notes, notice_id))
            
            conn.commit()
            conn.close()
            logger.info(f"更新公告审核状态成功: {notice_id}, 状态: {status}")
        except Exception as e:
            logger.error(f"更新审核状态失败: {e}")
    
    def get_pending_review_notices(self) -> List[Dict[str, Any]]:
        """
        获取待审核的公告
        
        Returns:
            待审核的公告列表
        """
        try:
            conn = sqlite3.connect(self.raw_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询待审核的公告
            cursor.execute('''
            SELECT * FROM raw_notices 
            WHERE review_status = 'unreviewed' 
            OR review_status = 'reviewing'
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典列表
            notices = []
            for row in rows:
                notice = dict(row)
                notices.append(notice)
            
            logger.info(f"获取到 {len(notices)} 条待审核公告")
            return notices
        except Exception as e:
            logger.error(f"获取待审核公告失败: {e}")
            return []
    
    def get_review_history(self) -> List[Dict[str, Any]]:
        """
        获取审核历史
        
        Returns:
            审核历史列表
        """
        try:
            conn = sqlite3.connect(self.raw_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询已审核的公告
            cursor.execute('''
            SELECT * FROM raw_notices 
            WHERE review_status = 'reviewed' 
            ORDER BY review_time DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典列表
            notices = []
            for row in rows:
                notice = dict(row)
                notices.append(notice)
            
            logger.info(f"获取到 {len(notices)} 条审核历史")
            return notices
        except Exception as e:
            logger.error(f"获取审核历史失败: {e}")
            return []
