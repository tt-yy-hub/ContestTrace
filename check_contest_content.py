#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查被错误排除的竞赛通知的完整内容
"""

import sqlite3

# 被错误排除的竞赛通知
missing_contests = [41, 533]

def check_contest_content():
    """
    检查被错误排除的竞赛通知的完整内容
    """
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    for contest_id in missing_contests:
        # 从数据库中获取该ID的通知
        cursor.execute("SELECT id, title, content FROM raw_notices WHERE id = ?", (contest_id,))
        row = cursor.fetchone()
        
        if row:
            notice_id, title, content = row
            print(f"\nID {contest_id}: {title}")
            print("=" * 80)
            print(f"完整内容:")
            print(content)
            print("=" * 80)
        else:
            print(f"\nID {contest_id}: 未找到")
    
    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    check_contest_content()
