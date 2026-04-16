#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行队友的爬虫，将数据存储到对应的数据库文件中
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

# 队友爬虫目录
TEAMMATE_SPIDER_DIR = Path("ContestTrace-main")

# 数据目录
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 检查链接是否已存在于数据库
def is_url_exists(db_path, url):
    """检查URL是否已存在于数据库中"""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notices';")
        if cursor.fetchone():
            # 检查URL是否存在
            cursor.execute("SELECT COUNT(*) FROM notices WHERE url = ?", (url,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        conn.close()
        return False
    except Exception as e:
        print(f"检查URL是否存在时出错: {e}")
        return False

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
            "--mode", "incremental",  # 使用增量模式，只爬取新增的
            "--db", str(db_path)
        ]
        print(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=False,  # 直接输出到控制台，这样可以看到详细的爬虫输出
            text=True
        )
        
        # 检查结果
        if result.returncode == 0:
            print(f"{spider_name} 爬虫运行成功！")
        else:
            print(f"{spider_name} 爬虫运行失败，返回码: {result.returncode}")
    except Exception as e:
        print(f"运行 {spider_name} 爬虫时出错: {e}")

# 主函数
def main():
    print("开始运行队友的爬虫...")
    
    # 爬虫配置列表
    spiders = [
        # 运行教务处爬虫
        ("jiaowuchu", "教务处", "contest_trace_raw_教务处.db", "hbue_jwc_notice_spider.py"),
        # 运行实验教学中心爬虫
        ("shiyanjiaoxue", "实验教学中心", "contest_trace_raw_实验教学中心.db", "hbue_etc_notice_spider.py"),
        # 运行统计与数学学院爬虫
        ("tongshu", "统计与数学学院", "contest_trace_raw_统计与数学学院.db", "hbue_tsxy_notice_spider.py"),
        # 运行工商管理学院爬虫
        ("gongshang", "工商管理学院", "contest_trace_raw_工商管理学院.db", "hbue_gsxy_notice_spider.py"),
        # 运行经济与贸易学院爬虫
        ("jingmaoxueyuan", "经济与贸易学院", "contest_trace_raw_经济与贸易学院.db", "hbue_jmxy_notice_spider.py"),
        # 运行金融学院爬虫
        ("jingrongxueyuan", "金融学院", "contest_trace_raw_金融学院.db", "hbue_jrxy_notice_spider.py"),
        # 运行会计学院爬虫
        ("kuaiji", "会计学院", "contest_trace_raw_会计学院.db", "hbue_kjxy_notice_spider.py"),
        # 运行旅游与酒店管理学院爬虫
        ("lvyoujiudian", "旅游与酒店管理学院", "contest_trace_raw_旅游与酒店管理学院.db", "hbue_lyxy_notice_spider.py"),
        # 运行外国语学院爬虫
        ("waiguoyu", "外国语学院", "contest_trace_raw_外国语学院.db", "hbue_jmxy_notice_spider.py"),
        # 运行湖北经济学院团委爬虫
        ("xiaotuanwei", "湖北经济学院团委", "contest_trace_raw_湖北经济学院团委.db", "hbue_tw_notice_spider.py"),
        # 运行信息管理学院爬虫
        ("xinguan", "信息管理学院", "contest_trace_raw_信息管理学院.db", "hbue_xgxy_notice_spider.py"),
        # 运行新闻与传播学院爬虫
        ("xinwenyuchuanbo", "新闻与传播学院", "contest_trace_raw_新闻与传播学院.db", "hbue_jmxy_notice_spider.py"),
        # 运行信息工程学院爬虫
        ("xinxigongcheng", "信息工程学院", "contest_trace_raw_信息工程学院.db", "hbue_ie_notice_spider.py"),
        # 运行学生工作处爬虫
        ("xueshenggongzuochu", "学生工作处", "contest_trace_raw_学生工作处.db", "hbue_xgc_notice_spider.py"),
        # 运行艺术学院爬虫
        ("yishusheji", "艺术学院", "contest_trace_raw_艺术学院.db", "hbue_ysxy_notice_spider.py"),
    ]
    
    # 运行所有爬虫
    for spider_config in spiders:
        run_spider(*spider_config)
    
    print("所有爬虫运行完成！")

if __name__ == "__main__":
    main()
