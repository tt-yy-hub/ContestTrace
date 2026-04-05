#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志模块
实现完整的日志系统，包括控制台和文件双输出，按天分割，自动清理7天前日志
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import shutil
from datetime import datetime, timedelta


def setup_logger(log_dir: str = "logs") -> logging.Logger:
    """
    设置日志系统
    
    Args:
        log_dir: 日志目录
    
    Returns:
        配置好的logger实例
    """
    # 确保日志目录存在
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 清理7天前的日志
    cleanup_old_logs(log_path)
    
    # 创建logger
    logger = logging.getLogger("ContestTrace")
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加handler
    if logger.handlers:
        logger.handlers.clear()
    
    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件handler（按天分割）
    file_handler = TimedRotatingFileHandler(
        str(log_path / "contesttrace.log"),
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def cleanup_old_logs(log_dir: Path):
    """
    清理7天前的日志文件
    
    Args:
        log_dir: 日志目录
    """
    try:
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        for file_path in log_dir.iterdir():
            if file_path.is_file() and file_path.name.endswith('.log'):
                # 检查是否是日期后缀的日志文件
                if '.' in file_path.name and file_path.name.split('.')[-2].isdigit():
                    try:
                        # 尝试解析日期
                        date_str = file_path.name.split('.')[-2]
                        log_date = datetime.strptime(date_str, '%Y-%m-%d')
                        if log_date < seven_days_ago:
                            file_path.unlink()
                            print(f"清理过期日志: {file_path}")
                    except ValueError:
                        pass
    except Exception as e:
        print(f"清理日志时出错: {e}")
