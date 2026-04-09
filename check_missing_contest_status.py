#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查缺失竞赛通知的筛选状态
"""

import sqlite3

if __name__ == "__main__":
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 查找缺失的竞赛通知
    missing_titles = [
        "第31届中国日报社 21世纪杯全国英语演讲比赛湖北经济学院校园选拔赛通知",
        "关于举行2026年（19届）中国大学生计算机设计大赛湖北经济学院校赛的通知",
        "蓝桥杯全国大学生软件和信息技术专业人才大赛校级比赛通知",
        "湖北经济学院关于组织学生参加2025年全国大学生数学竞赛选拔测试的通知",
        "湖北经济学院关于组织学生参加2026年华中杯大学生数学建模挑战赛通知",
        "湖北经济学院关于组织学生参加2025年全国大学生数学建模竞赛校内选拔赛通知",
        "关于组织参加2025年（第十一届）全国大学生统计建模大赛（本科生组）的通知",
        "2026年第十届米兰设计周-中国高校设计学科师生优秀作品展学科竞赛通知",
        "2026年第十七届蓝桥杯全国软件和信息技术专业人才大赛视觉艺术设计赛通知",
        "关于举行2026年（19届）中国大学生计算机设计大赛湖北经济学院校赛的通知",
        "关于举办湖北经济学院第三届浩然杯 读书演讲大赛的通知",
        "关于举办2026年挑战杯大学生 创业计划竞赛校级选拔赛的通知",
        "关于举办旅游与酒店管理学院第二届导游风采大赛的通知"
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
