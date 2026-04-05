#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 any 表达式
"""

# 测试案例
contest_keywords = [
    '竞赛', '比赛', '大赛', '挑战赛', '邀请赛', '杯赛',
    '锦标赛', '联赛', '总决赛', '半决赛', '初赛', '复赛',
    '报名', '参赛', '获奖', '奖项', '一等奖', '二等奖',
    '三等奖', '优秀奖', '冠军', '亚军', '季军', '名次',
    '评分', '评审', '评委', '专家组', '作品', '作品征集',
    '提交作品', '参赛作品'
]

# 测试标题
title = '关于举办2026年"挑战杯"大学生创业计划竞赛校级选拔赛的通知'

# 测试 any 表达式
result = any(keyword in title for keyword in contest_keywords)
print(f"any(keyword in title for keyword in contest_keywords): {result}")

# 测试逐个关键词
print("\n逐个关键词测试:")
for keyword in contest_keywords:
    if keyword in title:
        print(f"'{keyword}' in title: True")
