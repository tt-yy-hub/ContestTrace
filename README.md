# 湖北经济学院团委竞赛信息追踪系统（ContestTrace）

本项目是一套“新手零修改直接运行”的竞赛公告追踪工具，面向 `https://tw.hbue.edu.cn/` 团委官网 `通知公告` 栏目实现完整闭环：

- **自动分页爬取**：按页抓取通知列表与详情页
- **智能筛选**：用可配置关键词筛出“竞赛类公告”
- **全字段结构化解析**：标题/时间/正文 + 竞赛字段（尽可能提取）
- **严格去重入库**：以详情页URL为唯一键写入SQLite
- **可视化查询**：控制台菜单查询/按ID看全文/统计
- **一键导出**：Excel(.xlsx) / CSV

## 快速开始（推荐新手）

- **Windows**：双击运行 `run.bat`
- **Mac/Linux**：

```bash
chmod +x run.sh
./run.sh
```

也可以在终端直接运行（跨平台通用）：

```bash
python run_app.py
```

## 目录结构（工程化）

```
ContestTrace/
  config/                # 统一配置中心（新手只改这里）
    config.yaml
  src/contesttrace/      # 核心代码层
    __main__.py          # 主菜单入口
    config_center.py     # 配置中心
    utils.py             # 工具函数库（请求/日志/文本/校验）
    db.py                # SQLite数据库模块
    scraper.py           # 主爬虫程序
    exporter.py          # 导出模块（Excel/CSV）
    query_cli.py         # 控制台查询脚本
    env_check.py         # 环境检查脚本
  data/                  # 数据目录（数据库默认在此）
  logs/                  # 日志目录（自动生成，已忽略）
  cache/                 # 缓存目录（预留，已忽略）
  static_pages/          # 原始HTML（排查DOM变更，已忽略）
  exports/               # 导出文件（已忽略）
  requirements.txt
  新手运行说明.md
  配置说明.md
  run.bat
  run.sh
```

## 注意事项（合规与稳定）

- **合规反爬**：请求延时默认 ≥ 1 秒且随机；支持重试与超时；避免高频对目标站点造成压力  
- **DOM规则可配置**：当官网结构变化时，优先通过 `config/config.yaml` 调整解析规则  
- **严格去重**：以 `detail_url` 为唯一键，绝不重复写入同一条公告  

## 文档

- `新手运行说明.md`：从打开Cursor到运行/查询/导出，零基础一步一图式流程
- `配置说明.md`：配置文件每个参数详细解释（新手自定义不改代码）

# ContestTrace - 湖北经济学院竞赛信息追踪

一个自动爬取、筛选、存储湖北经济学院团委官网竞赛通知的 Python 小工具。

## 项目目录结构