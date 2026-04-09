#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出竞赛公告到文件
"""

import sqlite3

def export_competition_notices():
    """
    导出竞赛公告到文件
    """
    try:
        # 连接竞赛公告数据库
        conn = sqlite3.connect('data/contest_trace_competition.db')
        cursor = conn.cursor()
        
        # 查询数据库中的所有竞赛公告标题
        cursor.execute('SELECT title FROM competition_notices')
        comp_notices = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # 导出到文件
        with open('competition_notices.txt', 'w', encoding='utf-8') as f:
            f.write(f"竞赛公告数据库中共有 {len(comp_notices)} 条竞赛公告\n\n")
            f.write("竞赛公告数据库中的公告标题：\n")
            f.write("-" * 80 + "\n")
            for i, notice in enumerate(comp_notices, 1):
                f.write(f"{i}. {notice}\n")
        
        print("竞赛公告已导出到 competition_notices.txt 文件")
        
    except Exception as e:
        print(f"导出竞赛公告失败: {e}")

if __name__ == '__main__':
    export_competition_notices()
