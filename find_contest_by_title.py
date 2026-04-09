#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据标题查找竞赛通知
"""

import sqlite3

def find_contest_by_title():
    """
    根据标题查找竞赛通知
    """
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 用户提供的竞赛通知标题
    target_title = "关于举办2025年（第二届）大学生数据要素素质大赛的通知"
    
    # 查找包含关键词的通知
    cursor.execute("SELECT id, title, publish_time FROM raw_notices WHERE title LIKE ?", ('%数据要素%',))
    rows = cursor.fetchall()
    
    print("查找结果：")
    print("=" * 120)
    print(f"{'ID':<5} {'标题':<80} {'发布时间':<15}")
    print("=" * 120)
    
    for row in rows:
        notice_id, title, publish_time = row
        print(f"{notice_id:<5} {title[:80]:<80} {publish_time:<15}")
    
    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    find_contest_by_title()
