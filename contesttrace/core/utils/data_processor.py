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
            # 提取详细字段
            contest = self._extract_fields(contest)
            
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
    
    def _extract_fields(self, contest: dict) -> dict:
        """
        从公告内容中提取详细字段
        
        Args:
            contest: 竞赛信息字典
        
        Returns:
            提取字段后的竞赛信息字典
        """
        content = contest.get('content', '')
        title = contest.get('title', '')
        full_text = title + ' ' + content
        
        # 提取截止日期
        contest['deadline'] = self._extract_deadline(full_text)
        
        # 提取组织者
        contest['organizer'] = self._extract_organizer(full_text)
        
        # 提取参赛对象
        contest['participants'] = self._extract_participants(full_text)
        
        # 提取奖项设置
        contest['prize'] = self._extract_prize(full_text)
        
        # 提取联系方式
        contest['contact'] = self._extract_contact(full_text)
        
        # 提取要求
        contest['requirement'] = self._extract_requirement(full_text)
        
        return contest
    
    def _extract_deadline(self, text: str) -> str:
        """
        提取截止日期
        
        Args:
            text: 文本内容
        
        Returns:
            截止日期字符串
        """
        import re
        
        # 匹配各种日期格式
        date_patterns = [
            # 标准格式：截止日期：2026-03-19
            r'截止日期[:：]?\s*((?:\d{4}年\d{1,2}月\d{1,2}日)|(?:\d{4}-\d{1,2}-\d{1,2}))',
            # 报名截止：2026-03-19
            r'报名截止[:：]?\s*((?:\d{4}年\d{1,2}月\d{1,2}日)|(?:\d{4}-\d{1,2}-\d{1,2}))',
            # 截止时间：2026-03-19
            r'截止时间[:：]?\s*((?:\d{4}年\d{1,2}月\d{1,2}日)|(?:\d{4}-\d{1,2}-\d{1,2}))',
            # 截止：2026-03-19
            r'截止[:：]?\s*((?:\d{4}年\d{1,2}月\d{1,2}日)|(?:\d{4}-\d{1,2}-\d{1,2}))',
            # 2026-03-19 截止
            r'((?:\d{4}年\d{1,2}月\d{1,2}日)|(?:\d{4}-\d{1,2}-\d{1,2}))\s*截止',
            # 报名时间：即日起至2026-03-19
            r'报名时间[:：]?\s*即日起至((?:\d{4}年\d{1,2}月\d{1,2}日)|(?:\d{4}-\d{1,2}-\d{1,2}))',
            # 报名截止时间：2026-03-19
            r'报名截止时间[:：]?\s*((?:\d{4}年\d{1,2}月\d{1,2}日)|(?:\d{4}-\d{1,2}-\d{1,2}))',
            # 作品提交截止：2026-03-19
            r'作品提交截止[:：]?\s*((?:\d{4}年\d{1,2}月\d{1,2}日)|(?:\d{4}-\d{1,2}-\d{1,2}))',
            # 截止到2026-03-19
            r'截止到((?:\d{4}年\d{1,2}月\d{1,2}日)|(?:\d{4}-\d{1,2}-\d{1,2}))',
            # 报名截止日期：2026-03-19
            r'报名截止日期[:：]?\s*((?:\d{4}年\d{1,2}月\d{1,2}日)|(?:\d{4}-\d{1,2}-\d{1,2}))',
            # 报名截止：4月27日14:00点
            r'报名截止[:：]?\s*(\d{1,2}月\d{1,2}日)\s*\d{1,2}:\d{1,2}',
            # 截止时间：4月27日14:00
            r'截止时间[:：]?\s*(\d{1,2}月\d{1,2}日)\s*\d{1,2}:\d{1,2}',
            # 报名截止时间：4月27日14:00
            r'报名截止时间[:：]?\s*(\d{1,2}月\d{1,2}日)\s*\d{1,2}:\d{1,2}',
            # 作品提交截止时间：4月27日14:00
            r'作品提交截止时间[:：]?\s*(\d{1,2}月\d{1,2}日)\s*\d{1,2}:\d{1,2}',
            # 报名截止：4月27日
            r'报名截止[:：]?\s*(\d{1,2}月\d{1,2}日)',
            # 截止时间：4月27日
            r'截止时间[:：]?\s*(\d{1,2}月\d{1,2}日)',
            # 报名截止日期：4月27日
            r'报名截止日期[:：]?\s*(\d{1,2}月\d{1,2}日)'
        ]
        
        current_year = str(datetime.now().year)
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                # 转换为标准格式
                if '年' in date_str:
                    date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
                elif '月' in date_str:
                    # 添加当前年份
                    date_str = current_year + '-' + date_str.replace('月', '-').replace('日', '')
                # 清理日期格式
                date_str = re.sub(r'\s+', '', date_str)
                return date_str
        
        # 尝试提取数字格式的日期
        digit_patterns = [
            r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日]?\s*截止',
            r'截止\s*(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日]?',
            r'报名截止[:：]?\s*(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日]?',
            r'截止时间[:：]?\s*(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日]?'
        ]
        
        for pattern in digit_patterns:
            match = re.search(pattern, text)
            if match:
                year, month, day = match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # 尝试提取月日格式的日期
        month_day_patterns = [
            r'报名截止[:：]?\s*(\d{1,2})月(\d{1,2})日',
            r'截止时间[:：]?\s*(\d{1,2})月(\d{1,2})日',
            r'截止[:：]?\s*(\d{1,2})月(\d{1,2})日',
            r'截止到[:：]?\s*(\d{1,2})月(\d{1,2})日'
        ]
        
        for pattern in month_day_patterns:
            match = re.search(pattern, text)
            if match:
                month, day = match.groups()
                return f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return ''
    
    def _extract_organizer(self, text: str) -> str:
        """
        提取组织者
        
        Args:
            text: 文本内容
        
        Returns:
            组织者字符串
        """
        import re
        
        # 匹配组织者
        organizer_patterns = [
            # 主办单位：湖北经济学院教务处
            r'主办单位[:：]?\s*([^，。；;]+)',
            # 承办单位：统计与数学学院
            r'承办单位[:：]?\s*([^，。；;]+)',
            # 协办单位：问卷网
            r'协办单位[:：]?\s*([^，。；;]+)',
            # 主办：湖北经济学院教务处
            r'主办[:：]?\s*([^，。；;]+)',
            # 承办：统计与数学学院
            r'承办[:：]?\s*([^，。；;]+)',
            # 组织：湖北经济学院
            r'组织[:：]?\s*([^，。；;]+)',
            # 主办方：湖北经济学院
            r'主办方[:：]?\s*([^，。；;]+)',
            # 承办方：统计与数学学院
            r'承办方[:：]?\s*([^，。；;]+)',
            # 组委会：蓝桥杯全国大学生软件和信息技术大赛组委会
            r'组委会[:：]?\s*([^，。；;]+)',
            # 由...主办：由湖北经济学院主办
            r'由\s*([^，。；;]+)\s*主办'
        ]
        
        organizers = []
        for pattern in organizer_patterns:
            match = re.search(pattern, text)
            if match:
                organizer = match.group(1).strip()
                # 过滤掉无效内容
                if len(organizer) > 2 and '\n' not in organizer and '\r' not in organizer and '参赛对象' not in organizer:
                    organizers.append(organizer)
        
        if organizers:
            return '; '.join(organizers[:3])  # 最多返回3个组织者
        
        # 尝试从文本中提取包含"组委会"的内容
        committee_match = re.search(r'([^，。；;]*组委会[^，。；;]*)', text)
        if committee_match:
            committee = committee_match.group(1).strip()
            if len(committee) > 5:
                return committee
        
        return ''
    
    def _extract_participants(self, text: str) -> str:
        """
        提取参赛对象
        
        Args:
            text: 文本内容
        
        Returns:
            参赛对象字符串
        """
        import re
        
        # 匹配参赛对象
        participants_patterns = [
            # 参赛对象：全日制在校本科生
            r'参赛对象[:：]?\s*([^，。；;]+)',
            # 参赛人员：全体学生
            r'参赛人员[:：]?\s*([^，。；;]+)',
            # 报名对象：在校学生
            r'报名对象[:：]?\s*([^，。；;]+)',
            # 面向：全体学生
            r'面向[:：]?\s*([^，。；;]+)',
            # 对象：全日制在校本科生
            r'对象[:：]?\s*([^，。；;]+)',
            # 参赛要求：全日制在校本科生
            r'参赛要求[:：]?\s*([^，。；;]+)',
            # 报名条件：全日制在校本科生
            r'报名条件[:：]?\s*([^，。；;]+)',
            # 参赛资格：全日制在校本科生
            r'参赛资格[:：]?\s*([^，。；;]+)'
        ]
        
        for pattern in participants_patterns:
            match = re.search(pattern, text)
            if match:
                result = match.group(1).strip()
                # 过滤掉无效内容
                if '联系' not in result and '截止' not in result and '电话' not in result and '邮箱' not in result:
                    # 清理结果
                    result = re.sub(r'[\r\n\s]+', ' ', result)
                    if len(result) > 2:
                        return result
        
        # 常见默认值
        if '学生' in text:
            return '全体学生'
        elif '教师' in text:
            return '全体教师'
        
        return ''
    
    def _extract_prize(self, text: str) -> str:
        """
        提取奖项设置
        
        Args:
            text: 文本内容
        
        Returns:
            奖项设置字符串
        """
        import re
        
        # 匹配奖项设置
        prize_patterns = [
            # 奖项设置：一等奖3名，奖金1000元
            r'奖项设置[:：]?\s*([^，。；;]+)',
            # 奖励设置：一等奖3名，奖金1000元
            r'奖励设置[:：]?\s*([^，。；;]+)',
            # 奖项：一等奖3名，奖金1000元
            r'奖项[:：]?\s*([^，。；;]+)',
            # 奖励：一等奖3名，奖金1000元
            r'奖励[:：]?\s*([^，。；;]+)'
        ]
        
        # 匹配具体奖项
        specific_prize_patterns = [
            r'(一等奖[:：]?\s*[^，。；;]+)',
            r'(二等奖[:：]?\s*[^，。；;]+)',
            r'(三等奖[:：]?\s*[^，。；;]+)',
            r'(优秀奖[:：]?\s*[^，。；;]+)',
            r'(特等奖[:：]?\s*[^，。；;]+)'
        ]
        
        prizes = []
        
        # 先尝试匹配整体奖项设置
        for pattern in prize_patterns:
            match = re.search(pattern, text)
            if match:
                prize = match.group(1).strip()
                prize = re.sub(r'[\r\n\s]+', ' ', prize)
                if prize and len(prize) > 5 and len(prize) < 100:
                    prizes.append(prize)
                    return prize  # 整体匹配到就直接返回
        
        # 再尝试匹配具体奖项
        for pattern in specific_prize_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                prize = match.strip()
                prize = re.sub(r'[\r\n\s]+', ' ', prize)
                if prize and len(prize) > 3:
                    prizes.append(prize)
        
        if prizes:
            return '; '.join(prizes[:5])  # 最多返回5个奖项
        
        return ''
    
    def _extract_contact(self, text: str) -> str:
        """
        提取联系方式
        
        Args:
            text: 文本内容
        
        Returns:
            联系方式字符串
        """
        import re
        
        # 匹配联系方式
        contact_patterns = [
            # 联系人：张老师
            r'联系人[:：]?\s*([^，。；;]+)',
            # 联系电话：027-81977189
            r'联系电话[:：]?\s*([^，。；;]+)',
            # 联系邮箱：hbuetw@hbue.edu.cn
            r'联系邮箱[:：]?\s*([^，。；;]+)',
            # 联系方式：027-81977189
            r'联系方式[:：]?\s*([^，。；;]+)',
            # 电话：027-81977189
            r'电话[:：]?\s*([^，。；;]+)',
            # 邮箱：hbuetw@hbue.edu.cn
            r'邮箱[:：]?\s*([^，。；;]+)',
            # QQ：123456789
            r'QQ[:：]?\s*([^，。；;]+)',
            # 联系地址：行政楼A113
            r'联系地址[:：]?\s*([^，。；;]+)',
            # 联系电话：027-81977189（杜老师）
            r'联系电话[:：]?\s*([^，。；;]+)\s*\([^，。；;]+\)',
            # 邮箱地址：hbuetw@hbue.edu.cn
            r'邮箱地址[:：]?\s*([^，。；;]+)',
            # 联系方式：hbuetw@hbue.edu.cn
            r'联系方式[:：]?\s*([^，。；;]+@[^，。；;]+)'
        ]
        
        contacts = []
        
        # 先匹配具体的联系方式
        for pattern in contact_patterns:
            match = re.search(pattern, text)
            if match:
                contact = match.group(1).strip()
                # 清理结果
                contact = re.sub(r'[\r\n\s]+', ' ', contact)
                # 过滤掉无效内容
                if contact and len(contact) > 2 and '截止' not in contact and '报名' not in contact:
                    contacts.append(contact)
        
        # 尝试提取邮箱地址
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_matches = re.findall(email_pattern, text)
        for email in email_matches:
            if email not in contacts:
                contacts.append(email)
        
        # 尝试提取电话号码
        phone_pattern = r'1[3-9]\d{9}|0\d{2,3}-?\d{7,8}'
        phone_matches = re.findall(phone_pattern, text)
        for phone in phone_matches:
            if phone not in contacts:
                contacts.append(phone)
        
        # 尝试提取QQ号
        qq_pattern = r'QQ[:：]?\s*(\d{5,11})'
        qq_matches = re.findall(qq_pattern, text)
        for qq in qq_matches:
            if qq not in contacts:
                contacts.append(f'QQ: {qq}')
        
        if contacts:
            return '; '.join(contacts[:5])  # 最多返回5个联系方式
        
        return ''
    
    def _extract_requirement(self, text: str) -> str:
        """
        提取参赛要求
        
        Args:
            text: 文本内容
        
        Returns:
            参赛要求字符串
        """
        import re
        
        # 匹配参赛要求
        requirement_patterns = [
            # 参赛要求：全日制在校本科生
            r'参赛要求[:：]?\s*([^，。；;]+)',
            # 报名要求：全日制在校本科生
            r'报名要求[:：]?\s*([^，。；;]+)',
            # 要求：全日制在校本科生
            r'要求[:：]?\s*([^，。；;]+)',
            # 条件：全日制在校本科生
            r'条件[:：]?\s*([^，。；;]+)',
            # 作品要求：内容新颖有创意
            r'作品要求[:：]?\s*([^，。；;]+)',
            # 报名条件：全日制在校本科生
            r'报名条件[:：]?\s*([^，。；;]+)',
            # 参赛条件：全日制在校本科生
            r'参赛条件[:：]?\s*([^，。；;]+)',
            # 报名须知：请携带身份证
            r'报名须知[:：]?\s*([^，。；;]+)',
            # 注意事项：请按时提交作品
            r'注意事项[:：]?\s*([^，。；;]+)',
            # 参赛须知：请遵守比赛规则
            r'参赛须知[:：]?\s*([^，。；;]+)'
        ]
        
        for pattern in requirement_patterns:
            match = re.search(pattern, text)
            if match:
                requirement = match.group(1).strip()
                # 清理结果
                requirement = re.sub(r'[\r\n\s]+', ' ', requirement)
                # 过滤掉无效内容
                if requirement and len(requirement) > 5 and '联系' not in requirement and '截止' not in requirement and '电话' not in requirement and '邮箱' not in requirement:
                    return requirement
        
        # 尝试提取包含"要求"的内容
        requirement_match = re.search(r'要求[:：]?\s*([^，。；;]+)', text)
        if requirement_match:
            requirement = requirement_match.group(1).strip()
            requirement = re.sub(r'[\r\n\s]+', ' ', requirement)
            if requirement and len(requirement) > 5 and '联系' not in requirement and '截止' not in requirement:
                return requirement
        
        return ''
    
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
