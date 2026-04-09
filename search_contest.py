#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索竞赛公告
"""

import sqlite3

if __name__ == "__main__":
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 搜索包含"匠影定格"的公告
    cursor.execute('SELECT id, title FROM raw_notices WHERE title LIKE ?', ('%匠影定格%',))
    rows = cursor.fetchall()
    
    # 打印搜索结果
    print('找到的公告:')
    for row in rows:
        print(f'ID: {row[0]}, 标题: {row[1]}')
    
    # 关闭数据库连接
    conn.close()
