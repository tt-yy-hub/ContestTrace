#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计竞赛公告数量
"""

import json
import os

def count_contests():
    """
    统计竞赛公告数量
    """
    try:
        # 读取JSON文件
        json_path = "contesttrace/frontend/data/contests.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            contests = json.load(f)
        
        # 统计数量
        count = len(contests)
        print(f"竞赛公告数量: {count}")
        
        # 打印前几个标题，验证筛选效果
        print("\n前10个竞赛公告标题:")
        for i, contest in enumerate(contests[:10]):
            print(f"{i+1}. {contest.get('title', '无标题')}")
        
    except Exception as e:
        print(f"读取文件失败: {e}")

if __name__ == '__main__':
    count_contests()
