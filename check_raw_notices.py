#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查原始公告
"""

import sqlite3

if __name__ == "__main__":
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 查找缺失的竞赛通知
    missing_titles = [
        "会计学院2025年红色文化科普讲解案例大赛选拔通知",
        "关于开展会计学院第一届心理健康教育微课大赛作品征集的通知",
        "第十二届全国大学生能源经济学术创意大赛湖北赛区湖北经济学院校赛通知",
        "关于举办2026年全国大学生英语竞赛湖北赛区初赛的通知",
        "关于举办2025年（第二届）大学生数据要素素质大赛的通知",
        "关于2025年数据要素×大赛湖北经济学院校赛通知",
        "关于组织参加中国高校财经慕课联盟第三届同课异构教学竞赛的通知"
    ]
    
    # 标准化标题的函数
    def normalize_title(t):
        # 去除所有空格
        t = ''.join(t.split())
        # 去除所有引号
        t = t.replace('"', '').replace('“', '').replace('”', '')
        # 转换为小写
        t = t.lower()
        return t
    
    # 查找缺失的竞赛通知
    print("查找缺失的竞赛通知:")
    for title in missing_titles:
        # 标准化标题
        normalized_title = normalize_title(title)
        
        # 在数据库中查找匹配的通知
        cursor.execute("SELECT id, title, publish_time, filter_status FROM raw_notices")
        found = False
        for row in cursor.fetchall():
            notice_id, notice_title, publish_time, filter_status = row
            normalized_notice_title = normalize_title(notice_title)
            if normalized_notice_title == normalized_title:
                print(f"标题: {notice_title}")
                print(f"ID: {notice_id}")
                print(f"发布日期: {publish_time}")
                print(f"筛选状态: {filter_status}")
                print()
                found = True
                break
        if not found:
            print(f"未找到标题: {title}")
            print()
    
    # 关闭数据库连接
    conn.close()
