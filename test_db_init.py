#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库初始化
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from contesttrace.core.storage.db_manager import DatabaseManager
from contesttrace.core.utils.common import ensure_directory

print("当前工作目录:", os.getcwd())
print("测试ensure_directory函数...")
test_dir = "test_data"
result = ensure_directory(test_dir)
print(f"ensure_directory结果: {result}")
print(f"目录是否存在: {os.path.exists(test_dir)}")

print("\n测试DatabaseManager初始化...")
db_manager = DatabaseManager()
print(f"原始数据库路径: {db_manager.raw_db_path}")
print(f"竞赛数据库路径: {db_manager.comp_db_path}")
print(f"原始数据库文件是否存在: {os.path.exists(db_manager.raw_db_path)}")
print(f"竞赛数据库文件是否存在: {os.path.exists(db_manager.comp_db_path)}")

print("\n测试完成")
