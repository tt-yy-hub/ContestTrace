@echo off
setlocal

REM 示例：供 Windows 任务计划程序每周调用（增量抓取）
REM 进入脚本目录，避免相对路径出错
cd /d %~dp0

python hbue_jmxy_notice_spider.py --mode incremental

endlocal

