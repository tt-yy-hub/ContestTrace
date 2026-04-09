#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竞赛内容过滤器
"""

import logging

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
        # 初始化配置
        pass
    
    def filter_notices(self, notices):
        """
        筛选通知列表
        
        Args:
            notices: 通知列表
        
        Returns:
            筛选后的通知列表
        """
        filtered_notices = []
        for notice in notices:
            title = notice.get('title', '')
            content = notice.get('content', '')
            if self.is_contest(title, content):
                filtered_notices.append(notice)
        return filtered_notices
    
    def is_contest(self, title: str, content: str) -> bool:
        """
        判断是否为竞赛内容
        
        Args:
            title: 标题
            content: 内容
        
        Returns:
            是否为竞赛内容
        """
        # 标准化标题的函数
        def normalize_title(t):
            # 去除所有空格
            t = ''.join(t.split())
            # 去除所有引号
            t = t.replace('"', '').replace('“', '').replace('”', '')
            # 转换为小写
            t = t.lower()
            return t
        
        # 标准化当前标题
        normalized_title = normalize_title(title)
        normalized_content = content.lower()
        
        # 1. 检查是否包含非竞赛关键词（排除非竞赛通知）
        non_contest_keywords = [
            "考试", "培训", "遴选", "招生", "转专业", "讲座", "报告", "经验分享",
            "公示", "文件转发", "志愿服务", "升国旗", "暑期社会实践",
            "团日活动", "樱花", "田径运动会", "彩虹跑", "优秀学院学生会",
            "获全国", "获一等奖", "获二等奖", "获三等奖", "大赛（a类）", "大赛（a+类）",
            "校友返校", "庆祝荣休", "统测补考", "考生资格", "成绩等级", "补充说明",
            "成功晋级", "获奖队伍", "名单公布", "圆满举行", "斩获佳绩", "喜报",
            "心理委员", "培养考核", "阳光心灵", "文化节",
            "外聘教师", "信息统计", "学籍信息", "编制", "指南",
            "重修课表", "重修报名", "普通话测试", "学籍异动", "课程补修",
            "免修", "选修课程", "补选", "缓考", "补考", "招募", "志愿宣讲团",
            "获评", "指数", "奖学金", "评选", "教学改革", "教研项目",
            "竞赛奖励", "奖励申报", "考场安排", "工作量", "现场决赛", "拟推荐", "观看", "工作方案", "创新大赛现场赛",
            "教师数智教育", "智慧课程", "泛雅杯", "智慧树杯", "课创赛", "教学竞赛项目",
            "圆满落幕", "以歌传情", "唱响青春", "合唱队", "歌咏比赛",
            "我院团队荣获", "艺术设计学院在", "我院一团队获", "未来设计师", "全国大学生数字媒体科技作品及创意竞赛",
            "教师参加", "教学设计创新", "混合式教学设计", "同课异构", "超星杯"
        ]
        
        # 检查标题中是否包含非竞赛关键词
        for keyword in non_contest_keywords:
            if keyword in normalized_title:
                return False
        
        # 2. 检查是否包含竞赛相关关键词
        contest_keywords = [
            "竞赛", "比赛", "挑战杯", "设计大赛", "演讲比赛", "技能大赛", 
            "创新大赛", "创意大赛", "创业计划竞赛", "建模大赛", "数学竞赛", 
            "英语竞赛", "计算机设计大赛", "市场调查与分析大赛", "统计建模大赛", 
            "蓝桥杯", "21世纪杯", "米兰设计周", "能源经济学术创意大赛", 
            "数据要素素质大赛", "数据要素×大赛", "中国国际大学生创新大赛", "选拔赛", "校赛", "初赛"
        ]
        
        # 检查标题或内容中是否包含竞赛相关关键词
        for keyword in contest_keywords:
            if keyword in normalized_title or keyword in normalized_content:
                return True
        
        # 3. 特殊处理：包含"杯"且不包含非竞赛关键词的通知
        if "杯" in normalized_title and not any(keyword in normalized_title for keyword in non_contest_keywords):
            return True
        
        # 4. 特殊处理：包含"大赛"且不包含非竞赛关键词的通知
        if "大赛" in normalized_title and not any(keyword in normalized_title for keyword in non_contest_keywords):
            return True
        
        # 5. 特殊处理：包含"竞赛"且不包含非竞赛关键词的通知
        if "竞赛" in normalized_title and not any(keyword in normalized_title for keyword in non_contest_keywords):
            return True
        
        # 不在白名单中且不包含竞赛相关关键词的通知一律排除
        return False
