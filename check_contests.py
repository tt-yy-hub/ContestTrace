#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查竞赛公告，确保排除了非竞赛内容
"""

import json
import os

def check_contests():
    """
    检查竞赛公告，确保排除了非竞赛内容
    """
    try:
        # 读取JSON文件
        json_path = "contesttrace/frontend/data/contests.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            contests = json.load(f)
        
        # 统计数量
        count = len(contests)
        print(f"竞赛公告数量: {count}")
        
        # 打印所有标题，验证筛选效果
        print("\n所有竞赛公告标题:")
        for i, contest in enumerate(contests):
            title = contest.get('title', '无标题')
            print(f"{i+1}. {title}")
        
        # 检查是否包含非竞赛内容
        non_contest_keywords = ['获奖', '表彰', '颁奖', '名单', '结果', '公示', '已结束', '圆满举行']
        print("\n检查是否包含非竞赛内容:")
        for i, contest in enumerate(contests):
            title = contest.get('title', '无标题')
            content = contest.get('content', '')
            text = (title + ' ' + content).lower()
            
            for keyword in non_contest_keywords:
                if keyword.lower() in text:
                    print(f"警告: 第{i+1}条可能包含非竞赛内容: {title}")
                    break
        
    except Exception as e:
        print(f"读取文件失败: {e}")

if __name__ == '__main__':
    check_contests()
