#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
echo "=== 本地模拟 GitHub Actions 爬取流程 ==="
python3 -m pip install -r requirements.txt
python3 scripts/crawl_and_snapshot.py
echo "完成。可检查 data/reports/latest_snapshot.csv"
