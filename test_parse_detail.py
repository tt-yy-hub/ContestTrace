#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 parse_detail 方法
"""

from bs4 import BeautifulSoup
import re

# 读取测试详情页内容
with open('test_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 解析页面
soup = BeautifulSoup(content, 'html.parser')

# 提取标题
title = ""
title_tag = soup.find('h1', class_='arti_title')
if title_tag:
    title = title_tag.get_text(strip=True)
print(f"标题: {title}")

# 提取发布时间
publish_time = ""
metas_tag = soup.find('p', class_='arti_metas')
if metas_tag:
    time_match = re.search(r'发布时间：(.*?)[\s|<]', metas_tag.get_text())
    if time_match:
        publish_time = time_match.group(1)
print(f"发布时间: {publish_time}")

# 提取内容
content_text = ""
read_tag = soup.find('div', class_='read')
if read_tag:
    content_tag = read_tag.find('div', class_='wp_articlecontent')
    if content_tag:
        content_text = content_tag.get_text(strip=True)
print(f"内容长度: {len(content_text)}")
print(f"内容前100个字符: {content_text[:100]}...")
