"""Candidates：按主题分流候选集"""

from __future__ import annotations

from datetime import datetime

from .config import Config, TOPICS
from .dedup import dedup_semantic, title_in
from .storage import (
    briefing_file,
    extract_titles_from_md,
    extract_urls_from_md,
    load_published_index,
    url_hash,
)


def build_candidates(
    classified: list[dict],
    topic: str,
    date_str: str,
    cfg: Config,
    min_score: int = 12,
    require_main_topic: bool = False,
) -> dict:
    """构造候选集。

    过滤顺序：
    1. tags 命中 topic
    2. 如 require_main_topic=True，要求 main_topic == topic
    3. score.total >= min_score
    4. 不在 published_index 中（跨天去重）
    5. 不命中今日其他主题已写文件的标题/URL（跨主题去重）
    6. 语义去重（cfg.semantic_dedup.enabled）

    返回:
      {"topic", "date", "stats", "items"}
    """
    published = load_published_index()["items"]

    # 其他主题今日文件
    other_titles: list[str] = []
    other_urls: set[str] = set()
    for ot in TOPICS:
        if ot == topic:
            continue
        f = briefing_file(ot, date_str)
        other_titles.extend(extract_titles_from_md(f))
        other_urls |= extract_urls_from_md(f)

    kept: list[dict] = []
    stats = {
        "input": len(classified),
        "kept": 0,
        "filtered": {
            "no_topic_match": 0,
            "not_main_topic": 0,
            "low_score": 0,
            "published_before": 0,
            "cross_topic_dup": 0,
            "semantic_dup": 0,
        },
    }

    for it in classified:
        tags = it.get("tags") or []
        if topic not in tags:
            stats["filtered"]["no_topic_match"] += 1
            continue
        if require_main_topic and it.get("main_topic") != topic:
            stats["filtered"]["not_main_topic"] += 1
            continue
        total = (it.get("score") or {}).get("total", 0)
        if total < min_score:
            stats["filtered"]["low_score"] += 1
            continue
        uh = url_hash(it["url"])
        if uh in published:
            stats["filtered"]["published_before"] += 1
            continue
        if it["url"] in other_urls or title_in(it["title"], other_titles):
            stats["filtered"]["cross_topic_dup"] += 1
            continue
        kept.append(it)

    # 语义去重（可选）
    if cfg.semantic_dedup.enabled and kept:
        kept, removed = dedup_semantic(kept, cfg.semantic_dedup.threshold)
        stats["filtered"]["semantic_dup"] = len(removed)

    kept.sort(key=lambda x: (-x["score"]["total"], x.get("published", "")))
    stats["kept"] = len(kept)

    return {"topic": topic, "date": date_str, "stats": stats, "items": kept}
