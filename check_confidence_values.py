#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查竞赛数据库中的置信度值
"""

import sqlite3
import os

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_confidence_values(db_path):
    """
    检查指定数据库中的置信度值
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取竞赛公告表中的置信度值
        cursor.execute("SELECT id, title, confidence FROM competition_notices LIMIT 10;")
        rows = cursor.fetchall()
        
        logger.info(f"检查数据库：{db_path}")
        logger.info(f"前 10 条记录的置信度值：")
        
        for row in rows:
            logger.info(f"ID: {row[0]}, 标题: {row[1][:50]}..., 置信度: {row[2]}")
        
        # 统计置信度分布
        cursor.execute("SELECT MIN(confidence), MAX(confidence), AVG(confidence) FROM competition_notices;")
        stats = cursor.fetchone()
        if stats:
            logger.info(f"置信度统计：最小值: {stats[0]}, 最大值: {stats[1]}, 平均值: {stats[2]:.2f}")
        
        conn.close()
    except Exception as e:
        logger.error(f"处理 {db_path} 时出错：{str(e)}")

def main():
    """
    检查竞赛数据库中的置信度值
    """
    # 检查主竞赛数据库
    db_files = [
        'data/contest_trace_competition.db',
        'data/competiton.db'
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            check_confidence_values(db_file)
        else:
            logger.error(f"数据库文件不存在：{db_file}")

if __name__ == '__main__':
    main()
