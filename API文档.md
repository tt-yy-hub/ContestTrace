# ContestTrace API 说明（Python 模块级）

以下为面向二次开发者的常用入口（均在 `sys.path` 包含 `src` 后 `import contesttrace.xxx`）。

## 配置

- `contesttrace.config_center.load_config()` → `Config`  
  合并 `config/config.yaml`、`config/sites.yaml`、`config/model_config.yaml` 与可选 `config/local.json`，并加载 `.env`。

## 编码

- `contesttrace.encoding_fixer.smart_decode(raw_bytes, logger=None) -> (str, str)`  
  智能解码字节流，返回文本与选用编码标识；**所有 HTTP 文本响应在 `http_get_text` 中已统一调用**。

## 爬虫

- `contesttrace.scraper.run_crawl(cfg: Config) -> CrawlSummary`  
  多源爬取、附件下载、断点状态 `data/crawl_state.json`、robots 检查。

## 数据库

- `contesttrace.db.SQLiteDB`  
  `init_db`、`insert_one`、`query_filtered`、`get_by_id`、收藏/订阅/反馈等方法。

## 数据处理与标签

- `contesttrace.data_processor.run_batch_clean(db, logger, limit=500)`  
- `contesttrace.data_processor.run_jieba_tagging(db, logger, limit=200)`  

## 机器学习

- `contesttrace.ml_model.train_and_save(train_csv, model_path, logger)`  
- `contesttrace.ml_model.load_model(model_path, logger)`  
- `contesttrace.ml_model.predict_competition(model, text)`  

## 推荐

- `contesttrace.recommender.recommend_contests(profile, contests, model_cfg, logger, nl_query="")`  
  无 `OPENAI_API_KEY` 时自动使用规则引擎；有 Key 时尝试 OpenAI 兼容接口。

## 导出

- `contesttrace.exporter.export_data(db, exports_dir, logger, fmt="xlsx"|"csv", scope="all"|"date_range"|"unprocessed", ...)`  

## 邮件

- `contesttrace.mail_notify.send_email_smtp(to_addrs, subject, body)`  
  依赖环境变量 `SMTP_*`（见 `.env.example`）。
