#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出模块
支持Excel/CSV格式导出
"""

import csv
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ContestExporter:
    """
    竞赛数据导出器
    """
    
    def __init__(self, output_dir: str = "data/exports"):
        """
        初始化导出器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def export_csv(self, contests: list, filename: str = "contests.csv") -> str:
        """
        导出为CSV格式
        
        Args:
            contests: 竞赛信息列表
            filename: 输出文件名
        
        Returns:
            输出文件路径
        """
        try:
            output_path = Path(self.output_dir) / filename
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 写入表头
                headers = [
                    '标题', '来源', '发布时间', '截止时间', '分类',
                    '组织者', '参赛对象', '奖项设置', '联系方式', '摘要', '链接'
                ]
                writer.writerow(headers)
                
                # 写入数据
                for contest in contests:
                    row = [
                        contest.get('title', ''),
                        contest.get('source', ''),
                        contest.get('publish_time', ''),
                        contest.get('deadline', ''),
                        contest.get('category', ''),
                        contest.get('organizer', ''),
                        contest.get('participants', ''),
                        contest.get('prize', ''),
                        contest.get('contact', ''),
                        contest.get('summary', ''),
                        contest.get('url', '')
                    ]
                    writer.writerow(row)
            
            logger.info(f"成功导出CSV文件: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"导出CSV失败: {e}")
            return ""
    
    def export_json(self, contests: list, filename: str = "contests.json") -> str:
        """
        导出为JSON格式（用于前端）
        
        Args:
            contests: 竞赛信息列表
            filename: 输出文件名
        
        Returns:
            输出文件路径
        """
        try:
            output_path = Path(self.output_dir) / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(contests, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功导出JSON文件: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"导出JSON失败: {e}")
            return ""
    
    def export_to_frontend(self, contests: list) -> str:
        """
        导出到前端数据目录
        
        Args:
            contests: 竞赛信息列表
        
        Returns:
            输出文件路径
        """
        try:
            # 前端数据目录
            frontend_data_dir = Path("contesttrace/frontend/data")
            frontend_data_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = frontend_data_dir / "contests.json"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(contests, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功导出前端数据: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"导出前端数据失败: {e}")
            return ""
