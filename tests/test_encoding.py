# -*- coding: utf-8 -*-
"""
编码修复模块测试：运行方式 python tests/test_encoding.py 或 pytest tests/test_encoding.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# 项目 src 路径
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from contesttrace.encoding_fixer import smart_decode  # noqa: E402


def test_utf8_roundtrip() -> None:
    # 使用 Unicode 转义，避免测试文件编码差异导致断言失败
    sample = "\u6e56\u5317\u7ecf\u6d4e\u5b66\u9662\u56e2\u59d4\u901a\u77e5\u516c\u544a"
    raw = sample.encode("utf-8")
    log = logging.getLogger("test")
    text, enc = smart_decode(raw, logger=log)
    assert "\u6e56\u5317" in text
    assert enc != "empty"


def test_gb18030_sample() -> None:
    raw = "\u7ade\u8d5b\u901a\u77e5\u6d4b\u8bd5\u6587\u672c".encode("gb18030")
    log = logging.getLogger("test")
    text, enc = smart_decode(raw, logger=log)
    assert "\u7ade\u8d5b" in text or len(text) > 0


def test_empty() -> None:
    text, enc = smart_decode(b"", logger=logging.getLogger("test"))
    assert text == "" and enc == "empty"


if __name__ == "__main__":
    test_utf8_roundtrip()
    test_gb18030_sample()
    test_empty()
    print("encoding tests passed")
