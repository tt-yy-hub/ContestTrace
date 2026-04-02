# -*- coding: utf-8 -*-
"""
环境检查：Python 版本与关键依赖导入测试。
"""

from __future__ import annotations

import importlib
import sys
from typing import List, Tuple


REQUIRED_PYTHON = (3, 10)
# 模块名（import 名）列表
REQUIRED_PACKAGES = [
    "requests",
    "bs4",
    "lxml",
    "yaml",
    "openpyxl",
    "dateutil",
    "charset_normalizer",
    "dotenv",
    "pandas",
    "sklearn",
    "jieba",
    "joblib",
    "openai",
    "streamlit",
    "plotly",
]


def check_python() -> Tuple[bool, str]:
    """检查 Python 版本。"""

    ok = sys.version_info >= REQUIRED_PYTHON
    msg = f"Python版本：{sys.version.split()[0]}（要求 >= {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}）"
    return ok, msg


def check_packages() -> Tuple[bool, List[str]]:
    """检查依赖是否可导入。"""

    missing: List[str] = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except Exception:
            missing.append(pkg)
    return len(missing) == 0, missing


def main() -> None:
    print("=== ContestTrace 2.0 环境检查 ===")

    ok_py, msg = check_python()
    print(msg)
    if not ok_py:
        print("修复建议：请安装 Python 3.10+（推荐 3.11 / 3.12）。")
        sys.exit(1)

    ok_pkgs, missing = check_packages()
    if ok_pkgs:
        print("依赖检查：全部已安装。")
        print("环境正常，可直接运行：python run_app.py 或 python run_web.py")
        return

    print("依赖检查：缺少以下库：")
    for m in missing:
        print(f"- {m}")
    print("\n修复建议：在项目根目录执行：")
    print("  pip install -r requirements.txt")
    print("  或：python -m pip install -r requirements.txt")
    sys.exit(1)


if __name__ == "__main__":
    main()
