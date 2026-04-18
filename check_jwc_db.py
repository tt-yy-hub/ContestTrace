#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库表结构和数据
"""

import sqlite3
import os
from pathlib import Path

DATA_DIR = Path("data")

# 检查教务处数据库
db_path = DATA_DIR / "contest_trace_raw_教务处.db"

if not db_path.exists():
    print(f"数据库文件不存在: {db_path}")
else:
    print(f"数据库文件存在: {db_path}")
    print(f"文件大小: {db_path.stat().st_size} bytes")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # 列出所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"\n表列表: {[t[0] for t in tables]}")

    for table_name in tables:
        table = table_name[0]
        print(f"\n表 '{table}' 结构:")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

        # 检查数据数量
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  数据数量: {count}")

        # 如果有 url 列，检查几个样本
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        if 'url' in columns:
            cursor.execute(f"SELECT url FROM {table} LIMIT 3")
            urls = cursor.fetchall()
            print(f"  样本URL: {[u[0] for u in urls]}")

    conn.close()
