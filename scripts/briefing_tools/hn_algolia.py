"""Hacker News Algolia API 备用采集（hnrss.org 502/超时时启用）

Algolia HN API 的 numericFilters 参数已不可用（恒 400），因此：
- 使用 search_by_date 模拟 hnrss newest 语义
- points 阈值在客户端过滤
- 支持多关键词分别检索后合并去重
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

from .http import normalize_url

ALGOLIA_SEARCH_BY_DATE_URL = "https://hn.algolia.com/api/v1/search_by_date"
USER_AGENT = "BriefingTools/3.0 (HN Algolia fallback)"


def _resolve_search_terms(query: str, queries: list[str] | None) -> list[str]:
    if queries:
        return [q.strip() for q in queries if q and q.strip()]
    q = query.strip()
    if not q:
        return []
    # 兼容旧配置：整句 query 作为单条检索
    return [q]


def _search_by_date_page(
    term: str,
    *,
    tags: str,
    page: int,
    hits_per_page: int,
    timeout: int,
) -> list[dict]:
    params = {
        "query": term,
        "tags": tags,
        "hitsPerPage": hits_per_page,
        "page": page,
    }
    url = f"{ALGOLIA_SEARCH_BY_DATE_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return list(data.get("hits") or [])


def _search_term(
    term: str,
    *,
    tags: str,
    hits_per_page: int,
    max_pages: int,
    timeout: int,
) -> list[dict]:
    hits: list[dict] = []
    for page in range(max_pages):
        try:
            page_hits = _search_by_date_page(
                term,
                tags=tags,
                page=page,
                hits_per_page=hits_per_page,
                timeout=timeout,
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            break
        if not page_hits:
            break
        hits.extend(page_hits)
        if len(page_hits) < hits_per_page:
            break
    return hits


def _merge_hits(hits: list[dict]) -> list[dict]:
    by_id: dict[str, dict] = {}
    for hit in hits:
        oid = str(hit.get("objectID") or hit.get("story_id") or "").strip()
        if not oid:
            continue
        prev = by_id.get(oid)
        if not prev or (hit.get("created_at_i") or 0) > (prev.get("created_at_i") or 0):
            by_id[oid] = hit
    return list(by_id.values())


def _filter_hits(
    hits: list[dict],
    *,
    points_min: int | None,
    freshness_hours: int,
    limit: int,
) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=freshness_hours)
    filtered: list[dict] = []
    for hit in hits:
        title = (hit.get("title") or "").strip()
        if not title:
            continue
        points = int(hit.get("points") or 0)
        if points_min is not None and points < points_min:
            continue
        created = hit.get("created_at_i")
        if created:
            published_at = datetime.fromtimestamp(int(created), tz=timezone.utc)
            if published_at < cutoff:
                continue
        filtered.append(hit)
    filtered.sort(key=lambda h: h.get("created_at_i") or 0, reverse=True)
    return filtered[:limit]


def _hit_to_item(hit: dict) -> dict | None:
    title = (hit.get("title") or "").strip()
    object_id = hit.get("objectID") or hit.get("story_id")
    if not title or not object_id:
        return None
    created = hit.get("created_at_i")
    if created:
        published = datetime.fromtimestamp(int(created), tz=timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S %z"
        )
    else:
        published = ""
    points = hit.get("points") or 0
    url_story = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
    return {
        "title": title,
        "url": normalize_url(str(url_story)),
        "published": published,
        "description": f"HN {points} points — {hit.get('author', '')}",
        "source": "HN Algolia",
    }


def fetch_hn_algolia(
    query: str = "",
    *,
    queries: list[str] | None = None,
    tags: str = "story",
    points_min: int | None = None,
    hits_per_page: int = 30,
    freshness_hours: int = 168,
    max_pages_per_query: int = 2,
    timeout: int = 20,
) -> list[dict]:
    """从 Algolia HN API 拉取故事，归一化为 ingest 条目格式。"""
    terms = _resolve_search_terms(query, queries)
    if not terms:
        return []

    page_size = max(hits_per_page, 50)
    all_hits: list[dict] = []

    workers = min(len(terms), 4)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(
                _search_term,
                term,
                tags=tags,
                hits_per_page=page_size,
                max_pages=max_pages_per_query,
                timeout=timeout,
            )
            for term in terms
        ]
        for future in as_completed(futures):
            try:
                all_hits.extend(future.result())
            except Exception:
                continue

    merged = _merge_hits(all_hits)
    if not merged:
        return []

    selected = _filter_hits(
        merged,
        points_min=points_min,
        freshness_hours=freshness_hours,
        limit=hits_per_page,
    )

    # 结果不足时放宽 points 阈值（仍保留时效过滤）
    min_wanted = min(hits_per_page, 5)
    if len(selected) < min_wanted and points_min is not None and points_min > 5:
        relaxed = max(5, points_min // 2)
        selected = _filter_hits(
            merged,
            points_min=relaxed,
            freshness_hours=freshness_hours,
            limit=hits_per_page,
        )
        if selected:
            print(
                f"  ℹ️  Algolia 备用放宽 points 阈值 {points_min} → {relaxed}，"
                f"命中 {len(selected)} 条",
                file=sys.stderr,
            )

    items: list[dict] = []
    for hit in selected:
        item = _hit_to_item(hit)
        if item:
            items.append(item)
    return items
