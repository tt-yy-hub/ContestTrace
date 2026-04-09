#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查筛选状态
"""

import sqlite3

if __name__ == "__main__":
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 查询筛选状态统计
    cursor.execute('SELECT filter_status, COUNT(*) FROM raw_notices GROUP BY filter_status')
    status_counts = cursor.fetchall()
    
    # 打印筛选状态统计
    print('筛选状态统计:')
    for status, count in status_counts:
        print(f'状态: {status}, 数量: {count}')
    
    # 关闭数据库连接
    conn.close()
