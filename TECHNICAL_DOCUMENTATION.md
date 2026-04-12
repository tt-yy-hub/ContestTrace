# ContestTrace 技术文档

## 1. 系统架构

ContestTrace采用模块化设计，将系统分为爬虫、数据处理、存储和前端四个核心模块，各模块之间通过明确的接口进行通信。

### 1.1 模块结构

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
```

### 1.2 数据流

1. **爬虫采集**：从各学院和部门网站爬取通知公告
2. **原始数据存储**：将爬取的原始数据存储到独立的SQLite数据库
3. **数据汇总**：将多个原始数据库汇总为一个主原始数据库
4. **智能筛选**：通过关键词匹配和规则判断，筛选出竞赛相关通知
5. **竞赛数据存储**：将筛选后的竞赛数据存储到竞赛数据库
6. **前端展示**：将竞赛数据导出为JSON格式，供前端展示

## 2. 核心模块实现

### 2.1 爬虫模块

爬虫模块负责从各学院和部门的网站爬取通知公告，支持定期更新。

#### 2.1.1 实现方式

- **基础爬虫**：基于 `BaseSpider` 类，提供通用的爬取功能
- **学院爬虫**：继承基础爬虫，针对每个学院的网站结构进行定制
- **爬虫管理**：通过 `SpiderManager` 类管理多个爬虫的执行

#### 2.1.2 关键文件

- `contesttrace/core/spiders/base_spider.py`：基础爬虫类
- `contesttrace/core/spiders/spider_manager.py`：爬虫管理器
- `contesttrace/core/spiders/*.py`：各学院的具体爬虫实现

### 2.2 筛选模块

筛选模块通过关键词匹配和规则判断，从原始通知中筛选出竞赛相关的信息。

#### 2.2.1 实现方式

- **关键词匹配**：使用强竞赛词、次要关键词和排除关键词进行匹配
- **规则判断**：基于通知内容的特征进行规则判断
- **置信度计算**：根据关键词匹配和规则判断计算置信度

#### 2.2.2 关键文件

- `contesttrace/core/filter/competition_filter.py`：竞赛筛选核心逻辑

### 2.3 存储模块

存储模块管理数据的存储和检索，包括原始通知和筛选后的竞赛信息。

#### 2.3.1 实现方式

- **数据库管理**：通过 `DatabaseManager` 类管理数据库操作
- **表结构设计**：设计合理的表结构存储原始通知和竞赛信息
- **数据操作**：提供插入、更新、查询等数据操作功能

#### 2.3.2 关键文件

- `contesttrace/core/storage/db_manager.py`：数据库管理器

### 2.4 前端模块

前端模块提供直观的用户界面，支持竞赛信息的浏览、搜索和筛选。

#### 2.4.1 实现方式

- **HTML/CSS**：构建响应式的用户界面
- **JavaScript**：实现交互功能和数据处理
- **数据加载**：从JSON文件加载竞赛数据

#### 2.4.2 关键文件

- `contesttrace/frontend/index.html`：前端主页面
- `contesttrace/frontend/js/main.js`：前端主逻辑
- `contesttrace/frontend/js/data.js`：数据处理逻辑

## 3. 技术栈

| 类别 | 技术 | 用途 |
|------|------|------|
| 后端 | Python 3.7+ | 核心逻辑实现 |
| 数据库 | SQLite | 数据存储 |
| 爬虫 | Requests, BeautifulSoup | 网页爬取和解析 |
| 前端 | HTML, CSS, JavaScript | 用户界面构建 |
| 部署 | GitHub Actions | 自动化部署 |

## 4. 数据结构

### 4.1 原始通知表 (raw_notices)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | INTEGER | 自增主键 |
| title | TEXT | 通知标题 |
| url | TEXT | 通知链接 |
| source | TEXT | 通知来源 |
| publish_time | TEXT | 发布时间 |
| crawl_time | TEXT | 爬取时间 |
| deadline | TEXT | 截止时间 |
| category | TEXT | 通知类别 |
| organizer | TEXT | 组织者 |
| participants | TEXT | 参赛对象 |
| prize | TEXT | 奖项设置 |
| requirement | TEXT | 参赛要求 |
| contact | TEXT | 联系方式 |
| content | TEXT | 通知内容 |
| keywords | TEXT | 关键词 |
| tags | TEXT | 标签 |
| spider_name | TEXT | 爬虫名称 |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |

### 4.2 竞赛通知表 (competition_notices)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | INTEGER | 自增主键 |
| raw_notice_id | INTEGER | 原始通知ID |
| notice_url | TEXT | 通知链接 |
| title | TEXT | 通知标题 |
| publish_time | TEXT | 发布时间 |
| publisher | TEXT | 发布者 |
| content | TEXT | 通知内容 |
| source | TEXT | 通知来源 |
| filter_pass_time | TEXT | 筛选通过时间 |
| competition_name | TEXT | 竞赛名称 |
| competition_level | TEXT | 竞赛级别 |
| deadline | TEXT | 截止时间 |
| organizer | TEXT | 组织者 |
| participants | TEXT | 参赛对象 |
| prize | TEXT | 奖项设置 |
| requirement | TEXT | 参赛要求 |
| contact | TEXT | 联系方式 |
| confidence | REAL | 置信度 |

## 5. 配置文件

### 5.1 sites.yaml

配置爬虫目标网站，包括网站URL、爬取规则等。

### 5.2 config.yaml

主配置文件，包括爬虫配置、数据库配置等。

### 5.3 model_config.yaml

模型配置文件，包括筛选规则、关键词配置等。

## 6. 运行流程

### 6.1 完整流程

1. **安装依赖**：`pip install -r requirements.txt`
2. **运行爬虫**：`call run_teammate_spiders.bat`
3. **汇总数据**：`python create_raw_db.py`
4. **筛选数据**：`python filter_raw_to_competition.py`
5. **启动前端**：`python -m http.server 8000`（在frontend目录下）

### 6.2 一键运行

运行 `run.bat` 文件，选择相应的操作：

- 1. Install Dependencies
- 2. Run Spiders
- 3. Merge Raw Databases
- 4. Filter Data
- 5. Export Data
- 6. Start Frontend Server
- 7. Run Full Process (Spiders->Merge->Filter->Frontend)
- 0. Exit

## 7. 性能优化

### 7.1 爬虫优化

- **并发爬取**：使用多线程或异步IO提高爬取效率
- **增量爬取**：只爬取新的通知，避免重复爬取
- **错误处理**：添加错误处理机制，提高爬虫的稳定性

### 7.2 筛选优化

- **关键词匹配**：使用高效的关键词匹配算法
- **规则优化**：优化筛选规则，提高筛选准确性
- **批量处理**：批量处理通知，提高筛选效率

### 7.3 存储优化

- **索引优化**：为数据库表添加适当的索引
- **数据压缩**：压缩存储大文本字段
- **批量操作**：使用批量操作减少数据库访问次数

## 8. 部署与维护

### 8.1 本地部署

1. 克隆仓库：`git clone <repository-url>`
2. 安装依赖：`pip install -r requirements.txt`
3. 运行 `run.bat` 启动系统

### 8.2 自动化部署

使用 GitHub Actions 实现自动化部署，定期运行爬虫和更新数据。

### 8.3 维护建议

- **定期更新**：定期运行爬虫，保持数据的新鲜度
- **监控系统**：监控系统运行状态，及时发现和解决问题
- **数据备份**：定期备份数据库，防止数据丢失

## 9. 扩展与定制

### 9.1 添加新爬虫

1. 在 `contesttrace/core/spiders/` 目录下创建新的爬虫文件
2. 继承 `BaseSpider` 类，实现必要的方法
3. 在 `SpiderManager` 中注册新爬虫

### 9.2 定制筛选规则

修改 `contesttrace/core/filter/competition_filter.py` 文件，调整关键词和规则。

### 9.3 扩展前端功能

修改 `contesttrace/frontend/` 目录下的文件，添加新的功能和界面元素。

## 10. 故障排除

### 10.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 爬虫运行失败 | 网络问题或网站结构变化 | 检查网络连接，更新爬虫代码 |
| 筛选结果不准确 | 关键词配置不当 | 调整关键词和规则 |
| 前端无法加载数据 | 数据格式错误 | 检查数据导出过程 |
| 数据库连接失败 | 数据库文件损坏 | 重建数据库 |

### 10.2 日志系统

系统使用 Python 的 logging 模块记录运行日志，日志文件存储在 `logs/` 目录下。

## 11. 未来发展

### 11.1 功能扩展

- **用户系统**：添加用户注册和登录功能
- **通知系统**：添加竞赛提醒和通知功能
- **推荐系统**：基于用户兴趣推荐相关竞赛
- **数据分析**：添加竞赛数据分析和可视化功能

### 11.2 技术升级

- **数据库迁移**：考虑使用更强大的数据库系统
- **前端框架**：使用现代前端框架提升用户体验
- **API接口**：提供 RESTful API 接口
- **容器化部署**：使用 Docker 容器化部署系统

## 12. 总结

ContestTrace是一个功能完整、架构清晰的学科竞赛信息聚合平台，通过自动化的爬虫和智能的筛选系统，为用户提供准确、及时的竞赛信息。系统采用模块化设计，易于扩展和维护，具有良好的可扩展性和可定制性。

通过不断的优化和扩展，ContestTrace有望成为高校竞赛信息管理的重要工具，帮助学生和教师更便捷地获取和管理竞赛信息，促进学科竞赛的发展。
