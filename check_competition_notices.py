#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查竞赛通知
"""

import sqlite3

if __name__ == "__main__":
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_competition.db')
    cursor = conn.cursor()
    
    # 获取所有竞赛通知
    cursor.execute("SELECT id, title, publish_time FROM competition_notices")
    notices = cursor.fetchall()
    
    # 打印竞赛通知数量
    print(f"竞赛通知数量: {len(notices)}")
    
    # 打印所有竞赛通知
    print("\n竞赛通知列表:")
    for notice in notices:
        notice_id, title, publish_time = notice
        print(f"ID: {notice_id}, 标题: {title}, 发布日期: {publish_time}")
    
    # 关闭数据库连接
    conn.close()
