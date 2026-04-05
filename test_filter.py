#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 ContestFilter 类
"""

from contesttrace.core.parsers import ContestFilter

# 初始化过滤器
filter = ContestFilter()

# 测试案例
test_cases = [
    # 竞赛内容
    (
        "关于举办湖北经济学院第三届\"浩然杯\" 读书演讲大赛的通知",
        "为丰富校园文化生活，提高学生的演讲能力，我校决定举办第三届\"浩然杯\"读书演讲大赛。",
        True  # 应该被判定为竞赛
    ),
    # 非竞赛内容
    (
        "湖北经济学院2025年度\"优秀学院学生会\"评选名单公示",
        "根据湖北经济学院2025年度\"优秀学院学生会\"评审工作安排，经各学院学生会自评、学生民主评议及述职交流会评审，共评选出7个学院为2025年度\"优秀学院学生会\"。",
        False  # 应该被判定为非竞赛
    ),
    # 竞赛内容
    (
        "关于开展2026年大学生科研\"跬步计划\"项目评选工作的通知",
        "为鼓励学生参与科研活动，我校决定开展2026年大学生科研\"跬步计划\"项目评选工作。",
        False  # 应该被判定为非竞赛，因为包含"跬步计划"
    ),
    # 竞赛内容
    (
        '关于举办2026年"挑战杯"大学生创业计划竞赛校级选拔赛的通知',
        '为选拔优秀作品参加全国"挑战杯"大学生创业计划竞赛，我校决定举办校级选拔赛。',
        True  # 应该被判定为竞赛
    )
]

# 运行测试
for i, (title, content, expected) in enumerate(test_cases):
    # 调试信息
    print(f"测试案例 {i+1}:")
    print(f"标题: {title}")
    print(f"'竞赛' in 标题: {'竞赛' in title}")
    print(f"'大赛' in 标题: {'大赛' in title}")
    print(f"'挑战杯' in 标题: {'挑战杯' in title}")
    
    result = filter.is_contest(title, content)
    print(f"期望结果: {expected}")
    print(f"实际结果: {result}")
    print(f"测试 {'通过' if result == expected else '失败'}")
    print()
