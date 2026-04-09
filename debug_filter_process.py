#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试筛选过程
"""

import sqlite3
from contesttrace.core.filter.competition_filter import CompetitionFilter

if __name__ == "__main__":
    # 初始化过滤器
    filter = CompetitionFilter()
    
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 获取待筛选的公告
    cursor.execute("SELECT id, title, content, filter_status FROM raw_notices WHERE filter_status = 'pending' AND publish_time >= '2025-01-01'")
    pending_notices = cursor.fetchall()
    
    # 打印待筛选的公告数量
    print(f"待筛选的公告数量: {len(pending_notices)}")
    
    # 筛选公告
    filtered_notices = []
    for notice in pending_notices:
        notice_id, title, content, filter_status = notice
        notice_dict = {
            'id': notice_id,
            'title': title,
            'content': content,
            'filter_status': filter_status
        }
        if filter.is_contest(title, content):
            filtered_notices.append(notice_dict)
    
    # 打印筛选结果
    print(f"筛选通过的公告数量: {len(filtered_notices)}")
    print("\n筛选通过的公告:")
    for notice in filtered_notices:
        print(f"ID: {notice['id']}, 标题: {notice['title']}")
    
    # 关闭数据库连接
    conn.close()
