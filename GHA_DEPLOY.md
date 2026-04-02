# GitHub Actions 部署说明（ContestTrace）

## 功能说明

工作流文件：`.github/workflows/crawl.yml`

- **定时触发**：每日 UTC `0:00` 与 `10:00`（大致对应北京时间 8:00 与 18:00，具体以 GitHub 调度为准）。
- **手动触发**：在仓库 **Actions** 中选择 **ContestTrace Crawl**，点击 **Run workflow**。
- **执行内容**：安装依赖 → 运行 `scripts/crawl_and_snapshot.py` → 将 `data/reports/latest_snapshot.csv` 提交回仓库（若有变更）。
- **失败告警**：在仓库 **Settings → Secrets** 中配置 `GHA_ALERT_WEBHOOK_URL`（钉钉/企业微信/自建 HTTP 等可接收 POST 的地址），失败时会尝试 `curl` 通知。

## 必要权限

工作流已设置 `permissions: contents: write`，默认 `GITHUB_TOKEN` 可推送同仓库分支。

若仓库开启 **Branch protection** 禁止机器人推送，需要：

- 放宽规则，或
- 配置具备写权限的 **Personal Access Token** 并改用自定义推送步骤（进阶）。

## 可选 Secrets

| 名称 | 说明 |
|------|------|
| `HTTP_PROXY` / `HTTPS_PROXY` | 运行环境需要代理访问外网时填写 |
| `GHA_ALERT_WEBHOOK_URL` | 失败告警 Webhook |

## 本地模拟

- Windows：双击或运行 `scripts\gha_setup.bat`
- Mac/Linux：`chmod +x scripts/gha_setup.sh && ./scripts/gha_setup.sh`

## 合规提示

爬虫遵守 `config/config.yaml` 中 `respect_robots_txt` 与随机延时配置；数据仅用于学习研究，请勿用于商业用途。
