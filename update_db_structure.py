#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新数据库表结构，添加详细字段
"""

import sqlite3
import os
from contesttrace.core.utils.data_processor import DataProcessor

def update_db_structure():
    """
    更新数据库表结构，添加详细字段
    """
    try:
        # 连接竞赛公告数据库
        conn = sqlite3.connect('data/contest_trace_competition.db')
        cursor = conn.cursor()
        
        # 检查是否已存在详细字段
        cursor.execute('PRAGMA table_info(competition_notices)')
        columns = [row[1] for row in cursor.fetchall()]
        
        # 添加缺失的字段
        fields = ['deadline', 'organizer', 'participants', 'prize', 'requirement', 'contact', 'category']
        for field in fields:
            if field not in columns:
                cursor.execute(f'ALTER TABLE competition_notices ADD COLUMN {field} TEXT')
                print(f'添加字段: {field}')
        
        conn.commit()
        conn.close()
        print('数据库表结构更新成功')
        
    except Exception as e:
        print(f'更新数据库表结构失败: {e}')

def update_existing_data():
    """
    更新现有数据，提取详细字段
    """
    try:
        # 连接竞赛公告数据库
        conn = sqlite3.connect('data/contest_trace_competition.db')
        cursor = conn.cursor()
        
        # 查询所有竞赛公告
        cursor.execute('SELECT id, title, content FROM competition_notices')
        notices = cursor.fetchall()
        
        # 创建数据处理器
        data_processor = DataProcessor()
        
        # 更新每条竞赛公告的详细字段
        for notice in notices:
            notice_id, title, content = notice
            # 模拟竞赛数据字典
            contest = {
                'id': notice_id,
                'title': title,
                'content': content
            }
            # 处理数据
            processed_contest = data_processor.process_contest(contest)
            # 更新数据库
            cursor.execute('''
                UPDATE competition_notices 
                SET deadline = ?, organizer = ?, participants = ?, prize = ?, requirement = ?, contact = ?, category = ?
                WHERE id = ?
            ''', (
                processed_contest.get('deadline', ''),
                processed_contest.get('organizer', ''),
                processed_contest.get('participants', ''),
                processed_contest.get('prize', ''),
                processed_contest.get('requirement', ''),
                processed_contest.get('contact', ''),
                processed_contest.get('category', '其他竞赛'),
                notice_id
            ))
        
        conn.commit()
        conn.close()
        print(f'更新了 {len(notices)} 条竞赛公告数据')
        
    except Exception as e:
        print(f'更新现有数据失败: {e}')

def main():
    """
    主函数
    """
    print('开始更新数据库表结构...')
    update_db_structure()
    print('开始更新现有数据...')
    update_existing_data()
    print('更新完成！')

if __name__ == '__main__':
    main()
