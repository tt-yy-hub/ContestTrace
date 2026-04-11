@echo off
REM 信息工程学院通知公告 · 每周增量
cd /d "%~dp0"
python hbue_ie_notice_spider.py --mode incremental
