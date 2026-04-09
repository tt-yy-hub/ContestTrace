#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户提供的竞赛通知是否被正确筛选
"""

import sqlite3
import logging
from contesttrace.core.filter.competition_filter import CompetitionFilter

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 用户提供的竞赛通知（排除数据库中不存在的竞赛通知）
user_contests = [
    (8, "第31届中国日报社 \"21世纪杯\"全国英语演讲比赛湖北经济学院校园选拔赛通知", "2026-03-04"),
    (27, "关于举行2026年（19届）中国大学生计算机设计大赛湖北经济学院校赛的通知", "2026-04-07"),
    (29, "蓝桥杯全国大学生软件和信息技术专业人才大赛校级比赛通知", "2025-12-01"),
    (37, "湖北经济学院关于组织学生参加2025年全国大学生数学竞赛选拔测试的通知", "2025-05-27"),
    (38, "关于举办\"正大杯\"第十六届全国大学生市场调查与分析大赛（本科生组）湖北经济学院选拔赛的通知", "2026-03-16"),
    (40, "湖北经济学院关于组织学生参加2026年\"华中杯\"大学生数学建模挑战赛通知", "2026-03-12"),
    (41, "湖北经济学院关于组织学生参加第十六届全国大学生市场调查与分析大赛的通知", "2025-09-30"),
    (47, "关于组织参加2026年全国大学生统计建模大赛（本科生组）的通知", "2026-03-17"),
    (49, "湖北经济学院关于组织学生参加2025年全国大学生数学建模竞赛校内选拔赛通知", "2025-05-19"),
    (50, "关于组织参加2025年（第十一届）全国大学生统计建模大赛（本科生组）的通知", "2025-02-19"),
    (51, "2026年第十届\"米兰设计周-中国高校设计学科师生优秀作品展\"学科竞赛通知", "2026-03-18"),
    (53, "2026年第十七届蓝桥杯全国软件和信息技术专业人才大赛视觉艺术设计赛通知", "2026-03-10"),
    (55, "关于举行2026年（19届）中国大学生计算机设计大赛湖北经济学院校赛的通知", "2026-03-30"),
    (71, "关于举办湖北经济学院第三届\"浩然杯\" 读书演讲大赛的通知", "2026-03-27"),
    (94, "关于举办2026年\"挑战杯\"大学生 创业计划竞赛校级选拔赛的通知", "2025-11-18"),
    (179, "关于举办旅游与酒店管理学院第二届导游风采大赛的通知", "2026-03-10"),
    (269, "关于开展会计学院第一届职业生涯人物访谈大赛的通知", "2026-01-22"),
    (313, "关于开展湖北经济学院第二十三届\"藏龙杯\"健康之星心理知识大赛会计学院院赛的通知", "2025-10-24"),
    (328, "会计学院关于开展\"传承红色基因，续写青春华章\"主题微团课比赛的通知", "2025-10-10"),
    (400, "会计学院2025年红色文化科普讲解案例大赛选拔通知", "2025-03-14"),
    (404, "关于开展会计学院第一届心理健康教育微课大赛作品征集的通知", "2025-02-21"),
    (417, "第十二届全国大学生能源经济学术创意大赛湖北赛区湖北经济学院校赛通知", "2026-03-25"),
    (436, "关于组织参加2026年全国大学生统计建模大赛（本科生组）的通知", "2026-03-17"),
    (437, "关于举办\"正大杯\"第十六届全国大学生市场调查与分析大赛（本科生组）湖北经济学院选拔赛的通知", "2026-03-16"),
    (476, "关于举办2026年全国大学生英语竞赛湖北赛区初赛的通知", "2025-12-18"),
    (533, "湖北经济学院关于组织学生参加第十六届全国大学生市场调查与分析大赛的通知", "2025-09-30"),
    (594, "关于举办2025年（第二届）大学生数据要素素质大赛的通知", "2025-07-02"),
    (613, "关于2025年\"数据要素×\"大赛湖北经济学院校赛通知", "2025-05-28")
]

def test_user_contests():
    """
    测试用户提供的竞赛通知是否被正确筛选
    """
    # 连接数据库
    conn = sqlite3.connect('d:\ContestTrace_Project\ContestTrace\data\contest_trace_raw.db')
    cursor = conn.cursor()
    
    # 初始化过滤器
    filter = CompetitionFilter()
    
    # 测试结果
    results = []
    passed = 0
    failed = 0
    
    for contest_id, expected_title, expected_date in user_contests:
        # 从数据库中获取该ID的通知
        cursor.execute("SELECT id, title, content, publish_time FROM raw_notices WHERE id = ?", (contest_id,))
        row = cursor.fetchone()
        
        if row:
            notice_id, title, content, publish_date = row
            # 测试筛选
            is_contest = filter.is_contest(title, content)
            
            if is_contest:
                passed += 1
                results.append((contest_id, title, "通过", publish_date))
                logger.info(f"ID {contest_id}: {title} - 通过")
            else:
                failed += 1
                results.append((contest_id, title, "失败", publish_date))
                logger.error(f"ID {contest_id}: {title} - 失败")
        else:
            failed += 1
            results.append((contest_id, expected_title, "未找到", expected_date))
            logger.error(f"ID {contest_id}: {expected_title} - 未找到")
    
    # 关闭数据库连接
    conn.close()
    
    # 输出结果
    print("\n测试结果汇总：")
    print(f"总测试数: {len(user_contests)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {passed/len(user_contests)*100:.2f}%")
    
    print("\n失败的竞赛通知：")
    for result in results:
        if result[2] != "通过":
            print(f"ID: {result[0]}, 标题: {result[1]}, 状态: {result[2]}, 发布日期: {result[3]}")

if __name__ == "__main__":
    test_user_contests()
