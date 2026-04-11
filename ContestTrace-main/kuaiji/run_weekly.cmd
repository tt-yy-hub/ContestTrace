@echo off
REM 会计学院通知公告 · 每周增量
cd /d "%~dp0"
python hbue_kjxy_notice_spider.py --mode incremental
