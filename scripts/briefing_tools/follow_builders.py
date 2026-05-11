"""Follow Builders 中心化 feed 采集。

来源：https://github.com/zarazhangrui/follow-builders （MIT，公开 feed，无 key）

三个 feed：
- feed-x.json          — 25 个 AI builder 的近 24h 推文（官方 X API 中心化拉取）
- feed-podcasts.json   — 6 档头部 AI 播客 14 天内的 episode + transcript（Supadata）
- feed-blogs.json      — 官方博客（Anthropic Engineering / Claude Blog），已有 RSS，不启用

本模块把 feed 条目归一化成 PoolItem 结构（与 `parse_rss` 输出同形），
统一打 `source_topic_hints=["ai-agent"]`，丢回主 ingest 的 items 池，
走后续 dedup / freshness / classify / score。

生产加固（见 briefing-rules.md）：
1. per-feed 新鲜度覆盖（PoolItem.freshness_override_hours）：
   x 用 36h，podcasts 用 336h，blogs 用 72h，绕开全局 48h。
2. 上游 feed 新鲜度守卫：feed.generatedAt 超过 48h 视为停更，ok=False 让熔断接管。
3. X 准入三件套：长文 / 含链接 / 高 likes 任一命中即收。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .config import FollowBuildersCfg
from .http import http_get, normalize_url, parse_pub_date


FEED_FILES = {
    "x": "feed-x.json",
    "podcasts": "feed-podcasts.json",
    "blogs": "feed-blogs.json",
}

# per-feed 新鲜度覆盖：对齐上游各 feed 的 lookbackHours，避免全局 48h 错杀
FEED_FRESHNESS_HOURS = {
    "x": 36,
    "podcasts": 336,
    "blogs": 72,
}

# feed.generatedAt 超过这个小时数视为上游停更
FEED_STALE_THRESHOLD_HOURS = 48


def _normalize_iso(ts: str | None) -> str:
    """把 feed 里的 ISO8601 ('2026-05-10T07:06:29.000Z') 转成 parse_pub_date 能认的格式。

    现有 `parse_pub_date` 认 %z（+0000）但不认裸 Z，这里统一替换。
    空值原样返回，让 freshness 走"未知→保留"分支。
    """
    if not ts:
        return ""
    s = ts.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return s


def _feed_is_stale(generated_at: str | None, now: datetime | None = None) -> bool:
    """判断 feed.generatedAt 是否过旧（上游 GitHub Action 停更）"""
    if not generated_at:
        return False  # 没提供时间戳，放行让其他信号决策
    dt = parse_pub_date(_normalize_iso(generated_at))
    if dt is None:
        return False
    n = now or datetime.now(timezone.utc)
    if n.tzinfo is None:
        n = n.replace(tzinfo=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    age_hours = (n - dt).total_seconds() / 3600
    return age_hours > FEED_STALE_THRESHOLD_HOURS


def _fetch_json(url: str, timeout: int) -> dict[str, Any] | None:
    text = http_get(url, timeout=timeout)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


# ==============================================================
# feed-x.json -> PoolItem
# ==============================================================

def items_from_x(feed: dict[str, Any], cfg: FollowBuildersCfg) -> list[dict]:
    """把 X feed 展开成单条 tweet → PoolItem。

    准入规则（三件套，任一命中即收）：
    - 文本 ≥ 200 字（长推，有观点密度）
    - 含 http URL（带外链，有信号）
    - likes ≥ x_min_likes（广受认可）

    额外过滤：
    - 短 @ 回复（<120 字且不含链接）直接丢
    - 每作者按 likes 取 Top-N (x_max_per_author)
    """
    authors = feed.get("x") or []
    out: list[dict] = []
    min_likes = cfg.x_min_likes
    cap = cfg.x_max_per_author

    def _worth_keeping(t: dict) -> bool:
        text = (t.get("text") or "").strip()
        if not text:
            return False
        likes = int(t.get("likes") or 0)
        is_long = len(text) >= 200
        has_link = "http" in text
        is_reply_short = text.startswith("@") and not has_link and len(text) < 120
        if is_reply_short:
            return False
        # 三件套任一命中
        return is_long or has_link or likes >= min_likes

    for author in authors:
        handle = author.get("handle") or ""
        name = author.get("name") or handle
        tweets = author.get("tweets") or []

        filtered = [t for t in tweets if _worth_keeping(t)]
        filtered.sort(key=lambda t: int(t.get("likes") or 0), reverse=True)
        filtered = filtered[:cap]

        for t in filtered:
            url = t.get("url") or ""
            text = (t.get("text") or "").strip()
            if not url or not text:
                continue
            first_line = text.split("\n", 1)[0].strip()
            title = f"{name} (@{handle}): {first_line[:140]}"
            out.append({
                "title": title,
                "url": normalize_url(url),
                "published": _normalize_iso(t.get("createdAt")),
                "description": text[:500],
                "source": f"follow-builders/x/@{handle}",
                "source_topic_hints": ["ai-agent"],
                "freshness_override_hours": FEED_FRESHNESS_HOURS["x"],
            })
    return out


# ==============================================================
# feed-podcasts.json -> PoolItem
# ==============================================================

def items_from_podcasts(feed: dict[str, Any], cfg: FollowBuildersCfg) -> list[dict]:
    """podcasts feed 是扁平列表，每个 episode 一条。

    description 取 transcript 的前 N 字（受 cfg.podcast_description_chars 限制，
    推荐 ≤300）。transcript 带讲话人时间戳，不适合全文塞入 —— 只当 classify 的
    关键词 hint，下游 curate 阶段如要深入，应读 URL。
    """
    episodes = feed.get("podcasts") or []
    out: list[dict] = []
    for ep in episodes:
        url = ep.get("url") or ""
        title = (ep.get("title") or "").strip()
        if not url or not title:
            continue
        transcript = (ep.get("transcript") or "").strip()
        desc = transcript[: cfg.podcast_description_chars] if transcript else ""
        name = ep.get("name") or "podcast"
        out.append({
            "title": f"[Podcast] {title}",
            "url": normalize_url(url),
            "published": _normalize_iso(ep.get("publishedAt")),
            "description": desc,
            "source": f"follow-builders/podcast/{name}",
            "source_topic_hints": ["ai-agent"],
            "freshness_override_hours": FEED_FRESHNESS_HOURS["podcasts"],
        })
    return out


# ==============================================================
# feed-blogs.json -> PoolItem（默认不启用）
# ==============================================================

def items_from_blogs(feed: dict[str, Any], cfg: FollowBuildersCfg) -> list[dict]:
    blogs = feed.get("blogs") or []
    out: list[dict] = []
    for post in blogs:
        url = post.get("url") or ""
        title = (post.get("title") or "").strip()
        if not url or not title:
            continue
        desc = (post.get("description") or post.get("content") or "")[:800]
        name = post.get("name") or "blog"
        out.append({
            "title": title,
            "url": normalize_url(url),
            "published": _normalize_iso(post.get("publishedAt")),
            "description": desc,
            "source": f"follow-builders/blog/{name}",
            "source_topic_hints": ["ai-agent"],
            "freshness_override_hours": FEED_FRESHNESS_HOURS["blogs"],
        })
    return out


_BUILDERS = {
    "x": items_from_x,
    "podcasts": items_from_podcasts,
    "blogs": items_from_blogs,
}


# ==============================================================
# 入口
# ==============================================================

def fetch_follow_builders(cfg: FollowBuildersCfg) -> tuple[list[dict], list[dict]]:
    """采集配置启用的 feeds。

    返回 (items, per_feed_metrics)。每个 feed 对应一条 metrics，
    结构对齐 ingest 里 RSS 的 metrics，便于 health 记录和状态面板。

    守卫：feed.generatedAt 超过 FEED_STALE_THRESHOLD_HOURS 视为上游停更，
    metric.ok=False 让既有熔断机制接管（连续 N 天失败自动跳过）。
    """
    if not cfg.enabled:
        return [], []

    items: list[dict] = []
    metrics: list[dict] = []

    for feed_name in cfg.feeds:
        if feed_name not in _BUILDERS:
            continue
        filename = FEED_FILES[feed_name]
        url = f"{cfg.feed_base_url.rstrip('/')}/{filename}"
        source_label = f"follow-builders/{feed_name}"
        data = _fetch_json(url, timeout=cfg.timeout)
        if data is None:
            metrics.append({
                "name": source_label,
                "url": url,
                "count": 0,
                "elapsed_sec": 0.0,
                "ok": False,
            })
            continue
        # 守卫：上游 GitHub Action 是否停更
        if _feed_is_stale(data.get("generatedAt")):
            metrics.append({
                "name": source_label,
                "url": url,
                "count": 0,
                "elapsed_sec": 0.0,
                "ok": False,
                "reason": "stale",
            })
            continue
        feed_items = _BUILDERS[feed_name](data, cfg)
        items.extend(feed_items)
        metrics.append({
            "name": source_label,
            "url": url,
            "count": len(feed_items),
            "elapsed_sec": 0.0,
            "ok": True,
        })

    return items, metrics
