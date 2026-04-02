from __future__ import annotations

import datetime as dt
import json
import logging
import random
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .encoding_fixer import smart_decode


# =========================
# 路径工具
# =========================


def ensure_dir(path: Path) -> Path:
    """自动创建缺失目录（跨平台）。"""

    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_write_text(path: Path, text: str) -> None:
    """
    统一 UTF-8（无 BOM）写入文本。
    说明：源码与配置建议使用 UTF-8；Windows 下控制台另通过 configure_stdio_utf8 处理。
    """

    ensure_dir(path.parent)
    try:
        path.write_text(text, encoding="utf-8", errors="replace")
    except Exception:
        path.write_text(text, encoding="utf-8", errors="ignore")


def configure_stdio_utf8() -> None:
    """
    尽量将标准输出/错误设为 UTF-8，减少控制台中文乱码（Python 3.7+）。
    全平台 try，失败则静默忽略，不影响业务。
    """

    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# =========================
# 日志工具
# =========================


def setup_logger(logs_dir: Path, name: str = "contesttrace") -> logging.Logger:
    """
    统一日志配置：
    - 控制台 + 文件双输出
    - 按日期切分日志文件
    - 格式：时间 | 级别 | 模块(logger名) | 消息
    """

    ensure_dir(logs_dir)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加 handler（多次调用时很常见）
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台（UTF-8）
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    try:
        if hasattr(ch.stream, "reconfigure"):
            ch.stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    logger.addHandler(ch)

    # 文件：按日期生成，UTF-8
    today = dt.datetime.now().strftime("%Y-%m-%d")
    logfile = logs_dir / f"{today}.log"
    fh = logging.FileHandler(logfile, encoding="utf-8", errors="replace")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


def prune_old_logs(logs_dir: Path, keep_days: int = 7) -> None:
    """
    清理过期日志文件，仅删除 logs_dir 下 *.log，保留最近 keep_days 天。
    单条失败不影响整体。
    """

    try:
        ensure_dir(logs_dir)
        cutoff = dt.datetime.now() - dt.timedelta(days=int(keep_days))
        for p in logs_dir.glob("*.log"):
            try:
                mtime = dt.datetime.fromtimestamp(p.stat().st_mtime)
                if mtime < cutoff:
                    p.unlink(missing_ok=True)
            except Exception:
                continue
    except Exception:
        pass


# =========================
# 网络请求工具（合规反爬 + 容错）
# =========================


@dataclass(frozen=True)
class RequestOptions:
    """HTTP 请求参数（含可选 Cookie / 代理）。"""

    timeout_seconds: int
    max_retries: int
    retry_backoff_seconds: float
    delay_seconds_min: float
    delay_seconds_max: float
    user_agents: Iterable[str]
    default_headers: Dict[str, str]
    cookies: Optional[Dict[str, str]] = None
    proxies: Optional[Dict[str, str]] = None


def random_delay(min_s: float, max_s: float) -> None:
    """合规随机延时：最低不低于 1.5 秒。"""

    low = max(1.5, float(min_s))
    high = max(low, float(max_s))
    time.sleep(random.uniform(low, high))


def build_headers(default_headers: Dict[str, str], user_agents: Iterable[str]) -> Dict[str, str]:
    """随机UA + 默认头。"""

    headers = dict(default_headers or {})
    uas = list(user_agents or [])
    if uas:
        headers["User-Agent"] = random.choice(uas)
    else:
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    return headers


def http_get_text(url: str, options: RequestOptions, logger: logging.Logger) -> Optional[str]:
    """
    统一 GET 文本响应：
    - 随机延时（合规，>=1.5s）
    - 随机 UA + 可选 Cookie/代理
    - 响应体一律经 encoding_fixer.smart_decode，禁止硬编码单一编码
    """

    enc_logger = logging.getLogger("contesttrace.encoding")

    for attempt in range(1, options.max_retries + 1):
        try:
            random_delay(options.delay_seconds_min, options.delay_seconds_max)
            headers = build_headers(options.default_headers, options.user_agents)
            kwargs: Dict[str, Any] = {"headers": headers, "timeout": options.timeout_seconds}
            if options.proxies:
                kwargs["proxies"] = options.proxies
            if options.cookies:
                kwargs["cookies"] = options.cookies
            resp = requests.get(url, **kwargs)
            resp.raise_for_status()

            text, enc = smart_decode(resp.content or b"", logger=enc_logger)
            logger.debug(f"HTTP 文本解码完成 | url={url} | encoding={enc}")
            return text
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.warning(f"请求失败（{attempt}/{options.max_retries}）：{url} | {type(e).__name__}: {e}")
            if attempt < options.max_retries:
                time.sleep(options.retry_backoff_seconds * attempt)
            else:
                return None


def http_get_bytes(url: str, options: RequestOptions, logger: logging.Logger) -> Optional[bytes]:
    """
    下载二进制内容（附件等）：不做文本解码，直接返回 bytes。
    """

    for attempt in range(1, options.max_retries + 1):
        try:
            random_delay(options.delay_seconds_min, options.delay_seconds_max)
            headers = build_headers(options.default_headers, options.user_agents)
            kwargs: Dict[str, Any] = {"headers": headers, "timeout": options.timeout_seconds}
            if options.proxies:
                kwargs["proxies"] = options.proxies
            if options.cookies:
                kwargs["cookies"] = options.cookies
            resp = requests.get(url, **kwargs)
            resp.raise_for_status()
            return resp.content
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.warning(f"二进制下载失败（{attempt}/{options.max_retries}）：{url} | {type(e).__name__}: {e}")
            if attempt < options.max_retries:
                time.sleep(options.retry_backoff_seconds * attempt)
            else:
                return None


# =========================
# 文本处理工具
# =========================


_RE_TAG = re.compile(r"<[^>]+>")
_RE_SPACE = re.compile(r"[ \t\r\f\v]+")


def clean_html_to_text(html: str) -> str:
    """
    HTML清洗：去标签、去多余空白、保留换行结构。
    """

    if not html:
        return ""
    # BeautifulSoup 更稳：能把 <p>/<br> 转为换行
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n")
    text = text.replace("\u00a0", " ")
    # 合并空白
    lines = []
    for line in text.splitlines():
        line = _RE_SPACE.sub(" ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines).strip()


def normalize_datetime(value: str) -> Optional[str]:
    """
    时间格式智能归一化：
    - 输出统一格式：YYYY-MM-DD
    - 解析失败返回 None（不会报错）
    """

    if not value:
        return None
    s = str(value).strip()
    s = s.replace("更新时间：", "").replace("发布时间：", "").replace("时间：", "").strip()
    # 常见中文分隔符替换
    s = s.replace("年", "-").replace("月", "-").replace("日", "")
    try:
        d = date_parser.parse(s, fuzzy=True)
        return d.strftime("%Y-%m-%d")
    except Exception:
        return None


def regex_extract(text: str, patterns: Iterable[str]) -> Optional[str]:
    """
    正则信息提取通用方法：
    - patterns: 多个正则，命中任意一个就返回第一个捕获组或整体匹配
    """

    if not text:
        return None
    for pat in patterns:
        try:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if not m:
                continue
            if m.groups():
                return (m.group(1) or "").strip() or None
            return (m.group(0) or "").strip() or None
        except re.error:
            continue
    return None


def safe_json_dumps(obj: Any) -> str:
    """调试/日志用的安全JSON序列化。"""

    try:
        return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    except Exception:
        return str(obj)


# =========================
# 验证工具
# =========================


def is_valid_url(url: str) -> bool:
    """URL有效性校验（宽松版：只要求 scheme+netloc）。"""

    if not url:
        return False
    try:
        p = urlparse(url)
        return bool(p.scheme and p.netloc)
    except Exception:
        return False


def ensure_absolute_url(base_url: str, href: str) -> str:
    """把列表页的相对链接拼成绝对URL。"""

    return urljoin(base_url, href or "")


def not_empty(value: Any) -> bool:
    """数据非空校验（字符串/容器/None）。"""

    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) > 0
    return True


def keyword_match(title: str, positives: Iterable[str], negatives: Iterable[str]) -> Tuple[bool, str]:
    """
    智能筛选：
    - 先命中排除词 -> False
    - 再命中正向词 -> True
    - 两边都不命中 -> False（可在配置里调整关键词以提高召回）
    """

    t = (title or "").strip()
    if not t:
        return False, "标题为空"

    for n in negatives or []:
        n = str(n).strip()
        if n and n in t:
            return False, f"命中排除词：{n}"

    for p in positives or []:
        p = str(p).strip()
        if p and p in t:
            return True, f"命中正向词：{p}"

    return False, "未命中正向关键词"


def extract_competition_fields(full_text: str) -> Dict[str, Optional[str]]:
    """
    从公告全文中提取“竞赛字段”（能提多少提多少；提取失败不会报错）。
    字段可能因不同通知写法差异很大，因此使用多套正则兜底。
    """

    text = full_text or ""
    # 统一把全角冒号替换，降低正则复杂度
    t = text.replace("：", ":")

    fields: Dict[str, Optional[str]] = {}

    fields["event_name"] = regex_extract(
        t,
        [
            r"(?:赛事名称|竞赛名称|比赛名称|活动名称)\s*:\s*([^\n]{2,80})",
        ],
    )
    fields["organizer"] = regex_extract(
        t,
        [
            r"(?:主办单位|主办|主办方)\s*:\s*([^\n]{2,60})",
        ],
    )
    fields["undertaker"] = regex_extract(
        t,
        [
            r"(?:承办单位|承办|承办方)\s*:\s*([^\n]{2,60})",
        ],
    )
    fields["competition_level"] = regex_extract(
        t,
        [
            r"(?:赛事级别|竞赛级别|级别)\s*:\s*([^\n]{2,60})",
            r"(?:校级|省级|国家级|国赛|省赛|校赛)",
        ],
    )
    fields["competition_category"] = regex_extract(
        t,
        [
            r"(?:赛事类别|竞赛类别|类别|学科类别)\s*:\s*([^\n]{2,40})",
            r"\b([ABC])[类級]类竞赛",
            r"(A类|B类|C类)",
        ],
    )
    fields["target_audience"] = regex_extract(
        t,
        [
            r"(?:参赛对象|参赛人员|参赛范围|参赛资格)\s*:\s*([^\n]{2,120})",
            r"(?:面向|对象)\s*:\s*([^\n]{2,120})",
        ],
    )
    fields["signup_deadline"] = regex_extract(
        t,
        [
            r"(?:报名截止|报名截止时间|报名时间截止)\s*:\s*([^\n]{4,40})",
            r"(?:报名时间)\s*:\s*.*?截止\s*([0-9]{4}[-/.][0-9]{1,2}[-/.][0-9]{1,2})",
        ],
    )
    fields["submission_deadline"] = regex_extract(
        t,
        [
            r"(?:作品提交截止|提交截止|作品截止|材料提交截止)\s*:\s*([^\n]{4,40})",
            r"(?:提交时间)\s*:\s*.*?截止\s*([0-9]{4}[-/.][0-9]{1,2}[-/.][0-9]{1,2})",
        ],
    )
    fields["competition_time"] = regex_extract(
        t,
        [
            r"(?:比赛时间|竞赛时间|时间安排)\s*:\s*([^\n]{4,80})",
            r"(?:比赛|竞赛)\s*时间\s*:\s*([^\n]{4,80})",
        ],
    )
    fields["requirements"] = regex_extract(
        t,
        [
            r"(?:参赛要求|作品要求|报名要求|参赛条件)\s*:\s*([^\n]{6,200})",
            r"(?:要求如下)\s*:\s*([^\n]{6,200})",
        ],
    )
    fields["awards"] = regex_extract(
        t,
        [
            r"(?:奖项设置|奖项|奖励办法|奖励)\s*:\s*([^\n]{4,200})",
            r"(?:设置).{0,10}(?:一等奖|二等奖|三等奖|优秀奖)[^\n]{0,120}",
        ],
    )
    fields["contact"] = regex_extract(
        t,
        [
            r"(?:联系方式|联系人)\s*:\s*([^\n]{4,120})",
            r"(?:联系电话|电话)\s*:\s*([0-9\\-]{7,20})",
            r"(?:邮箱|Email)\s*:\s*([A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\\.[A-Za-z0-9-.]+)",
        ],
    )

    # 时间字段尽量归一化
    for k in ["signup_deadline", "submission_deadline", "competition_time"]:
        if fields.get(k):
            norm = normalize_datetime(fields[k] or "")
            fields[k] = norm or fields[k]

    return fields

