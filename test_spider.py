#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬虫
"""

from contesttrace.core.spiders import HBUFESpider
from contesttrace.core.utils import setup_logger

# 设置日志
logger = setup_logger()

# 测试爬虫
spider = HBUFESpider()

# 测试获取页面内容
url = "https://tw.hbue.edu.cn/31/list1.htm"
print(f"测试获取页面: {url}")
content = spider.fetch(url)

if content:
    print(f"成功获取页面，长度: {len(content)}")
    # 保存页面内容到文件
    with open('test_page.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("页面内容已保存到 test_page.html")
    
    # 测试解析列表页面
    print("\n测试解析列表页面...")
    detail_urls = spider.parse_list(content)
    print(f"成功解析出 {len(detail_urls)} 个详情页URL")
    for i, detail_url in enumerate(detail_urls[:5]):  # 只打印前5个
        print(f"{i+1}. {detail_url}")
    
    # 测试获取下一页
    print("\n测试获取下一页...")
    next_page = spider.get_next_page(content)
    print(f"下一页URL: {next_page}")
    
    # 测试解析详情页面
    if detail_urls:
        print("\n测试解析详情页面...")
        detail_url = detail_urls[0]  # 测试第一个详情页
        print(f"测试解析详情页: {detail_url}")
        detail_content = spider.fetch(detail_url)
        if detail_content:
            print(f"成功获取详情页，长度: {len(detail_content)}")
            # 保存详情页内容到文件
            with open('test_detail.html', 'w', encoding='utf-8') as f:
                f.write(detail_content)
            print("详情页内容已保存到 test_detail.html")
            
            # 解析详情页
            contest = spider.parse_detail(detail_content, detail_url)
            if contest:
                print("\n成功解析详情页，获取到竞赛信息:")
                print(f"标题: {contest.get('title', '未知')}")
                print(f"来源: {contest.get('source', '未知')}")
                print(f"发布时间: {contest.get('publish_time', '未知')}")
                print(f"关键词: {contest.get('keywords', [])}")
            else:
                print("解析详情页失败")
        else:
            print("获取详情页失败")
else:
    print("获取页面失败")
