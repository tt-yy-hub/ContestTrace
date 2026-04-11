#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行队友的爬虫，将数据存储到对应的数据库文件中
"""

import os
import sys
import subprocess
from pathlib import Path

# 队友爬虫目录
TEAMMATE_SPIDER_DIR = Path("ContestTrace-main")

# 数据目录
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 运行单个爬虫
def run_spider(spider_dir, spider_name, db_file, spider_file):
    print(f"运行 {spider_name} 爬虫...")
    
    # 构建爬虫路径
    spider_path = TEAMMATE_SPIDER_DIR / spider_dir / spider_file
    print(f"爬虫文件路径: {spider_path}")
    
    # 构建数据库路径
    db_path = DATA_DIR / db_file
    print(f"数据库文件路径: {db_path}")
    
    # 检查爬虫文件是否存在
    if not spider_path.exists():
        print(f"爬虫文件不存在: {spider_path}")
        return
    
    # 运行爬虫
    try:
        # 构建命令
        cmd = [
            sys.executable,
            str(spider_path),
            "--mode", "full",
            "--db", str(db_path)
        ]
        print(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        # 检查结果
        if result.returncode == 0:
            print(f"{spider_name} 爬虫运行成功！")
        else:
            print(f"{spider_name} 爬虫运行失败，返回码: {result.returncode}")
            print(f"错误输出: {result.stderr}")
    except Exception as e:
        print(f"运行 {spider_name} 爬虫时出错: {e}")

# 主函数
def main():
    print("开始运行队友的爬虫...")
    
    # 运行教务处爬虫
    run_spider(
        "jiaowuchu",
        "教务处",
        "contest_trace_raw_教务处.db",
        "hbue_jwc_notice_spider.py"
    )
    
    print("测试爬虫运行完成！")

if __name__ == "__main__":
    main()
