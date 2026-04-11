#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 data\competiton.db 中的表结构和 confidence 字段
"""

import sqlite3

# 连接数据库
conn = sqlite3.connect('data/competiton.db')
cursor = conn.cursor()

# 检查表结构
print("表结构:")
cursor.execute('PRAGMA table_info(competition_notices);')
columns = cursor.fetchall()
for col in columns:
    print(f"ID: {col[0]}, 名称: {col[1]}, 类型: {col[2]}, 是否为主键: {col[5]}")

# 检查是否有 confidence 字段
has_confidence = any(col[1] == 'confidence' for col in columns)
print(f"\n是否包含 confidence 字段: {has_confidence}")

# 如果有 confidence 字段，查看前10条记录的置信度
if has_confidence:
    print("\n前10条记录的置信度:")
    cursor.execute('SELECT id, title, confidence FROM competition_notices LIMIT 10;')
    records = cursor.fetchall()
    for record in records:
        print(f"ID: {record[0]}, 标题: {record[1][:50]}..., 置信度: {record[2]}")

# 关闭连接
conn.close()
