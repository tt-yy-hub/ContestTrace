#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中 deadline 字段是否包含前缀
"""

import sqlite3

# 连接数据库
conn = sqlite3.connect('data/competiton.db')
c = conn.cursor()

# 查询前 10 条记录的 deadline 字段
print("查询前 10 条记录的 deadline 字段：")
c.execute("SELECT id, title, deadline FROM competition_notices LIMIT 10")
for row in c.fetchall():
    id, title, deadline = row
    print(f"ID: {id}, 标题: {title[:50]}..., Deadline: '{deadline}'")

# 统计包含前缀的记录数
c.execute("SELECT COUNT(*) FROM competition_notices WHERE deadline LIKE '%截止日期：%' OR deadline LIKE '%活动日期：%'")
prefixed_count = c.fetchone()[0]

# 统计总记录数
c.execute("SELECT COUNT(*) FROM competition_notices")
total_count = c.fetchone()[0]

print(f"\n总记录数: {total_count}")
print(f"包含前缀的记录数: {prefixed_count}")
print(f"前缀率: {prefixed_count / total_count * 100:.2f}%")

# 关闭连接
conn.close()
