@echo off
REM 学生工作处通知公告 · 每周增量
cd /d "%~dp0"
python hbue_xgc_notice_spider.py --mode incremental
