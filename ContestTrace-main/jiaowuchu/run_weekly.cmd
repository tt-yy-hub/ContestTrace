@echo off
REM 教务处通知公告 · 每周增量
cd /d "%~dp0"
python hbue_jwc_notice_spider.py --mode incremental
