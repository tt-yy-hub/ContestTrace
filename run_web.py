# -*- coding: utf-8 -*-
"""
一键启动 Streamlit Web 前端（双击或 python run_web.py）。

自动将 src 加入 Python 路径，并设置控制台 UTF-8。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    src = root / "src"
    if src.exists() and str(src) not in sys.path:
        sys.path.insert(0, str(src))

    from contesttrace.utils import configure_stdio_utf8

    configure_stdio_utf8()

    app = root / "src" / "contesttrace" / "web" / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(app), "--server.headless", "true"]
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
