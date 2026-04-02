# -*- coding: utf-8 -*-
"""
智能编码修复模块（全项目字节流解码唯一入口）

设计原则：
- 优先使用 charset-normalizer 检测编码；高置信度时直接采用检测结果解码
- 置信度不足时按固定优先级尝试多种编码，并基于「替换字符数量 + 中文占比」择优
- 每次选择结果写入日志，便于排查乱码问题

注意：二进制文件（附件）不应调用本模块，应直接写入 bytes。
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

from charset_normalizer import from_bytes

# 日志记录器名称，便于在统一日志格式中识别模块
LOGGER_NAME = "contesttrace.encoding"

# 与需求对齐：检测置信度阈值（percent_coherence 为 0~100 时使用 >=90）
CONFIDENCE_PERCENT_MIN = 90

# 当库未提供 percent 时，用 chaos 近似（chaos 越低越好）
CHAOS_MAX_FOR_HIGH_CONFIDENCE = 0.10


def _count_cjk(text: str) -> int:
    """统计中日韩统一表意文字数量，用于择优。"""

    return len(re.findall(r"[\u4e00-\u9fff]", text))


def _score_decoded(text: str) -> int:
    """
    解码质量打分：中文越多越好，Unicode 替换字符越少越好。
    """

    bad = text.count("\ufffd")
    cjk = _count_cjk(text)
    # 乱码常见拉丁扩展（UTF-8 被误用单字节解码时）
    moj = len(re.findall(r"[åäöüèéêÃ¤Ã¥Ã¨Ã©Ã±]", text))
    return cjk * 10 - bad * 80 - moj * 6


def _try_manual_decodes(raw: bytes) -> List[Tuple[str, str]]:
    """
    手动尝试多种常见编码（按需求顺序）。
    返回 (encoding_name, decoded_text) 列表。
    """

    order = ["utf-8-sig", "gb18030", "gbk", "big5", "utf-8"]
    out: List[Tuple[str, str]] = []
    for enc in order:
        try:
            if enc == "utf-8":
                txt = raw.decode("utf-8", errors="replace")
            else:
                txt = raw.decode(enc, errors="strict")
            out.append((enc, txt))
        except Exception:
            continue
    return out


def smart_decode(raw_bytes: bytes, logger: Optional[logging.Logger] = None) -> Tuple[str, str]:
    """
    将字节流智能解码为 Unicode 字符串。

    :param raw_bytes: 原始字节（HTTP 响应体、文件读入的 bytes 等）
    :param logger: 可选日志器；为 None 时使用本模块默认 logger
    :return: (解码后的文本, 选用的编码标识字符串)

    说明：
    - 绝不硬编码「整个站点永远用某一种编码」；每次根据内容与检测结果决定
    - 空字节返回 ("", "empty")
    """

    log = logger or logging.getLogger(LOGGER_NAME)

    if raw_bytes is None or len(raw_bytes) == 0:
        log.info("smart_decode: 输入为空，返回空字符串")
        return "", "empty"

    # 优先尝试 UTF-8（含 BOM）：大量现代站点实为 UTF-8，避免被误判为其它编码导致乱码
    for enc in ("utf-8-sig", "utf-8"):
        try:
            txt = raw_bytes.decode(enc, errors="strict")
            if _count_cjk(txt) > 0 or len(txt) > 0:
                log.info(f"smart_decode: 采用严格 {enc} 解码成功（优先策略）")
                return txt, enc
        except Exception:
            continue

    try:
        results = from_bytes(raw_bytes)
        best = results.best()
    except Exception as e:
        log.warning(f"charset-normalizer 检测异常，将使用手动回退链：{type(e).__name__}: {e}")
        best = None

    chosen_encoding = "unknown"
    text = ""

    if best is not None:
        # 不同版本 CharsetMatch 字段略有差异，做兼容读取
        pct = getattr(best, "percent_coherence", None)
        chaos = getattr(best, "chaos", None)
        coherence = getattr(best, "coherence", None)  # 部分版本为 0~1 浮点
        high_conf = False
        if pct is not None:
            high_conf = float(pct) >= float(CONFIDENCE_PERCENT_MIN)
        elif coherence is not None:
            high_conf = float(coherence) >= 0.9
        elif chaos is not None:
            high_conf = float(chaos) <= float(CHAOS_MAX_FOR_HIGH_CONFIDENCE)

        if high_conf:
            try:
                text = str(best)
                chosen_encoding = getattr(best, "encoding", None) or "charset-normalizer"
                log.info(
                    f"smart_decode: 采用 charset-normalizer 高置信结果 | "
                    f"encoding={chosen_encoding} | "
                    f"percent_coherence={pct!s} | chaos={chaos!s}"
                )
                return text, chosen_encoding
            except Exception as e:
                log.warning(f"高置信匹配解码失败，进入回退：{type(e).__name__}: {e}")

    # 置信不足或解码失败：手动链 + 评分择优
    candidates = _try_manual_decodes(raw_bytes)
    if not candidates:
        # 最后兜底：utf-8 replace
        text = raw_bytes.decode("utf-8", errors="replace")
        chosen_encoding = "utf-8-replace"
        log.warning(f"smart_decode: 所有严格解码失败，使用 utf-8 replace | bad_chars={text.count(chr(0xfffd))}")
        return text, chosen_encoding

    best_pair: Optional[Tuple[str, str]] = None
    best_score = None
    for enc_name, txt in candidates:
        sc = _score_decoded(txt)
        if best_score is None or sc > best_score:
            best_score = sc
            best_pair = (enc_name, txt)

    assert best_pair is not None
    chosen_encoding, text = best_pair
    log.info(
        f"smart_decode: 采用手动回退链择优 | encoding={chosen_encoding} | "
        f"cjk={_count_cjk(text)} | replacement={text.count(chr(0xfffd))}"
    )
    return text, chosen_encoding


def read_text_file(path, logger: Optional[logging.Logger] = None) -> Tuple[str, str]:
    """
    以二进制读取文件后统一走 smart_decode，保证磁盘文本与网络一致处理。
    """

    from pathlib import Path

    p = Path(path)
    raw = p.read_bytes()
    return smart_decode(raw, logger=logger)
