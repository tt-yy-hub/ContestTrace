#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 data 目录下所有数据库的 confidence 字段
"""

import sqlite3
import os

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入竞赛过滤器
from contesttrace.core.filter.competition_filter import CompetitionFilter

def update_database_confidence(db_path):
    """
    更新指定数据库中的 confidence 字段
    """
    try:
        # 初始化过滤器
        competition_filter = CompetitionFilter()
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取数据库中的表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        logger.info(f"处理数据库：{db_path}")
        
        for table in tables:
            table_name = table[0]
            # 跳过 sqlite_sequence 系统表
            if table_name == 'sqlite_sequence':
                continue
            
            # 检查表结构，确认是否包含 title 和 content 字段
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'title' in column_names and 'content' in column_names and 'confidence' in column_names:
                # 获取所有记录
                cursor.execute(f"SELECT id, title, content FROM {table_name};")
                records = cursor.fetchall()
                
                if records:
                    logger.info(f"  处理表 {table_name}，共 {len(records)} 条记录")
                    
                    # 更新每条记录的置信度
                    updated_count = 0
                    for record in records:
                        record_id, title, content = record
                        
                        # 计算置信度
                        _, confidence = competition_filter.is_contest(title, content)
                        
                        # 更新置信度
                        cursor.execute(f"UPDATE {table_name} SET confidence = ? WHERE id = ?", (confidence, record_id))
                        updated_count += 1
                        
                        if updated_count % 10 == 0:
                            logger.info(f"    已更新 {updated_count} 条记录")
                    
                    logger.info(f"  表 {table_name} 更新完成，共更新 {updated_count} 条记录")
                else:
                    logger.info(f"  表 {table_name} 无记录，跳过")
            else:
                logger.info(f"  表 {table_name} 缺少必要字段（title, content, confidence），跳过")
        
        # 提交事务
        conn.commit()
        conn.close()
        
        logger.info(f"数据库 {db_path} 更新完成")
        
    except Exception as e:
        logger.error(f"更新数据库 {db_path} 失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """
    主函数
    """
    # 遍历 data 目录下的所有数据库文件
    data_dir = 'data'
    db_files = [f for f in os.listdir(data_dir) if f.endswith('.db')]
    
    logger.info(f"找到 {len(db_files)} 个数据库文件")
    
    for db_file in db_files:
        db_path = os.path.join(data_dir, db_file)
        update_database_confidence(db_path)
    
    logger.info("所有数据库更新完成")

if __name__ == '__main__':
    main()
