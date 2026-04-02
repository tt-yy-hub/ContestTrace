from __future__ import annotations

"""
新手零修改启动器（重要）：

本项目采用更规范的 `src/` 目录布局。
为了让新手无需安装包/无需设置环境变量，也能直接运行，
本启动器会自动把 `src` 加入 sys.path，然后启动主菜单。
"""

import sys
from pathlib import Path


def _bootstrap_src_path() -> None:
    root = Path(__file__).resolve().parent
    src = root / "src"
    if src.exists() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> None:
    _bootstrap_src_path()
    from contesttrace.utils import configure_stdio_utf8

    configure_stdio_utf8()
    from contesttrace.__main__ import main as app_main

    app_main()


if __name__ == "__main__":
    main()

