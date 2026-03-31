#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "=== ContestTrace 一键运行 ==="
echo "[1/2] 正在检查环境..."
python3 check_env.py || {
  echo ""
  echo "环境检查未通过，请先按提示安装依赖后再运行。"
  exit 1
}

echo ""
echo "[2/2] 启动主菜单..."
python3 run_app.py

