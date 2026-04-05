# ContestTrace - 竞赛信息智能采集与自动化平台

## 项目简介

ContestTrace是一个专注于竞赛信息智能采集、处理和展示的自动化平台。它能够从多个来源定向爬取竞赛信息，进行智能解析和筛选，然后通过纯静态前端展示给用户，支持个性化推荐、收藏、订阅和数据导出等功能。

## 核心功能

### 1. 多源定向爬虫
- 支持湖北经济学院团委官网等多个数据源
- 自动分页、自动重试、合规反爬
- 结构化抽取不少于15个竞赛核心字段

### 2. 智能解析与筛选
- 智能解析结构化字段
- 严格去重（以详情页URL为唯一键）
- 精准过滤非竞赛内容
- 机器学习辅助分类

### 3. 数据存储与处理
- SQLite轻量数据库存储
- 时间格式归一化
- 缺失值智能填充
- 关键词标签自动提取

### 4. 纯静态前端
- 支持GitHub Pages直接部署
- 竞赛列表/搜索/筛选
- 收藏功能
- 订阅关键词浏览器通知
- 截止时间倒计时提醒
- 一键导出CSV
- 个性化推荐
- 数据可视化看板
- 响应式适配手机/PC

### 5. 自动化与部署
- GitHub Actions定时自动爬取
- 手动触发爬取
- 自动更新静态数据文件

## 技术栈

- **后端**：Python 3.9+
- **前端**：HTML5, CSS3, JavaScript
- **数据库**：SQLite
- **爬虫**：Requests, BeautifulSoup4
- **机器学习**：scikit-learn
- **数据可视化**：Chart.js

## 快速开始

### 环境要求

- Python 3.9+
- pip 20.0+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 一键启动

#### Windows

双击 `run.bat` 文件即可启动。

#### Mac/Linux

```bash
chmod +x run.sh
./run.sh
```

### 手动运行

1. **爬取数据**

```bash
python run.py --crawl
```

2. **启动前端服务器**（可选）

```bash
python -m http.server 8000 --directory contesttrace/frontend
```

然后在浏览器中访问 `http://localhost:8000`。

## 项目结构

```
contesttrace/
├── core/                  # 核心模块
│   ├── spiders/           # 爬虫模块
│   ├── parsers/           # 解析器模块
│   ├── database/          # 数据库模块
│   ├── utils/             # 工具模块
│   ├── recommender/       # 推荐模块
│   └── exporter/          # 导出模块
├── frontend/              # 前端
│   ├── index.html         # 主页面
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件
│   └── data/              # 前端数据
├── data/                  # 数据存储
├── logs/                  # 日志文件
├── config/                # 配置文件
├── scripts/               # 脚本文件
└── docs/                  # 文档
```

## 配置说明

### 爬虫配置

在 `config/spiders.json` 中配置爬虫参数：

```json
{
  "spiders": [
    {
      "name": "湖北经济学院团委",
      "url": "http://youth.hbue.edu.cn/szll.htm",
      "enabled": true
    }
  ]
}
```

### 运行配置

在 `config/config.json` 中配置运行参数：

```json
{
  "crawl_interval": 86400,  // 爬取间隔（秒）
  "user_agents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
  ]
}
```

## GitHub Pages部署

1.  Fork本仓库
2.  在GitHub仓库设置中，启用GitHub Pages
3.  选择 `contesttrace/frontend` 目录作为发布源
4.  等待自动部署完成
5.  访问分配的GitHub Pages URL

## 常见问题

### 1. 爬虫被网站封禁

- 增加爬取间隔
- 使用更多的User-Agent
- 遵守robots.txt规则

### 2. 前端数据不更新

- 检查GitHub Actions是否正常运行
- 手动运行 `python run.py --crawl` 更新数据

### 3. 中文乱码

- 项目已实现统一智能编码识别函数，支持多种编码格式
- 所有文件均使用UTF-8编码

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

本项目采用MIT许可证。
