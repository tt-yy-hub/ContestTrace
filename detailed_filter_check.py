#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细检查筛选结果
"""

import sqlite3
from contesttrace.core.filter.competition_filter import CompetitionFilter

# 用户提供的竞赛通知（28个）
user_contests = [
    (8, "第31届中国日报社 \"21世纪杯\"全国英语演讲比赛湖北经济学院校园选拔赛通知"),
    (27, "关于举行2026年（19届）中国大学生计算机设计大赛湖北经济学院校赛的通知"),
    (29, "蓝桥杯全国大学生软件和信息技术专业人才大赛校级比赛通知"),
    (37, "湖北经济学院关于组织学生参加2025年全国大学生数学竞赛选拔测试的通知"),
    (38, "关于举办\"正大杯\"第十六届全国大学生市场调查与分析大赛（本科生组）湖北经济学院选拔赛的通知"),
    (40, "湖北经济学院关于组织学生参加2026年\"华中杯\"大学生数学建模挑战赛通知"),
    (41, "湖北经济学院关于组织学生参加第十六届全国大学生市场调查与分析大赛的通知"),
    (47, "关于组织参加2026年全国大学生统计建模大赛（本科生组）的通知"),
    (49, "湖北经济学院关于组织学生参加2025年全国大学生数学建模竞赛校内选拔赛通知"),
    (50, "关于组织参加2025年（第十一届）全国大学生统计建模大赛（本科生组）的通知"),
    (51, "2026年第十届\"米兰设计周-中国高校设计学科师生优秀作品展\"学科竞赛通知"),
    (53, "2026年第十七届蓝桥杯全国软件和信息技术专业人才大赛视觉艺术设计赛通知"),
    (55, "关于举行2026年（19届）中国大学生计算机设计大赛湖北经济学院校赛的通知"),
    (71, "关于举办湖北经济学院第三届\"浩然杯\" 读书演讲大赛的通知"),
    (94, "关于举办2026年\"挑战杯\"大学生 创业计划竞赛校级选拔赛的通知"),
    (179, "关于举办旅游与酒店管理学院第二届导游风采大赛的通知"),
    (269, "关于开展会计学院第一届职业生涯人物访谈大赛的通知"),
    (313, "关于开展湖北经济学院第二十三届\"藏龙杯\"健康之星心理知识大赛会计学院院赛的通知"),
    (328, "会计学院关于开展\"传承红色基因，续写青春华章\"主题微团课比赛的通知"),
    (400, "会计学院2025年红色文化科普讲解案例大赛选拔通知"),
    (404, "关于开展会计学院第一届心理健康教育微课大赛作品征集的通知"),
    (417, "第十二届全国大学生能源经济学术创意大赛湖北赛区湖北经济学院校赛通知"),
    (436, "关于组织参加2026年全国大学生统计建模大赛（本科生组）的通知"),
    (437, "关于举办\"正大杯\"第十六届全国大学生市场调查与分析大赛（本科生组）湖北经济学院选拔赛的通知"),
    (476, "关于举办2026年全国大学生英语竞赛湖北赛区初赛的通知"),
    (533, "湖北经济学院关于组织学生参加第十六届全国大学生市场调查与分析大赛的通知"),
    (594, "关于举办2025年（第二届）大学生数据要素素质大赛的通知"),
    (613, "关于2025年\"数据要素×\"大赛湖北经济学院校赛通知")
]

def detailed_filter_check():
    """
    详细检查筛选结果
    """
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 初始化过滤器
    filter = CompetitionFilter()
    
    # 获取所有原始通知
    cursor.execute("SELECT id, title, content FROM raw_notices")
    all_notices = cursor.fetchall()
    
    # 筛选通知
    filtered_notices = []
    
    for notice in all_notices:
        notice_id, title, content = notice
        if filter.is_contest(title, content):
            filtered_notices.append((notice_id, title))
    
    # 检查用户提供的竞赛通知是否被筛选出来
    user_contests_in_filtered = []
    user_contests_not_in_filtered = []
    
    for contest_id, expected_title in user_contests:
        found = False
        for filtered_id, filtered_title in filtered_notices:
            if contest_id == filtered_id:
                user_contests_in_filtered.append((contest_id, filtered_title))
                found = True
                break
        if not found:
            user_contests_not_in_filtered.append((contest_id, expected_title))
    
    # 检查筛选结果中的非用户提供的通知
    non_user_contests = []
    for filtered_id, filtered_title in filtered_notices:
        is_user_contest = False
        for contest_id, _ in user_contests:
            if filtered_id == contest_id:
                is_user_contest = True
                break
        if not is_user_contest:
            non_user_contests.append((filtered_id, filtered_title))
    
    # 关闭数据库连接
    conn.close()
    
    # 输出结果
    print("详细筛选结果检查：")
    print("=" * 120)
    
    print(f"\n1. 用户提供的竞赛通知总数：{len(user_contests)}")
    print(f"2. 被筛选出来的用户竞赛通知：{len(user_contests_in_filtered)}")
    print(f"3. 未被筛选出来的用户竞赛通知：{len(user_contests_not_in_filtered)}")
    print(f"4. 筛选结果中的非用户竞赛通知：{len(non_user_contests)}")
    print(f"5. 总筛选结果：{len(filtered_notices)}")
    
    if user_contests_not_in_filtered:
        print("\n未被筛选出来的用户竞赛通知：")
        print("-" * 120)
        for contest_id, title in user_contests_not_in_filtered:
            print(f"ID: {contest_id}, 标题: {title}")
    
    if non_user_contests:
        print("\n筛选结果中的非竞赛通知：")
        print("-" * 120)
        print(f"共 {len(non_user_contests)} 个非竞赛通知被错误筛选")
        print("部分非竞赛通知示例：")
        for i, (notice_id, title) in enumerate(non_user_contests[:5]):
            try:
                print(f"ID: {notice_id}, 标题: {title[:60]}")
            except:
                print(f"ID: {notice_id}, 标题: [无法显示]")
        if len(non_user_contests) > 5:
            print(f"... 还有 {len(non_user_contests) - 5} 个非竞赛通知")

if __name__ == "__main__":
    detailed_filter_check()
