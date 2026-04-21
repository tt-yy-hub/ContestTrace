#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编码处理模块
实现统一智能编码识别和转换功能
"""

import logging
from charset_normalizer import from_bytes

logger = logging.getLogger(__name__)

def smart_decode(content: bytes) -> str:
    """
    智能解码函数，支持多种编码格式
    备选解码顺序：utf-8-sig → gb18030 → gbk → big5 → utf-8
    
    Args:
        content: 字节流
    
    Returns:
        解码后的字符串
    """
    if not content:
        return ""
    
    # 尝试使用charset-normalizer自动检测编码
    try:
        result = from_bytes(content).best()
        if result:
            decoded = result.decode()
            return decoded
    except Exception:
        pass
    
    # 备选解码顺序
    encodings = ['utf-8-sig', 'gb18030', 'gbk', 'big5', 'utf-8']
    
    for encoding in encodings:
        try:
            decoded = content.decode(encoding)
            return decoded
        except Exception:
            pass
    
    # 兜底方案：使用utf-8并替换错误字符
    try:
        decoded = content.decode('utf-8', errors='replace')
        logger.debug("使用utf-8错误替换模式解码")
        return decoded
    except Exception as e:
        logger.error(f"所有解码尝试失败: {e}")
        return ""

def ensure_utf8(text: str) -> str:
    """
    确保文本为UTF-8编码
    
    Args:
        text: 输入文本
    
    Returns:
        UTF-8编码的文本
    """
    if not text:
        return ""
    
    try:
        # 先编码为UTF-8字节，再解码
        return text.encode('utf-8', errors='replace').decode('utf-8')
    except Exception as e:
        logger.error(f"UTF-8编码处理失败: {e}")
        return text
