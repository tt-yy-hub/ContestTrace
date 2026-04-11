#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验教学中心爬虫
"""

import re
from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from .base_spider import BaseSpider
from ..utils import normalize_date, extract_keywords
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class EtcSpider(BaseSpider):
    """
    实验教学中心爬虫
    """
    
    def __init__(self):
        """
        初始化爬虫
        """
        super().__init__(
            name="实验教学中心",
            base_url="https://etc.hbue.edu.cn/xkjs_10388/list.htm"
        )
    
    def parse_list(self, content: str) -> list[str]:
        """
        解析列表页面
        
        Args:
            content: 页面内容
        
        Returns:
            详情页URL列表
        """
        try:
            soup = BeautifulSoup(content, 'html.parser')
            detail_urls = []
            
            # 查找新闻列表
            ul = soup.select_one("ul.news_list.list2") or soup.select_one("ul.news_list")
            if not ul:
                logger.error("列表页未找到 ul.news_list")
                return detail_urls
            
            for li in ul.select("li.news"):
                a = li.select_one("span.news_title a")
                if not a or not a.get("href"):
                    continue
                
                # 提取链接
                href = a["href"].strip()
                detail_url = urljoin("https://etc.hbue.edu.cn/", href)
                
                # 过滤掉非详情页链接
                if 'htm' in detail_url and 'list' not in detail_url:
                    detail_urls.append(detail_url)
            
            # 去重
            detail_urls = list(set(detail_urls))
            return detail_urls
        except Exception as e:
            logger.error(f"解析列表页面失败: {e}")
            return []
    
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
            soup = BeautifulSoup(content, 'html.parser')
            
            # 提取标题
            title = ""
            title_tag = soup.find('h1', class_='arti_title')
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            # 提取发布时间
            publish_time = ""
            # 尝试从不同位置提取发布时间
            arti_update = soup.select_one("span.arti_update")
            if arti_update:
                time_match = re.search(r'发布时间[：:]\s*(\d{4}-\d{1,2}-\d{1,2})|(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', arti_update.get_text())
                if time_match:
                    if time_match.group(1):
                        publish_time = normalize_date(time_match.group(1))
                    else:
                        publish_time = normalize_date(f"{time_match.group(2)}-{time_match.group(3)}-{time_match.group(4)}")
            
            # 如果没有找到，尝试从其他位置提取
            if not publish_time:
                plain_text = soup.get_text("\n", strip=True)
                time_match = re.search(r'发布时间[：:]\s*(\d{4}-\d{1,2}-\d{1,2})|(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', plain_text)
                if time_match:
                    if time_match.group(1):
                        publish_time = normalize_date(time_match.group(1))
                    else:
                        publish_time = normalize_date(f"{time_match.group(2)}-{time_match.group(3)}-{time_match.group(4)}")
            
            # 提取来源
            source = "实验教学中心"
            arti_publisher = soup.select_one("span.arti_publisher")
            if arti_publisher:
                source_match = re.match(r'发布者[：:]\s*(.+)', arti_publisher.get_text())
                if source_match and source_match.group(1).strip():
                    source = source_match.group(1).strip()
            
            # 提取内容（改进版）
            content_text = self._extract_content(soup)
            
            # 提取关键词
            keywords = extract_keywords(title + " " + content_text)
            
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
            
            return contest
        except Exception as e:
            logger.error(f"解析详情页面失败: {url}, 错误: {e}")
            return {}
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        提取正文内容，处理表格、链接等
        
        Args:
            soup: BeautifulSoup对象
        
        Returns:
            提取的内容
        """
        # 正文中需保留为「文档超链接」的文件扩展名（不区分大小写）
        document_extensions = {'.jpg', '.jpeg', '.pdf', '.doc', '.docx', '.xls', '.xlsx'}
        
        def is_document_href(href: str) -> bool:
            if not href:
                return False
            h = href.strip()
            if h.startswith("#") or h.lower().startswith("javascript"):
                return False
            path = h.split("?", 1)[0].split("#", 1)[0]
            return path.lower().endswith(tuple(document_extensions))
        
        def abs_asset_url(href: str) -> str:
            return urljoin("https://etc.hbue.edu.cn/", href.strip())
        
        def normalize_text_lines(raw: str, *, collapse_soft_breaks: bool = False) -> str:
            """按行压缩空白；collapse_soft_breaks 为 True 时把行内换行收成空格（用于表格单元格）。"""
            if collapse_soft_breaks:
                raw = re.sub(r'[\s\u00a0]*\n[\s\u00a0]*', " ", raw)
            lines: list[str] = []
            for line in raw.split("\n"):
                lines.append(re.sub(r'[\s\u00a0]+', " ", line).strip())
            out = "\n".join(L for L in lines if L)
            return out
        
        def inline_merged_text(el: Tag, *, collapse_soft_breaks: bool = False) -> str:
            """
            提取块级元素内全部可读文本：行内标签（span/font 等）不插入换行，与网页连续阅读一致；
            仅显式 <br> 产生换行。文档类 <a href>、<img src> 输出「锚文本 + 空格 + 绝对 URL」。
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
                            if href and is_document_href(href):
                                abs_u = abs_asset_url(href)
                                label = re.sub(r"\s+", " ", c.get_text(separator=" ", strip=True)).strip()
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
                            if src and is_document_href(src):
                                abs_u = abs_asset_url(src)
                                alt = (c.get("alt") or "").strip()
                                lab = alt if alt else "[图片]"
                                parts.append(f"{lab} {abs_u}")
                                parts.append(" ")
                        elif low == "table":
                            t = table_to_text(c)
                            if t:
                                parts.append("\n" + t + "\n")
                        elif low in ("script", "style"):
                            continue
                        else:
                            walk(c)

            walk(el)
            raw = "".join(parts)
            return normalize_text_lines(raw, collapse_soft_breaks=collapse_soft_breaks).strip()
        
        def table_to_text(table: Tag) -> str:
            lines: list[str] = []
            for tr in table.find_all("tr"):
                cells = tr.find_all(["td", "th"], recursive=False)
                if not cells:
                    continue
                row = [inline_merged_text(c, collapse_soft_breaks=True) for c in cells]
                lines.append("\t".join(row))
            return "\n".join(L for L in lines if any(L.split("\t")))
        
        def process_block_node(el: Tag, blocks: list[str]) -> None:
            low = el.name.lower()
            if low in ("script", "style"):
                return
            if low == "table":
                txt = table_to_text(el)
                if txt:
                    blocks.append(txt)
                return
            if low in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre"):
                txt = inline_merged_text(el)
                if txt:
                    blocks.append(txt)
                return
            if low == "ul":
                for li in el.find_all("li", recursive=False):
                    txt = inline_merged_text(li)
                    if txt:
                        blocks.append(txt)
                return
            if low == "ol":
                for i, li in enumerate(el.find_all("li", recursive=False), 1):
                    txt = inline_merged_text(li)
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
                            process_block_node(c, blocks)
                else:
                    txt = inline_merged_text(el)
                    if txt:
                        blocks.append(txt)
                return

            if el.find(["p", "table", "ul", "ol", "div"], recursive=False):
                for c in el.children:
                    if isinstance(c, Tag):
                        process_block_node(c, blocks)
            else:
                txt = inline_merged_text(el)
                if txt:
                    blocks.append(txt)
        
        def append_document_link_section(plain: str, container: Tag) -> str:
            """DOM 顺序收集文档类 a/img，若 URL 尚未出现在正文中则追加【文档链接】区块。"""
            seen_urls: set[str] = set()
            lines: list[str] = []
            for el in container.find_all(["a", "img"]):
                if el.name == "a":
                    href = (el.get("href") or "").strip()
                    if not href or not is_document_href(href):
                        continue
                    abs_u = abs_asset_url(href)
                else:
                    src = (el.get("src") or "").strip()
                    if not src or not is_document_href(src):
                        continue
                    abs_u = abs_asset_url(src)
                if abs_u in seen_urls:
                    continue
                seen_urls.add(abs_u)
                if abs_u in plain:
                    continue
                if el.name == "a":
                    label = re.sub(r"\s+", " ", el.get_text(separator=" ", strip=True)).strip()
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
        
        # 提取内容容器
        container = (
            soup.select_one("div.wp_articlecontent")
            or soup.select_one("#vsb_content")
            or soup.select_one(".article-content")
            or soup.select_one("div.read")
        )
        
        if not container:
            return ""
        
        # 移除脚本和样式
        for s in container.find_all(["script", "style"]):
            s.decompose()

        # 处理内容块
        blocks: list[str] = []
        for child in container.children:
            if isinstance(child, Tag):
                process_block_node(child, blocks)
        
        # 合并内容
        merged = "\n\n".join(b for b in blocks if b)
        merged = merged.strip()
        
        # 追加文档链接
        merged = append_document_link_section(merged, container)
        
        return merged
    
    def get_next_page(self, content: str, current_url: str) -> str:
        """
        获取下一页URL
        
        Args:
            content: 当前页面内容
            current_url: 当前页面URL
        
        Returns:
            下一页URL，为空表示没有下一页
        """
        try:
            # 首先尝试从页面中查找下一页链接
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找下一页链接
            next_href = None
            nxt = soup.select_one("a.next")
            if nxt and nxt.get("href"):
                h = nxt["href"].strip()
                if h and not h.startswith("javascript"):
                    next_href = urljoin("https://etc.hbue.edu.cn/", h)
            
            if next_href:
                logger.info(f"找到下一页URL: {next_href}")
                return next_href
            
            # 如果没有找到，尝试从URL生成下一页URL
            # 匹配list后面的数字
            match = re.search(r'list(\d+)\.htm', current_url)
            if match:
                current_page = int(match.group(1))
                next_page = current_page + 1
                # 生成下一页URL
                next_url = current_url.replace(f'list{current_page}.htm', f'list{next_page}.htm')
                logger.info(f"生成下一页URL: {next_url}")
                return next_url
            else:
                # 处理 list.htm 格式的URL
                if 'list.htm' in current_url:
                    # 视为第一页，生成第二页URL
                    next_url = current_url.replace('list.htm', 'list2.htm')
                    logger.info(f"生成下一页URL: {next_url}")
                    return next_url
        except Exception as e:
            logger.error(f"获取下一页失败: {e}")
        
        return ""
