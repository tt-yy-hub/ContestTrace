@echo off
REM 实验教学中心通知公告 · 每周增量
cd /d "%~dp0"
python hbue_etc_notice_spider.py --mode incremental
