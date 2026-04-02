# -*- coding: utf-8 -*-
"""
多源定向爬虫：配置驱动、robots 合规、断点续爬、附件下载、优雅中断。

字段覆盖：基础信息 + 竞赛核心字段（与 extract_competition_fields / DB 对齐，不少于 15 个业务维度）。
"""

from __future__ import annotations

import hashlib
import json
import re
import signal
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .config_center import Config, cookies_from_env, get_negative_keywords, get_positive_keywords, proxies_from_env
from .crawl_state import get_next_page, load_state, save_state, set_next_page
from .db import SQLiteDB
from .robots_checker import can_fetch_url
from .utils import (
    RequestOptions,
    clean_html_to_text,
    ensure_absolute_url,
    ensure_dir,
    extract_competition_fields,
    http_get_bytes,
    http_get_text,
    is_valid_url,
    keyword_match,
    normalize_datetime,
    prune_old_logs,
    safe_write_text,
    setup_logger,
)


@dataclass
class CrawlSummary:
    """单次运行汇总。"""

    sites: int = 0
    pages_total: int = 0
    list_items_total: int = 0
    filtered_out: int = 0
    skipped_duplicate: int = 0
    inserted: int = 0
    failed: int = 0
    attachments_saved: int = 0
    interrupted: bool = False
    notes: List[str] = field(default_factory=list)


class GracefulKiller:
    """Ctrl+C 优雅停止。"""

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
    if not enabled:
        return
    if limit and counter > limit:
        return
    try:
        ensure_dir(out_dir)
        safe_write_text(out_dir / filename, html)
    except Exception as e:
        logger.warning(f"保存HTML失败：{filename} | {type(e).__name__}: {e}")


def parse_list_page(site: Dict[str, Any], html: str, logger) -> List[Dict[str, str]]:
    """解析列表页。"""

    rules = site["list_page"]
    base_url = site["base_url"]
    soup = BeautifulSoup(html, "lxml")
    container = soup.select_one(rules["list_container_css"])
    if not container:
        logger.warning(f"[{site.get('id')}] 列表容器未找到，可能 DOM 变更")
        return []

    items: List[Dict[str, str]] = []
    for li in container.select(rules["item_css"]):
        a = li.select_one(rules["title_link_css"])
        d = li.select_one(rules["publish_date_css"]) if rules.get("publish_date_css") else None
        if not a:
            continue
        title = (a.get_text(strip=True) or "").strip()
        href = (a.get("href") or "").strip()
        publish_date = normalize_datetime((d.get_text(strip=True) if d else "") or "")
        if not title or not href:
            continue
        detail_url = ensure_absolute_url(base_url, href)
        if not is_valid_url(detail_url):
            continue
        items.append({"title": title, "detail_url": detail_url, "publish_date": publish_date})
    return items


def _collect_attachment_urls(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
    """从正文中收集常见附件链接。"""

    exts = (".pdf", ".doc", ".docx", ".zip", ".rar", ".xlsx", ".ppt", ".pptx")
    out: List[Dict[str, str]] = []
    seen: Set[str] = set()
    for a in soup.select("a[href]"):
        try:
            href = (a.get("href") or "").strip()
            if not href or href.startswith("javascript"):
                continue
            low = href.split("?")[0].lower()
            if not any(low.endswith(e) for e in exts):
                continue
            full = ensure_absolute_url(base_url, href)
            if full in seen:
                continue
            seen.add(full)
            name = Path(urlparse(full).path).name or f"file_{uuid.uuid4().hex[:8]}"
            out.append({"url": full, "filename": name})
        except Exception:
            continue
    return out


def parse_detail_page(site: Dict[str, Any], detail_url: str, html: str, logger) -> Dict[str, Optional[str]]:
    """解析详情页 + 附件列表元数据。"""

    rules = site["detail_page"]
    base_url = site["base_url"]
    soup = BeautifulSoup(html, "lxml")

    title_el = soup.select_one(rules["title_css"])
    publisher_el = soup.select_one(rules["publisher_css"]) if rules.get("publisher_css") else None
    update_el = soup.select_one(rules["update_time_css"]) if rules.get("update_time_css") else None
    content_el = soup.select_one(rules["content_css"])

    title = (title_el.get_text(strip=True) if title_el else "") or None
    publisher = (publisher_el.get_text(strip=True) if publisher_el else "") or None
    update_time_raw = (update_el.get_text(strip=True) if update_el else "") or None
    update_time = normalize_datetime(update_time_raw or "") if update_time_raw else None

    content_html = str(content_el) if content_el else ""
    full_text = clean_html_to_text(content_html)
    if not full_text:
        full_text = clean_html_to_text(html)
        logger.warning(f"正文容器降级为整页：{detail_url}")

    fields = extract_competition_fields(full_text)
    # 附件链接可能在正文区或页面其它区域，使用整页 soup 扫描
    att_meta = _collect_attachment_urls(soup, base_url)

    return {
        "title": title,
        "publisher": publisher,
        "update_time": update_time,
        "full_text": full_text,
        "attachment_meta": att_meta,
        **fields,
    }


def _download_attachments(
    meta: List[Dict[str, str]],
    site_id: str,
    dest_root: Path,
    opts: RequestOptions,
    logger,
    max_mb: float,
) -> List[Dict[str, str]]:
    """下载附件到磁盘，返回已保存文件信息列表。"""

    saved: List[Dict[str, str]] = []
    max_bytes = int(max_mb * 1024 * 1024)
    sub = ensure_dir(dest_root / site_id)
    for m in meta:
        try:
            url = m["url"]
            fn = (m.get("filename") or "file").strip()
            fn = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", fn)[:120] or "file"
            raw = http_get_bytes(url, opts, logger)
            if raw is None:
                continue
            if len(raw) > max_bytes:
                logger.warning(f"附件过大已跳过：{url}")
                continue
            path = sub / f"{uuid.uuid4().hex[:10]}_{fn}"
            path.write_bytes(raw)
            saved.append({"url": url, "local_path": str(path), "filename": fn})
        except Exception as e:
            logger.warning(f"附件下载失败：{m.get('url')} | {e}")
            continue
    return saved


def _build_request_options(cfg: Config) -> RequestOptions:
    """由全局配置 + 环境变量构造请求选项。"""

    return RequestOptions(
        timeout_seconds=int(cfg.crawl["timeout_seconds"]),
        max_retries=int(cfg.crawl["max_retries"]),
        retry_backoff_seconds=float(cfg.crawl["retry_backoff_seconds"]),
        delay_seconds_min=float(cfg.crawl["delay_seconds_min"]),
        delay_seconds_max=float(cfg.crawl["delay_seconds_max"]),
        user_agents=cfg.anti_crawl.get("user_agents") or [],
        default_headers=cfg.anti_crawl.get("default_headers") or {},
        cookies=cookies_from_env(),
        proxies=proxies_from_env(),
    )


def run_crawl(cfg: Config) -> CrawlSummary:
    """执行多源爬取主流程。"""

    logger = setup_logger(cfg.paths.logs_dir)
    keep_days = int(cfg.raw.get("logging", {}).get("keep_days", 7))
    prune_old_logs(cfg.paths.logs_dir, keep_days=keep_days)

    db = SQLiteDB(cfg.paths.db_path, cfg.database.get("table_name") or "contest_announcements")
    db.init_db(logger)

    positives = get_positive_keywords(cfg)
    negatives = get_negative_keywords(cfg)
    opts = _build_request_options(cfg)

    killer = GracefulKiller()
    summary = CrawlSummary()

    save_raw = bool(cfg.crawl.get("save_raw_html", True))
    limit_list = int(cfg.crawl.get("save_raw_html_limit_list_pages", 0) or 0)
    limit_detail = int(cfg.crawl.get("save_raw_html_limit_detail_pages", 0) or 0)
    respect_robots = bool(cfg.crawl.get("respect_robots_txt", True))
    incremental = bool(cfg.crawl.get("incremental", True))
    max_mb = float(cfg.crawl.get("attachment_max_mb", 20))

    state = load_state(cfg.paths.crawl_state_file, logger)
    ua_for_robots = (list(opts.user_agents) or ["*"])[0]

    sites = cfg.enabled_sites()
    if not sites:
        logger.warning("没有启用的站点，请在 config/sites.yaml 中将 enabled 设为 true")
        return summary

    summary.sites = len(sites)
    list_saved = 0
    detail_saved = 0

    for site in sites:
        if killer.stop:
            summary.interrupted = True
            break

        sid = str(site.get("id") or "unknown")
        base_url = site["base_url"]
        tpl = site["list_url_template"]
        p_start = int(site.get("start_page", 1))
        p_end = int(site.get("end_page", 1))

        if incremental:
            p_start = get_next_page(state, sid, p_start)

        logger.info(f"===== 站点 [{sid}] {site.get('display_name','')} 页码 {p_start}-{p_end} =====")

        for page in range(p_start, p_end + 1):
            if killer.stop:
                summary.interrupted = True
                break

            summary.pages_total += 1
            list_url = tpl.format(page=page)

            if respect_robots and not can_fetch_url(ua_for_robots, base_url, list_url, logger):
                logger.info(f"robots.txt 禁止访问，跳过：{list_url}")
                summary.failed += 1
                continue

            logger.info(f"列表页 p={page} | {list_url}")
            html = http_get_text(list_url, opts, logger)
            if not html:
                summary.failed += 1
                continue

            list_saved += 1
            _save_raw_html_if_needed(
                html, cfg.paths.static_pages_dir, f"{sid}_list_{page}.html", save_raw, limit_list, list_saved, logger
            )

            items = parse_list_page(site, html, logger)
            summary.list_items_total += len(items)

            for idx, it in enumerate(items, start=1):
                if killer.stop:
                    summary.interrupted = True
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
                    logger.info(f"跳过（URL重复）：{title}")
                    continue

                if respect_robots and not can_fetch_url(ua_for_robots, base_url, detail_url, logger):
                    logger.info(f"robots 禁止详情：{detail_url}")
                    summary.failed += 1
                    continue

                logger.info(f"详情：{title}")
                dhtml = http_get_text(detail_url, opts, logger)
                if not dhtml:
                    summary.failed += 1
                    continue

                detail_saved += 1
                _save_raw_html_if_needed(
                    dhtml,
                    cfg.paths.static_pages_dir,
                    f"{sid}_detail_{page}_{idx}.html",
                    save_raw,
                    limit_detail,
                    detail_saved,
                    logger,
                )

                detail_data = parse_detail_page(site, detail_url, dhtml, logger)
                full_text = detail_data.get("full_text") or ""
                content_hash = hashlib.sha256(full_text.encode("utf-8", errors="replace")).hexdigest()

                att_saved_list: List[Dict[str, str]] = []
                try:
                    att_saved_list = _download_attachments(
                        detail_data.get("attachment_meta") or [],
                        sid,
                        cfg.paths.attachments_dir,
                        opts,
                        logger,
                        max_mb=max_mb,
                    )
                    summary.attachments_saved += len(att_saved_list)
                except Exception as e:
                    logger.warning(f"附件批处理异常：{e}")

                event_name = detail_data.get("event_name") or detail_data.get("title") or title

                payload = {
                    "title": detail_data.get("title") or title,
                    "publish_date": it.get("publish_date"),
                    "detail_url": detail_url,
                    "publisher": detail_data.get("publisher"),
                    "update_time": detail_data.get("update_time"),
                    "full_text": full_text,
                    "organizer": detail_data.get("organizer"),
                    "undertaker": detail_data.get("undertaker"),
                    "competition_level": detail_data.get("competition_level"),
                    "competition_category": detail_data.get("competition_category"),
                    "target_audience": detail_data.get("target_audience"),
                    "signup_deadline": detail_data.get("signup_deadline"),
                    "submission_deadline": detail_data.get("submission_deadline"),
                    "competition_time": detail_data.get("competition_time"),
                    "requirements": detail_data.get("requirements"),
                    "awards": detail_data.get("awards"),
                    "contact": detail_data.get("contact"),
                    "status": "new",
                    "source_site_id": sid,
                    "event_name": event_name,
                    "attachments_json": json.dumps(att_saved_list, ensure_ascii=False) if att_saved_list else None,
                    "content_hash": content_hash,
                }

                try:
                    inserted = db.insert_one(payload, logger)
                    if inserted:
                        summary.inserted += 1
                        logger.info(f"入库成功：{title}")
                    else:
                        summary.skipped_duplicate += 1
                except Exception as e:
                    summary.failed += 1
                    logger.error(f"入库异常：{e}")

            if killer.stop:
                break

            if incremental:
                set_next_page(state, sid, page + 1)
                save_state(cfg.paths.crawl_state_file, state, logger)

    if incremental and not killer.stop:
        save_state(cfg.paths.crawl_state_file, state, logger)

    msg = (
        f"爬取结束 | 站点={summary.sites} 页={summary.pages_total} 列表项={summary.list_items_total} "
        f"筛掉={summary.filtered_out} 跳过={summary.skipped_duplicate} 新增={summary.inserted} "
        f"失败={summary.failed} 附件={summary.attachments_saved}"
    )
    if summary.interrupted:
        msg += " | 已手动中断（Ctrl+C），状态已尽量保存"
    logger.info(msg)
    summary.notes.append(msg)
    return summary


def main() -> None:
    from .config_center import load_config

    cfg = load_config()
    run_crawl(cfg)


if __name__ == "__main__":
    main()
