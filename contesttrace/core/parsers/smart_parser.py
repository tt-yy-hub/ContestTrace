#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能解析模块
从爬取的内容中提取更多结构化字段
"""

import re
from ..utils import normalize_date
import logging

logger = logging.getLogger(__name__)


class SmartParser:
    """
    智能解析器
    """
    
    def __init__(self):
        """
        初始化解析器
        """
        # 截止日期正则表达式
        self.deadline_patterns = [
            r'截止日期[:：]?\s*([^，。；;\n]+)',
            r'报名截止[:：]?\s*([^，。；;\n]+)',
            r'截止时间[:：]?\s*([^，。；;\n]+)',
            r'截至[:：]?\s*([^，。；;\n]+)',
            r'报名截至[:：]?\s*([^，。；;\n]+)',
            r'报名时间[:：]?\s*即日起至\s*([^，。；;\n]+)',
            r'报名时间[:：]?\s*[0-9]+月[0-9]+日至\s*([^，。；;\n]+)',
            r'报名截止时间[:：]?\s*([^，。；;\n]+)',
            r'截止日期[:：]?\s*([0-9]+年[0-9]+月[0-9]+日)',
            r'报名截止[:：]?\s*([0-9]+年[0-9]+月[0-9]+日)',
            r'截止时间[:：]?\s*([0-9]+年[0-9]+月[0-9]+日)',
            r'截至[:：]?\s*([0-9]+年[0-9]+月[0-9]+日)',
            r'报名截至[:：]?\s*([0-9]+年[0-9]+月[0-9]+日)',
            r'报名时间[:：]?\s*([0-9]+年[0-9]+月[0-9]+日)\s*至\s*([0-9]+年[0-9]+月[0-9]+日)',
            r'报名时间[:：]?\s*([0-9]+年[0-9]+月[0-9]+日)\s*—\s*([0-9]+年[0-9]+月[0-9]+日)',
            r'报名时间[:：]?\s*([0-9]+年[0-9]+月[0-9]+日)\s*到\s*([0-9]+年[0-9]+月[0-9]+日)',
            r'截止[:：]?\s*([0-9]+年[0-9]+月[0-9]+日)',
            r'报名截止[:：]?\s*([0-9]+月[0-9]+日)',
            r'截止时间[:：]?\s*([0-9]+月[0-9]+日)',
            r'截至[:：]?\s*([0-9]+月[0-9]+日)',
            r'报名截至[:：]?\s*([0-9]+月[0-9]+日)',
            r'即日起至\s*([0-9]+年[0-9]+月[0-9]+日)',
            r'即日起至\s*([0-9]+月[0-9]+日)',
        ]
        
        # 组织者正则表达式
        self.organizer_patterns = [
            r'主办[:：]?\s*([^，。；;\n]+)',
            r'主办方[:：]?\s*([^，。；;\n]+)',
            r'组织[:：]?\s*([^，。；;\n]+)',
            r'承办[:：]?\s*([^，。；;\n]+)',
            r'承办方[:：]?\s*([^，。；;\n]+)'
        ]
        
        # 参与者正则表达式
        self.participants_patterns = [
            r'参赛对象[:：]?\s*([^，。；;\n]+)',
            r'参与对象[:：]?\s*([^，。；;\n]+)',
            r'面向[:：]?\s*([^，。；;\n]+)',
            r'对象[:：]?\s*([^，。；;\n]+)'
        ]
        
        # 奖项正则表达式
        self.prize_patterns = [
            r'奖项设置[:：]?\s*([^，。；;\n]+)',
            r'奖励[:：]?\s*([^，。；;\n]+)',
            r'奖品[:：]?\s*([^，。；;\n]+)',
            r'奖金[:：]?\s*([^，。；;\n]+)'
        ]
        
        # 联系方式正则表达式
        self.contact_patterns = [
            r'联系电话[:：]?\s*([^，。；;\n]+)',
            r'联系方式[:：]?\s*([^，。；;\n]+)',
            r'联系人[:：]?\s*([^，。；;\n]+)',
            r'电话[:：]?\s*([^，。；;\n]+)',
            r'邮箱[:：]?\s*([^，。；;\n]+)'
        ]
    
    def parse_deadline(self, text: str) -> str:
        """
        解析截止日期
        
        Args:
            text: 文本内容
        
        Returns:
            归一化的截止日期
        """
        # 尝试匹配常见的截止日期格式
        for pattern in self.deadline_patterns:
            match = re.search(pattern, text)
            if match:
                # 处理有两个日期的情况（开始日期和截止日期）
                if len(match.groups()) == 2:
                    return normalize_date(match.group(2))  # 返回截止日期
                else:
                    return normalize_date(match.group(1))
        
        # 尝试匹配 "即日起至4月11日17:00" 这样的格式
        pattern = r'即日起至\s*([^，。；;\n]+)'
        match = re.search(pattern, text)
        if match:
            return normalize_date(match.group(1))
        
        # 尝试匹配 "报名时间：2024年3月27日—2024年4月17日" 这样的格式
        pattern = r'报名时间[:：]?\s*[^—]+—\s*([^，。；;\n]+)'
        match = re.search(pattern, text)
        if match:
            return normalize_date(match.group(1))
        
        # 尝试匹配 "报名截止时间：2024年5月31日" 这样的格式
        pattern = r'报名截止时间[:：]?\s*([^，。；;\n]+)'
        match = re.search(pattern, text)
        if match:
            return normalize_date(match.group(1))
        
        # 尝试匹配 "截止到" 格式
        pattern = r'截止到\s*([^，。；;\n]+)'
        match = re.search(pattern, text)
        if match:
            return normalize_date(match.group(1))
        
        # 尝试匹配 "报名截止于" 格式
        pattern = r'报名截止于\s*([^，。；;\n]+)'
        match = re.search(pattern, text)
        if match:
            return normalize_date(match.group(1))
        
        return ""
    
    def parse_organizer(self, text: str) -> str:
        """
        解析组织者
        
        Args:
            text: 文本内容
        
        Returns:
            组织者信息
        """
        for pattern in self.organizer_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return ""
    
    def parse_participants(self, text: str) -> str:
        """
        解析参与者要求
        
        Args:
            text: 文本内容
        
        Returns:
            参与者信息
        """
        for pattern in self.participants_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return ""
    
    def parse_prize(self, text: str) -> str:
        """
        解析奖项信息
        
        Args:
            text: 文本内容
        
        Returns:
            奖项信息
        """
        for pattern in self.prize_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return ""
    
    def parse_contact(self, text: str) -> str:
        """
        解析联系方式
        
        Args:
            text: 文本内容
        
        Returns:
            联系方式
        """
        for pattern in self.contact_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return ""
    
    def parse_requirement(self, text: str) -> str:
        """
        解析参赛要求
        
        Args:
            text: 文本内容
        
        Returns:
            参赛要求
        """
        # 简单提取参赛要求相关内容
        patterns = [
            r'参赛要求[:：]?\s*([^，。；;\n]+)',
            r'报名要求[:：]?\s*([^，。；;\n]+)',
            r'要求[:：]?\s*([^，。；;\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return ""
    
    def generate_summary(self, title: str, content: str, max_length: int = 100) -> str:
        """
        生成摘要
        
        Args:
            title: 标题
            content: 内容
            max_length: 摘要最大长度
        
        Returns:
            摘要
        """
        # 简单摘要生成逻辑
        if not content:
            return ""
        
        # 移除多余空白字符
        content = re.sub(r'\s+', ' ', content)
        
        # 截取前max_length个字符
        summary = content[:max_length]
        if len(content) > max_length:
            summary += "..."
        
        return summary
    
    def parse_all(self, contest: dict) -> dict:
        """
        解析所有字段
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            解析后的竞赛信息字典
        """
        try:
            text = contest.get('title', '') + " " + contest.get('content', '')
            
            # 解析截止日期
            contest['deadline'] = self.parse_deadline(text)
            
            # 解析组织者
            contest['organizer'] = self.parse_organizer(text)
            
            # 解析参与者
            contest['participants'] = self.parse_participants(text)
            
            # 解析奖项
            contest['prize'] = self.parse_prize(text)
            
            # 解析联系方式
            contest['contact'] = self.parse_contact(text)
            
            # 解析参赛要求
            contest['requirement'] = self.parse_requirement(text)
            
            # 生成摘要
            contest['summary'] = self.generate_summary(
                contest.get('title', ''),
                contest.get('content', '')
            )
            
            # 生成标签
            contest['tags'] = self.generate_tags(contest)
            
        except Exception as e:
            logger.error(f"解析竞赛信息失败: {e}")
        
        return contest
    
    def generate_tags(self, contest: dict) -> list:
        """
        生成标签
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            标签列表
        """
        tags = []
        
        # 从关键词中提取标签
        keywords = contest.get('keywords', [])
        for keyword in keywords[:5]:  # 取前5个关键词作为标签
            if keyword not in tags:
                tags.append(keyword)
        
        # 根据内容添加标签
        content = contest.get('content', '')
        if '省级' in content:
            tags.append('省级')
        if '国家级' in content:
            tags.append('国家级')
        if '国际' in content:
            tags.append('国际级')
        if '团队' in content:
            tags.append('团队赛')
        if '个人' in content:
            tags.append('个人赛')
        
        return tags[:10]  # 最多10个标签
