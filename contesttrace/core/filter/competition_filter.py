#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竞赛内容过滤器
"""

import logging
import time
from typing import Dict, Tuple, List

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CompetitionFilter:
    """
    竞赛内容过滤器
    """
    
    def __init__(self):
        """
        初始化过滤器
        """
        # 初始化关键词权重
        self._init_keywords()
        # 性能统计
        self.performance_stats = {
            'total_notices': 0,
            'filtered_notices': 0,
            'filter_time': 0
        }
    
    def _init_keywords(self):
        """
        初始化关键词权重
        """
        # 强竞赛词列表（至少50个）
        self.strong_competition_keywords = {
            "竞赛": 5,
            "比赛": 5,
            "挑战杯": 10,
            "设计大赛": 8,
            "演讲比赛": 8,
            "技能大赛": 8,
            "创新大赛": 8,
            "创意大赛": 8,
            "创业计划竞赛": 10,
            "建模大赛": 8,
            "数学竞赛": 8,
            "英语竞赛": 8,
            "计算机设计大赛": 8,
            "市场调查与分析大赛": 8,
            "统计建模大赛": 8,
            "蓝桥杯": 10,
            "21世纪杯": 10,
            "米兰设计周": 8,
            "能源经济学术创意大赛": 8,
            "数据要素素质大赛": 8,
            "数据要素×大赛": 8,
            "中国国际大学生创新大赛": 10,
            "互联网+": 10,
            "全国大学生数学建模竞赛": 10,
            "全国大学生英语竞赛": 10,
            "全国大学生电子设计竞赛": 10,
            "全国大学生机械创新设计大赛": 10,
            "全国大学生结构设计竞赛": 10,
            "全国大学生化工设计竞赛": 10,
            "全国大学生智能汽车竞赛": 10,
            "全国大学生程序设计竞赛": 10,
            "全国大学生数学竞赛": 10,
            "全国大学生物理实验竞赛": 10,
            "全国大学生化学实验竞赛": 10,
            "全国大学生生命科学竞赛": 10,
            "全国大学生环境设计大赛": 10,
            "全国大学生工业设计大赛": 10,
            "全国大学生广告艺术大赛": 10,
            "全国大学生摄影艺术大赛": 10,
            "全国大学生书法大赛": 10,
            "全国大学生文学作品大赛": 10,
            "全国大学生创业大赛": 10,
            "全国大学生职业规划大赛": 10,
            "全国大学生就业创业大赛": 10,
            "全国大学生社会实践大赛": 10,
            "全国大学生志愿服务大赛": 10,
            "全国大学生科技作品竞赛": 10,
            "全国大学生发明创造大赛": 10,
            "全国大学生专利申请大赛": 10,
            "全国大学生知识产权竞赛": 10,
            "全国大学生法律知识竞赛": 10,
            "全国大学生历史知识竞赛": 10,
            "全国大学生地理知识竞赛": 10,
            "全国大学生生物知识竞赛": 10,
            "全国大学生计算机知识竞赛": 10
        }
        
        # 次要关键词（中权重）
        self.secondary_keywords = {
            "选拔赛": 4,
            "校赛": 4,
            "初赛": 4,
            "决赛": 4,
            "报名": 3,
            "参赛": 3,
            "获奖": 3,
            "奖金": 3,
            "奖项": 3,
            "征集": 2,
            "评选": 2,
            "展示": 2,
            "活动": 2
        }
        
        # 排除关键词（至少30个）
        self.exclude_keywords = {
            "考试": -10,
            "培训": -10,
            "遴选": -10,
            "招生": -10,
            "转专业": -10,
            "讲座": -10,
            "报告": -10,
            "经验分享": -10,
            "公示": -10,
            "文件转发": -10,
            "志愿服务": -10,
            "升国旗": -10,
            "暑期社会实践": -10,
            "团日活动": -10,
            "主题团日": -10,
            "班会": -10,
            "晚讲评": -10,
            "招聘": -10,
            "宣讲会": -10,
            "访企拓岗": -10,
            "心理健康": -10,
            "培训": -10,
            "表彰": -10,
            "学工": -10,
            "辅导员": -10,
            "班主任": -10,
            "学生工作": -10,
            "例会": -10,
            "会议": -10,
            "召开": -10,
            "举行": -10,
            "放假": -10,
            "缴费": -10,
            "樱花": -10,
            "田径运动会": -10,
            "彩虹跑": -10,
            "优秀学院学生会": -10,
            "获全国": -10,
            "获一等奖": -10,
            "获二等奖": -10,
            "获三等奖": -10,
            "大赛（a类）": -10,
            "大赛（a+类）": -10,
            "校友返校": -10,
            "庆祝荣休": -10,
            "统测补考": -10,
            "考生资格": -10,
            "成绩等级": -10,
            "补充说明": -10,
            "成功晋级": -10,
            "获奖队伍": -10,
            "名单公布": -10,
            "圆满举行": -10,
            "斩获佳绩": -10,
            "喜报": -10,
            "心理委员": -10,
            "培养考核": -10,
            "阳光心灵": -10,
            "文化节": -10,
            "外聘教师": -10,
            "信息统计": -10,
            "学籍信息": -10,
            "编制": -10,
            "指南": -10,
            "重修课表": -10,
            "重修报名": -10,
            "普通话测试": -10,
            "学籍异动": -10,
            "课程补修": -10,
            "免修": -10,
            "选修课程": -10,
            "补选": -10,
            "缓考": -10,
            "补考": -10,
            "招募": -10,
            "志愿宣讲团": -10,
            "获评": -10,
            "指数": -10,
            "奖学金": -10,
            "评选": -10,
            "教学改革": -10,
            "教研项目": -10,
            "竞赛奖励": -10,
            "奖励申报": -10,
            "考场安排": -10,
            "工作量": -10,
            "现场决赛": -10,
            "拟推荐": -10,
            "观看": -10,
            "工作方案": -10,
            "创新大赛现场赛": -10,
            "教师数智教育": -10,
            "智慧课程": -10,
            "泛雅杯": -10,
            "智慧树杯": -10,
            "课创赛": -10,
            "教学竞赛项目": -10,
            "圆满落幕": -10,
            "以歌传情": -10,
            "唱响青春": -10,
            "合唱队": -10,
            "歌咏比赛": -10,
            "我院团队荣获": -10,
            "艺术设计学院在": -10,
            "我院一团队获": -10,
            "未来设计师": -10,
            "全国大学生数字媒体科技作品及创意竞赛": -10,
            "教师参加": -10,
            "教学设计创新": -10,
            "混合式教学设计": -10,
            "同课异构": -10,
            "超星杯": -10
        }
    
    def filter_notices(self, notices):
        """
        筛选通知列表
        
        Args:
            notices: 通知列表
        
        Returns:
            筛选后的通知列表
        """
        start_time = time.time()
        filtered_notices = []
        
        for notice in notices:
            title = notice.get('title', '')
            content = notice.get('content', '')
            is_contest, confidence = self.is_contest(title, content)
            if is_contest:
                # 添加置信度分数
                notice['filter_confidence'] = confidence
                filtered_notices.append(notice)
        
        # 更新性能统计
        self.performance_stats['total_notices'] += len(notices)
        self.performance_stats['filtered_notices'] += len(filtered_notices)
        self.performance_stats['filter_time'] += time.time() - start_time
        
        logger.info(f"筛选完成：共处理 {len(notices)} 条通知，筛选出 {len(filtered_notices)} 条竞赛通知")
        return filtered_notices
    
    def calculate_confidence(self, title: str, content: str) -> float:
        """
        计算竞赛置信度
        
        Args:
            title: 标题
            content: 内容
        
        Returns:
            0-1之间的置信度
        """
        # 标准化文本的函数
        def normalize_text(t):
            # 去除所有空格
            t = ''.join(t.split())
            # 去除所有引号
            t = t.replace('"', '').replace('“', '').replace('”', '')
            # 转换为小写
            t = t.lower()
            return t
        
        # 标准化文本
        normalized_title = normalize_text(title)
        normalized_content = normalize_text(content)
        
        # 计算置信度分数
        confidence = 0
        
        # 1. 快速过滤：检查排除关键词（优先）
        exclude_score = 0
        for keyword, weight in self.exclude_keywords.items():
            if keyword in normalized_title:
                exclude_score += weight
                # 如果排除关键词权重过高，直接返回低置信度
                if exclude_score < -5:
                    return 0.0
        
        # 2. 正向匹配：计算强竞赛词权重
        strong_score = 0
        for keyword, weight in self.strong_competition_keywords.items():
            if keyword in normalized_title:
                strong_score += weight * 2  # 标题中的关键词权重更高
            elif keyword in normalized_content:
                strong_score += weight
        
        # 3. 计算次要关键词权重
        secondary_score = 0
        for keyword, weight in self.secondary_keywords.items():
            if keyword in normalized_title:
                secondary_score += weight * 1.5  # 标题中的关键词权重更高
            elif keyword in normalized_content:
                secondary_score += weight
        
        # 4. 特殊处理：包含"杯"且不包含排除关键词的通知
        if "杯" in normalized_title and strong_score > 0:
            strong_score += 3
        
        # 5. 特殊处理：包含"大赛"且不包含排除关键词的通知
        if "大赛" in normalized_title and strong_score > 0:
            strong_score += 3
        
        # 6. 特殊处理：包含"竞赛"且不包含排除关键词的通知
        if "竞赛" in normalized_title and strong_score > 0:
            strong_score += 3
        
        # 计算总置信度
        total_score = strong_score + secondary_score + exclude_score
        
        # 计算归一化置信度（0-1之间）
        normalized_confidence = min(1.0, max(0.0, total_score / 30))
        
        return normalized_confidence
    
    def is_contest(self, title: str, content: str) -> Tuple[bool, float]:
        """
        判断是否为竞赛内容
        
        Args:
            title: 标题
            content: 内容
        
        Returns:
            (是否为竞赛内容, 置信度分数)
        """
        confidence = self.calculate_confidence(title, content)
        
        # 根据置信度判断
        if confidence >= 0.7:
            return True, confidence
        elif confidence >= 0.3:
            # 待审核
            return False, confidence
        else:
            # 拒绝
            return False, confidence
    
    def get_performance_stats(self) -> Dict[str, float]:
        """
        获取过滤器性能统计
        
        Returns:
            性能统计信息
        """
        return self.performance_stats
    
    def reset_performance_stats(self):
        """
        重置性能统计
        """
        self.performance_stats = {
            'total_notices': 0,
            'filtered_notices': 0,
            'filter_time': 0
        }
    
    def analyze_notice(self, title: str, content: str) -> Dict[str, any]:
        """
        分析通知，返回详细的筛选信息
        
        Args:
            title: 标题
            content: 内容
        
        Returns:
            分析结果
        """
        # 标准化文本
        def normalize_text(t):
            t = ''.join(t.split())
            t = t.replace('"', '').replace('“', '').replace('”', '')
            t = t.lower()
            return t
        
        normalized_title = normalize_text(title)
        normalized_content = normalize_text(content)
        
        # 分析关键词匹配情况
        matched_core = []
        matched_secondary = []
        matched_exclude = []
        
        for keyword in self.core_keywords:
            if keyword in normalized_title or keyword in normalized_content:
                matched_core.append(keyword)
        
        for keyword in self.secondary_keywords:
            if keyword in normalized_title or keyword in normalized_content:
                matched_secondary.append(keyword)
        
        for keyword in self.exclude_keywords:
            if keyword in normalized_title:
                matched_exclude.append(keyword)
        
        # 计算置信度
        is_contest, confidence = self.is_contest(title, content)
        
        return {
            'is_contest': is_contest,
            'confidence': confidence,
            'matched_core_keywords': matched_core,
            'matched_secondary_keywords': matched_secondary,
            'matched_exclude_keywords': matched_exclude
        }
