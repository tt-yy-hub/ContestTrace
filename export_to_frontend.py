#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从data\competiton.db导出数据到前端需要的JSON格式
"""

import os
import sqlite3
import json

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def export_to_frontend():
    """
    从data\competiton.db导出数据到前端需要的JSON格式
    """
    # 数据库路径
    db_path = os.path.join('data', 'competiton.db')
    
    # 检查数据库是否存在
    if not os.path.exists(db_path):
        logger.error(f"数据库不存在: {db_path}")
        return
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询所有竞赛通知
    cursor.execute('SELECT * FROM competition_notices')
    rows = cursor.fetchall()
    
    # 获取列名
    column_names = [description[0] for description in cursor.description]
    
    # 转换为JSON格式
    contests = []
    for row in rows:
        contest = dict(zip(column_names, row))
        # 处理字段名，确保与前端代码匹配
        contest['url'] = contest.get('notice_url', '')
        contest['source_department'] = contest.get('publisher', '')
        contest['sign_up_deadline'] = contest.get('deadline', '')
        # 确保包含前端需要的所有字段
        contest['category'] = contest.get('category', '其他竞赛')
        contest['summary'] = contest.get('summary', '')
        contest['keywords'] = contest.get('keywords', [])
        contest['tags'] = contest.get('tags', '')
        contest['competition_level'] = contest.get('competition_level', '未知等级')
        contests.append(contest)
    
    # 关闭连接
    conn.close()
    
    # 创建前端数据目录
    frontend_data_dir = os.path.join('contesttrace', 'frontend', 'data')
    os.makedirs(frontend_data_dir, exist_ok=True)
    
    # 导出到JSON文件
    export_path = os.path.join(frontend_data_dir, 'contests.json')
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(contests, f, ensure_ascii=False, indent=2)
    
    logger.info(f"导出完成，共导出 {len(contests)} 条竞赛通知到 {export_path}")
    return export_path

if __name__ == '__main__':
    export_to_frontend()
