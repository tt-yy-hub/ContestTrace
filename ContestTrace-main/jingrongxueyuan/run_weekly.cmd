@echo off
REM 金融学院通知公告 · 每周增量（任务计划程序指向本文件）
cd /d "%~dp0"
python hbue_jrxy_notice_spider.py --mode incremental
