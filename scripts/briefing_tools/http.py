"""HTTP 抓取 + RSS/Atom 解析 + 时效过滤 + URL 归一化"""

from __future__ import annotations

import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

from .config import BASE_DIR

USER_AGENT = "BriefingTools/3.0 (Walter's Knowledge Base)"


def http_get(url: str, timeout: int = 10, retries: int = 1) -> str | None:
    """标准库 HTTP GET，带错误处理和自动重试"""
    last_err: Exception | None = None
    for attempt in range(1 + retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(3)
                continue
    _log_error(f"HTTP GET 失败: {url} — {last_err}")
    return None


def _log_error(msg: str) -> None:
    log_file = BASE_DIR / ".errors.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"  ⚠️  {msg}", file=sys.stderr)


# ============================================
# URL 归一化
# ============================================

_TRACKING_PARAMS = {"ref", "source", "from"}


def normalize_url(url: str) -> str:
    """归一化 URL：去 fragment、utm_ 追踪、部分尾斜杠"""
    if not url:
        return ""
    u = url.strip()
    if not u:
        return ""
    if "#" in u:
        u = u.split("#", 1)[0]
    if "?" in u:
        head, qs = u.split("?", 1)
        kept = []
        for p in qs.split("&"):
            if not p:
                continue
            k = p.split("=", 1)[0].lower()
            if k.startswith("utm_") or k in _TRACKING_PARAMS:
                continue
            kept.append(p)
        u = head + ("?" + "&".join(kept) if kept else "")
    # 去非根路径的尾斜杠；保留 "https://host/" 这种纯根路径
    if u.endswith("/"):
        # 计算斜杠数量：scheme 贡献 2 个 (//)，host 后的斜杠是 path 斜杠
        # "https://host/" 有 3 个斜杠（2 scheme + 1 root），不该剥
        # "https://host/path/" 有 4 个，剥
        if u.count("/") > 3:
            u = u.rstrip("/")
    return u


# ============================================
# RSS / Atom 解析
# ============================================

def parse_rss(xml_text: str, source_name: str) -> list[dict]:
    """解析 RSS 2.0 和 Atom"""
    items: list[dict] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        _log_error(f"RSS 解析失败 ({source_name}): {e}")
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # RSS 2.0
    for item in root.iter("item"):
        title = _text(item, "title") or ""
        link = _text(item, "link") or ""
        pub_date = _text(item, "pubDate") or ""
        description = _text(item, "description") or ""
        if title and link:
            items.append({
                "title": title.strip(),
                "url": normalize_url(link.strip()),
                "published": pub_date.strip(),
                "description": _clean_html(description)[:500],
                "source": source_name,
            })

    # Atom
    if not items:
        for entry in root.iter(f"{{{ns['atom']}}}entry"):
            title = _text(entry, f"{{{ns['atom']}}}title") or ""
            link_el = entry.find(f"{{{ns['atom']}}}link[@rel='alternate']")
            if link_el is None:
                link_el = entry.find(f"{{{ns['atom']}}}link")
            link = link_el.get("href", "") if link_el is not None else ""
            pub_date = (
                _text(entry, f"{{{ns['atom']}}}published")
                or _text(entry, f"{{{ns['atom']}}}updated")
                or ""
            )
            summary = _text(entry, f"{{{ns['atom']}}}summary") or ""
            if title and link:
                items.append({
                    "title": title.strip(),
                    "url": normalize_url(link.strip()),
                    "published": pub_date.strip(),
                    "description": _clean_html(summary)[:500],
                    "source": source_name,
                })
    return items


def _text(el, tag: str, ns: dict | None = None) -> str | None:
    child = el.find(tag, ns) if ns else el.find(tag)
    return child.text if child is not None and child.text else None


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


# ============================================
# 时效过滤
# ============================================

_DATE_FORMATS = [
    "%a, %d %b %Y %H:%M:%S %z",
    "%a, %d %b %Y %H:%M:%S %Z",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S  %z",
    "%Y-%m-%d %H:%M:%S %z",
    "%a, %d %b %Y %H:%M:%S GMT",
    "%Y-%m-%dT%H:%M:%S.%f%z",
]


def parse_pub_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def hours_since_published(date_str: str, now: datetime | None = None) -> float | None:
    dt = parse_pub_date(date_str)
    if dt is None:
        return None
    n = now or datetime.now()
    try:
        if dt.tzinfo is not None:
            n_aware = n.astimezone() if n.tzinfo is None else n
            delta = n_aware - dt
        else:
            delta = n - dt.replace(tzinfo=None)
        return delta.total_seconds() / 3600
    except Exception:
        return None


def filter_by_freshness(items: list[dict], hours: int, now: datetime | None = None) -> list[dict]:
    if hours <= 0:
        return items
    kept = []
    for item in items:
        hrs = hours_since_published(item.get("published", ""), now)
        if hrs is None or hrs <= hours:
            kept.append(item)
    return kept
