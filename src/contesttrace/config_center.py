from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass(frozen=True)
class AppPaths:
    """统一路径配置（全部基于项目根目录，跨平台兼容）。"""

    project_root: Path
    data_dir: Path
    db_path: Path
    logs_dir: Path
    cache_dir: Path
    static_pages_dir: Path
    exports_dir: Path


@dataclass(frozen=True)
class Config:
    """统一配置中心：所有可修改参数均从配置文件读取。"""

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


def find_project_root(start: Path | None = None) -> Path:
    """
    自动定位项目根目录：
    - 优先从当前文件位置向上找（包含 config/config.yaml 或 requirements.txt 的目录）
    - 也允许通过环境变量 CONTESTTRACE_ROOT 覆盖（方便部署/调试）
    """

    env_root = os.environ.get("CONTESTTRACE_ROOT")
    if env_root:
        p = Path(env_root).expanduser().resolve()
        return p

    start_path = (start or Path(__file__).resolve()).resolve()
    for p in [start_path, *start_path.parents]:
        if (p / "config" / "config.yaml").exists() or (p / "requirements.txt").exists():
            return p
    return Path.cwd().resolve()


def load_config(config_path: str | Path | None = None) -> Config:
    """读取 YAML 配置，并解析所有路径为绝对 Path。"""

    root = find_project_root()
    cfg_path = Path(config_path) if config_path else (root / "config" / "config.yaml")
    cfg_path = cfg_path.expanduser().resolve()

    if not cfg_path.exists():
        raise FileNotFoundError(
            f"未找到配置文件：{cfg_path}\n"
            f"请确认项目根目录存在 `config/config.yaml`，或通过参数/环境变量指定。"
        )

    with cfg_path.open("r", encoding="utf-8") as f:
        raw: Dict[str, Any] = yaml.safe_load(f) or {}

    # 基本字段校验（新手友好：缺啥就报清楚）
    for key in ["paths", "site", "crawl", "filter", "anti_crawl", "database"]:
        if key not in raw:
            raise ValueError(f"配置文件缺少顶层字段：`{key}`（请检查 config/config.yaml）")

    paths_raw = raw["paths"]
    paths = AppPaths(
        project_root=root,
        data_dir=root / paths_raw["data_dir"],
        db_path=root / paths_raw["db_path"],
        logs_dir=root / paths_raw["logs_dir"],
        cache_dir=root / paths_raw["cache_dir"],
        static_pages_dir=root / paths_raw["static_pages_dir"],
        exports_dir=root / paths_raw["exports_dir"],
    )

    return Config(raw=raw, paths=paths)


def get_positive_keywords(cfg: Config) -> List[str]:
    """读取正向关键词列表（自动去重、去空）。"""

    kws = cfg.filter.get("positive_keywords", []) or []
    cleaned = []
    seen = set()
    for k in kws:
        s = str(k).strip()
        if s and s not in seen:
            cleaned.append(s)
            seen.add(s)
    return cleaned


def get_negative_keywords(cfg: Config) -> List[str]:
    """读取反向排除关键词列表（自动去重、去空）。"""

    kws = cfg.filter.get("negative_keywords", []) or []
    cleaned = []
    seen = set()
    for k in kws:
        s = str(k).strip()
        if s and s not in seen:
            cleaned.append(s)
            seen.add(s)
    return cleaned

