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
            # 获取当前文件的绝对路径，然后构建前端数据目录的绝对路径
            current_dir = Path(__file__).resolve().parent.parent.parent.parent
            logger.info(f"当前工作目录: {current_dir}")
            
            # 前端数据目录
            frontend_data_dir = current_dir / "contesttrace" / "frontend" / "data"
            logger.info(f"前端数据目录: {frontend_data_dir}")
            
            # 确保目录存在
            frontend_data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"前端数据目录已确保存在: {frontend_data_dir}")
            
            # 处理竞赛数据，映射字段并添加缺失的字段
            processed_contests = []
            for contest in contests:
                # 映射字段
                processed_contest = {
                    'id': contest.get('id') or contest.get('raw_notice_id') or 0,
                    'title': contest.get('title') or '无标题',
                    'url': contest.get('url') or contest.get('notice_url') or '',
                    'source': contest.get('source') or contest.get('source_department') or '未知来源',
                    'publish_time': contest.get('publish_time') or '2025-01-01',
                    'deadline': contest.get('deadline') or '未知',
                    'category': contest.get('category') or '其他竞赛',
                    'organizer': contest.get('organizer') or '未知',
                    'participants': contest.get('participants') or '全体学生',
                    'prize': contest.get('prize') or '未知',
                    'requirement': contest.get('requirement') or '',
                    'contact': contest.get('contact') or '未知',
                    'content': contest.get('content') or '无详细内容',
                    'summary': contest.get('summary') or (contest.get('content') and contest.get('content')[:100] + '...') or '无摘要',
                    'keywords': contest.get('keywords') or [],
                    'tags': contest.get('tags') or [],
                    'spider_name': contest.get('spider_name') or contest.get('source_department') or '未知'
                }
                processed_contests.append(processed_contest)
            
            # 导出 JSON 文件
            output_path = frontend_data_dir / "contests.json"
            logger.info(f"导出 JSON 文件到: {output_path}")
            
            # 写入 JSON 文件
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(processed_contests, f, ensure_ascii=False, indent=2)
                logger.info(f"成功导出 JSON 文件: {output_path}")
                logger.info(f"JSON 文件大小: {output_path.stat().st_size} 字节")
                logger.info(f"处理后的数据条数: {len(processed_contests)}")
            except Exception as json_error:
                logger.error(f"导出 JSON 文件失败: {json_error}")
                import traceback
                logger.error(traceback.format_exc())
                return ""
            
            # 导出 JavaScript 文件，用于将数据保存到 localStorage
            js_output_path = frontend_data_dir / "init_data.js"
            logger.info(f"导出 JavaScript 文件到: {js_output_path}")
            
            # 生成 JavaScript 代码，使用 JSON.parse 来解析数据
            js_content = "// 初始化数据到 localStorage\n"
            js_content += "if (!localStorage.getItem('contest_data')) {\n"
            js_content += "    // 从 contests.json 加载数据\n"
            js_content += "    fetch('data/contests.json')\n"
            js_content += "        .then(response => response.json())\n"
            js_content += "        .then(data => {\n"
            js_content += "            localStorage.setItem('contest_data', JSON.stringify(data));\n"
            js_content += "            console.log('数据已初始化到 localStorage');\n"
            js_content += "        })\n"
            js_content += "        .catch(error => {\n"
            js_content += "            console.error('加载数据失败:', error);\n"
            js_content += "        });\n"
            js_content += "}\n"
            
            # 写入 JavaScript 文件
            try:
                with open(js_output_path, 'w', encoding='utf-8') as f:
                    f.write(js_content)
                logger.info(f"成功导出初始化数据脚本: {js_output_path}")
                logger.info(f"JavaScript 文件大小: {js_output_path.stat().st_size} 字节")
            except Exception as js_error:
                logger.error(f"导出 JavaScript 文件失败: {js_error}")
                import traceback
                logger.error(traceback.format_exc())
                return ""
            
            # 验证文件是否存在
            if js_output_path.exists():
                logger.info(f"初始化数据脚本文件已存在: {js_output_path}")
            else:
                logger.error(f"初始化数据脚本文件不存在: {js_output_path}")
            
            return str(output_path)
        except Exception as e:
            logger.error(f"导出前端数据失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return ""
