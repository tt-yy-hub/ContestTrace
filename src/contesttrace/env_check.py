from __future__ import annotations

import importlib
import sys
from typing import List, Tuple


REQUIRED_PYTHON = (3, 10)
REQUIRED_PACKAGES = [
    "requests",
    "bs4",
    "lxml",
    "yaml",
    "openpyxl",
    "dateutil",
]


def check_python() -> Tuple[bool, str]:
    """检查Python版本。"""

    ok = sys.version_info >= REQUIRED_PYTHON
    msg = f"Python版本：{sys.version.split()[0]}（要求 >= {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}）"
    return ok, msg


def check_packages() -> Tuple[bool, List[str]]:
    """检查依赖是否安装。"""

    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except Exception:
            missing.append(pkg)
    return len(missing) == 0, missing


def main() -> None:
    print("=== ContestTrace 环境检查 ===")

    ok_py, msg = check_python()
    print(msg)
    if not ok_py:
        print("修复建议：请安装/切换到 Python 3.10+（推荐 3.11 或 3.12）。")
        sys.exit(1)

    ok_pkgs, missing = check_packages()
    if ok_pkgs:
        print("依赖检查：全部已安装。")
        print("环境正常，可直接运行。")
        return

    print("依赖检查：缺少以下库：")
    for m in missing:
        print(f"- {m}")
    print("\n修复建议：在项目根目录执行：")
    print("  pip install -r requirements.txt")
    print("\n如果提示 pip 找不到：")
    print("  python -m pip install -r requirements.txt")
    sys.exit(1)


if __name__ == "__main__":
    main()

