#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析用户提供的竞赛公告
"""

import sqlite3
from contesttrace.core.filter.competition_filter import CompetitionFilter

# 用户提供的竞赛公告列表
user_contests = [
    '第31届中国日报社 "21世纪杯"全国英语演讲比赛湖北经济学院校园选拔赛通知',
    '关于举行2026年（19届）中国大学生计算机设计大赛湖北经济学院校赛的通知',
    '蓝桥杯全国大学生软件和信息技术专业人才大赛校级比赛通知',
    '湖北经济学院关于组织学生参加2025年全国大学生数学竞赛选拔测试的通知',
    '关于举办"正大杯"第十六届全国大学生市场调查与分析大赛（本科生组）湖北经济学院选拔赛的通知',
    '湖北经济学院关于组织学生参加2026年"华中杯"大学生数学建模挑战赛通知',
    '湖北经济学院关于组织学生参加第十六届全国大学生市场调查与分析大赛的通知',
    '关于组织参加2026年全国大学生统计建模大赛（本科生组）的通知',
    '湖北经济学院关于组织学生参加2025年全国大学生数学建模竞赛校内选拔赛通知',
    '关于组织参加2025年（第十一届）全国大学生统计建模大赛（本科生组）的通知',
    '2026年第十届"米兰设计周-中国高校设计学科师生优秀作品展"学科竞赛通知',
    '2026年第十七届蓝桥杯全国软件和信息技术专业人才大赛视觉艺术设计赛通知',
    '关于举行2026年（19届）中国大学生计算机设计大赛湖北经济学院校赛的通知',
    '关于举办湖北经济学院第三届"浩然杯" 读书演讲大赛的通知',
    '关于举办2026年"挑战杯"大学生 创业计划竞赛校级选拔赛的通知',
    '关于举办旅游与酒店管理学院第二届导游风采大赛的通知',
    '关于开展会计学院第一届职业生涯人物访谈大赛的通知',
    '关于开展湖北经济学院第二十三届"藏龙杯"健康之星心理知识大赛会计学院院赛的通知',
    '会计学院关于开展"传承红色基因，续写青春华章"主题微团课比赛的通知',
    '会计学院2025年红色文化科普讲解案例大赛选拔通知',
    '关于开展会计学院第一届心理健康教育微课大赛作品征集的通知',
    '第十二届全国大学生能源经济学术创意大赛湖北赛区湖北经济学院校赛通知',
    '关于组织参加2026年全国大学生统计建模大赛（本科生组）的通知',
    '关于举办"正大杯"第十六届全国大学生市场调查与分析大赛（本科生组）湖北经济学院选拔赛的通知',
    '关于举办2026年全国大学生英语竞赛湖北赛区初赛的通知',
    '湖北经济学院关于组织参加第十六届全国大学生市场调查与分析大赛的通知',
    '关于举办2025年（第二届）大学生数据要素素质大赛的通知',
    '关于2025年"数据要素×"大赛湖北经济学院校赛通知',
    '关于举办中国国际大学生创新大赛( 2025）湖北经济学院选拔赛的通知',
    '关于举办湖北经济学院第六届"藏龙杯"经典诵读与写作大赛的通知',
    '关于举办"正大杯"第十五届全国大学生市场调查与分析大赛（本科生组）湖北经济学院选拔赛的通知',
    '关于举办第十五届全国大学生电子商务"创新、创意及创业"挑战赛湖北经济学院校级选拔赛的通知',
    '关于举办2025年全国大学生英语竞赛湖北赛区初赛的通知'
]

def analyze_user_contests():
    """
    分析用户提供的竞赛公告
    """
    try:
        # 连接原始公告数据库
        conn = sqlite3.connect('data/contest_trace_raw.db')
        cursor = conn.cursor()
        
        # 创建筛选器实例
        filter = CompetitionFilter()
        
        found_count = 0
        not_found = []
        filtered_in = []
        filtered_out = []
        
        print("分析用户提供的竞赛公告：")
        print("-" * 150)
        
        for i, user_contest in enumerate(user_contests, 1):
            # 查找原始公告
            cursor.execute('SELECT id, title, content FROM raw_notices WHERE title = ?', (user_contest,))
            result = cursor.fetchone()
            
            if result:
                notice_id, title, content = result
                found_count += 1
                
                # 检查是否被筛选为竞赛
                is_contest = filter.is_contest(title, content)
                if is_contest:
                    filtered_in.append((i, title))
                    print(f"{i}. 找到且被筛选为竞赛: {title}")
                else:
                    filtered_out.append((i, title))
                    print(f"{i}. 找到但未被筛选为竞赛: {title}")
            else:
                not_found.append((i, user_contest))
                print(f"{i}. 未找到: {user_contest}")
        
        conn.close()
        
        print("-" * 150)
        print(f"统计：共 {len(user_contests)} 条竞赛公告，其中 {found_count} 条存在于原始公告数据库中")
        print(f"在找到的 {found_count} 条中，{len(filtered_in)} 条被筛选为竞赛，{len(filtered_out)} 条未被筛选为竞赛")
        
        if not_found:
            print("\n未找到的竞赛公告：")
            for i, contest in not_found:
                print(f"{i}. {contest}")
        
        if filtered_out:
            print("\n未被筛选为竞赛的公告：")
            for i, contest in filtered_out:
                print(f"{i}. {contest}")
        
    except Exception as e:
        print(f"分析竞赛公告失败: {e}")

if __name__ == '__main__':
    analyze_user_contests()
