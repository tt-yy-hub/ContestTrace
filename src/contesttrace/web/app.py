# -*- coding: utf-8 -*-
"""
ContestTrace Streamlit 轻量化 Web 前端。

功能：列表检索、筛选、详情、收藏、订阅、推荐反馈、图表看板、导出 Excel/CSV/PDF。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# 确保项目根在路径中（streamlit 直接启动时）
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from contesttrace.config_center import load_config
from contesttrace.data_processor import run_batch_clean, run_jieba_tagging
from contesttrace.db import SQLiteDB
from contesttrace.exporter import export_data
from contesttrace.recommender import recommend_contests
from contesttrace.utils import configure_stdio_utf8, setup_logger

configure_stdio_utf8()

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="ContestTrace 竞赛平台",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_runtime():
    """缓存配置与数据库连接（进程内单例）。"""

    cfg = load_config()
    logger = setup_logger(cfg.paths.logs_dir)
    db = SQLiteDB(cfg.paths.db_path, cfg.database.get("table_name") or "contest_announcements")
    db.init_db(logger)
    return cfg, logger, db


def main() -> None:
    cfg, logger, db = get_runtime()

    st.markdown(
        """
        <style>
        .block-container { padding-top: 1rem; max-width: 1200px; }
        @media (max-width: 768px) {
            .block-container { padding-left: 0.5rem; padding-right: 0.5rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("ContestTrace 竞赛信息智能采集与自动化平台")
    st.caption("数据来源于配置的官方站点，仅供学习研究使用。")

    user_id = st.sidebar.number_input("用户 ID（默认本地用户）", min_value=1, value=1, step=1)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["竞赛大厅", "数据看板", "个人中心", "智能推荐", "数据维护", "导出"]
    )

    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            kw = st.text_input("标题/正文关键词", "")
        with c2:
            level = st.text_input("级别关键词", "")
        with c3:
            cat = st.text_input("类别关键词", "")
        d1, d2 = st.columns(2)
        with d1:
            sd = st.text_input("发布开始日期 YYYY-MM-DD", "")
        with d2:
            ed = st.text_input("发布结束日期 YYYY-MM-DD", "")

        rows = db.query_filtered(
            keyword=kw, level=level, category=cat, start_date=sd, end_date=ed, limit=300
        )
        st.write(f"共 {len(rows)} 条")
        if rows:
            show = pd.DataFrame(rows)[
                [k for k in ["id", "title", "publish_date", "competition_level", "competition_category", "source_site_id"] if k in rows[0]]
            ]
            st.dataframe(show, use_container_width=True, hide_index=True)
            pick = st.selectbox("选择 ID 查看详情", options=[r["id"] for r in rows])
            if pick:
                row = db.get_by_id(int(pick))
                if row:
                    st.subheader(row.get("title"))
                    st.write(
                        {
                            "发布时间": row.get("publish_date"),
                            "来源站点": row.get("source_site_id"),
                            "级别": row.get("competition_level"),
                            "类别": row.get("competition_category"),
                            "详情链接": row.get("detail_url"),
                        }
                    )
                    st.text_area("正文摘要", (row.get("full_text") or "")[:4000], height=320)
                    att = row.get("attachments_json")
                    if att:
                        try:
                            for a in json.loads(att):
                                p = Path(a.get("local_path", ""))
                                if p.exists():
                                    with p.open("rb") as f:
                                        st.download_button(
                                            f"下载 {a.get('filename')}",
                                            f.read(),
                                            file_name=a.get("filename") or "file",
                                        )
                        except Exception:
                            st.caption("附件解析失败")
                    if st.button("加入收藏", key=f"fav_{pick}"):
                        db.add_favorite(int(user_id), int(pick), logger)
                        st.success("已收藏")

    with tab2:
        st.subheader("可视化看板")
        stats = db.stats()
        st.metric("竞赛公告总数", stats.get("total", 0))
        bm = stats.get("by_month") or []
        if bm:
            dfm = pd.DataFrame(bm)
            fig = px.bar(dfm, x="month", y="count", title="按月数量")
            st.plotly_chart(fig, use_container_width=True)
        all_rows = db.query_all(limit=500)
        if all_rows:
            df = pd.DataFrame(all_rows)
            if "competition_level" in df.columns:
                vc = df["competition_level"].fillna("未知").value_counts().reset_index()
                vc.columns = ["level", "count"]
                st.plotly_chart(px.pie(vc, names="level", values="count", title="级别分布"), use_container_width=True)

    with tab3:
        st.subheader("个人中心")
        prof_row = db.get_user_profile(int(user_id))
        prof = prof_row.get("profile", {}) if prof_row else {}
        major = st.text_input("专业", value=str(prof.get("major", "")))
        grade = st.text_input("年级", value=str(prof.get("grade", "")))
        interests = st.text_input("兴趣标签（逗号分隔）", value=",".join(prof.get("interests") or []))
        if st.button("保存画像"):
            new_p = {
                "major": major.strip(),
                "grade": grade.strip(),
                "interests": [x.strip() for x in interests.split(",") if x.strip()],
            }
            db.save_user_profile(int(user_id), new_p, logger)
            st.success("已保存")

        st.write("我的收藏 ID：", db.list_favorites(int(user_id)))
        st.divider()
        sk = st.text_input("订阅关键词", key="sub_kw")
        em = st.text_input("通知邮箱（可选）", key="sub_em")
        if st.button("添加订阅"):
            db.add_subscription(int(user_id), sk, em, logger)
            st.success("订阅已添加（邮件需配置 SMTP 环境变量）")

    with tab4:
        st.subheader("智能推荐")
        nl = st.text_area("自然语言描述你的情况", placeholder="例如：会计专业大二，想参加省级创新创业类竞赛")
        prof_row = db.get_user_profile(int(user_id)) or {}
        profile = prof_row.get("profile") or {}
        if st.button("生成推荐"):
            pool = db.query_all(limit=80)
            recs = recommend_contests(profile, pool, cfg.raw.get("model_config") or {}, logger, nl_query=nl)
            st.json(recs[:15])
            if recs and isinstance(recs[0], dict) and recs[0].get("contest_id"):
                cid = recs[0].get("contest_id")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("点赞本条推荐"):
                        db.add_recommend_feedback(int(user_id), int(cid), 1, nl, logger)
                        st.success("感谢反馈")
                with col_b:
                    if st.button("点踩本条推荐"):
                        db.add_recommend_feedback(int(user_id), int(cid), -1, nl, logger)
                        st.success("已记录")

    with tab5:
        st.subheader("数据维护")
        if st.button("运行批量清洗（级别/类别/时间归一化）"):
            n = run_batch_clean(db, logger, limit=500)
            st.success(f"处理完成，更新约 {n} 条")
        if st.button("提取关键词标签（jieba TF-IDF）"):
            n2 = run_jieba_tagging(db, logger, limit=300)
            st.success(f"标签更新约 {n2} 条")

    with tab6:
        st.subheader("导出")
        st.caption("中文内容建议优先导出 Excel/CSV（UTF-8）。如需 PDF，可在本地用 WPS/Office 打开 xlsx 后另存为 PDF。")
        fmt = st.radio("格式", ["xlsx", "csv"], horizontal=True)
        if st.button("导出当前库全量"):
            p = export_data(db, cfg.paths.exports_dir, logger, fmt=fmt, scope="all")
            st.success(f"已导出：{p}")


if __name__ == "__main__":
    main()
