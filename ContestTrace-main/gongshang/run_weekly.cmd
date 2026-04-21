@echo off
REM 工商管理学院通知公告 · 每周增量
cd /d "%~dp0"
python hbue_gsxy_notice_spider.py --mode incremental
