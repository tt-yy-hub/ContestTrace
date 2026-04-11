@echo off
REM 艺术设计学院通知公告 · 每周增量
cd /d "%~dp0"
python hbue_ysxy_notice_spider.py --mode incremental
