@echo off
REM 校团委通知公告 · 每周增量
cd /d "%~dp0"
python hbue_tw_notice_spider.py --mode incremental
