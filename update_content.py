#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 data\contest_trace_raw_实验教学中心.db 中获取三条公告的内容，然后更新 data\contest_trace_raw.db 中对应的记录
"""

import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 数据目录
DATA_DIR = Path("data")

# 原始数据库路径
RAW_DB = DATA_DIR / "contest_trace_raw.db"

# 实验教学中心数据库路径
ETC_DB = DATA_DIR / "contest_trace_raw_实验教学中心.db"

def update_content():
    """
    从 data\contest_trace_raw_实验教学中心.db 中获取三条公告的内容，然后更新 data\contest_trace_raw.db 中对应的记录
    """
    logger.info("开始更新公告内容...")
    
    # 确保数据目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 检查数据库是否存在
    if not RAW_DB.exists():
        logger.error(f"原始数据库 {RAW_DB} 不存在")
        return
    
    if not ETC_DB.exists():
        logger.error(f"实验教学中心数据库 {ETC_DB} 不存在")
        return
    
    # 连接实验教学中心数据库
    etc_conn = sqlite3.connect(ETC_DB)
    etc_cursor = etc_conn.cursor()
    
    # 连接原始数据库
    raw_conn = sqlite3.connect(RAW_DB)
    raw_cursor = raw_conn.cursor()
    
    try:
        # 从实验教学中心数据库获取三条公告的内容
        etc_cursor.execute('SELECT id, title, content FROM raw_notices WHERE id IN (1, 2, 3)')
        etc_rows = etc_cursor.fetchall()
        
        # 创建标题到内容的映射
        content_map = {}
        for row in etc_rows:
            title = row[1]
            content = row[2]
            content_map[title] = content
        
        logger.info(f"从实验教学中心数据库获取到 {len(content_map)} 条公告内容")
        
        # 更新原始数据库中的对应记录
        update_count = 0
        
        # 对应关系
        mappings = [
            (402, '2025年中国大学生工程实践与创新能力大赛虚拟仿真赛道企业运营仿真赛项校赛成功举行'),
            (403, '2025年全国企业竞争模拟大赛湖北经济学院校赛通知'),
            (404, '第十二届湖北省高校企业竞争模拟大赛校赛成功举行')
        ]
        
        for raw_id, title in mappings:
            if title in content_map:
                content = content_map[title]
                
                # 更新记录
                raw_cursor.execute('''
                UPDATE raw_notices 
                SET content = ? 
                WHERE id = ?
                ''', (content, raw_id))
                
                if raw_cursor.rowcount > 0:
                    update_count += 1
                    logger.info(f"更新记录 ID: {raw_id} 成功")
                else:
                    logger.warning(f"记录 ID: {raw_id} 未找到")
            else:
                logger.warning(f"标题 '{title}' 未在实验教学中心数据库中找到")
        
        # 提交事务
        raw_conn.commit()
        logger.info(f"更新完成！共更新 {update_count} 条记录")
    except Exception as e:
        logger.error(f"更新内容失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raw_conn.rollback()
    finally:
        etc_conn.close()
        raw_conn.close()

if __name__ == "__main__":
    update_content()
