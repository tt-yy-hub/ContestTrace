@echo off
setlocal

REM 示例：每周增量抓取（任务计划程序调用）
REM 注意：命令不要拼成 update_content_only.pypython ...

python hbue_jmxy_notice_spider.py --mode incremental --db notices.db --log weekly_spider.log

endlocal
