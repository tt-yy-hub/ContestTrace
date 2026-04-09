#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库结构
"""

import sqlite3

def check_db_structure():
    """
    检查数据库结构
    """
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 获取表结构
    cursor.execute("PRAGMA table_info(raw_notices)")
    columns = cursor.fetchall()
    
    print("表结构:")
    for column in columns:
        print(f"列名: {column[1]}, 类型: {column[2]}, 是否为主键: {column[5]}")
    
    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    check_db_structure()
