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
        logger.info(f"开始获取页面: {url}")
        for i in range(max_retries):
            try:
                logger.info(f"尝试获取页面 ({i+1}/{max_retries}): {url}")
                self.headers['User-Agent'] = get_user_agent()
                logger.info(f"使用User-Agent: {self.headers['User-Agent']}")
                response = self.session.get(url, headers=self.headers, timeout=10)  # 减少超时时间，提高执行速度
                logger.info(f"获取页面响应，状态码: {response.status_code}")
                response.raise_for_status()
                content = smart_decode(response.content)
                logger.info(f"成功获取页面: {url}, 长度: {len(content)}")
                # 随机延时，合规反爬
                random_delay(0.5, 1.5)  # 减少延时时间，提高执行速度
                return content
            except Exception as e:
                logger.warning(f"获取页面失败 ({i+1}/{max_retries}): {url}, 错误: {e}")
                if i < max_retries - 1:
                    logger.info(f"等待后重试")
                    random_delay(1, 2)  # 减少延时时间，提高执行速度
                else:
                    logger.error(f"最终获取页面失败: {url}")
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
    def get_next_page(self, content: str) -> str:
        """
        获取下一页URL
        
        Args:
            content: 当前页面内容
        
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
        max_pages = 10  # 增加爬取深度，确保覆盖更多页面
        
        # 用于增量爬取的URL集合
        crawled_urls = set()
        
        try:
            logger.info(f"初始化爬虫，当前URL: {current_url}, 页码: {page_count}, 最大页码: {max_pages}")
            
            while current_url and page_count < max_pages:
                logger.info(f"爬取页面: {current_url} (第 {page_count+1} 页)")
                
                content = self.fetch(current_url)
                logger.info(f"获取页面内容完成，长度: {len(content) if content else 0}")
                
                if not content:
                    logger.error(f"无法获取页面内容: {current_url}")
                    break
                
                # 解析列表页面，获取详情页URL
                detail_urls = self.parse_list(content)
                logger.info(f"解析列表页面完成，找到 {len(detail_urls)} 个竞赛链接")
                
                # 过滤已爬取的URL，实现增量爬取
                new_detail_urls = [url for url in detail_urls if url not in crawled_urls]
                logger.info(f"过滤后，新增 {len(new_detail_urls)} 个竞赛链接")
                
                # 解析所有详情页，不限制数量，确保不遗漏
                for i, detail_url in enumerate(new_detail_urls):
                    try:
                        logger.info(f"解析详情页 {i+1}/{len(new_detail_urls)}: {detail_url}")
                        detail_content = self.fetch(detail_url)
                        logger.info(f"成功获取详情页内容，长度: {len(detail_content) if detail_content else 0}")
                        if detail_content:
                            contest = self.parse_detail(detail_content, detail_url)
                            logger.info("解析详情页内容完成")
                            if contest:
                                all_contests.append(contest)
                                crawled_urls.add(detail_url)  # 添加到已爬取集合
                                logger.info(f"成功解析竞赛: {contest.get('title', '未知')}")
                            else:
                                logger.warning(f"解析详情页失败: {detail_url}")
                        else:
                            logger.error(f"无法获取详情页内容: {detail_url}")
                    except Exception as e:
                        logger.error(f"解析详情页失败: {detail_url}, 错误: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                
                # 获取下一页
                current_url = self.get_next_page(content)
                logger.info(f"获取下一页完成，下一页URL: {current_url}")
                page_count += 1
                logger.info(f"更新页码，当前URL: {current_url}, 页码: {page_count}, 最大页码: {max_pages}")
        except Exception as e:
            logger.error(f"爬虫执行失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        logger.info(f"爬取完成，共获取 {len(all_contests)} 个竞赛")
        return all_contests
