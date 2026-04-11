#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 data/competiton.db 中的置信度值
"""

import sqlite3
import os

# 配置日志
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入竞赛过滤器
from contesttrace.core.filter.competition_filter import CompetitionFilter

def update_competiton_confidence():
    """
    更新 data/competiton.db 中的置信度值
    """
    try:
        # 初始化过滤器
        competition_filter = CompetitionFilter()
        
        # 连接数据库
        db_path = 'data/competiton.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有竞赛公告
        cursor.execute("SELECT id, title, content FROM competition_notices;")
        notices = cursor.fetchall()
        
        logger.info(f"找到 {len(notices)} 条竞赛公告")
        
        # 更新每条公告的置信度
        updated_count = 0
        for notice in notices:
            notice_id, title, content = notice
            
            # 计算置信度
            _, confidence = competition_filter.is_contest(title, content)
            
            # 更新置信度
            cursor.execute("UPDATE competition_notices SET confidence = ? WHERE id = ?", (confidence, notice_id))
            updated_count += 1
            
            if updated_count % 10 == 0:
                logger.info(f"已更新 {updated_count} 条公告的置信度")
        
        # 提交事务
        conn.commit()
        conn.close()
        
        logger.info(f"更新完成，共更新 {updated_count} 条公告的置信度")
        
    except Exception as e:
        logger.error(f"更新置信度失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """
    主函数
    """
    update_competiton_confidence()

if __name__ == '__main__':
    main()
