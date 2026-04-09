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
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化数据库管理器
        
        Args:
            data_dir: 数据目录
        """
        # 确保数据目录存在
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 数据库文件路径
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
                source_department TEXT NOT NULL,
                content TEXT,
                raw_html TEXT,
                crawl_time TEXT NOT NULL,
                filter_status TEXT DEFAULT 'pending',
                filter_time TEXT,
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
                raw_notice_id INTEGER UNIQUE NOT NULL,
                notice_url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                publish_time TEXT NOT NULL,
                source_department TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT,
                tags TEXT,
                sign_up_deadline TEXT,
                filter_pass_time TEXT NOT NULL,
                UNIQUE(raw_notice_id),
                UNIQUE(notice_url)
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
            source_department = notice.get('source', '未知来源')
            content = notice.get('content', '无内容')
            raw_html = notice.get('raw_html', '')
            crawl_time = notice.get('crawl_time', datetime.now().isoformat())
            
            # 执行插入
            cursor.execute('''
            INSERT OR IGNORE INTO raw_notices 
            (notice_url, title, publish_time, source_department, content, raw_html, crawl_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (notice_url, title, publish_time, source_department, content, raw_html, crawl_time))
            
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
            source_department = notice.get('source_department', '')
            content = notice.get('content', '')
            summary = notice.get('summary', '')
            tags = notice.get('tags', '')
            sign_up_deadline = notice.get('sign_up_deadline', '')
            filter_pass_time = notice.get('filter_pass_time', datetime.now().isoformat())
            
            # 处理竞赛公告，提取详细字段
            data_processor = DataProcessor()
            contest = {
                'id': raw_notice_id,
                'title': title,
                'content': content
            }
            processed_contest = data_processor.process_contest(contest)
            
            # 执行插入
            cursor.execute('''
            INSERT OR IGNORE INTO competition_notices 
            (raw_notice_id, notice_url, title, publish_time, source_department, 
             content, summary, tags, sign_up_deadline, filter_pass_time, 
             deadline, organizer, participants, prize, requirement, contact, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (raw_notice_id, notice_url, title, publish_time, source_department, 
                 content, summary, tags, sign_up_deadline, filter_pass_time, 
                 processed_contest.get('deadline', ''),
                 processed_contest.get('organizer', ''),
                 processed_contest.get('participants', ''),
                 processed_contest.get('prize', ''),
                 processed_contest.get('requirement', ''),
                 processed_contest.get('contact', ''),
                 processed_contest.get('category', '其他竞赛')))
            
            inserted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if inserted:
                logger.info(f"竞赛公告插入成功: {title}")
            else:
                logger.info(f"竞赛公告已存在，跳过: {title}")
            
            return inserted
        except Exception as e:
            logger.error(f"插入竞赛公告失败: {e}")
            return False
    
    def get_competition_notices(self) -> List[Dict[str, Any]]:
        """
        获取所有竞赛公告
        
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
            
            logger.info(f"获取到 {len(notices)} 条竞赛公告")
            return notices
        except Exception as e:
            logger.error(f"获取竞赛公告失败: {e}")
            return []
    
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
