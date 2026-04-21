#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精准筛选模块
过滤非竞赛内容
"""

import re
import logging

logger = logging.getLogger(__name__)


class ContestFilter:
    """
    竞赛内容过滤器
    """
    
    def __init__(self):
        """
        初始化过滤器
        """
        # 非竞赛内容关键词
        self.non_contest_keywords = [
            # 团日活动
            '团日活动', '主题团日', '团日会议',
            # 培训
            '培训', '培训班', '培训课程', '学习培训',
            # 志愿服务
            '志愿服务', '志愿活动', '义工', '志愿者',
            # 青马工程
            '青马工程', '青年马克思主义', '青马班',
            # 跬步计划
            '跬步计划',
            # 科研立项结题
            '科研立项', '结题', '项目结题', '科研项目',
            # 公示
            '公示', '公告', '通知', '公示期',
            # 会议
            '会议', '研讨会', '座谈会', '推进会',
            # 其他非竞赛内容
            '讲座', '报告', '演讲', '论坛',
            '招聘', '就业', '实习', '奖学金',
            '表彰', '表扬', '先进', '优秀',
            '调研', '考察', '访问', '交流',
            '团建', '党建', '组织生活', '民主生活会',
            '假期', '放假', '值班', '作息'
        ]
        
        # 竞赛关键词
        self.contest_keywords = [
            '竞赛', '比赛', '大赛', '挑战赛',
            '邀请赛', '杯赛', '锦标赛', '联赛',
            '总决赛', '半决赛', '初赛', '复赛',
            '报名', '参赛', '获奖', '奖项',
            '一等奖', '二等奖', '三等奖', '优秀奖',
            '冠军', '亚军', '季军', '名次',
            '评分', '评审', '评委', '专家组',
            '作品', '作品征集', '提交作品', '参赛作品'
        ]
    
    def is_contest(self, title: str, content: str) -> bool:
        """
        判断是否为竞赛内容
        
        Args:
            title: 标题
            content: 内容
        
        Returns:
            是否为竞赛内容
        """
        text = (title + " " + content).lower()
        title_lower = title.lower()
        content_lower = content.lower()
        
        # 首先检查是否包含公示类关键词（优先级最高）
        public_notice_keywords = [
            '公示', '名单', '入围', '拟入选', '拟推荐', '当选', '聘任', '任命', '公示期',
            '获奖名单', '表彰名单', '结果公示', '拟表彰', '拟奖励'
        ]
        for keyword in public_notice_keywords:
            if keyword in title_lower or keyword in content_lower:
                logger.debug(f"跳过（筛选）：{title} | 命中公示类关键词：{keyword}")
                return False
        
        # 硬排除关键词（即使包含竞赛关键词也排除）
        hard_exclude_keywords = [
            '团日活动', '主题团日', '团日会议', '团日',
            '征文', '征文活动', '樱花市集', '摊位招租', '摊位招募',
            '社会实践', '返家乡', '志愿者', '志愿服务',
            '社团申请', '社团成立', '田径运动会', '彩虹跑',
            '代表大会', '提案征集', '应急救护培训', '向上向善好青年',
            '学风建设', '启动仪式', '宣介动员', '红十字', '寻访活动',
            '培训通知', '备赛培训', '积思', '主题寻访活动'
        ]
        
        # 检查硬排除关键词
        text_lower = text.lower()
        for keyword in hard_exclude_keywords:
            if keyword.lower() in text_lower:
                logger.debug(f"跳过（硬排除）：{title} | 命中硬排除关键词：{keyword}")
                return False
        
        # 特殊处理：排除备赛培训通知
        if '备赛培训' in text or ('培训' in title_lower and '竞赛' in text):
            logger.debug(f"跳过（硬排除）：{title} | 命中备赛培训关键词")
            return False
        
        # 特殊处理：排除学风建设活动
        if '学风建设' in text:
            logger.debug(f"跳过（硬排除）：{title} | 命中学风建设关键词")
            return False
        
        # 检查是否包含竞赛关键词
        contest_keywords = [
            '竞赛', '比赛', '大赛', '挑战赛', '邀请赛', '杯赛',
            '锦标赛', '联赛', '总决赛', '半决赛', '初赛', '复赛', '决赛',
            '报名', '参赛', '选拔赛', '申报', '作品征集',
            '挑战杯', '互联网+', '创新创业', '数学建模', '英语竞赛',
            '程序设计', '机器人', '电子设计', '化学竞赛', '物理竞赛',
            '生物竞赛', '创业计划', '学科竞赛', '技能竞赛', '创青春',
            '浩然杯', '三创赛', '学创杯', '知翰杯', 'ican', '电子商务',
            '数学竞赛', '计算机竞赛', '统计建模', '科研竞赛', '创新竞赛'
        ]
        
        # 检查是否包含非竞赛类关键词
        non_contest_keywords = [
            '团日', '培训', '青马工程', '跬步计划',
            '科研立项', '结题', '项目结题', '科研项目',
            '会议', '研讨会', '座谈会', '推进会',
            '讲座', '报告', '论坛', '招聘', '就业',
            '实习', '奖学金', '表彰', '表扬', '先进', '优秀',
            '调研', '考察', '访问', '交流', '团建', '党建',
            '组织生活', '民主生活会', '假期', '放假', '值班', '作息',
            '西部计划', '文艺', '宣讲', '学生会', '歌词',
            '校歌征集', '团员发展', '人事任免',
            '十佳志愿者', '优秀学院', '评选活动', '评优', '先进个人',
            '先进集体', '表彰大会', '颁奖仪式', '获奖者', '获奖情况',
            '评选工作', '评选活动', '评选通知', '评选办法',
            '科研项目', '科研立项', '项目申报', '项目结题'
        ]
        
        # 检查是否包含活动/征文类关键词
        activity_keywords = [
            '活动', '征集', '报名活动', '主题活动', '系列活动',
            '读书活动', '演讲活动', '文艺活动', '文化活动'
        ]
        for keyword in activity_keywords:
            if keyword in text:
                # 特殊处理：如果包含竞赛关键词，则保留
                has_contest_keyword = any(contest_keyword in text for contest_keyword in contest_keywords)
                if not has_contest_keyword:
                    logger.debug(f"跳过（筛选）：{title} | 命中活动类关键词：{keyword}")
                    return False
        
        # 检查是否包含报名或赛事安排相关词汇
        registration_keywords = [
            '报名', '截止', '时间', '要求', '条件', '流程', '安排',
            '通知', '参赛', '资格', '材料', '提交', '评审', '奖励',
            '报名时间', '截止日期', '参赛条件', '报名方式', '比赛规则',
            '赛程安排', '赛事安排', '奖项设置', '评审标准', '报名流程'
        ]
        
        # 首先检查标题中是否包含竞赛关键词
        title_has_contest = any(keyword in title_lower for keyword in contest_keywords)
        
        # 然后检查内容中是否包含竞赛关键词和报名相关词汇
        content_has_contest = any(keyword in content_lower for keyword in contest_keywords)
        content_has_registration = any(keyword in content_lower for keyword in registration_keywords)
        
        # 判断逻辑：标题包含竞赛关键词，或者内容包含竞赛关键词和报名相关词汇
        if title_has_contest or (content_has_contest and content_has_registration):
            # 进一步检查是否包含结果公示、表彰等非报名类内容
            result_keywords = [
                '获奖', '表彰', '颁奖', '名单', '结果', '公示',
                '已结束', '已完成', '圆满结束', '落下帷幕'
            ]
            has_result_keyword = any(keyword in text for keyword in result_keywords)
            
            # 如果包含结果关键词，但同时包含报名关键词，则保留
            if has_result_keyword:
                has_registration_keyword = any(keyword in text for keyword in registration_keywords)
                if not has_registration_keyword:
                    logger.debug(f"跳过（筛选）：{title} | 命中结果类关键词，且无报名相关词汇")
                    return False
            
            # 进一步检查是否包含评选类内容
            selection_keywords = [
                '评选', '评选工作', '评选活动', '评选通知', '评选办法',
                '评选标准', '评选流程', '评选结果', '评选委员会'
            ]
            has_selection_keyword = any(keyword in text for keyword in selection_keywords)
            
            # 如果包含评选关键词，但同时包含竞赛关键词和报名关键词，则保留
            if has_selection_keyword:
                has_contest_keyword = any(keyword in text for keyword in contest_keywords)
                has_registration_keyword = any(keyword in text for keyword in registration_keywords)
                if not (has_contest_keyword and has_registration_keyword):
                    logger.debug(f"跳过（筛选）：{title} | 命中评选类关键词，且无竞赛和报名相关词汇")
                    return False
            
            # 特殊处理：排除跬步计划等科研项目评选
            if '跬步计划' in text:
                logger.debug(f"跳过（筛选）：{title} | 命中跬步计划，排除科研项目评选")
                return False
            
            # 特殊处理：排除十佳志愿者等评选活动
            if '十佳志愿者' in text:
                logger.debug(f"跳过（筛选）：{title} | 命中十佳志愿者评选")
                return False
            
            # 特殊处理：排除西部计划等志愿服务活动
            if '西部计划' in text:
                logger.debug(f"跳过（筛选）：{title} | 命中西部计划，排除志愿服务活动")
                return False
            
            # 特殊处理：排除优秀学院学生会等评选活动
            if '优秀学院学生会' in text:
                logger.debug(f"跳过（筛选）：{title} | 命中优秀学院学生会评选")
                return False
            
            logger.debug(f"判定为竞赛内容: {title}")
            return True
        
        # 默认不是竞赛内容
        logger.debug(f"跳过（筛选）：{title} | 未命中竞赛关键词或报名相关词汇")
        return False
    
    def filter_contests(self, contests: list) -> list:
        """
        过滤竞赛列表
        
        Args:
            contests: 竞赛信息列表
        
        Returns:
            过滤后的竞赛信息列表
        """
        filtered_contests = []
        total = len(contests)
        filtered = 0
        
        for contest in contests:
            title = contest.get('title', '')
            content = contest.get('content', '')
            
            if self.is_contest(title, content):
                filtered_contests.append(contest)
            else:
                filtered += 1
        
        logger.info(f"筛选完成：共 {total} 条，过滤 {filtered} 条，保留 {len(filtered_contests)} 条竞赛")
        return filtered_contests
