@echo off
REM 任务计划程序：每周一 09:00 触发，操作「启动程序」指向本文件
cd /d "%~dp0"
python hbue_jmxy_notice_spider.py --mode incremental
