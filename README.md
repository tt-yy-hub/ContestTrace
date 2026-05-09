# ContestTrace——竞赛信息智能采集与自动化平台

## 项目简介

ContestTrace是一个专注于聚合和管理高校学科竞赛信息的平台，通过爬虫技术自动收集各学院和部门的竞赛通知，经过智能筛选和处理后，为用户提供结构化、易访问的竞赛信息。

## 功能特点

- **自动爬虫**：定期爬取各学院和部门的通知公告
- **智能筛选**：通过关键词匹配和规则判断，准确识别竞赛相关通知
- **数据汇总**：将分散的原始数据汇总为统一的数据库
- **前端展示**：提供直观的前端界面，方便用户浏览和筛选竞赛信息
- **数据导出**：支持将竞赛数据导出为CSV格式，方便进一步分析
- **AI助手**：支持本地大模型重排功能，提供更智能的推荐

## 技术栈

- **后端**：Python 3.7+、SQLite
- **前端**：HTML、CSS、JavaScript
- **爬虫**：Requests、BeautifulSoup
- **部署**：GitHub Actions

## 快速开始

### 环境要求

- Python 3.7+
- pip
- Windows/Linux/macOS

### 启动菜单

运行以下命令打开主菜单：

```bash
# Windows
run.bat

# Linux/macOS
python run.py
```

菜单选项如下：

```
=======================================
      ContestTrace Menu
=======================================
1. Install Dependencies
2. Run Spiders Only
3. Merge Raw Databases
4. Filter Data
5. Export Data to Frontend
6. Start Frontend Server
7. Run Full Process (Spiders-Merge-Filter-Export-Frontend)
8. Start AI Rerank API Server
0. Exit
=======================================
```

### 推荐首次运行流程

**首次运行或更新数据时，推荐选择选项 `7`（全流程）**

1. 选择 `1` 安装依赖（如首次运行）
2. 选择 `7` 运行全流程（自动完成以下步骤）
3. 浏览器访问 `http://localhost:8000`

### 各选项说明

| 选项 | 功能 | 说明 |
|------|------|------|
| `1` | Install Dependencies | 安装Python依赖包 |
| `2` | Run Spiders Only | 只运行爬虫（增量抓取各学院通知） |
| `3` | Merge Raw Databases | 合并原始数据库（汇总各学院数据到 `contest_trace_raw.db`） |
| `4` | Filter Data | 筛选数据（生成竞赛库 `competition.db`） |
| `5` | Export Data to Frontend | 导出数据到前端（生成 `frontend/data/contests.json`） |
| `6` | Start Frontend Server | 启动前端服务器（访问 `http://localhost:8000`） |
| `7` | Run Full Process | 全流程：爬虫→合并→筛选→导出→启动前端 |
| `8` | Start AI Rerank API Server | 启动AI重排后端API（端口8001，可选） |
| `0` | Exit | 退出程序 |

### 分步运行说明

如果需要分步执行，按以下顺序：

```bash
1 → 2 → 3 → 4 → 5 → 6
```

- `2`：运行爬虫抓取最新通知
- `3`：将各学院数据汇总到原始数据库
- `4`：从原始数据中筛选出竞赛相关通知
- `5`：导出竞赛数据到前端目录
- `6`：启动前端服务器

### 重要提示

> **前端必须执行过选项 `5` 或 `7` 才能看到数据**

如果前端页面空白，请确认已执行过导出步骤，并检查 `frontend/data/contests.json` 文件存在且大小不为0。

## 项目结构

```
ContestTrace/
├── ContestTrace-main/      # 爬虫模块（各学院爬虫脚本）
│   ├── jiaowuchu/          # 教务处爬虫
│   ├── gongshang/          # 工商管理学院爬虫
│   ├── kuaiji/             # 会计学院爬虫
│   ├── xinguan/            # 信息管理学院爬虫
│   └── ...                 # 其他学院爬虫（共14个）
├── contesttrace/          # 核心代码
│   ├── core/             # 核心功能模块
│   │   ├── database/     # 数据库操作
│   │   ├── exporter/     # 数据导出
│   │   ├── filter/       # 竞赛筛选逻辑
│   │   ├── recommender/  # 推荐系统
│   │   └── utils/        # 工具函数
│   ├── frontend/         # 前端界面
│   │   ├── css/          # 样式文件
│   │   ├── js/           # JavaScript文件
│   │   └── data/         # 前端数据
│   └── api_server.py     # AI重排API服务器
├── config/               # 配置文件（网站配置、模型配置等）
├── data/                 # 数据存储目录（SQLite数据库）
├── .github/workflows/    # GitHub Actions配置（定时爬虫）
├── .env.example          # 环境变量示例
├── run.bat               # Windows主运行脚本
├── run.py                # Python主脚本
└── requirements.txt      # 依赖配置
```

## 配置说明

### 环境变量配置（非必须）

复制 `.env.example` 为 `.env`，根据需要修改配置项。默认配置即可运行基本功能。

主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `PUBLIC_API_BASE` | AI重排API地址 | 空（使用本地Ollama） |

### 配置文件说明

| 文件 | 说明 |
|------|------|
| `config/sites.yaml` | 爬虫目标网站配置 |
| `config/config.yaml` | 主配置文件 |
| `config/model_config.yaml` | 模型配置文件 |

## 核心模块说明

### 1. 爬虫模块（ContestTrace-main）

负责从各学院和部门的网站爬取通知公告，支持定期更新。每个学院都有独立的爬虫脚本和数据存储。

### 2. 筛选模块

通过关键词匹配和规则判断，从原始通知中筛选出竞赛相关的信息。

### 3. 存储模块

管理数据的存储和检索，包括原始通知和筛选后的竞赛信息。

### 4. 推荐模块

基于用户画像和竞赛属性，为用户推荐个性化的竞赛信息，支持大模型重排。

### 5. 前端模块

提供直观的用户界面，支持竞赛信息的浏览、搜索和筛选。

## 关于AI助手

### 本地使用（需要Ollama）

1. 安装 Ollama
2. 下载模型：`ollama pull qwen2.5:1.5b`
3. 选择菜单选项 `8` 启动AI重排API服务器
4. 前端将自动调用本地API进行推荐重排

### AI不可用时

当大模型不可用时，系统会自动降级到规则重排，保证推荐功能稳定可用。

## 常见问题（FAQ）

### Q1：前端页面空白，没有竞赛数据怎么办？

A：请确保已执行过选项 `5`（导出数据）或 `7`（全流程），并确认 `frontend/data/contests.json` 文件存在且大小不为0。

### Q2：爬虫运行后没有抓到任何通知？

A：检查网络连接，确认 `config/sites.yaml` 中的目标网站可访问；某些网站可能需要配置Cookie（参见 `.env.example` 中的 `SITE_COOKIES_JSON`）。

### Q3：AI助手不工作？

A：先执行选项 `8` 启动API服务器，并确保前端配置了正确的API地址（默认 `http://127.0.0.1:8001`）；若无大模型，系统会自动降级，不影响主功能。

### Q4：如何更新竞赛数据？

A：运行 `run.bat`，选择选项 `2`（运行爬虫）可增量抓取最新通知；或选择选项 `7`（全流程）重新执行整个数据处理流程。

## 数据流程

```
爬虫抓取 → 原始数据库 → 合并汇总 → 筛选竞赛 → 导出前端 → 前端展示
   (2)        (3)          (4)        (5)       (6)
```

## 部署说明

### GitHub Pages部署

前端目录 `contesttrace/frontend` 可直接部署到GitHub Pages。

### GitHub Actions自动更新

`.github/workflows/crawl-and-filter.yml` 配置了每日自动爬取和筛选功能。

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件

## 联系方式

如有问题或建议，请通过 GitHub Issues 提交。