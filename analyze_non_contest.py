#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析筛选结果中的非竞赛通知
"""

import sqlite3
from contesttrace.core.filter.competition_filter import CompetitionFilter

# 用户提供的竞赛通知ID
user_contest_ids = [8, 27, 29, 37, 38, 40, 41, 47, 49, 50, 51, 53, 55, 71, 94, 179, 269, 313, 328, 400, 404, 417, 436, 437, 476, 533, 594, 613]

def analyze_non_contest():
    """
    分析筛选结果中的非竞赛通知
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
    
    # 分析非竞赛通知
    non_user_contests = []
    for filtered_id, filtered_title in filtered_notices:
        if filtered_id not in user_contest_ids:
            non_user_contests.append((filtered_id, filtered_title))
    
    # 关闭数据库连接
    conn.close()
    
    # 输出结果
    print("非竞赛通知分析：")
    print("=" * 120)
    print(f"筛选结果总数：{len(filtered_notices)}")
    print(f"用户竞赛通知数：{len([n for n in filtered_notices if n[0] in user_contest_ids])}")
    print(f"非竞赛通知数：{len(non_user_contests)}")
    
    if non_user_contests:
        print("\n非竞赛通知列表：")
        print("-" * 120)
        for notice_id, title in non_user_contests:
            print(f"ID: {notice_id}, 标题: {title[:80]}")

if __name__ == "__main__":
    analyze_non_contest()
