#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出数据库数据为CSV表格文件
"""

import sqlite3
import csv
import os
from pathlib import Path

# 数据库文件路径
RAW_DB_PATH = "data/contest_trace_raw.db"
COMP_DB_PATH = "data/contest_trace_competition.db"

# 导出目录
EXPORT_DIR = "data/exports"

# 确保导出目录存在
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_table_to_csv(db_path, table_name, output_file):
    """
    导出数据库表为CSV文件
    
    Args:
        db_path: 数据库文件路径
        table_name: 表名
        output_file: 输出CSV文件路径
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        
        # 查询所有数据
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # 写入CSV文件
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(columns)
            # 写入数据
            for row in rows:
                writer.writerow(row)
        
        conn.close()
        print(f"成功导出 {len(rows)} 条数据到 {output_file}")
        return True
    except Exception as e:
        print(f"导出失败: {e}")
        return False

def main():
    """
    主函数
    """
    print("开始导出数据库数据为CSV文件...")
    
    # 导出原始公告数据
    raw_output = os.path.join(EXPORT_DIR, "raw_notices.csv")
    export_table_to_csv(RAW_DB_PATH, "raw_notices", raw_output)
    
    # 导出竞赛公告数据
    comp_output = os.path.join(EXPORT_DIR, "competition_notices.csv")
    export_table_to_csv(COMP_DB_PATH, "competition_notices", comp_output)
    
    print("\n导出完成！")
    print(f"原始公告数据: {raw_output}")
    print(f"竞赛公告数据: {comp_output}")
    print("\n这些CSV文件可以直接用Excel打开，也可以发送给豆包。")

if __name__ == '__main__':
    main()
