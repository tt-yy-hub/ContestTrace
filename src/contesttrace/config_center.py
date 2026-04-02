# -*- coding: utf-8 -*-
"""
统一配置中心模块。

职责：
- 定位项目根目录
- 加载主配置 config/config.yaml（YAML）
- 加载多站点配置 config/sites.yaml
- 加载模型配置 config/model_config.yaml
- 可选合并 config/local.json（本地覆盖，不提交仓库）
- 通过 python-dotenv 加载 .env 中的环境变量（敏感信息不入库）
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover

    def load_dotenv(*_a, **_k):  # type: ignore
        return False


@dataclass(frozen=True)
class AppPaths:
    """所有业务目录统一收敛到此，全部 pathlib.Path，跨平台。"""

    project_root: Path
    data_dir: Path
    db_path: Path
    logs_dir: Path
    cache_dir: Path
    static_pages_dir: Path
    exports_dir: Path
    attachments_dir: Path
    models_dir: Path
    reports_dir: Path
    crawl_state_file: Path
    training_dir: Path


@dataclass(frozen=True)
class Config:
    """运行时配置对象：raw 为合并后的字典，paths 为解析后的绝对路径。"""

    raw: Dict[str, Any]
    paths: AppPaths

    @property
    def site(self) -> Dict[str, Any]:
        return self.raw["site"]

    @property
    def crawl(self) -> Dict[str, Any]:
        return self.raw["crawl"]

    @property
    def filter(self) -> Dict[str, Any]:
        return self.raw["filter"]

    @property
    def anti_crawl(self) -> Dict[str, Any]:
        return self.raw["anti_crawl"]

    @property
    def database(self) -> Dict[str, Any]:
        return self.raw["database"]

    def enabled_sites(self) -> List[Dict[str, Any]]:
        """返回 sites.yaml 中 enabled=true 的站点列表。"""

        sites = self.raw.get("sites") or []
        out = []
        for s in sites:
            try:
                if s.get("enabled"):
                    out.append(s)
            except Exception:
                continue
        return out


def find_project_root(start: Path | None = None) -> Path:
    """
    自动定位项目根目录。
    支持环境变量 CONTESTTRACE_ROOT 覆盖。
    """

    env_root = os.environ.get("CONTESTTRACE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    start_path = (start or Path(__file__).resolve()).resolve()
    for p in [start_path, *start_path.parents]:
        if (p / "config" / "config.yaml").exists() or (p / "requirements.txt").exists():
            return p
    return Path.cwd().resolve()


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """浅层+一层字典递归合并（满足 local.json 覆盖需求）。"""

    out = dict(base)
    for k, v in (override or {}).items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(
    config_path: str | Path | None = None,
    sites_path: str | Path | None = None,
    model_path: str | Path | None = None,
    local_json: str | Path | None = None,
) -> Config:
    """
    加载并合并全部配置。
    """

    root = find_project_root()
    # 敏感信息：优先从 .env 注入（文件若不存在则忽略）
    try:
        load_dotenv(root / ".env", override=False)
    except Exception:
        pass

    cfg_path = Path(config_path) if config_path else (root / "config" / "config.yaml")
    cfg_path = cfg_path.expanduser().resolve()
    if not cfg_path.exists():
        raise FileNotFoundError(f"未找到主配置：{cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as f:
        raw: Dict[str, Any] = yaml.safe_load(f) or {}

    for key in ["paths", "site", "crawl", "filter", "anti_crawl", "database"]:
        if key not in raw:
            raise ValueError(f"配置文件缺少顶层字段：`{key}`")

    # 多站点 YAML
    sp = Path(sites_path) if sites_path else (root / "config" / "sites.yaml")
    sp = sp.expanduser().resolve()
    if sp.exists():
        try:
            with sp.open("r", encoding="utf-8") as f:
                sy = yaml.safe_load(f) or {}
            raw["sites"] = sy.get("sites") or []
        except Exception:
            raw["sites"] = []
    else:
        raw["sites"] = []

    # 若 sites.yaml 为空，从旧版 site + crawl 页码合成单站点（保证零配置可跑）
    if not raw["sites"]:
        raw["sites"] = [
            {
                "id": "legacy_default",
                "enabled": True,
                "display_name": "默认站点",
                "base_url": raw["site"]["base_url"],
                "list_url_template": raw["site"]["list_url_template"],
                "start_page": int(raw["crawl"].get("start_page", 1)),
                "end_page": int(raw["crawl"].get("end_page", 1)),
                "list_page": raw["site"]["list_page"],
                "detail_page": raw["site"]["detail_page"],
            }
        ]

    # 模型配置
    mp = Path(model_path) if model_path else (root / "config" / "model_config.yaml")
    mp = mp.expanduser().resolve()
    if mp.exists():
        try:
            with mp.open("r", encoding="utf-8") as f:
                raw["model_config"] = yaml.safe_load(f) or {}
        except Exception:
            raw["model_config"] = {}
    else:
        raw["model_config"] = {}

    # 本地 JSON 覆盖
    lj = Path(local_json) if local_json else (root / "config" / "local.json")
    lj = lj.expanduser().resolve()
    if lj.exists():
        try:
            with lj.open("r", encoding="utf-8") as f:
                local = json.load(f)
            if isinstance(local, dict):
                raw = _deep_merge(raw, local)
        except Exception:
            pass

    paths_raw = raw["paths"]
    paths = AppPaths(
        project_root=root,
        data_dir=root / paths_raw["data_dir"],
        db_path=root / paths_raw["db_path"],
        logs_dir=root / paths_raw["logs_dir"],
        cache_dir=root / paths_raw["cache_dir"],
        static_pages_dir=root / paths_raw["static_pages_dir"],
        exports_dir=root / paths_raw["exports_dir"],
        attachments_dir=root / paths_raw.get("attachments_dir", "data/attachments"),
        models_dir=root / paths_raw.get("models_dir", "data/models"),
        reports_dir=root / paths_raw.get("reports_dir", "data/reports"),
        crawl_state_file=root / paths_raw.get("crawl_state_file", "data/crawl_state.json"),
        training_dir=root / paths_raw.get("training_dir", "data/training_data"),
    )

    return Config(raw=raw, paths=paths)


def get_positive_keywords(cfg: Config) -> List[str]:
    """正向关键词列表（去重、去空）。"""

    kws = cfg.filter.get("positive_keywords", []) or []
    cleaned: List[str] = []
    seen = set()
    for k in kws:
        s = str(k).strip()
        if s and s not in seen:
            cleaned.append(s)
            seen.add(s)
    return cleaned


def get_negative_keywords(cfg: Config) -> List[str]:
    """反向排除关键词。"""

    kws = cfg.filter.get("negative_keywords", []) or []
    cleaned: List[str] = []
    seen = set()
    for k in kws:
        s = str(k).strip()
        if s and s not in seen:
            cleaned.append(s)
            seen.add(s)
    return cleaned


def proxies_from_env() -> Optional[Dict[str, str]]:
    """从环境变量读取 HTTP(S) 代理，供 requests 使用。"""

    http_p = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    https_p = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if not http_p and not https_p:
        return None
    d: Dict[str, str] = {}
    if http_p:
        d["http"] = http_p
    if https_p:
        d["https"] = https_p
    elif http_p:
        d["https"] = http_p
    return d or None


def cookies_from_env() -> Optional[Dict[str, str]]:
    """
    可选：环境变量 SITE_COOKIES_JSON 提供 Cookie 字典 JSON。
    高级场景使用，默认 None。
    """

    raw = os.environ.get("SITE_COOKIES_JSON", "").strip()
    if not raw:
        return None
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return {str(k): str(v) for k, v in obj.items()}
    except Exception:
        pass
    return None
