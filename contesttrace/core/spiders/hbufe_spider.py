#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
湖北经济学院团委官网爬虫
"""

import re
from bs4 import BeautifulSoup
from .base_spider import BaseSpider
from ..utils import normalize_date, extract_keywords
import logging

logger = logging.getLogger(__name__)


class HBUFESpider(BaseSpider):
    """
    湖北经济学院团委官网爬虫
    """
    
    def __init__(self):
        """
        初始化爬虫
        """
        super().__init__(
            name="湖北经济学院团委",
            base_url="https://tw.hbue.edu.cn/31/list1.htm"
        )
    
    def parse_list(self, content: str) -> list:
        """
        解析列表页面
        
        Args:
            content: 页面内容
        
        Returns:
            详情页URL列表
        """
        detail_urls = []
        
        try:
            logger.info("开始解析列表页面")
            # 保存页面内容到文件，以便调试
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("页面内容已保存到 debug_page.html")
            
            logger.info("创建BeautifulSoup对象")
            soup = BeautifulSoup(content, 'html.parser')
            
            # 打印页面标题，确认页面是否正确加载
            title_tag = soup.find('title')
            if title_tag:
                logger.info(f"页面标题: {title_tag.get_text()}")
            
            # 查找新闻列表 - 根据实际页面结构
            logger.info("查找新闻列表")
            news_list = soup.find('ul', class_='wp_article_list')
            if not news_list:
                logger.warning("未找到新闻列表")
                # 打印页面的前500个字符，以便了解页面结构
                logger.info(f"页面前500字符: {content[:500]}")
                return detail_urls
            
            # 查找所有新闻链接
            logger.info("查找所有新闻链接")
            items = news_list.find_all('li', class_='list_item')
            logger.info(f"找到 {len(items)} 个列表项")
            
            for i, item in enumerate(items):
                logger.info(f"处理列表项 {i+1}")
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
                        logger.info(f"找到链接: {detail_url}")
            
            logger.info(f"共找到 {len(detail_urls)} 个链接")
        except Exception as e:
            logger.error(f"解析列表页面失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return detail_urls
    
    def parse_detail(self, content: str, url: str) -> dict:
        """
        解析详情页面
        
        Args:
            content: 页面内容
            url: 详情页URL
        
        Returns:
            竞赛信息字典
        """
        try:
            logger.info(f"开始解析详情页面: {url}")
            soup = BeautifulSoup(content, 'html.parser')
            
            # 提取标题
            title = ""
            title_tag = soup.find('h1', class_='arti_title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                logger.info(f"提取标题: {title}")
            else:
                logger.warning("未找到标题")
            
            # 提取发布时间
            publish_time = ""
            metas_tag = soup.find('p', class_='arti_metas')
            if metas_tag:
                logger.info(f"提取发布时间: {metas_tag.get_text()}")
                time_match = re.search(r'发布时间：(\d{4}-\d{2}-\d{2})', metas_tag.get_text())
                if time_match:
                    publish_time = normalize_date(time_match.group(1))
                    logger.info(f"提取到发布时间: {publish_time}")
                else:
                    logger.warning("未找到发布时间")
            else:
                logger.warning("未找到发布时间标签")
            
            # 提取内容
            content_text = ""
            read_tag = soup.find('div', class_='read')
            if read_tag:
                content_tag = read_tag.find('div', class_='wp_articlecontent')
                if content_tag:
                    content_text = content_tag.get_text(strip=True)
                    logger.info(f"提取内容长度: {len(content_text)}")
                else:
                    logger.warning("未找到内容标签")
            else:
                logger.warning("未找到read标签")
            
            # 提取来源
            source = "湖北经济学院团委"
            
            # 提取关键词
            logger.info("提取关键词")
            keywords = extract_keywords(title + " " + content_text)
            logger.info(f"提取到关键词: {keywords}")
            
            # 构建竞赛信息字典
            contest = {
                'title': title,
                'url': url,
                'source': source,
                'publish_time': publish_time,
                'content': content_text,
                'keywords': keywords,
                'spider_name': self.name,
                'crawl_time': '',  # 会在后续处理中填充
                'deadline': '',  # 会在后续处理中提取
                'category': '',  # 会在后续处理中分类
                'organizer': '',  # 会在后续处理中提取
                'participants': '',  # 会在后续处理中提取
                'prize': '',  # 会在后续处理中提取
                'requirement': '',  # 会在后续处理中提取
                'contact': '',  # 会在后续处理中提取
                'summary': '',  # 会在后续处理中生成
                'tags': []  # 会在后续处理中生成
            }
            
            logger.info(f"成功解析详情页面: {title}")
            return contest
        except Exception as e:
            logger.error(f"解析详情页面失败: {url}, 错误: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}
    
    def get_next_page(self, content: str) -> str:
        """
        获取下一页URL
        
        Args:
            content: 当前页面内容
        
        Returns:
            下一页URL，为空表示没有下一页
        """
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找分页导航 - 根据实际页面结构
            pagination = soup.find('div', id='wp_paging_w6')
            if not pagination:
                return ""
            
            # 查找下一页链接
            next_page = pagination.find('a', class_='next')
            if next_page and 'href' in next_page.attrs:
                href = next_page['href']
                # 构建完整URL
                if href.startswith('http'):
                    return href
                else:
                    if href.startswith('/'):
                        return f"https://tw.hbue.edu.cn{href}"
                    else:
                        return f"https://tw.hbue.edu.cn/{href}"
        except Exception as e:
            logger.error(f"获取下一页失败: {e}")
        
        return ""
