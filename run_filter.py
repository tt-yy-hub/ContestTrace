#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行完整的筛选流程
"""

import sqlite3
import logging
from contesttrace.core.filter.competition_filter import CompetitionFilter

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_filter():
    """
    运行完整的筛选流程
    """
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 获取所有原始通知
    cursor.execute("SELECT id, title, content FROM raw_notices")
    notices = cursor.fetchall()
    
    # 初始化过滤器
    filter = CompetitionFilter()
    
    # 筛选通知
    filtered_notices = []
    passed = 0
    rejected = 0
    
    for notice in notices:
        notice_id, title, content = notice
        if filter.is_contest(title, content):
            filtered_notices.append(notice)
            passed += 1
        else:
            rejected += 1
    
    # 关闭数据库连接
    conn.close()
    
    # 输出结果
    print(f"筛选完成：共 {len(notices)} 条，通过 {passed} 条，拒绝 {rejected} 条")
    
    # 检查用户提供的竞赛通知是否都在筛选结果中（排除数据库中不存在的竞赛通知）
    user_contest_ids = [8, 27, 29, 37, 38, 40, 41, 47, 49, 50, 51, 53, 55, 71, 94, 179, 269, 313, 328, 400, 404, 417, 436, 437, 476, 533, 592, 613]
    
    user_contests_in_filtered = 0
    non_user_contests = 0
    
    # 统计用户提供的竞赛通知和非用户提供的竞赛通知
    for notice in filtered_notices:
        notice_id, _, _ = notice
        is_user_contest = notice_id in user_contest_ids
        if is_user_contest:
            user_contests_in_filtered += 1
        else:
            non_user_contests += 1
    
    # 检查哪些用户提供的竞赛通知没有被筛选出来
    missing_user_contests = []
    for contest_id in user_contest_ids:
        found = False
        for notice in filtered_notices:
            if notice[0] == contest_id:
                found = True
                break
        if not found:
            missing_user_contests.append(contest_id)
    
    print("\n筛选结果统计：")
    print("=" * 80)
    print(f"用户提供的竞赛通知在筛选结果中：{user_contests_in_filtered}/33")
    print(f"非用户提供的竞赛通知在筛选结果中：{non_user_contests}")
    print(f"总筛选结果：{len(filtered_notices)}")
    
    if missing_user_contests:
        print("\n未被筛选出来的用户竞赛通知ID：")
        print(missing_user_contests)
    else:
        print("\n所有用户提供的竞赛通知都被筛选出来了！")

if __name__ == "__main__":
    run_filter()
