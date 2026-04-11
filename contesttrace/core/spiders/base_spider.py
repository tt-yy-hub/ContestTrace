#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫基类
定义通用爬虫功能
"""

import requests
from abc import ABC, abstractmethod
from ..utils import smart_decode, random_delay, get_user_agent, extract_keywords
import logging
from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from urllib.parse import urljoin, urlparse

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
    
    def fetch(self, url: str, max_retries: int = 5) -> str:
        """
        获取页面内容
        
        Args:
            url: 页面URL
            max_retries: 最大重试次数
        
        Returns:
            页面内容
        """
        last_err = None
        
        # 不同的 User-Agent 列表
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        
        for i in range(max_retries):
            try:
                # 随机选择一个 User-Agent
                import random
                self.headers['User-Agent'] = random.choice(user_agents)
                
                # 增加更多的请求头
                self.headers['Accept-Encoding'] = 'gzip, deflate, br'
                self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
                self.headers['Upgrade-Insecure-Requests'] = '1'
                self.headers['Connection'] = 'keep-alive'
                self.headers['Cache-Control'] = 'max-age=0'
                self.headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
                
                # 发送请求
                response = self.session.get(url, headers=self.headers, timeout=60)
                
                # 处理状态码
                if response.status_code in (401, 503, 429):
                    logger.warning(f"{response.status_code} 错误，尝试更新请求头: {url}")
                    # 尝试使用不同的 User-Agent
                    self.headers['User-Agent'] = random.choice(user_agents)
                    # 增加延时
                    random_delay(5, 10)
                    # 重新发送请求
                    response = self.session.get(url, headers=self.headers, timeout=60)
                
                if response.status_code >= 400:
                    logger.error(f"获取页面失败，状态码: {response.status_code}, URL: {url}")
                    if i < max_retries - 1:
                        # 增加延时，避免被封禁
                        delay = 5 + i * 2
                        random_delay(delay, delay + 3)
                        continue
                    else:
                        return ""
                
                response.raise_for_status()
                content = smart_decode(response.content)
                
                # 随机延时，合规反爬
                random_delay(2, 4)
                return content
            except requests.exceptions.RequestException as e:
                last_err = e
                logger.warning(f"获取页面失败 (尝试 {i+1}/{max_retries}): {url}, 错误: {e}")
                if i < max_retries - 1:
                    # 增加延时，避免被封禁
                    delay = 5 + i * 2
                    random_delay(delay, delay + 3)
                else:
                    logger.error(f"最终获取页面失败: {url}, 错误: {last_err}")
                    return ""
            except Exception as e:
                last_err = e
                logger.warning(f"获取页面失败 (尝试 {i+1}/{max_retries}): {url}, 错误: {e}")
                if i < max_retries - 1:
                    # 增加延时，避免被封禁
                    delay = 5 + i * 2
                    random_delay(delay, delay + 3)
                else:
                    logger.error(f"最终获取页面失败: {url}, 错误: {last_err}")
                    return ""
    
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
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # 尝试多种可能的页面结构
            list_containers = []
            
            # 1. 尝试常见的列表容器类
            container_classes = ['wp_article_list', 'news_list', 'list', 'article_list', 'articles']
            for class_name in container_classes:
                containers = soup.find_all(['ul', 'div'], class_=class_name)
                list_containers.extend(containers)
            
            # 2. 尝试查找包含最多li的ul
            all_ul = soup.find_all('ul')
            if all_ul:
                # 按li数量排序，选择前3个作为候选
                sorted_ul = sorted(all_ul, key=lambda ul: len(ul.find_all('li')), reverse=True)[:3]
                list_containers.extend(sorted_ul)
            
            # 3. 尝试查找包含a标签的div容器
            all_div = soup.find_all('div')
            for div in all_div:
                if len(div.find_all('a')) > 5:
                    list_containers.append(div)
            
            # 去重
            list_containers = list(set(list_containers))
            
            # 提取链接
            for container in list_containers:
                # 查找所有a标签
                a_tags = container.find_all('a')
                
                for a_tag in a_tags:
                    if 'href' in a_tag.attrs:
                        href = a_tag['href']
                        # 构建完整URL
                        if href.startswith('http'):
                            detail_url = href
                        else:
                            if href.startswith('/'):
                                detail_url = f"{self.base_url.split('/list')[0]}{href}"
                            else:
                                detail_url = f"{self.base_url.rsplit('/', 1)[0]}/{href}"
                        
                        # 过滤掉非详情页链接
                        if 'htm' in detail_url and 'list' not in detail_url:
                            detail_urls.append(detail_url)
            
            # 去重
            detail_urls = list(set(detail_urls))
        except Exception as e:
            logger.error(f"解析列表页面失败: {e}")
        
        return detail_urls
    
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
    
    def _is_document_href(self, href: str) -> bool:
        """
        检查链接是否为文档链接
        """
        if not href:
            return False
        h = href.strip()
        if h.startswith("#") or h.lower().startswith("javascript"):
            return False
        from pathlib import Path
        _DOCUMENT_EXTENSIONS = {".jpg", ".jpeg", ".pdf", ".doc", ".docx", ".xls", ".xlsx"}
        path = h.split("?", 1)[0].split("#", 1)[0]
        return Path(path).suffix.lower() in _DOCUMENT_EXTENSIONS
    
    def _abs_asset_url(self, href: str) -> str:
        """
        获取绝对资源URL
        """
        return urljoin(self.base_url + "/", href.strip())
    
    def _normalize_text_lines(self, raw: str, *, collapse_soft_breaks: bool = False) -> str:
        """
        规范化文本行
        """
        import re
        if collapse_soft_breaks:
            raw = re.sub(r"[\s\u00a0]*\n[\s\u00a0]*", " ", raw)
        lines: list[str] = []
        for line in raw.split("\n"):
            lines.append(re.sub(r"[\s\u00a0]+", " ", line).strip())
        out = "\n".join(L for L in lines if L)
        return out
    
    def _inline_merged_text(self, el: Tag, *, collapse_soft_breaks: bool = False) -> str:
        """
        提取块级元素内全部可读文本
        """
        parts: list[str] = []

        def walk(n: Tag) -> None:
            for c in n.children:
                if isinstance(c, NavigableString):
                    if isinstance(c, Comment):
                        continue
                    parts.append(str(c))
                elif isinstance(c, Tag):
                    low = c.name.lower()
                    if low == "br":
                        parts.append("\n")
                    elif low == "a":
                        href = (c.get("href") or "").strip()
                        if href and self._is_document_href(href):
                            abs_u = self._abs_asset_url(href)
                            label = " ".join(c.stripped_strings) if c.stripped_strings else ""
                            if not label:
                                inner_img = c.find("img")
                                if inner_img and (inner_img.get("alt") or "").strip():
                                    label = inner_img.get("alt", "").strip()
                            parts.append(f"{label} {abs_u}" if label else abs_u)
                            parts.append(" ")
                        else:
                            walk(c)
                    elif low == "img":
                        src = (c.get("src") or "").strip()
                        if src and self._is_document_href(src):
                            abs_u = self._abs_asset_url(src)
                            alt = (c.get("alt") or "").strip()
                            lab = alt if alt else "[图片]"
                            parts.append(f"{lab} {abs_u}")
                            parts.append(" ")
                    elif low == "table":
                        t = self._table_to_text(c)
                        if t:
                            parts.append("\n" + t + "\n")
                    elif low in ("script", "style"):
                        continue
                    else:
                        walk(c)

        walk(el)
        raw = "".join(parts)
        return self._normalize_text_lines(raw, collapse_soft_breaks=collapse_soft_breaks).strip()
    
    def _table_to_text(self, table: Tag) -> str:
        """
        将表格转换为文本
        """
        lines: list[str] = []
        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"], recursive=False)
            if not cells:
                continue
            row = [self._inline_merged_text(c, collapse_soft_breaks=True) for c in cells]
            lines.append("\t".join(row))
        return "\n".join(L for L in lines if any(L.split("\t")))
    
    def _process_block_node(self, el: Tag, blocks: list[str]) -> None:
        """
        处理块节点
        """
        low = el.name.lower()
        if low in ("script", "style"):
            return
        if low == "table":
            txt = self._table_to_text(el)
            if txt:
                blocks.append(txt)
            return
        if low in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre"):
            txt = self._inline_merged_text(el)
            if txt:
                blocks.append(txt)
            return
        if low == "ul":
            for li in el.find_all("li", recursive=False):
                txt = self._inline_merged_text(li)
                if txt:
                    blocks.append(txt)
            return
        if low == "ol":
            for i, li in enumerate(el.find_all("li", recursive=False), 1):
                txt = self._inline_merged_text(li)
                if txt:
                    blocks.append(f"{i}. {txt}")
            return
        if low == "div":
            has_struct = bool(
                el.find(
                    ["p", "table", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "div"],
                    recursive=False,
                )
            )
            if has_struct:
                for c in el.children:
                    if isinstance(c, Tag):
                        self._process_block_node(c, blocks)
            else:
                txt = self._inline_merged_text(el)
                if txt:
                    blocks.append(txt)
            return

        if el.find(["p", "table", "ul", "ol", "div"], recursive=False):
            for c in el.children:
                if isinstance(c, Tag):
                    self._process_block_node(c, blocks)
        else:
            txt = self._inline_merged_text(el)
            if txt:
                blocks.append(txt)
    
    def _append_document_link_section(self, plain: str, container: Tag) -> str:
        """
        追加文档链接部分
        """
        seen_urls: set[str] = set()
        lines: list[str] = []
        for el in container.find_all(["a", "img"]):
            if el.name == "a":
                href = (el.get("href") or "").strip()
                if not href or not self._is_document_href(href):
                    continue
                abs_u = self._abs_asset_url(href)
            else:
                src = (el.get("src") or "").strip()
                if not src or not self._is_document_href(src):
                    continue
                abs_u = self._abs_asset_url(src)
            if abs_u in seen_urls:
                continue
            seen_urls.add(abs_u)
            if abs_u in plain:
                continue
            if el.name == "a":
                label = " ".join(el.stripped_strings) if el.stripped_strings else ""
                if not label:
                    im = el.find("img")
                    if im and (im.get("alt") or "").strip():
                        label = im.get("alt", "").strip()
                if not label:
                    label = abs_u
            else:
                label = (el.get("alt") or "").strip() or "[图片]"
            lines.append(f"{label}\t{abs_u}")
        if not lines:
            return plain
        return plain + "\n\n【文档链接】\n" + "\n".join(lines)
    
    def extract_article_plain(self, container: Tag) -> str:
        """
        提取文章纯文本
        """
        if not container:
            return ""
        for s in container.find_all(["script", "style"]):
            s.decompose()

        blocks: list[str] = []
        for child in container.children:
            if isinstance(child, Tag):
                self._process_block_node(child, blocks)
        merged = "\n\n".join(b for b in blocks if b)
        merged = merged.strip()
        return self._append_document_link_section(merged, container)
    
    def extract_content_from_soup(self, soup: BeautifulSoup) -> str:
        """
        从 soup 中提取内容
        """
        container = (
            soup.select_one("div.wp_articlecontent")
            or soup.select_one("#vsb_content")
            or soup.select_one(".article-content")
            or soup.select_one("div.read")
        )
        return self.extract_article_plain(container) if container else ""
    
    def extract_content_from_html(self, html: str) -> str:
        """
        从 HTML 中提取内容
        """
        return self.extract_content_from_soup(BeautifulSoup(html, "html.parser"))
    
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
            while current_url and page_count < 1000 and consecutive_no_result_pages < 5:
                page_count += 1
                logger.info(f"正在爬取第 {page_count} 页: {current_url}")
                
                content = self.fetch(current_url)
                
                if not content:
                    logger.error(f"无法获取页面内容: {current_url}")
                    # 继续尝试下一页，不要因为单个页面失败而停止
                    next_url = self.get_next_page(None, current_url)
                    if next_url and next_url != current_url:
                        current_url = next_url
                        logger.info(f"页面获取失败，尝试下一页: {current_url}")
                        continue
                    else:
                        break
                
                # 解析列表页面，获取详情页URL
                detail_urls = self.parse_list(content)
                logger.info(f"找到 {len(detail_urls)} 个公告链接")
                
                page_valid_notices = 0  # 当前页面有效公告数量
                found_old_notice = False  # 标记是否遇到2025年之前的公告
                
                # 解析详情页，遇到2025年之前的公告时不再爬取下一页，但继续处理当前页面的所有链接
                logger.info(f"开始解析 {len(detail_urls)} 个详情页")
                
                for i, detail_url in enumerate(detail_urls):
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
                                        # 遇到2025年之前的公告，标记但继续处理当前页面的其他链接
                                        logger.info(f"遇到2025年之前的公告，跳过: {title}")
                                        found_old_notice = True  # 标记遇到了2025年之前的公告
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
                
                # 如果遇到2025年之前的公告，不再爬取下一页
                if not found_old_notice:
                    current_url = self.get_next_page(content, current_url)
                else:
                    # 遇到2025年之前的公告，停止爬取下一页
                    logger.info("遇到2025年之前的公告，停止爬取下一页")
                    current_url = None
        except Exception as e:
            logger.error(f"爬虫执行失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        logger.info(f"爬取完成，共爬取 {page_count} 页，成功获取 {total_valid_notices} 条2025年后的公告")
        return all_contests
