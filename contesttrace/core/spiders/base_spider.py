#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫基类
定义通用爬虫功能
"""

import requests
from abc import ABC, abstractmethod
from ..utils import smart_decode, random_delay, get_user_agent
import logging

logger = logging.getLogger(__name__)


class BaseSpider(ABC):
    """
    爬虫基类
    """
    
    def __init__(self, name: str, base_url: str):
        """
        初始化爬虫
        
        Args:
            name: 爬虫名称
            base_url: 基础URL
        """
        self.name = name
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = {
            'User-Agent': get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
    
    def fetch(self, url: str, max_retries: int = 3) -> str:
        """
        获取页面内容
        
        Args:
            url: 页面URL
            max_retries: 最大重试次数
        
        Returns:
            页面内容
        """
        for i in range(max_retries):
            try:
                self.headers['User-Agent'] = get_user_agent()
                response = self.session.get(url, headers=self.headers, timeout=10)  # 减少超时时间，提高执行速度
                if response.status_code >= 400:
                    logger.error(f"获取页面失败，状态码: {response.status_code}, URL: {url}")
                    if i < max_retries - 1:
                        random_delay(1, 2)  # 减少延时时间，提高执行速度
                        continue
                    else:
                        return ""
                response.raise_for_status()
                content = smart_decode(response.content)
                # 随机延时，合规反爬
                random_delay(0.5, 1.5)  # 减少延时时间，提高执行速度
                return content
            except Exception as e:
                if i < max_retries - 1:
                    random_delay(1, 2)  # 减少延时时间，提高执行速度
                else:
                    logger.error(f"最终获取页面失败: {url}, 错误: {e}")
                    return ""
    
    @abstractmethod
    def parse_list(self, content: str) -> list:
        """
        解析列表页面
        
        Args:
            content: 页面内容
        
        Returns:
            详情页URL列表
        """
        pass
    
    @abstractmethod
    def parse_detail(self, content: str, url: str) -> dict:
        """
        解析详情页面
        
        Args:
            content: 页面内容
            url: 详情页URL
        
        Returns:
            竞赛信息字典
        """
        pass
    
    @abstractmethod
    def get_next_page(self, content: str, current_url: str) -> str:
        """
        获取下一页URL
        
        Args:
            content: 当前页面内容
            current_url: 当前页面URL
        
        Returns:
            下一页URL，为空表示没有下一页
        """
        pass
    
    def crawl(self) -> list:
        """
        执行爬虫
        
        Returns:
            竞赛信息列表
        """
        logger.info(f"开始爬取 {self.name}")
        
        all_contests = []
        current_url = self.base_url
        page_count = 0
        max_pages = 500  # 增加爬取深度，确保覆盖所有页面
        consecutive_no_result_pages = 0  # 连续无结果页数
        total_valid_notices = 0  # 累计成功入库的公告数量
        
        try:
            while current_url and page_count < max_pages and consecutive_no_result_pages < 3:
                page_count += 1
                logger.info(f"正在爬取第 {page_count} 页")
                
                content = self.fetch(current_url)
                
                if not content:
                    logger.error(f"无法获取页面内容: {current_url}")
                    break
                
                # 解析列表页面，获取详情页URL
                detail_urls = self.parse_list(content)
                logger.info(f"找到 {len(detail_urls)} 个公告链接")
                
                page_valid_notices = 0  # 当前页面有效公告数量
                
                # 解析详情页，一旦遇到2025年之前的公告，停止处理当前页面的后续链接
                logger.info(f"开始解析 {len(detail_urls)} 个详情页")
                stop_processing = False  # 标记是否停止处理当前页面的后续链接
                for i, detail_url in enumerate(detail_urls):
                    if stop_processing:
                        logger.info(f"遇到2025年之前的公告，停止处理当前页面的后续链接")
                        break
                    
                    logger.info(f"正在解析第 {i+1}/{len(detail_urls)} 个详情页: {detail_url}")
                    try:
                        # 过滤无效链接
                        if 'main.htm' in detail_url or 'index.html' in detail_url:
                            logger.info(f"跳过无效链接: {detail_url}")
                            continue
                        
                        detail_content = self.fetch(detail_url)
                        if detail_content:
                            # 解析详情页，获取竞赛信息
                            contest = self.parse_detail(detail_content, detail_url)
                            
                            # 确保contest是一个字典
                            if not isinstance(contest, dict):
                                logger.info(f"解析详情页返回非字典类型: {type(contest)}")
                                contest = {}
                            
                            # 确保必要字段存在，即使为空
                            contest.setdefault('url', detail_url)
                            contest.setdefault('title', '无标题')
                            contest.setdefault('source', self.name)
                            contest.setdefault('publish_time', '2025-01-01')
                            contest.setdefault('content', detail_content)  # 确保存储全文
                            contest.setdefault('deadline', '')  # 确保有截止日期字段
                            contest.setdefault('raw_html', detail_content)  # 存储原始HTML
                            
                            # 过滤无效公告
                            title = contest.get('title', '')
                            if not title or title.strip() == '':
                                logger.info(f"跳过无标题公告: {detail_url}")
                                continue
                            
                            # 检查发布时间是否在2025.1.1及以后
                            publish_time = contest.get('publish_time')
                            if publish_time:
                                try:
                                    # 解析发布时间为日期对象
                                    from datetime import datetime
                                    publish_date = datetime.strptime(publish_time, '%Y-%m-%d')
                                    # 检查是否在2025.1.1及以后
                                    if publish_date >= datetime(2025, 1, 1):
                                        all_contests.append(contest)
                                        page_valid_notices += 1
                                        total_valid_notices += 1
                                        logger.info(f"添加有效公告: {title}")
                                    else:
                                        # 遇到2025年之前的公告，停止处理当前页面的后续链接
                                        logger.info(f"遇到2025年之前的公告，停止处理当前页面的后续链接: {title}")
                                        stop_processing = True
                                except Exception as e:
                                    # 发布时间解析失败，使用默认值
                                    contest['publish_time'] = '2025-01-01'
                                    all_contests.append(contest)
                                    page_valid_notices += 1
                                    total_valid_notices += 1
                                    logger.info(f"发布时间解析失败，使用默认值，添加公告: {title}")
                            else:
                                # 如果没有发布时间，使用默认值并添加该公告
                                contest['publish_time'] = '2025-01-01'
                                all_contests.append(contest)
                                page_valid_notices += 1
                                total_valid_notices += 1
                                logger.info(f"无发布时间，使用默认值，添加公告: {title}")
                        else:
                            logger.error(f"无法获取详情页内容: {detail_url}")
                    except Exception as e:
                        logger.error(f"解析详情页失败: {detail_url}, 错误: {e}")
                logger.info(f"解析详情页完成，当前页面有效公告数量: {page_valid_notices}")
                
                # 更新连续无结果页数
                if page_valid_notices == 0:
                    consecutive_no_result_pages += 1
                    logger.info(f"第 {page_count} 页无有效公告，连续无结果页数: {consecutive_no_result_pages}")
                else:
                    consecutive_no_result_pages = 0
                    logger.info(f"第 {page_count} 页成功获取 {page_valid_notices} 条有效公告，累计: {total_valid_notices}")
                
                # 获取下一页
                current_url = self.get_next_page(content, current_url)
        except Exception as e:
            logger.error(f"爬虫执行失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        logger.info(f"爬取完成，共爬取 {page_count} 页，成功获取 {total_valid_notices} 条2025年后的公告")
        return all_contests
