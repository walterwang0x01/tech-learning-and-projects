"""Hacker News Algolia API 备用采集（hnrss.org 502/超时时启用）"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from .http import normalize_url

ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search"


def fetch_hn_algolia(
    query: str,
    *,
    tags: str = "story",
    points_min: int | None = None,
    hits_per_page: int = 30,
    timeout: int = 20,
) -> list[dict]:
    """从 Algolia HN API 拉取故事，归一化为 ingest 条目格式。"""
    params: dict[str, str | int] = {
        "query": query,
        "tags": tags,
        "hitsPerPage": hits_per_page,
    }
    if points_min is not None:
        params["numericFilters"] = f"points>{points_min}"

    url = f"{ALGOLIA_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "BriefingTools/3.0 (HN Algolia fallback)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return []

    items: list[dict] = []
    for hit in data.get("hits") or []:
        title = (hit.get("title") or "").strip()
        object_id = hit.get("objectID") or hit.get("story_id")
        if not title or not object_id:
            continue
        created = hit.get("created_at_i")
        if created:
            published = datetime.fromtimestamp(int(created), tz=timezone.utc).strftime(
                "%a, %d %b %Y %H:%M:%S %z"
            )
        else:
            published = ""
        points = hit.get("points") or 0
        url_story = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
        items.append({
            "title": title,
            "url": normalize_url(str(url_story)),
            "published": published,
            "description": f"HN {points} points — {hit.get('author', '')}",
            "source": "HN Algolia",
        })
    return items
