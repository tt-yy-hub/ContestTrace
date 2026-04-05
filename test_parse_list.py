#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 parse_list 方法
"""

from bs4 import BeautifulSoup
import re

# 读取测试页面内容
with open('test_page.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 解析页面
soup = BeautifulSoup(content, 'html.parser')

# 查找新闻列表 - 根据实际页面结构
news_list = soup.find('ul', class_='wp_article_list')
print(f"新闻列表是否找到: {news_list is not None}")

if news_list:
    # 查找所有新闻链接
    detail_urls = []
    for item in news_list.find_all('li', class_='list_item'):
        title_span = item.find('span', class_='Article_Title')
        if title_span:
            a_tag = title_span.find('a')
            if a_tag and 'href' in a_tag.attrs:
                href = a_tag['href']
                # 构建完整URL
                if href.startswith('http'):
                    detail_url = href
                else:
                    # 处理相对路径
                    if href.startswith('/'):
                        detail_url = f"https://tw.hbue.edu.cn{href}"
                    else:
                        detail_url = f"https://tw.hbue.edu.cn/{href}"
                detail_urls.append(detail_url)
                print(f"找到链接: {detail_url}")
    
    print(f"共找到 {len(detail_urls)} 个链接")
else:
    print("未找到新闻列表")
