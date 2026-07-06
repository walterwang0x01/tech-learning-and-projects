"""补充采集层 — 无 Cookie、可脚本化的社区源（Agent-Reach 能力在生产侧的轻量落地）

设计原则：
- 只接入无需登录、可 HTTP/CLI 确定性拉取的源
- 产出与 RSS 同形的 pool 条目，走同一套 classify/candidates 流程
- Agent-Reach CLI 若已安装，可作为可选增强（doctor 检测后启用）
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from typing import Any

from .config import Config
from .http import http_get, normalize_url


def _unix_ts_to_rss(ts: int | float) -> str:
    dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z")


def _fetch_json(url: str, timeout: int = 15, headers: dict[str, str] | None = None) -> dict[str, Any] | None:
    import urllib.request

    hdrs = {"User-Agent": "BriefingTools/3.0 (Walter's Knowledge Base)"}
    if headers:
        hdrs.update(headers)
    try:
        req = urllib.request.Request(url, headers=hdrs)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8", errors="replace")
        return json.loads(text)
    except Exception:
        return None


_BILI_HEADERS = {
    "Referer": "https://www.bilibili.com",
    "Origin": "https://www.bilibili.com",
}


def fetch_bilibili_search(
    queries: list[str],
    *,
    max_per_query: int = 5,
    topic_hints: list[str] | None = None,
    timeout: int = 15,
) -> tuple[list[dict], dict]:
    """B站视频搜索（公开 API，无需登录；高频/无 Referer 可能 412）"""
    hints = topic_hints or ["china-tech"]
    items: list[dict] = []
    t0 = time.time()
    ok = True

    for i, q in enumerate(queries):
        if not q.strip():
            continue
        if i > 0:
            time.sleep(0.6)  # 降低 412 风控概率
        from urllib.parse import quote

        url = (
            "https://api.bilibili.com/x/web-interface/search/type"
            f"?search_type=video&keyword={quote(q)}&page=1&page_size={max_per_query}"
        )
        data = _fetch_json(url, timeout=timeout, headers=_BILI_HEADERS)
        if not data or data.get("code") != 0:
            ok = False
            continue
        for row in (data.get("data") or {}).get("result") or []:
            bvid = row.get("bvid") or ""
            title = (row.get("title") or "").replace('<em class="keyword">', "").replace("</em>", "")
            title = title.strip()
            if not bvid or not title:
                continue
            desc = (row.get("description") or row.get("desc") or "")[:500]
            pubdate = row.get("pubdate") or row.get("pub_time") or 0
            items.append({
                "title": title,
                "url": normalize_url(f"https://www.bilibili.com/video/{bvid}"),
                "published": _unix_ts_to_rss(pubdate) if pubdate else "",
                "description": desc,
                "source": "supplement/bilibili",
                "source_topic_hints": list(hints),
            })

    metric = {
        "name": "supplement/bilibili",
        "url": "https://api.bilibili.com/x/web-interface/search/type",
        "count": len(items),
        "elapsed_sec": round(time.time() - t0, 2),
        "ok": ok or bool(items),
    }
    return items, metric


def fetch_v2ex(
    *,
    nodes: list[str] | None = None,
    include_hot: bool = True,
    max_per_node: int = 10,
    topic_hints: list[str] | None = None,
    timeout: int = 15,
) -> tuple[list[dict], dict]:
    """V2EX 热门 + 节点帖子（公开 API）"""
    hints = topic_hints or ["ai-agent", "global-tech"]
    items: list[dict] = []
    seen_urls: set[str] = set()
    t0 = time.time()
    ok = True

    def _add_topic(t: dict, label: str) -> None:
        url = normalize_url(t.get("url") or "")
        if not url or url in seen_urls:
            return
        title = (t.get("title") or "").strip()
        if not title:
            return
        seen_urls.add(url)
        created = t.get("created") or t.get("last_modified") or 0
        node_name = (t.get("node") or {}).get("name", label)
        content = (t.get("content") or "")[:300]
        items.append({
            "title": title,
            "url": url,
            "published": _unix_ts_to_rss(created) if created else "",
            "description": content,
            "source": f"supplement/v2ex/{node_name}",
            "source_topic_hints": list(hints),
        })

    if include_hot:
        data = _fetch_json("https://www.v2ex.com/api/topics/hot.json", timeout=timeout)
        if data is None:
            ok = False
        else:
            for t in (data if isinstance(data, list) else [])[:max_per_node]:
                _add_topic(t, "hot")

    for node in nodes or []:
        if not node.strip():
            continue
        from urllib.parse import quote

        url = f"https://www.v2ex.com/api/topics/show.json?node_name={quote(node)}"
        data = _fetch_json(url, timeout=timeout)
        if data is None:
            ok = False
            continue
        for t in (data if isinstance(data, list) else [])[:max_per_node]:
            _add_topic(t, node)

    metric = {
        "name": "supplement/v2ex",
        "url": "https://www.v2ex.com/api/",
        "count": len(items),
        "elapsed_sec": round(time.time() - t0, 2),
        "ok": ok or bool(items),
    }
    return items, metric


def try_agent_reach_bilibili(
    queries: list[str],
    *,
    max_per_query: int = 5,
    topic_hints: list[str] | None = None,
) -> tuple[list[dict], dict | None]:
    """若本机装了 bili-cli / agent-reach，尝试 CLI 搜索（可选增强）。"""
    bili = shutil.which("bili") or shutil.which("bili-cli")
    if not bili:
        return [], None

    hints = topic_hints or ["china-tech"]
    items: list[dict] = []
    t0 = time.time()
    ok = True

    for q in queries:
        try:
            proc = subprocess.run(
                [bili, "search", q, "--json", "--limit", str(max_per_query)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode != 0:
                ok = False
                continue
            rows = json.loads(proc.stdout or "[]")
            if isinstance(rows, dict):
                rows = rows.get("items") or rows.get("results") or []
            for row in rows if isinstance(rows, list) else []:
                url = normalize_url(str(row.get("url") or row.get("link") or ""))
                title = str(row.get("title") or "").strip()
                if url and title:
                    items.append({
                        "title": title,
                        "url": url,
                        "published": str(row.get("published") or ""),
                        "description": str(row.get("description") or "")[:500],
                        "source": "supplement/bilibili-cli",
                        "source_topic_hints": list(hints),
                    })
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            ok = False

    if not items:
        return [], None
    return items, {
        "name": "supplement/bilibili-cli",
        "url": bili,
        "count": len(items),
        "elapsed_sec": round(time.time() - t0, 2),
        "ok": ok,
    }


def run_supplements(cfg: Config) -> tuple[list[dict], list[dict]]:
    """按 config.supplement_sources 拉取补充条目。返回 (items, metrics)。"""
    raw = cfg.raw.get("supplement_sources") or {}
    if not raw.get("enabled", False):
        return [], []

    all_items: list[dict] = []
    metrics: list[dict] = []

    bili_cfg = raw.get("bilibili") or {}
    if bili_cfg.get("enabled", False):
        queries = list(bili_cfg.get("queries") or [])
        max_q = int(bili_cfg.get("max_per_query", 5))
        hints = list(bili_cfg.get("topic_hints") or ["china-tech", "ai-agent"])
        # 优先 CLI（Agent-Reach 生态），失败走公开 API
        cli_items, cli_metric = try_agent_reach_bilibili(
            queries, max_per_query=max_q, topic_hints=hints,
        )
        if cli_items and cli_metric:
            all_items.extend(cli_items)
            metrics.append(cli_metric)
        else:
            items, metric = fetch_bilibili_search(
                queries, max_per_query=max_q, topic_hints=hints,
            )
            all_items.extend(items)
            metrics.append(metric)

    v2_cfg = raw.get("v2ex") or {}
    if v2_cfg.get("enabled", False):
        items, metric = fetch_v2ex(
            nodes=list(v2_cfg.get("nodes") or ["ai", "programmer"]),
            include_hot=bool(v2_cfg.get("include_hot", True)),
            max_per_node=int(v2_cfg.get("max_per_node", 10)),
            topic_hints=list(v2_cfg.get("topic_hints") or ["ai-agent", "global-tech"]),
        )
        all_items.extend(items)
        metrics.append(metric)

    return all_items, metrics
