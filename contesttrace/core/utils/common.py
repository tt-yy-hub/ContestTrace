#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具模块
包含文件操作、时间处理等常用功能
"""

import os
import re
from pathlib import Path
from datetime import datetime, timedelta
import json
import random
import time


def ensure_directory(path: str) -> Path:
    """
    确保目录存在
    
    Args:
        path: 目录路径
    
    Returns:
        Path对象
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_json(file_path: str) -> dict:
    """
    读取JSON文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        JSON数据
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取JSON文件失败: {e}")
        return {}


def write_json(file_path: str, data: dict):
    """
    写入JSON文件
    
    Args:
        file_path: 文件路径
        data: 要写入的数据
    """
    try:
        # 确保目录存在
        ensure_directory(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"写入JSON文件失败: {e}")


def normalize_date(date_str: str) -> str:
    """
    时间格式归一化
    
    Args:
        date_str: 时间字符串
    
    Returns:
        归一化后的时间字符串 (YYYY-MM-DD)
    """
    if not date_str:
        return ""
    
    # 尝试多种日期格式
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y年%m月%d日',
        '%m-%d-%Y',
        '%m/%d/%Y',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%Y年%m月',
        '%Y.%m.%d',
        '%Y年%m月%d日 %H:%M',
        '%Y-%m-%d %H:%M',
        '%Y/%m/%d %H:%M',
        '%m-%d-%y',  # 处理 MM-DD-YY 格式
        '%d-%m-%y',  # 处理 DD-MM-YY 格式
        '%y-%m-%d'   # 处理 YY-MM-DD 格式
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            pass
    
    # 处理只有月日的情况，如 "4月11日"
    month_day_pattern = r'(\d+)月(\d+)日'
    match = re.search(month_day_pattern, date_str)
    if match:
        try:
            month = match.group(1)
            day = match.group(2)
            current_year = str(datetime.now().year)
            return f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
        except Exception:
            pass
    
    # 尝试提取数字
    digits = re.findall(r'\d+', date_str)
    if len(digits) >= 3:
        try:
            # 假设是年月日
            if len(digits[0]) == 4:
                # YYYY-MM-DD
                return f"{digits[0]}-{digits[1].zfill(2)}-{digits[2].zfill(2)}"
            elif len(digits[2]) == 4:
                # MM-DD-YYYY
                return f"{digits[2]}-{digits[0].zfill(2)}-{digits[1].zfill(2)}"
            else:
                # 处理其他格式，如 DD-MM-YY 或 MM-DD-YY
                current_year = str(datetime.now().year)
                current_century = current_year[:2]
                if len(digits) == 3 and len(digits[2]) == 2:
                    # 假设是 DD-MM-YY 或 MM-DD-YY
                    year = current_century + digits[2]
                    if int(digits[0]) <= 12:
                        # 假设是 MM-DD-YY
                        return f"{year}-{digits[0].zfill(2)}-{digits[1].zfill(2)}"
                    else:
                        # 假设是 DD-MM-YY
                        return f"{year}-{digits[1].zfill(2)}-{digits[0].zfill(2)}"
                # 处理 YYYYMMDD 格式
                elif len(digits) == 1 and len(digits[0]) == 8:
                    year = digits[0][:4]
                    month = digits[0][4:6]
                    day = digits[0][6:8]
                    return f"{year}-{month}-{day}"
        except Exception:
            pass
    elif len(digits) == 2:
        try:
            # 假设是月日，添加当前年份
            current_year = str(datetime.now().year)
            return f"{current_year}-{digits[0].zfill(2)}-{digits[1].zfill(2)}"
        except Exception:
            pass
    
    # 处理特殊格式，如 "4月11日17:00"
    month_day_pattern = r'(\d+)月(\d+)日'
    match = re.search(month_day_pattern, date_str)
    if match:
        try:
            month = match.group(1)
            day = match.group(2)
            current_year = str(datetime.now().year)
            return f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
        except Exception:
            pass
    
    # 处理只有月日的情况，如 "4月11日"
    if len(digits) == 2:
        try:
            # 假设是月日，添加当前年份
            current_year = str(datetime.now().year)
            return f"{current_year}-{digits[0].zfill(2)}-{digits[1].zfill(2)}"
        except Exception:
            pass
    
    # 处理 "即日起至4月11日17:00" 格式
    即日起_pattern = r'即日起至(.*?)[\s:：]'
    match = re.search(即日起_pattern, date_str)
    if match:
        return normalize_date(match.group(1))
    
    # 处理 "即日起至4月11日" 格式（无时间部分）
    即日起_pattern2 = r'即日起至(.*)'
    match = re.search(即日起_pattern2, date_str)
    if match:
        return normalize_date(match.group(1))
    
    return ""


def random_delay(min_seconds: float = 1.5, max_seconds: float = 3.5):
    """
    随机延时
    
    Args:
        min_seconds: 最小延时秒数
        max_seconds: 最大延时秒数
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def get_user_agent() -> str:
    """
    获取随机User-Agent
    
    Returns:
        User-Agent字符串
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'
    ]
    return random.choice(user_agents)


def extract_keywords(text: str, max_keywords: int = 10) -> list:
    """
    提取关键词
    
    Args:
        text: 文本内容
        max_keywords: 最大关键词数量
    
    Returns:
        关键词列表
    """
    if not text:
        return []
    
    # 简单的关键词提取逻辑
    # 实际项目中可以使用更复杂的算法
    try:
        import jieba
        
        # 使用jieba分词
        words = jieba.cut(text)
        
        # 过滤停用词
        stop_words = set([
            '的', '了', '和', '与', '或', '是', '在', '有', '为', '以', '我们', '你们', '他们',
            '这个', '那个', '这些', '那些', '然后', '但是', '因为', '所以', '如果', '虽然',
            '然而', '因此', '此外', '另外', '同时', '并且', '而且', '或者', '不过', '可是'
        ])
        
        # 统计词频
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 1:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按词频排序，返回前max_keywords个
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_keywords]]
    except Exception as e:
        print(f"关键词提取失败: {e}")
        return []
