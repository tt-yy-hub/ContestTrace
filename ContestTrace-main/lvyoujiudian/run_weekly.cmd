@echo off
REM 旅游与酒店管理学院通知公告 · 每周增量
cd /d "%~dp0"
python hbue_lyxy_notice_spider.py --mode incremental
