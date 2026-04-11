@echo off
REM 统计与数学学院通知公告 · 每周增量
cd /d "%~dp0"
python hbue_tsxy_notice_spider.py --mode incremental
