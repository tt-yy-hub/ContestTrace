@echo off
chcp 65001 >nul
echo 开始运行队友的爬虫...

rem 运行教务处爬虫
echo 运行教务处爬虫...
python ContestTrace-main\jiaowuchu\hbue_jwc_notice_spider.py --mode full --db data\contest_trace_raw_教务处.db

rem 运行实验教学中心爬虫
echo 运行实验教学中心爬虫...
python ContestTrace-main\shiyanjiaoxue\hbue_etc_notice_spider.py --mode full --db data\contest_trace_raw_实验教学中心.db

rem 运行统计与数学学院爬虫
echo 运行统计与数学学院爬虫...
python ContestTrace-main\tongshu\hbue_tsxy_notice_spider.py --mode full --db data\contest_trace_raw_统计与数学学院.db

rem 运行工商管理学院爬虫
echo 运行工商管理学院爬虫...
python ContestTrace-main\gongshang\hbue_gsxy_notice_spider.py --mode full --db data\contest_trace_raw_工商管理学院.db

rem 运行经济与贸易学院爬虫
echo 运行经济与贸易学院爬虫...
python ContestTrace-main\jingmaoxueyuan\hbue_jmxy_notice_spider.py --mode full --db data\contest_trace_raw_经济与贸易学院.db

rem 运行金融学院爬虫
echo 运行金融学院爬虫...
python ContestTrace-main\jingrongxueyuan\hbue_jrxy_notice_spider.py --mode full --db data\contest_trace_raw_金融学院.db

rem 运行会计学院爬虫
echo 运行会计学院爬虫...
python ContestTrace-main\kuaiji\hbue_kjxy_notice_spider.py --mode full --db data\contest_trace_raw_会计学院.db

rem 运行旅游与酒店管理学院爬虫
echo 运行旅游与酒店管理学院爬虫...
python ContestTrace-main\lvyoujiudian\hbue_lyxy_notice_spider.py --mode full --db data\contest_trace_raw_旅游与酒店管理学院.db

rem 运行外国语学院爬虫
echo 运行外国语学院爬虫...
python ContestTrace-main\waiguoyu\hbue_jmxy_notice_spider.py --mode full --db data\contest_trace_raw_外国语学院.db

rem 运行湖北经济学院团委爬虫
echo 运行湖北经济学院团委爬虫...
python ContestTrace-main\xiaotuanwei\hbue_tw_notice_spider.py --mode full --db data\contest_trace_raw_湖北经济学院团委.db

rem 运行信息管理学院爬虫
echo 运行信息管理学院爬虫...
python ContestTrace-main\xinguan\hbue_xgxy_notice_spider.py --mode full --db data\contest_trace_raw_信息管理学院.db

rem 运行新闻与传播学院爬虫
echo 运行新闻与传播学院爬虫...
python ContestTrace-main\xinwenyuchuanbo\hbue_jmxy_notice_spider.py --mode full --db data\contest_trace_raw_新闻与传播学院.db

rem 运行信息工程学院爬虫
echo 运行信息工程学院爬虫...
python ContestTrace-main\xinxigongcheng\hbue_ie_notice_spider.py --mode full --db data\contest_trace_raw_信息工程学院.db

rem 运行学生工作处爬虫
echo 运行学生工作处爬虫...
python ContestTrace-main\xueshenggongzuochu\hbue_xgc_notice_spider.py --mode full --db data\contest_trace_raw_学生工作处.db

rem 运行艺术学院爬虫
echo 运行艺术学院爬虫...
python ContestTrace-main\yishusheji\hbue_ysxy_notice_spider.py --mode full --db data\contest_trace_raw_艺术学院.db

echo 所有爬虫运行完成！
pause
