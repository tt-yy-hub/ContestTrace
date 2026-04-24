# ContestTrace - 学科竞赛信息聚合平台

## 项目简介

ContestTrace是一个专注于聚合和管理高校学科竞赛信息的平台，通过爬虫技术自动收集各学院和部门的竞赛通知，经过智能筛选和处理后，为用户提供结构化、易访问的竞赛信息。

## 功能特点

- **自动爬虫**：定期爬取各学院和部门的通知公告
- **智能筛选**：通过关键词匹配和规则判断，准确识别竞赛相关通知
- **数据汇总**：将分散的原始数据汇总为统一的数据库
- **前端展示**：提供直观的前端界面，方便用户浏览和筛选竞赛信息
- **数据导出**：支持将竞赛数据导出为CSV格式，方便进一步分析

## 项目结构

```
ContestTrace/
├── contesttrace/          # 核心代码
│   ├── core/             # 核心功能模块
│   │   ├── filter/       # 竞赛筛选逻辑
│   │   ├── spiders/      # 爬虫模块
│   │   ├── storage/      # 数据存储
│   │   └── utils/        # 工具函数
│   └── frontend/         # 前端界面
├── config/               # 配置文件
├── data/                 # 数据存储目录
├── scripts/              # 辅助脚本
├── .github/              # GitHub Actions 配置
├── run.bat               # 主运行脚本
├── run.py                # Python 主脚本
└── requirements.txt      # 依赖配置
```

## 快速开始

### 环境要求

- Python 3.7+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行步骤

1. **运行爬虫**：爬取各学院和部门的通知
2. **汇总数据**：将分散的原始数据汇总为统一的数据库
3. **筛选数据**：筛选出竞赛相关的通知
4. **启动前端**：启动前端服务器，访问竞赛信息

### 接入本地大模型（AI 小助手重排）

项目已支持 OpenAI 兼容接口（可对接本地 Ollama）。

1. 复制 `.env.example` 为 `.env`，并确认：

```bash
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://127.0.0.1:11434/v1
OPENAI_MODEL=qwen2.5:1.5b
AI_API_HOST=127.0.0.1
AI_API_PORT=8001
```

2. 启动 AI 重排后端：

```bash
python contesttrace/api_server.py
```

3. 启动前端：

```bash
cd contesttrace/frontend
python -m http.server 8000
```

4. 验证：
   - 健康检查：`http://127.0.0.1:8001/health`
   - 前端页面：`http://127.0.0.1:8000`
   - AI 助手默认调用：`http://127.0.0.1:8001/api/ai/rerank`

说明：模型不可用时，会自动降级到规则重排，保证推荐稳定可用。

### 让 GitHub Pages 也能调用大模型（公网 API）

如果前端部署在 GitHub Pages（例如 [ContestTrace](https://tt-yy-hub.github.io/ContestTrace/)），本地 `127.0.0.1` 模型接口无法被网页直接访问。需要把后端 API 部署到公网。

#### 1) 部署后端到 Render（推荐）

本仓库已提供：

- `render.yaml`
- `Procfile`
- `gunicorn` 依赖

在 Render 新建 Web Service，连接本仓库后可直接识别配置。需要设置环境变量：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`（你的大模型 OpenAI 兼容地址）
- `OPENAI_MODEL`（例如 `qwen2.5:1.5b`）

部署成功后会得到公网地址，例如：

`https://contesttrace-ai-rerank.onrender.com`

健康检查：

`https://contesttrace-ai-rerank.onrender.com/health`

#### 2) 前端配置公网 API

编辑 `contesttrace/frontend/js/runtime-config.js`：

```js
var PUBLIC_API_BASE = "https://contesttrace-ai-rerank.onrender.com";
```

前端会自动拼接为：

`https://contesttrace-ai-rerank.onrender.com/api/ai/rerank`

#### 3) 发布前端到 GitHub Pages

将修改推送到 GitHub 对应分支后，GitHub Pages 页面即可调用公网大模型重排接口。

### 一键运行

运行 `run.bat` 文件，选择相应的操作：

```
=======================================
       ContestTrace Menu
=======================================
1. Install Dependencies
2. Run Spiders
3. Merge Raw Databases
4. Filter Data
5. Export Data
6. Start Frontend Server
7. Run Full Process (Spiders->Merge->Filter->Frontend)
0. Exit
=======================================
```

## 核心模块

### 1. 爬虫模块

负责从各学院和部门的网站爬取通知公告，支持定期更新。

### 2. 筛选模块

通过关键词匹配和规则判断，从原始通知中筛选出竞赛相关的信息。

### 3. 存储模块

管理数据的存储和检索，包括原始通知和筛选后的竞赛信息。

### 4. 前端模块

提供直观的用户界面，支持竞赛信息的浏览、搜索和筛选。

## 数据流程

1. **爬虫采集** → 2. **原始数据存储** → 3. **数据汇总** → 4. **智能筛选** → 5. **竞赛数据存储** → 6. **前端展示**

## 配置说明

- **config/sites.yaml**：配置爬虫目标网站
- **config/config.yaml**：主配置文件
- **config/model_config.yaml**：模型配置文件

## 技术栈

- **后端**：Python、SQLite
- **前端**：HTML、CSS、JavaScript
- **爬虫**：Requests、BeautifulSoup
- **部署**：GitHub Actions

## 贡献指南

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件

## 联系方式

如有问题或建议，请通过 GitHub Issues 提交。
