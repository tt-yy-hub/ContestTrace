#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查竞赛公告是否已被筛选进数据库
"""

import sqlite3

# 用户提供的竞赛公告列表
user_contests = [
    '关于举办2025年"挑战杯"大学生课外学术科技作品竞赛校赛报名通知',
    '2025年全国大学生数学建模竞赛湖北经济学院选拔赛通知',
    '2025年"互联网+"大学生创新创业大赛院内选拔赛启动通知',
    '信息工程学院2025年软件设计大赛报名通知',
    '统计与数学学院2025年统计建模竞赛通知',
    '会计学院2025年"用友杯"会计技能竞赛报名通知',
    '关于举办2025年"外研社·国才杯"全国英语演讲大赛校赛的通知',
    '工商管理学院2025年"企业经营模拟沙盘"竞赛通知',
    '经济与贸易学院2025年"国际贸易实务"技能竞赛报名通知',
    '金融学院2025年"金融建模与投资分析"竞赛通知',
    '旅游与酒店管理学院2025年"酒店服务技能"竞赛通知',
    '2025年全国大学生电子设计竞赛湖北经济学院选拔赛通知',
    '创新创业学院2025年"创业计划书"大赛通知',
    '信息管理学院2025年"大数据分析与可视化"竞赛通知',
    '艺术设计学院2025年"数字媒体艺术设计"竞赛通知',
    '学生工作处2025年"职业生涯规划"大赛通知（竞赛类）',
    '2025年"全国大学生市场调查与分析大赛"校赛报名通知',
    '会计学院2025年"内部控制案例分析"竞赛通知',
    '金融学院2025年"保险产品设计"竞赛通知'
]

def check_contest_inclusion():
    """
    检查竞赛公告是否已被筛选进数据库
    """
    try:
        # 连接竞赛公告数据库
        conn = sqlite3.connect('data/contest_trace_competition.db')
        cursor = conn.cursor()
        
        # 查询数据库中的所有竞赛公告标题
        cursor.execute('SELECT title FROM competition_notices')
        db_contests = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        print(f"数据库中共有 {len(db_contests)} 条竞赛公告")
        print("\n检查用户提供的竞赛公告是否已被筛选进数据库：")
        print("-" * 80)
        
        included_count = 0
        not_included = []
        
        for i, user_contest in enumerate(user_contests, 1):
            included = any(db_contest == user_contest for db_contest in db_contests)
            if included:
                print(f"已包含 {i}: {user_contest}")
                included_count += 1
            else:
                print(f"未包含 {i}: {user_contest}")
                not_included.append(user_contest)
        
        print("-" * 80)
        print(f"统计：共 {len(user_contests)} 条竞赛公告，其中 {included_count} 条已包含，{len(not_included)} 条未包含")
        
        if not_included:
            print("\n未包含的竞赛公告：")
            for i, contest in enumerate(not_included, 1):
                print(f"{i}. {contest}")
        
    except Exception as e:
        print(f"检查竞赛公告失败: {e}")

if __name__ == '__main__':
    check_contest_inclusion()
