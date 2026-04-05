#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 is_contest 方法
"""

from contesttrace.core.parsers import ContestFilter

# 初始化过滤器
filter = ContestFilter()

# 测试标题和内容
title = '关于举办2026年"挑战杯"大学生创业计划竞赛校级选拔赛的通知'
content = '为选拔优秀作品参加全国"挑战杯"大学生创业计划竞赛，我校决定举办校级选拔赛。'

# 测试 is_contest 方法
result = filter.is_contest(title, content)
print(f"is_contest 结果: {result}")

# 测试排除词
print("\n测试排除词:")
exclude_keywords = [
    '团日', '培训', '志愿服务', '志愿者', '青马工程', '跬步计划',
    '科研立项', '结题', '公示', '公告', '会议',
    '讲座', '报告', '论坛', '招聘', '就业',
    '实习', '奖学金', '表彰', '表扬', '先进', '优秀',
    '调研', '考察', '访问', '交流', '团建', '党建',
    '组织生活', '民主生活会', '假期', '放假', '值班', '作息',
    '社会实践', '西部计划'
]

for keyword in exclude_keywords:
    if keyword in title or keyword in content:
        print(f"命中排除词: {keyword}")
