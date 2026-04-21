@echo off
REM 信息管理学院通知公告 · 每周增量
cd /d "%~dp0"
python hbue_xgxy_notice_spider.py --mode incremental
