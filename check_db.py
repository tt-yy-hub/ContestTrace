#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的竞赛数据
"""

import sqlite3
from pathlib import Path

db_path = "data/contest.db"

if not Path(db_path).exists():
    print(f"数据库文件不存在: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(contests)")
    columns = cursor.fetchall()
    print("表结构:")
    for column in columns:
        print(f"- {column[1]} ({column[2]})")
    
    # 检查数据量
    cursor.execute("SELECT COUNT(*) FROM contests")
    count = cursor.fetchone()[0]
    print(f"\n数据库中共有 {count} 条竞赛数据")
    
    # 检查前5条数据
    cursor.execute("SELECT title, url, publish_time FROM contests LIMIT 5")
    rows = cursor.fetchall()
    print("\n前5条竞赛数据:")
    for i, row in enumerate(rows):
        title, url, publish_time = row
        print(f"{i+1}. 标题: {title}")
        print(f"   URL: {url}")
        print(f"   发布时间: {publish_time}")
        print()
    
    conn.close()
except Exception as e:
    print(f"检查数据库失败: {e}")
