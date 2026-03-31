from __future__ import annotations

"""
新手零修改环境检查启动器：
- 自动把 src/ 加入 sys.path
- 然后运行 contesttrace.env_check
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
    from contesttrace.env_check import main as env_main

    env_main()


if __name__ == "__main__":
    main()

