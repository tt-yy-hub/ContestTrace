#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找缺失的竞赛通知
"""

import sqlite3
from contesttrace.core.filter.competition_filter import CompetitionFilter

if __name__ == "__main__":
    # 初始化过滤器
    filter = CompetitionFilter()
    
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 用户提供的竞赛通知标题白名单
    user_contest_titles = [
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
    for user_title in user_contest_titles:
        # 标准化白名单标题
        normalized_user_title = normalize_title(user_title)
        
        # 在数据库中查找匹配的通知
        cursor.execute("SELECT id, title, content FROM raw_notices")
        found = False
        for row in cursor.fetchall():
            notice_id, title, content = row
            normalized_title = normalize_title(title)
            if normalized_title == normalized_user_title:
                # 测试筛选逻辑
                is_contest = filter.is_contest(title, content)
                print(f"标题: {title}")
                print(f"标准化后: {normalized_title}")
                print(f"是否为竞赛: {is_contest}")
                print()
                found = True
                break
        if not found:
            print(f"未找到标题: {user_title}")
            print()
    
    # 关闭数据库连接
    conn.close()
