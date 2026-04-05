#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复是否有效
"""

from contesttrace.core.parsers.filter import ContestFilter
from contesttrace.core.utils.common import normalize_date

# 测试筛选逻辑
def test_filter():
    print("测试筛选逻辑...")
    filter = ContestFilter()
    
    # 测试非竞赛内容
    test_cases = [
        ("关于开展三月主题团日活动的通知", "", False),
        ("关于开展经院的樱花征文活动的通知", "", False),
        ("关于举办湖北经济学院第三届浩然杯读书演讲大赛的通知", "", True),
        ("关于举办2025年经舞校园舞蹈大赛的预通知", "", True),
    ]
    
    for title, content, expected in test_cases:
        result = filter.is_contest(title, content)
        status = "OK" if result == expected else "FAIL"
        print(f"{status} {title} -> {result} (期望: {expected})")

# 测试日期解析
def test_date_normalization():
    print("\n测试日期解析...")
    test_cases = [
        ("11-17-04", "2004-11-17"),
        ("2024-04-11", "2024-04-11"),
        ("2024年4月11日", "2024-04-11"),
        ("4月11日", f"{datetime.now().year}-04-11"),
        ("即日起至4月11日17:00", f"{datetime.now().year}-04-11"),
        ("即日起至4月11日", f"{datetime.now().year}-04-11"),
    ]
    
    for date_str, expected in test_cases:
        result = normalize_date(date_str)
        status = "OK" if result == expected else "FAIL"
        print(f"{status} {date_str} -> {result} (期望: {expected})")

if __name__ == "__main__":
    from datetime import datetime
    test_filter()
    test_date_normalization()
    print("\n测试完成！")
