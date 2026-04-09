#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查未被筛选为竞赛的公告
"""

import sqlite3
from contesttrace.core.filter.competition_filter import CompetitionFilter

# 未被筛选为竞赛的公告标题
filtered_out_titles = [
    '第31届中国日报社 "21世纪杯"全国英语演讲比赛湖北经济学院校园选拔赛通知',
    '关于组织参加2026年全国大学生统计建模大赛（本科生组）的通知',
    '湖北经济学院关于组织学生参加2025年全国大学生数学建模竞赛校内选拔赛通知',
    '关于组织参加2025年（第十一届）全国大学生统计建模大赛（本科生组）的通知',
    '关于组织参加2026年全国大学生统计建模大赛（本科生组）的通知'
]

def check_filtered_out_contests():
    """
    检查未被筛选为竞赛的公告
    """
    try:
        # 连接原始公告数据库
        conn = sqlite3.connect('data/contest_trace_raw.db')
        cursor = conn.cursor()
        
        # 创建筛选器实例
        filter = CompetitionFilter()
        
        print("检查未被筛选为竞赛的公告：")
        print("-" * 150)
        
        for title in filtered_out_titles:
            # 查找原始公告
            cursor.execute('SELECT id, title, content FROM raw_notices WHERE title = ?', (title,))
            result = cursor.fetchone()
            
            if result:
                notice_id, title, content = result
                print(f"\n公告ID: {notice_id}")
                print(f"标题: {title}")
                print(f"内容前200字符: {content[:200]}...")
                
                # 检查是否被筛选为竞赛
                is_contest = filter.is_contest(title, content)
                print(f"是否被筛选为竞赛: {is_contest}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查竞赛公告失败: {e}")

if __name__ == '__main__':
    check_filtered_out_contests()
