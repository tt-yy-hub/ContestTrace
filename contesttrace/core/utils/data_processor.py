#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能数据处理模块
实现数据清洗、标准化等功能
"""

from datetime import datetime
import logging
from .common import normalize_date
from .contest_guide_parser import get_competition_level, get_competition_name
from ..parsers.smart_parser import SmartParser

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    数据处理器
    """
    
    def __init__(self):
        """
        初始化数据处理器
        """
        self.smart_parser = SmartParser()
    
    def process_contest(self, contest: dict) -> dict:
        """
        处理单个竞赛数据
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            处理后的竞赛信息字典
        """
        try:
            # 使用智能解析器提取详细字段
            contest = self.smart_parser.parse_all(contest)
            
            # 处理时间字段
            contest['publish_time'] = normalize_date(contest.get('publish_time', ''))
            # 不处理 deadline 字段，保持原样（包含前缀）
            
            # 处理缺失值
            contest = self._fill_missing_values(contest)
            
            # 字段标准化
            contest = self._normalize_fields(contest)
            
            # 提取竞赛名称
            contest['competition_name'] = get_competition_name(contest.get('title', ''))
            
            # 提取竞赛级别
            contest['competition_level'] = get_competition_level(contest.get('title', ''))
            
            # 确保空值处理正确
            if contest['competition_name'] is None:
                contest['competition_name'] = ''
            if contest['competition_level'] is None:
                contest['competition_level'] = ''
            
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
        # 支持 notice_url 和 url 两种字段名
        contest['url'] = contest.get('notice_url', contest.get('url', '')).strip()
        # 确保 notice_url 字段也存在
        if 'notice_url' not in contest:
            contest['notice_url'] = contest['url']
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
            deadline: 截止日期字符串，可能带前缀（如 "截止日期：2025-03-13"）
        
        Returns:
            剩余天数，负数表示已过期
        """
        if not deadline:
            return -1
        
        try:
            # 从带前缀的字符串中提取日期部分
            import re
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', deadline)
            if date_match:
                date_str = date_match.group(0)
                deadline_date = datetime.strptime(date_str, '%Y-%m-%d')
                today = datetime.now().date()
                days_left = (deadline_date.date() - today).days
                return days_left
            else:
                logger.error(f"无法从 {deadline} 中提取日期")
                return -1
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
