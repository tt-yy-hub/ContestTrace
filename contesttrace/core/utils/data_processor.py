#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能数据处理模块
实现数据清洗、标准化等功能
"""

from datetime import datetime
import logging
from .common import normalize_date

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    数据处理器
    """
    
    def __init__(self):
        """
        初始化数据处理器
        """
        pass
    
    def process_contest(self, contest: dict) -> dict:
        """
        处理单个竞赛数据
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            处理后的竞赛信息字典
        """
        try:
            # 处理时间字段
            contest['publish_time'] = normalize_date(contest.get('publish_time', ''))
            contest['deadline'] = normalize_date(contest.get('deadline', ''))
            
            # 处理缺失值
            contest = self._fill_missing_values(contest)
            
            # 字段标准化
            contest = self._normalize_fields(contest)
            
            # 计算截止时间剩余天数
            contest['days_left'] = self._calculate_days_left(contest.get('deadline', ''))
            
        except Exception as e:
            logger.error(f"处理竞赛数据失败: {e}")
        
        return contest
    
    def _fill_missing_values(self, contest: dict) -> dict:
        """
        填充缺失值
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            填充后的竞赛信息字典
        """
        # 填充基本字段
        contest['title'] = contest.get('title', '').strip()
        contest['url'] = contest.get('url', '').strip()
        contest['source'] = contest.get('source', '').strip()
        contest['content'] = contest.get('content', '').strip()
        contest['summary'] = contest.get('summary', '').strip()
        
        # 填充列表字段
        contest['keywords'] = contest.get('keywords', [])
        contest['tags'] = contest.get('tags', [])
        
        # 填充其他字段
        contest['category'] = contest.get('category', '').strip()
        contest['organizer'] = contest.get('organizer', '').strip()
        contest['participants'] = contest.get('participants', '').strip()
        contest['prize'] = contest.get('prize', '').strip()
        contest['requirement'] = contest.get('requirement', '').strip()
        contest['contact'] = contest.get('contact', '').strip()
        
        return contest
    
    def _normalize_fields(self, contest: dict) -> dict:
        """
        字段标准化
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            标准化后的竞赛信息字典
        """
        # 标准化标题
        contest['title'] = contest['title'].replace('\n', ' ').replace('\r', ' ').strip()
        
        # 标准化内容
        contest['content'] = contest['content'].replace('\n', ' ').replace('\r', ' ').strip()
        
        # 标准化摘要
        if not contest['summary'] and contest['content']:
            contest['summary'] = contest['content'][:100] + '...' if len(contest['content']) > 100 else contest['content']
        
        # 标准化分类
        if not contest['category']:
            contest['category'] = self._infer_category(contest)
        
        return contest
    
    def _infer_category(self, contest: dict) -> str:
        """
        推断竞赛分类
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            推断的分类
        """
        text = (contest.get('title', '') + ' ' + contest.get('content', '')).lower()
        
        # 分类关键词
        categories = {
            '学科竞赛': ['学科', '专业', '学术', '科研', '论文'],
            '技能竞赛': ['技能', '技术', '操作', '实践'],
            '创业竞赛': ['创业', '创新', '商业', '计划书'],
            '文体竞赛': ['文艺', '体育', '艺术', '音乐', '舞蹈', '绘画'],
            '其他竞赛': []
        }
        
        # 匹配分类
        for category, keywords in categories.items():
            if category == '其他竞赛':
                continue
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return '其他竞赛'
    
    def _calculate_days_left(self, deadline: str) -> int:
        """
        计算截止时间剩余天数
        
        Args:
            deadline: 截止日期字符串 (YYYY-MM-DD)
        
        Returns:
            剩余天数，负数表示已过期
        """
        if not deadline:
            return -1
        
        try:
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
            today = datetime.now().date()
            days_left = (deadline_date.date() - today).days
            return days_left
        except Exception as e:
            logger.error(f"计算剩余天数失败: {e}")
            return -1
    
    def process_contests(self, contests: list) -> list:
        """
        批量处理竞赛数据
        
        Args:
            contests: 竞赛信息列表
        
        Returns:
            处理后的竞赛信息列表
        """
        processed_contests = []
        for contest in contests:
            processed_contest = self.process_contest(contest)
            processed_contests.append(processed_contest)
        
        logger.info(f"数据处理完成，共处理 {len(processed_contests)} 条竞赛数据")
        return processed_contests
