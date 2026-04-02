# ContestTrace 2.0 — 竞赛信息智能采集与自动化平台

面向高校竞赛通知的**多源爬取 → 结构化解析 → 去重入库 → 数据处理/标签 → 可选大模型推荐 → Streamlit 可视化 → 导出与自动化**的一体化方案。默认启用 **湖北经济学院团委** 站点（`config/sites.yaml`），其它站点可按 DOM 规则扩展。

## 核心特性

- **智能编码**：`charset-normalizer` + UTF-8 优先策略 + 多编码回退，全链路减少中文乱码（见 `encoding_fixer.py`）。
- **多源爬虫**：`config/sites.yaml` 配置化；robots.txt 合规；随机 UA；延时 **≥1.5s**；支持代理/Cookie（环境变量）；断点续爬；附件下载。
- **SQLite**：URL 唯一去重；用户画像、收藏、订阅、推荐反馈等扩展表。
- **Streamlit Web**：列表/筛选/详情/看板/个人中心/推荐/导出。
- **GitHub Actions**：定时或手动爬取并更新 `data/reports/latest_snapshot.csv`（见 `GHA_DEPLOY.md`）。

## 快速开始

```bash
python -m pip install -r requirements.txt
python check_env.py
python run_app.py          # 终端主菜单
python run_web.py          # Web 界面（Streamlit）
```

Windows 可继续双击 `run.bat`；Mac/Linux 使用 `run.sh`。

## 目录结构（摘要）

```
config/           config.yaml, sites.yaml, model_config.yaml
src/contesttrace/ 核心包（爬虫、DB、编码、ML、推荐、web）
data/             数据库、附件、训练样本、CI 快照（部分已 .gitignore）
scripts/          crawl_and_snapshot, gha_setup, train_ml
tests/            test_encoding.py
.github/workflows/ crawl.yml
```

## 文档

| 文件 | 说明 |
|------|------|
| `新手运行说明.md` | 零基础安装与运行 |
| `配置说明.md` | 主配置说明 |
| `GHA_DEPLOY.md` | GitHub Actions 部署 |
| `API文档.md` | 模块级 API |
| `学术研究文档.md` | 方案与参考文献（示例） |

## 合规声明

数据仅用于学习研究；请遵守目标站点 robots 与使用条款；勿高频抓取。
