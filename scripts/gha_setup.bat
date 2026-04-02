@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo === 本地模拟 GitHub Actions 爬取流程 ===
python -m pip install -r requirements.txt
python scripts\crawl_and_snapshot.py
echo 完成。可检查 data\reports\latest_snapshot.csv
pause
