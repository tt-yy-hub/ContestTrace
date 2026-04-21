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
    
    def __init__(self, guide_competitions=None):
        """
        初始化过滤器
        
        Args:
            guide_competitions: 官方竞赛指南数据，包含name、level和aliases字段
        """
        # 初始化关键词权重
        self._init_keywords()
        # 性能统计
        self.performance_stats = {
            'total_notices': 0,
            'filtered_notices': 0,
            'filter_time': 0
        }
        # 指南竞赛数据
        self.guide_competitions = guide_competitions or []
        # 构建按名称长度降序排序的竞赛列表
        self.sorted_competitions = sorted(
            self.guide_competitions,
            key=lambda x: len(x['name']),
            reverse=True
        )
        # 匹配结果
        self.matched_guide_name = None
        self.matched_guide_level = None
    
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
            "全国大学生计算机知识竞赛": 10,
            "导游风采大赛": 8,
            "微团课比赛": 8,
            "红色文化科普讲解": 8,
            "企业竞争模拟": 8,
            "工程实践与创新能力": 8,
            "CaTICs": 8,
            "节能减排": 8,
            "藏龙杯": 8,
            "浩然杯": 8,
            "导游风采": 8,
            "微团课": 8,
            "心理知识大赛": 8,
            "红色文化科普讲解案例大赛": 8,
            "经典诵读": 8,
            "写作大赛": 8,
            "统计建模": 8,
            "华中杯": 8,
            "创新创业大赛": 10,
            "职业规划大赛": 8,
            "企业经营模拟": 8,
            "案例分析大赛": 8,
            "辩论赛": 8,
            "知识竞赛": 8
        }
        
        # 次要关键词（中权重）
        self.secondary_keywords = {
            "选拔赛": 6,  # 提高权重
            "校赛": 6,      # 提高权重
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
            "表彰": -10,
            "学工": -10,
            "辅导员": -10,
            "班主任": -10,
            "学生工作": -10,
            "例会": -10,
            "放假": -10,
            "缴费": -10,
            "樱花": -10,
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
            "喜报": -10,
            "心理委员": -10,
            "心理委员培训": -10,
            "培养考核": -10,
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
            "超星杯": -10,
            "学工例会": -10,
            "工作例会": -10,
            "会议纪要": -10,
            "会议通知": -10,
            "年审": -10,
            "年检": -10,
            "年审合格": -10,
            "社团年审": -10,
            "招生简章": -10,
            "微专业": -10,
            "辅修": -10,
            "双学位": -10,
            "召开": -10,
            "部署": -10,
            "总结会": -10,
            "表彰会": -10,
            "颁奖会": -10,
            "班委会": -10,
            "查寝": -10,
            "查课": -10,
            "招聘会": -10,
            "就业服务": -10,
            "心理普查": -10,
            "心灵剧场": -10,
            "心委评选": -10,
            "党校": -10,
            "入党积极分子": -10,
            "发展对象": -10,
            "预备党员": -10,
            "五四评优": -10,
            "评优评先": -10,
            "评奖评优": -10,
            "答疑会": -10,
            "座谈会": -10,
            "交流会": -10,
            "研讨会": -10,
            "论坛": -10,
            "报告会": -10,
            "部门例会": -10,
            "全体会议": -10,
            "专题会议": -10,
            "答疑": -10,
            "讲座": -10,
            "学术讲座": -10,
            "学术报告": -10,
            "教授应邀": -10,
            "应邀": -10,
            "培训": -10,
            "暑期培训": -10,
            "辅导": -10,
            "考前辅导": -10,
            "经验分享": -10,
            "教师教学创新大赛": -10,
            "辅导员素质能力大赛": -10,
            "班主任基本功": -10,
            "教职工运动会": -10,
            "教工组": -10
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
            notice_id = notice.get('id', '')
            # 检查是否是我们关注的缺失赛事
            if notice_id in [694, 733, 1230]:
                print(f"处理通知 ID: {notice_id}, 标题: {title}")
            is_contest, confidence = self.is_contest(title, content)
            if is_contest:
                # 添加置信度分数
                notice['filter_confidence'] = confidence
                filtered_notices.append(notice)
                if notice_id in [694, 733, 1230]:
                    print(f"通知 ID: {notice_id} 被判定为竞赛，置信度: {confidence}")
            elif notice_id in [694, 733, 1230]:
                print(f"通知 ID: {notice_id} 未被判定为竞赛，置信度: {confidence}")
        
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
        # 优先执行指南匹配
        combined_text = title + content
        matched_name, matched_level = self._match_guide_competition(combined_text)
        if matched_name:
            # 匹配到指南竞赛，直接返回高置信度
            return 0.95
        
        # 未匹配到指南竞赛，执行原有逻辑
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
        normalized_text = normalize_text(combined_text)
        title_lower = title.lower()
        content_lower = content.lower()
        
        # 检查教师竞赛，直接排除
        teacher_competition_keywords = [
            "教师教学创新大赛", "辅导员素质能力大赛", "班主任基本功", 
            "教师数智教育", "混合式教学设计", "同课异构", 
            "泛雅杯", "智慧树杯"
        ]
        for keyword in teacher_competition_keywords:
            if keyword in normalized_title or keyword in normalized_content:
                return 0.0
        
        # 检查体育比赛，排除教职工相关
        if "运动会" in normalized_title or "彩虹跑" in normalized_title or "羽毛球赛" in normalized_title:
            if "教职工" in normalized_title or "教工组" in normalized_title:
                return 0.0
            elif "学生" in normalized_title:
                # 学生田径运动会保留
                return 0.9
        
        # 标题权重提升：标题中出现竞赛相关词，直接高置信度
        title_competition_indicators = ["赛", "杯", "大赛", "挑战杯", "蓝桥杯"]
        if any(indicator in normalized_title for indicator in title_competition_indicators):
            # 检查是否为获奖报道
            award_report_patterns = ["获全国", "获一等奖", "获二等奖", "获三等奖", "荣获", "斩获"]
            if not any(pattern in normalized_title for pattern in award_report_patterns):
                return 0.85
        
        # 1. 快速过滤：检查排除关键词（优先）
        exclude_score = 0
        excluded = False
        for keyword, weight in self.exclude_keywords.items():
            if keyword in normalized_title:
                exclude_score += weight
                excluded = True
                # 如果排除关键词权重过高，直接返回低置信度
                if exclude_score < -5:
                    return 0.0
        
        # 新增：如果命中排除词且标题中无任何强竞赛词，直接拒绝
        if excluded and not any(kw in title_lower for kw in self.strong_competition_keywords):
            # 如果排除词命中，即使标题有少量竞赛词，但排除词数量较多也拒绝
            if sum(1 for kw in self.exclude_keywords if kw in normalized_text) >= 3:
                return 0.0
        
        # 2. 正向匹配：计算强竞赛词权重
        strong_score = 0
        strong_count = 0
        for keyword, weight in self.strong_competition_keywords.items():
            if keyword in normalized_title:
                strong_score += weight * 2  # 标题中的关键词权重更高
                strong_count += 1
            elif keyword in normalized_content:
                strong_score += weight
                strong_count += 1
        
        # 3. 计算次要关键词权重
        secondary_score = 0
        for keyword, weight in self.secondary_keywords.items():
            if keyword in normalized_title:
                secondary_score += weight * 1.5  # 标题中的关键词权重更高
            elif keyword in normalized_content:
                secondary_score += weight
        
        # 4. 内容特征强化：增加置信度
        content_positive_features = [
            "报名截止", "参赛对象", "奖项设置", "一等奖", "二等奖", 
            "颁发证书", "奖金", "推荐参加省赛", "推荐参加国赛",
            "指导老师", "评委", "答辩", "路演"
        ]
        for feature in content_positive_features:
            if feature in normalized_content:
                strong_score += 2
        
        # 5. 特殊处理：包含"杯"且不包含排除关键词的通知
        if "杯" in normalized_title and strong_score > 0:
            strong_score += 3
        
        # 6. 特殊处理：包含"大赛"且不包含排除关键词的通知
        if "大赛" in normalized_title and strong_score > 0:
            strong_score += 3
        
        # 7. 特殊处理：包含"竞赛"且不包含排除关键词的通知
        if "竞赛" in normalized_title and strong_score > 0:
            strong_score += 3
        
        # 计算总置信度
        total_score = strong_score + secondary_score + exclude_score
        
        # 计算归一化置信度（0-1之间），调整分母为20，降低得分门槛
        raw_score = min(1.0, max(0.0, total_score / 20))
        
        # 降权因子1：若文本包含会议相关词语，降权
        meeting_indicators = ["会议指出", "会议强调", "会议要求", "例会", "工作部署", "总结讲话", "会议总结", "会议认为"]
        # 如果标题中无竞赛词，则大幅降权；否则小幅降权
        if any(ind in combined_text for ind in meeting_indicators):
            if not any(kw in title_lower for kw in self.strong_competition_keywords):
                raw_score *= 0.5  # 标题无竞赛词，会议特征明显 → 降低置信度
            else:
                raw_score *= 0.8
        
        # 降权因子2：统计排除词命中次数和强竞赛词命中次数
        exclude_count = sum(1 for keyword in self.exclude_keywords if keyword in normalized_text)
        if exclude_count >= 2 and strong_count <= 1:
            raw_score *= 0.6
        
        # 降权因子3：若标题中无强竞赛词，根据内容中竞赛词数量进行降权
        if not any(kw in title_lower for kw in self.strong_competition_keywords):
            content_comp_count = sum(1 for kw in self.strong_competition_keywords if kw in content_lower)
            if content_comp_count == 0:
                raw_score *= 0.5
            elif content_comp_count <= 2:
                raw_score *= 0.6
            elif content_comp_count <= 4:
                raw_score *= 0.8
            # 内容竞赛词超过4个仍保留原权重（可能是真正的竞赛通知但标题未体现）
        
        # 降权因子4：讲座类内容（即使包含少量竞赛词，也降权）
        lecture_indicators = ["讲座", "学术报告", "报告会", "主讲人", "主持人", "本次讲座", "报告内容"]
        lecture_count = sum(1 for ind in lecture_indicators if ind in content_lower)
        if lecture_count >= 2:
            raw_score *= 0.4  # 讲座特征明显，降低置信度
        elif lecture_count == 1:
            # 如果只有一个讲座词，但标题无竞赛词，也降权
            if not any(kw in title_lower for kw in self.strong_competition_keywords):
                raw_score *= 0.6
        
        # 最终置信度
        final_confidence = min(raw_score, 1.0)
        
        return final_confidence
    
    def is_contest(self, title: str, content: str) -> Tuple[bool, float]:
        """
        判断是否为竞赛内容
        
        Args:
            title: 标题
            content: 内容
        
        Returns:
            (是否为竞赛内容, 置信度分数)
        """
        # 先判断是否明显不是竞赛
        if self._is_obviously_non_competition(title, content):
            return False, 0.0
        
        confidence = self.calculate_confidence(title, content)
        
        # 根据置信度判断
        if confidence >= 0.6:
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
    
    def _is_obviously_non_competition(self, title: str, content: str) -> bool:
        """
        判断是否明显不是竞赛通知
        
        Args:
            title: 标题
            content: 内容
        
        Returns:
            是否明显不是竞赛通知
        """
        import re
        
        # 保护：竞赛结果报道（如“获...奖”、“斩获佳绩”）应保留
        if re.search(r"(荣获|斩获|获得).*(一等奖|二等奖|三等奖|金奖|银奖|铜奖)", title):
            return False  # 不视为非竞赛
        
        # 保护：明显的竞赛通知应保留
        competition_patterns = [
            r"关于举办.*(竞赛|大赛|挑战赛)",
            r"关于组织参加.*(竞赛|大赛|挑战赛)",
            r".*(藏龙杯|华中杯|统计建模).*比赛",
            r".*(经典诵读|写作).*大赛"
        ]
        for pattern in competition_patterns:
            if re.search(pattern, title):
                return False  # 不视为非竞赛
        
        # 排除教师教学创新大赛（仅针对教师）
        if "教师教学创新" in title or "产教融合组" in title:
            return True
        
        # 排除单纯的作品征集活动（无竞赛性质）
        if "征集活动" in title and "竞赛" not in title and "大赛" not in title:
            return True
        
        # 排除跬步计划等非竞赛
        if "跬步计划" in title or "科研项目评选" in title:
            return True
        
        # 强制排除团日活动
        if "团日活动" in title or "主题团日" in title:
            return True
        
        # 标准化文本
        def normalize_text(t):
            # 去除所有空格
            t = ''.join(t.split())
            # 去除所有引号
            t = t.replace('"', '').replace('“', '').replace('”', '')
            # 转换为小写
            t = t.lower()
            return t
        
        combined_text = title + content
        normalized_text = normalize_text(combined_text)
        normalized_title = normalize_text(title)
        
        # 检查是否包含竞赛词
        has_competition_word = any(keyword in normalized_text for keyword in self.strong_competition_keywords)
        
        # 判断逻辑1：匹配会议相关模式
        meeting_pattern = r'(召开|举行|举办).*(学工例会|工作例会|会议|部署会|总结会)'
        if re.search(meeting_pattern, normalized_text) and not has_competition_word:
            return True
        
        # 判断逻辑2：包含会议结构词
        meeting_structure_words = ["会议指出", "会议强调", "参会人员", "会议认为", "会议要求"]
        if any(word in normalized_text for word in meeting_structure_words):
            return True
        
        # 判断逻辑3：匹配公示相关模式
        public_notice_pattern = r'公示.*(名单|结果|合格|年审)'
        if re.search(public_notice_pattern, normalized_text):
            return True
        
        # 判断逻辑4：匹配招生相关模式
        recruitment_pattern = r'(招生简章|微专业|辅修专业|双学位).*报名'
        if re.search(recruitment_pattern, normalized_text):
            return True
        
        # 判断逻辑5：匹配查寝查课等模式
        check_pattern = r'(查寝|查课|晚讲评|心理健康普查)'
        if re.search(check_pattern, normalized_text):
            return True
        
        # 标题包含会议/答疑类词汇，直接判定为非竞赛
        meeting_title_patterns = [
            r"召开.*(学工例会|工作例会|部门例会|全体会议|专题会议|答疑会|座谈会|交流会)",
            r"^(学工例会|工作例会|部门例会|转专业.*答疑会|答疑会)"
        ]
        if any(re.search(pattern, title) for pattern in meeting_title_patterns):
            return True
        
        # 标题以“召开”开头且包含“会议”，且无竞赛词
        if title.startswith("召开") and "会议" in title:
            if not any(kw in title for kw in self.strong_competition_keywords):
                return True
        
        # 转专业相关通知
        if "转专业" in title and ("答疑" in title or "座谈会" in title):
            return True
        
        # 学工例会（无论内容如何）
        if "学工例会" in title:
            return True
        
        # 学术讲座/报告类：标题包含讲座关键词，且不是竞赛结果报道
        if re.search(r"(讲座|学术报告|报告会|教授应邀|应邀.*讲座)", title):
            # 如果标题中没有"竞赛"、"大赛"、"挑战杯"等词，直接排除
            if not re.search(r"(竞赛|大赛|挑战杯|设计大赛|创新大赛|创业大赛)", title):
                return True
            # 如果有竞赛词，但内容主要是讲座介绍（如包含"主讲人"、"主持人"、"报告内容"），也排除
            if re.search(r"(主讲人|主持人|报告内容|本次讲座|讲座内容)", content):
                return True
        
        # 纯培训类通知（无竞赛性质）
        if re.search(r"(培训|暑期培训|辅导班|考前培训)", title):
            if not re.search(r"(竞赛|大赛|挑战杯|选拔赛)", title):
                return True
        
        return False
    
    def _match_guide_competition(self, text):
        """
        匹配官方竞赛指南中的竞赛名称
        
        Args:
            text: 文本（标题+内容）
            
        Returns:
            (匹配到的竞赛名称, 竞赛级别)，未匹配返回(None, None)
        """
        # 标准化文本
        def normalize_text(t):
            # 去除所有空格
            t = ''.join(t.split())
            # 去除所有引号
            t = t.replace('"', '').replace('“', '').replace('”', '')
            # 转换为小写
            t = t.lower()
            return t
        
        normalized_text = normalize_text(text)
        
        # 优先匹配完整竞赛名称
        for competition in self.sorted_competitions:
            name = competition['name']
            normalized_name = normalize_text(name)
            if normalized_name in normalized_text:
                self.matched_guide_name = name
                self.matched_guide_level = competition['level']
                return name, competition['level']
        
        # 尝试匹配别名
        for competition in self.sorted_competitions:
            for alias in competition['aliases']:
                normalized_alias = normalize_text(alias)
                if normalized_alias in normalized_text:
                    self.matched_guide_name = competition['name']
                    self.matched_guide_level = competition['level']
                    return competition['name'], competition['level']
        
        # 未匹配
        self.matched_guide_name = None
        self.matched_guide_level = None
        return None, None
    
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
