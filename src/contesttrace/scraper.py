from __future__ import annotations

import datetime as dt
import random
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

from .config_center import Config, get_negative_keywords, get_positive_keywords
from .db import SQLiteDB
from .utils import (
    RequestOptions,
    clean_html_to_text,
    ensure_absolute_url,
    ensure_dir,
    extract_competition_fields,
    http_get_text,
    is_valid_url,
    normalize_datetime,
    safe_write_text,
    setup_logger,
    keyword_match,
)


@dataclass
class CrawlSummary:
    """爬虫运行总结（控制台可读）。"""

    pages_total: int = 0
    list_items_total: int = 0
    filtered_out: int = 0
    skipped_duplicate: int = 0
    inserted: int = 0
    failed: int = 0


class GracefulKiller:
    """优雅中断：支持 Ctrl+C 保存已爬取数据并输出提示。"""

    def __init__(self) -> None:
        self.stop = False
        signal.signal(signal.SIGINT, self._handle)

    def _handle(self, signum, frame) -> None:  # noqa: ARG002
        self.stop = True


def _save_raw_html_if_needed(
    html: str,
    out_dir: Path,
    filename: str,
    enabled: bool,
    limit: int,
    counter: int,
    logger,
) -> None:
    """保存原始HTML（便于排查DOM变更导致解析失败）。"""

    if not enabled:
        return
    if limit and counter > limit:
        return
    try:
        ensure_dir(out_dir)
        safe_write_text(out_dir / filename, html)
    except Exception as e:
        logger.warning(f"保存HTML失败：{filename} | {type(e).__name__}: {e}")


def parse_list_page(cfg: Config, html: str, logger) -> List[Dict[str, str]]:
    """
    解析列表页：
    - 提取标题、相对链接、发布时间
    - 输出标准结构：title, detail_url, publish_date
    """

    rules = cfg.site["list_page"]
    soup = BeautifulSoup(html, "lxml")
    container = soup.select_one(rules["list_container_css"])
    if not container:
        logger.warning("列表页解析失败：未找到列表容器（可能DOM结构变更）。")
        return []

    items = []
    for li in container.select(rules["item_css"]):
        a = li.select_one(rules["title_link_css"])
        d = li.select_one(rules["publish_date_css"])
        if not a:
            continue

        title = (a.get_text(strip=True) or "").strip()
        href = (a.get("href") or "").strip()
        publish_date = normalize_datetime((d.get_text(strip=True) if d else "") or "")

        if not title or not href:
            continue

        detail_url = ensure_absolute_url(cfg.site["base_url"], href)
        if not is_valid_url(detail_url):
            continue

        items.append(
            {
                "title": title,
                "detail_url": detail_url,
                "publish_date": publish_date,
            }
        )

    return items


def parse_detail_page(cfg: Config, detail_url: str, html: str, logger) -> Dict[str, Optional[str]]:
    """
    解析详情页全字段：
    - 标题、发布人、更新时间、正文全文
    - 从全文中提取竞赛字段（尽量提取，提取不到不报错）
    """

    rules = cfg.site["detail_page"]
    soup = BeautifulSoup(html, "lxml")

    title_el = soup.select_one(rules["title_css"])
    publisher_el = soup.select_one(rules.get("publisher_css") or "")
    update_el = soup.select_one(rules["update_time_css"])
    content_el = soup.select_one(rules["content_css"])

    title = (title_el.get_text(strip=True) if title_el else "") or None
    publisher = (publisher_el.get_text(strip=True) if publisher_el else "") or None
    update_time_raw = (update_el.get_text(strip=True) if update_el else "") or None
    update_time = normalize_datetime(update_time_raw or "") if update_time_raw else None

    content_html = str(content_el) if content_el else ""
    full_text = clean_html_to_text(content_html)

    # 如果正文没抓到，降级：尽量从整页提取文本，避免空入库
    if not full_text:
        full_text = clean_html_to_text(html)
        logger.warning(f"详情页正文容器未命中，已使用整页文本降级：{detail_url}")

    fields = extract_competition_fields(full_text)

    return {
        "title": title,
        "publisher": publisher,
        "update_time": update_time,
        "full_text": full_text,
        **fields,
    }


def run_crawl(cfg: Config) -> CrawlSummary:
    """
    主爬虫程序（闭环）：
    初始化配置 → 初始化数据库 → 遍历分页 → 解析列表 → 智能筛选 → 去重 → 解析详情 → 入库 → 统计输出
    """

    logger = setup_logger(cfg.paths.logs_dir)
    db = SQLiteDB(cfg.paths.db_path, cfg.database.get("table_name") or "contest_announcements")
    db.init_db(logger)

    positives = get_positive_keywords(cfg)
    negatives = get_negative_keywords(cfg)

    opts = RequestOptions(
        timeout_seconds=int(cfg.crawl["timeout_seconds"]),
        max_retries=int(cfg.crawl["max_retries"]),
        retry_backoff_seconds=float(cfg.crawl["retry_backoff_seconds"]),
        delay_seconds_min=float(cfg.crawl["delay_seconds_min"]),
        delay_seconds_max=float(cfg.crawl["delay_seconds_max"]),
        user_agents=cfg.anti_crawl.get("user_agents") or [],
        default_headers=cfg.anti_crawl.get("default_headers") or {},
    )

    killer = GracefulKiller()
    summary = CrawlSummary()

    save_raw = bool(cfg.crawl.get("save_raw_html", True))
    limit_list = int(cfg.crawl.get("save_raw_html_limit_list_pages", 0) or 0)
    limit_detail = int(cfg.crawl.get("save_raw_html_limit_detail_pages", 0) or 0)
    list_saved = 0
    detail_saved = 0

    start_page = int(cfg.crawl["start_page"])
    end_page = int(cfg.crawl["end_page"])
    pages = list(range(start_page, end_page + 1))

    logger.info(f"开始爬取：页码 {start_page} - {end_page}（合规低频随机延时已开启）")

    for page in pages:
        if killer.stop:
            logger.warning("检测到手动中断（Ctrl+C）。已停止继续翻页。")
            break

        summary.pages_total += 1
        list_url = cfg.site["list_url_template"].format(page=page)
        logger.info(f"抓取列表页：第 {page} 页 | {list_url}")

        html = http_get_text(list_url, opts, logger)
        if not html:
            summary.failed += 1
            continue

        list_saved += 1
        _save_raw_html_if_needed(
            html=html,
            out_dir=cfg.paths.static_pages_dir,
            filename=f"list_{page}.html",
            enabled=save_raw,
            limit=limit_list,
            counter=list_saved,
            logger=logger,
        )

        items = parse_list_page(cfg, html, logger)
        summary.list_items_total += len(items)

        for idx, it in enumerate(items, start=1):
            if killer.stop:
                logger.warning("检测到手动中断（Ctrl+C）。已停止继续抓取详情。")
                break

            title = it["title"]
            detail_url = it["detail_url"]

            ok, reason = keyword_match(title, positives, negatives)
            if not ok:
                summary.filtered_out += 1
                logger.info(f"跳过（筛选）：{title} | {reason}")
                continue

            if db.exists_by_url(detail_url):
                summary.skipped_duplicate += 1
                logger.info(f"跳过（重复）：{title}")
                continue

            logger.info(f"抓取详情：{title} | {detail_url}")
            dhtml = http_get_text(detail_url, opts, logger)
            if not dhtml:
                summary.failed += 1
                logger.warning(f"详情抓取失败：{title}")
                continue

            detail_saved += 1
            _save_raw_html_if_needed(
                html=dhtml,
                out_dir=cfg.paths.static_pages_dir,
                filename=f"detail_{page}_{idx}.html",
                enabled=save_raw,
                limit=limit_detail,
                counter=detail_saved,
                logger=logger,
            )

            detail_data = parse_detail_page(cfg, detail_url, dhtml, logger)
            payload = {
                "title": detail_data.get("title") or title,
                "publish_date": it.get("publish_date"),
                "detail_url": detail_url,
                "publisher": detail_data.get("publisher"),
                "update_time": detail_data.get("update_time"),
                "full_text": detail_data.get("full_text"),
                "organizer": detail_data.get("organizer"),
                "competition_level": detail_data.get("competition_level"),
                "target_audience": detail_data.get("target_audience"),
                "signup_deadline": detail_data.get("signup_deadline"),
                "submission_deadline": detail_data.get("submission_deadline"),
                "competition_time": detail_data.get("competition_time"),
                "requirements": detail_data.get("requirements"),
                "awards": detail_data.get("awards"),
                "contact": detail_data.get("contact"),
                "status": "new",
            }

            try:
                inserted = db.insert_one(payload, logger)
                if inserted:
                    summary.inserted += 1
                    logger.info(f"入库成功：{title}")
                else:
                    summary.skipped_duplicate += 1
                    logger.info(f"入库跳过（重复/失败）：{title}")
            except Exception as e:
                summary.failed += 1
                logger.error(f"入库异常：{title} | {type(e).__name__}: {e}")

    logger.info(
        "爬取结束统计："
        f"页数={summary.pages_total}，列表条目={summary.list_items_total}，"
        f"筛掉={summary.filtered_out}，重复跳过={summary.skipped_duplicate}，"
        f"新增入库={summary.inserted}，失败={summary.failed}"
    )
    return summary


def main() -> None:
    """脚本入口：新手双击/命令行运行都能用。"""

    from .config_center import load_config

    cfg = load_config()
    run_crawl(cfg)


if __name__ == "__main__":
    main()

