#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细调试筛选过程
"""

import sqlite3
from contesttrace.core.filter.competition_filter import CompetitionFilter
from contesttrace.core.storage.db_manager import DatabaseManager

if __name__ == "__main__":
    # 初始化数据库管理器
    db_manager = DatabaseManager()
    
    # 初始化过滤器
    filter = CompetitionFilter()
    
    # 获取待筛选的公告
    pending_notices = db_manager.get_pending_notices()
    
    # 打印待筛选的公告数量
    print(f"待筛选的公告数量: {len(pending_notices)}")
    
    # 检查待筛选的公告是否包含那些缺失的竞赛通知
    missing_titles = [
        "第31届中国日报社 21世纪杯全国英语演讲比赛湖北经济学院校园选拔赛通知",
        "关于举行2026年（19届）中国大学生计算机设计大赛湖北经济学院校赛的通知",
        "蓝桥杯全国大学生软件和信息技术专业人才大赛校级比赛通知",
        "湖北经济学院关于组织学生参加2025年全国大学生数学竞赛选拔测试的通知",
        "关于举办正大杯第十六届全国大学生市场调查与分析大赛（本科生组）湖北经济学院选拔赛的通知",
        "湖北经济学院关于组织学生参加2026年华中杯大学生数学建模挑战赛通知",
        "湖北经济学院关于组织学生参加第十六届全国大学生市场调查与分析大赛的通知",
        "关于组织参加2026年全国大学生统计建模大赛（本科生组）的通知",
        "湖北经济学院关于组织学生参加2025年全国大学生数学建模竞赛校内选拔赛通知",
        "关于组织参加2025年（第十一届）全国大学生统计建模大赛（本科生组）的通知",
        "2026年第十届米兰设计周-中国高校设计学科师生优秀作品展学科竞赛通知",
        "2026年第十七届蓝桥杯全国软件和信息技术专业人才大赛视觉艺术设计赛通知",
        "关于举行2026年（19届）中国大学生计算机设计大赛湖北经济学院校赛的通知",
        "关于举办湖北经济学院第三届浩然杯 读书演讲大赛的通知",
        "关于举办2026年挑战杯大学生 创业计划竞赛校级选拔赛的通知",
        "关于举办旅游与酒店管理学院第二届导游风采大赛的通知",
        "关于开展会计学院第一届职业生涯人物访谈大赛的通知",
        "关于开展湖北经济学院第二十三届藏龙杯健康之星心理知识大赛会计学院院赛的通知",
        "会计学院关于开展传承红色基因，续写青春华章主题微团课比赛的通知",
        "会计学院2025年红色文化科普讲解案例大赛选拔通知",
        "关于开展会计学院第一届心理健康教育微课大赛作品征集的通知",
        "第十二届全国大学生能源经济学术创意大赛湖北赛区湖北经济学院校赛通知",
        "关于组织参加2026年全国大学生统计建模大赛（本科生组）的通知",
        "关于举办正大杯第十六届全国大学生市场调查与分析大赛（本科生组）湖北经济学院选拔赛的通知",
        "关于举办2026年全国大学生英语竞赛湖北赛区初赛的通知",
        "湖北经济学院关于组织学生参加第十六届全国大学生市场调查与分析大赛的通知",
        "关于举办2025年（第二届）大学生数据要素素质大赛的通知",
        "关于2025年数据要素×大赛湖北经济学院校赛通知",
        "关于组织参加中国高校财经慕课联盟第三届同课异构教学竞赛的通知"
    ]
    
    # 标准化标题的函数
    def normalize_title(t):
        # 去除所有空格
        t = ''.join(t.split())
        # 去除所有引号
        t = t.replace('"', '').replace('“', '').replace('”', '')
        # 转换为小写
        t = t.lower()
        return t
    
    # 检查待筛选的公告是否包含那些缺失的竞赛通知
    print("\n检查待筛选的公告是否包含缺失的竞赛通知:")
    for title in missing_titles:
        # 标准化标题
        normalized_title = normalize_title(title)
        
        # 在待筛选的公告中查找匹配的通知
        found = False
        for notice in pending_notices:
            notice_title = notice.get('title', '')
            normalized_notice_title = normalize_title(notice_title)
            if normalized_notice_title == normalized_title:
                print(f"找到匹配: {notice_title}")
                print(f"ID: {notice.get('id')}")
                print(f"筛选状态: {notice.get('filter_status')}")
                print(f"发布日期: {notice.get('publish_time')}")
                print()
                found = True
                break
        if not found:
            print(f"未找到匹配: {title}")
            print()
    
    # 筛选公告
    filtered_notices = filter.filter_notices(pending_notices)
    
    # 打印筛选结果
    print(f"\n筛选通过的公告数量: {len(filtered_notices)}")
    print("\n筛选通过的公告:")
    for notice in filtered_notices:
        print(f"ID: {notice.get('id')}, 标题: {notice.get('title')}")
    
    # 关闭数据库连接
    db_manager = None
