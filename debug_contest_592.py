#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试ID: 592的竞赛通知
"""

import sqlite3
import logging
from contesttrace.core.filter.competition_filter import CompetitionFilter

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_contest_592():
    """
    调试ID: 592的竞赛通知
    """
    # 连接数据库
    conn = sqlite3.connect('data/contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 初始化过滤器
    filter = CompetitionFilter()
    
    # 从数据库中获取ID: 592的通知
    cursor.execute("SELECT id, title, content FROM raw_notices WHERE id = ?", (592,))
    row = cursor.fetchone()
    
    if row:
        notice_id, title, content = row
        print(f"\n调试 ID {notice_id}: {title}")
        print("=" * 80)
        print(f"标题: {title}")
        print(f"内容: {content}")
        
        # 测试筛选
        is_contest = filter.is_contest(title, content)
        print(f"筛选结果: {'通过' if is_contest else '失败'}")
    else:
        print("\nID 592: 未找到")
    
    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    debug_contest_592()
