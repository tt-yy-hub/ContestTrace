#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查未被筛选出来的用户竞赛通知
"""

import sqlite3

# 未被筛选出来的用户竞赛通知ID
missing_ids = [618, 655, 668, 671, 715]

def check_missing_contests():
    """
    检查未被筛选出来的用户竞赛通知
    """
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    print("未被筛选出来的通知详情：")
    print("=" * 100)
    print(f"{'ID':<5} {'标题':<80}")
    print("=" * 100)
    
    for contest_id in missing_ids:
        # 从数据库中获取该ID的通知
        cursor.execute("SELECT id, title FROM raw_notices WHERE id = ?", (contest_id,))
        row = cursor.fetchone()
        
        if row:
            notice_id, title = row
            print(f"{notice_id:<5} {title[:80]:<80}")
        else:
            print(f"{contest_id:<5} 未找到")
    
    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    check_missing_contests()
