#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将raw_notices表按照competition_notices的格式导出为CSV文件
"""

import sqlite3
import csv
import os
from datetime import datetime

# 数据库文件路径
RAW_DB_PATH = "data/contest_trace_raw.db"

# 导出目录
EXPORT_DIR = "data/exports"

# 确保导出目录存在
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_raw_as_competition_format():
    """
    将raw_notices表按照competition_notices的格式导出为CSV文件
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(RAW_DB_PATH)
        cursor = conn.cursor()
        
        # 查询raw_notices表的所有数据
        cursor.execute("SELECT * FROM raw_notices")
        rows = cursor.fetchall()
        
        # 定义输出文件路径
        output_file = os.path.join(EXPORT_DIR, "raw_notices_as_competition_format.csv")
        
        # 写入CSV文件，使用competition_notices的格式
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 写入表头（与competition_notices.csv格式一致）
            writer.writerow([
                'id', 'raw_notice_id', 'notice_url', 'title', 'publish_time', 
                'source_department', 'content', 'summary', 'tags', 'sign_up_deadline', 'filter_pass_time'
            ])
            
            # 写入数据
            for i, row in enumerate(rows, 1):
                # 提取raw_notices表的字段
                raw_id = row[0]
                notice_url = row[1]
                title = row[2]
                publish_time = row[3]
                source_department = row[4]
                content = row[5]
                
                # 其他字段使用空值，因为raw_notices表中没有这些字段
                summary = ''
                tags = ''
                sign_up_deadline = ''
                filter_pass_time = ''
                
                # 写入一行数据
                writer.writerow([
                    i, raw_id, notice_url, title, publish_time, 
                    source_department, content, summary, tags, sign_up_deadline, filter_pass_time
                ])
        
        conn.close()
        print(f"成功导出 {len(rows)} 条数据到 {output_file}")
        print("导出格式与competition_notices.csv一致，可以直接发送给豆包。")
        return True
    except Exception as e:
        print(f"导出失败: {e}")
        return False

def main():
    """
    主函数
    """
    print("开始将raw_notices表按照competition_notices的格式导出...")
    export_raw_as_competition_format()

if __name__ == '__main__':
    main()
