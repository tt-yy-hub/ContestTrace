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
