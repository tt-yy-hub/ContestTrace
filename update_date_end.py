#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新所有爬虫文件的 DATE_END 设置为当前日期
"""

import os
import re
from pathlib import Path

# 爬虫目录
SPIDERS_DIR = Path("ContestTrace-main")

# 要修改的文件模式
SPIDER_FILES_PATTERN = "*_notice_spider.py"

# 匹配 DATE_END 行的正则表达式
DATE_END_PATTERN = r"DATE_END = date\(\d{4}, \d{1,2}, \d{1,2}\)"

# 替换为使用当前日期
REPLACEMENT = "DATE_END = date.today()"

# 遍历所有爬虫文件
def update_date_end():
    print("开始更新所有爬虫文件的 DATE_END 设置...")
    
    # 遍历所有子目录
    for subdir in SPIDERS_DIR.iterdir():
        if not subdir.is_dir():
            continue
        
        # 查找爬虫文件
        spider_files = list(subdir.glob(SPIDER_FILES_PATTERN))
        for spider_file in spider_files:
            print(f"处理文件: {spider_file}")
            
            # 读取文件内容
            try:
                with open(spider_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换 DATE_END 行
                new_content = re.sub(DATE_END_PATTERN, REPLACEMENT, content)
                
                # 检查是否有修改
                if new_content != content:
                    # 写回文件
                    with open(spider_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  [OK] 已更新 DATE_END 为 date.today()")
                else:
                    print(f"  [SKIP] 无需更新")
                    
            except Exception as e:
                print(f"  [ERROR] 处理失败: {e}")
    
    print("\n所有文件处理完成！")

if __name__ == "__main__":
    update_date_end()
