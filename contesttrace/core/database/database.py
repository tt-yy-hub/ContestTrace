#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模块
使用SQLite轻量数据库存储竞赛信息
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ContestDatabase:
    """
    竞赛数据库
    """
    
    def __init__(self, db_path: str = "data/contest.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        # 确保数据库目录存在
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._init_db()
    
    def _init_db(self):
        """
        初始化数据库表结构
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # 创建竞赛表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS contests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    url TEXT UNIQUE,
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
                    summary TEXT,
                    keywords TEXT,
                    tags TEXT,
                    spider_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON contests (url)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_publish_time ON contests (publish_time)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_deadline ON contests (deadline)')
            
            self.conn.commit()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
    
    def insert_contest(self, contest: dict) -> bool:
        """
        插入竞赛信息
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            是否插入成功
        """
        try:
            # 检查是否已存在
            url = contest.get('url', '')
            if not url:
                logger.error(f"竞赛URL为空，跳过插入: {contest.get('title', '未知')}")
                return False
                
            if self._exists(url):
                logger.debug(f"竞赛已存在: {contest.get('title', '')} - {url}")
                return False
            
            # 填充爬取时间
            contest['crawl_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 序列化列表字段
            try:
                contest['keywords'] = json.dumps(contest.get('keywords', []), ensure_ascii=False)
                contest['tags'] = json.dumps(contest.get('tags', []), ensure_ascii=False)
            except Exception as e:
                logger.error(f"序列化字段失败: {e}")
                contest['keywords'] = '[]'
                contest['tags'] = '[]'
            
            # 插入数据
            try:
                # 检查必要字段
                title = contest.get('title', '')
                source = contest.get('source', '')
                
                if not title:
                    logger.error(f"竞赛标题为空，跳过插入: {url}")
                    return False
                
                if not source:
                    logger.error(f"竞赛来源为空，跳过插入: {title}")
                    return False
                
                self.cursor.execute('''
                    INSERT INTO contests (
                        title, url, source, publish_time, crawl_time, deadline, 
                        category, organizer, participants, prize, requirement, contact, 
                        content, summary, keywords, tags, spider_name
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                ''', (
                    title,
                    url,
                    source,
                    contest.get('publish_time', ''),
                    contest.get('crawl_time', ''),
                    contest.get('deadline', ''),
                    contest.get('category', ''),
                    contest.get('organizer', ''),
                    contest.get('participants', ''),
                    contest.get('prize', ''),
                    contest.get('requirement', ''),
                    contest.get('contact', ''),
                    contest.get('content', ''),
                    contest.get('summary', ''),
                    contest.get('keywords', '[]'),
                    contest.get('tags', '[]'),
                    contest.get('spider_name', '')
                ))
                
                self.conn.commit()
                logger.info(f"插入竞赛成功: {title} - {url}")
                return True
            except Exception as e:
                logger.error(f"执行SQL失败: {e}")
                logger.error(f"竞赛数据: {contest.get('title', '未知')} - {contest.get('url', '未知')}")
                import traceback
                logger.error(traceback.format_exc())
                return False
        except Exception as e:
            logger.error(f"插入竞赛失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def batch_insert_contests(self, contests: list) -> int:
        """
        批量插入竞赛信息
        
        Args:
            contests: 竞赛信息列表
        
        Returns:
            成功插入的数量
        """
        if not contests:
            logger.info("批量插入：没有竞赛数据需要插入")
            return 0
        
        count = 0
        total = len(contests)
        logger.info(f"开始批量插入，共 {total} 条竞赛数据")
        
        for i, contest in enumerate(contests):
            if i % 10 == 0:
                logger.info(f"正在处理第 {i+1}/{total} 条竞赛数据")
            
            if self.insert_contest(contest):
                count += 1
        
        logger.info(f"批量插入完成，成功 {count} 条，失败 {total - count} 条")
        return count
    
    def _exists(self, url: str) -> bool:
        """
        检查竞赛是否已存在
        
        Args:
            url: 竞赛详情页URL
        
        Returns:
            是否存在
        """
        try:
            self.cursor.execute('SELECT id FROM contests WHERE url = ?', (url,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"检查竞赛存在性失败: {e}")
            return False
    
    def get_contest(self, url: str) -> dict:
        """
        获取单个竞赛信息
        
        Args:
            url: 竞赛详情页URL
        
        Returns:
            竞赛信息字典
        """
        try:
            self.cursor.execute('SELECT * FROM contests WHERE url = ?', (url,))
            row = self.cursor.fetchone()
            if row:
                return self._row_to_dict(row)
        except Exception as e:
            logger.error(f"获取竞赛失败: {e}")
        return {}
    
    def get_all_contests(self) -> list:
        """
        获取所有竞赛信息
        
        Returns:
            竞赛信息列表
        """
        try:
            self.cursor.execute('SELECT * FROM contests ORDER BY publish_time DESC')
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取所有竞赛失败: {e}")
            return []
    
    def get_contests_by_filter(self, **kwargs) -> list:
        """
        根据条件筛选竞赛
        
        Args:
            **kwargs: 筛选条件
        
        Returns:
            竞赛信息列表
        """
        try:
            where_clauses = []
            params = []
            
            for key, value in kwargs.items():
                if value:
                    where_clauses.append(f"{key} LIKE ?")
                    params.append(f"%{value}%")
            
            query = 'SELECT * FROM contests'
            if where_clauses:
                query += ' WHERE ' + ' AND '.join(where_clauses)
            query += ' ORDER BY publish_time DESC'
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"筛选竞赛失败: {e}")
            return []
    
    def update_contest(self, contest: dict) -> bool:
        """
        更新竞赛信息
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            是否更新成功
        """
        try:
            url = contest.get('url', '')
            if not url:
                return False
            
            # 序列化列表字段
            contest['keywords'] = json.dumps(contest.get('keywords', []), ensure_ascii=False)
            contest['tags'] = json.dumps(contest.get('tags', []), ensure_ascii=False)
            
            self.cursor.execute('''
                UPDATE contests SET 
                    title = ?, source = ?, publish_time = ?, crawl_time = ?, 
                    deadline = ?, category = ?, organizer = ?, participants = ?, 
                    prize = ?, requirement = ?, contact = ?, content = ?, 
                    summary = ?, keywords = ?, tags = ?, spider_name = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE url = ?
            ''', (
                contest.get('title', ''),
                contest.get('source', ''),
                contest.get('publish_time', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                contest.get('deadline', ''),
                contest.get('category', ''),
                contest.get('organizer', ''),
                contest.get('participants', ''),
                contest.get('prize', ''),
                contest.get('requirement', ''),
                contest.get('contact', ''),
                contest.get('content', ''),
                contest.get('summary', ''),
                contest.get('keywords', '[]'),
                contest.get('tags', '[]'),
                contest.get('spider_name', ''),
                url
            ))
            
            self.conn.commit()
            logger.debug(f"更新竞赛成功: {contest.get('title', '')}")
            return True
        except Exception as e:
            logger.error(f"更新竞赛失败: {e}")
            return False
    
    def delete_contest(self, url: str) -> bool:
        """
        删除竞赛信息
        
        Args:
            url: 竞赛详情页URL
        
        Returns:
            是否删除成功
        """
        try:
            self.cursor.execute('DELETE FROM contests WHERE url = ?', (url,))
            self.conn.commit()
            logger.debug(f"删除竞赛成功: {url}")
            return True
        except Exception as e:
            logger.error(f"删除竞赛失败: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        try:
            # 总竞赛数
            self.cursor.execute('SELECT COUNT(*) FROM contests')
            total = self.cursor.fetchone()[0]
            
            # 按来源统计
            self.cursor.execute('SELECT source, COUNT(*) FROM contests GROUP BY source')
            by_source = dict(self.cursor.fetchall())
            
            # 按月份统计
            self.cursor.execute('''
                SELECT SUBSTR(publish_time, 1, 7) AS month, COUNT(*) 
                FROM contests 
                WHERE publish_time != '' 
                GROUP BY month 
                ORDER BY month DESC
            ''')
            by_month = dict(self.cursor.fetchall())
            
            return {
                'total': total,
                'by_source': by_source,
                'by_month': by_month
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def _row_to_dict(self, row) -> dict:
        """
        将数据库行转换为字典
        
        Args:
            row: 数据库行
        
        Returns:
            竞赛信息字典
        """
        columns = [
            'id', 'title', 'url', 'source', 'publish_time', 'crawl_time',
            'deadline', 'category', 'organizer', 'participants', 'prize',
            'requirement', 'contact', 'content', 'summary', 'keywords',
            'tags', 'spider_name', 'created_at', 'updated_at'
        ]
        
        contest = dict(zip(columns, row))
        
        # 反序列化列表字段
        try:
            contest['keywords'] = json.loads(contest.get('keywords', '[]'))
            contest['tags'] = json.loads(contest.get('tags', '[]'))
        except Exception as e:
            logger.error(f"反序列化字段失败: {e}")
            contest['keywords'] = []
            contest['tags'] = []
        
        return contest
    
    def close(self):
        """
        关闭数据库连接
        """
        try:
            if self.conn:
                self.conn.close()
                logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")
    
    def __enter__(self):
        """
        上下文管理器入口
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口
        """
        self.close()
