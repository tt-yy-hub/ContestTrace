from __future__ import annotations

import datetime as dt
import json
import logging
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser


# =========================
# 路径工具
# =========================


def ensure_dir(path: Path) -> Path:
    """自动创建缺失目录（跨平台）。"""

    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_write_text(path: Path, text: str) -> None:
    """统一UTF-8写入文本（避免Windows乱码）。"""

    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8", errors="ignore")


# =========================
# 日志工具
# =========================


def setup_logger(logs_dir: Path, name: str = "contesttrace") -> logging.Logger:
    """
    统一日志配置：
    - 控制台 + 文件
    - 按日期切分文件名
    - 新手可直接定位错误
    """

    ensure_dir(logs_dir)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加 handler（多次调用时很常见）
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # 文件：按日期生成
    today = dt.datetime.now().strftime("%Y-%m-%d")
    logfile = logs_dir / f"{today}.log"
    fh = logging.FileHandler(logfile, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


# =========================
# 网络请求工具（合规反爬 + 容错）
# =========================


@dataclass(frozen=True)
class RequestOptions:
    timeout_seconds: int
    max_retries: int
    retry_backoff_seconds: float
    delay_seconds_min: float
    delay_seconds_max: float
    user_agents: Iterable[str]
    default_headers: Dict[str, str]


def _decode_response_best_effort(resp: requests.Response) -> str:
    """
    网站页面偶尔会出现“声明UTF-8但实际内容是GB编码”的情况。
    为了保证中文不乱码，使用多编码尝试，选“替换字符(�)最少”的结果。
    """

    raw = resp.content or b""
    candidates = []

    # 先用响应头/requests推断的编码
    if resp.encoding:
        candidates.append(resp.encoding)

    # 常见中文网页编码兜底
    candidates.extend(["utf-8", "gb18030", "gbk"])

    def score_text(text: str) -> int:
        # � 替换字符越少越好
        bad = text.count("\ufffd")
        # 中文字符越多越好（适配中文站点）
        cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
        # 常见乱码特征（utf-8 被 latin-1 解码后常出现 å ä è 等）
        moj = len(re.findall(r"[åäöüèéêÃ¤Ã¥Ã¨Ã©Ã±]", text))
        # 综合打分：中文权重更高
        return cjk * 10 - bad * 50 - moj * 5

    best_text = ""
    best_score = None
    for enc in candidates:
        try:
            text = raw.decode(enc, errors="replace")
        except Exception:
            continue
        sc = score_text(text)
        if best_score is None or sc > best_score:
            best_score = sc
            best_text = text

    return best_text


def random_delay(min_s: float, max_s: float) -> None:
    """合规随机延时：避免高频请求造成压力。"""

    low = max(1.0, float(min_s))  # 硬性要求：不得低于1秒
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
    统一GET请求：
    - 随机延时（合规）
    - 随机UA
    - 超时 + 重试
    - 全异常捕获（不会直接崩溃）
    """

    for attempt in range(1, options.max_retries + 1):
        try:
            random_delay(options.delay_seconds_min, options.delay_seconds_max)
            headers = build_headers(options.default_headers, options.user_agents)
            resp = requests.get(url, headers=headers, timeout=options.timeout_seconds)
            resp.raise_for_status()

            return _decode_response_best_effort(resp)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.warning(f"请求失败（{attempt}/{options.max_retries}）：{url} | {type(e).__name__}: {e}")
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

    fields["organizer"] = regex_extract(
        t,
        [
            r"(?:主办单位|主办|主办方)\s*:\s*([^\n]{2,60})",
            r"(?:承办单位|承办)\s*:\s*([^\n]{2,60})",
        ],
    )
    fields["competition_level"] = regex_extract(
        t,
        [
            r"(?:赛事级别|竞赛级别|级别)\s*:\s*([^\n]{2,60})",
            r"(?:校级|省级|国家级|国赛|省赛|校赛)",
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

