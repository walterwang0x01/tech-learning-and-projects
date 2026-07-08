"""hn_algolia 备用采集单元测试"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from briefing_tools.hn_algolia import (
    _filter_hits,
    _merge_hits,
    _resolve_search_terms,
    fetch_hn_algolia,
)


def _hit(oid: str, title: str, points: int, created_at_i: int) -> dict:
    return {
        "objectID": oid,
        "title": title,
        "points": points,
        "created_at_i": created_at_i,
        "author": "tester",
        "url": f"https://example.com/{oid}",
    }


def test_resolve_search_terms_prefers_queries_list():
    assert _resolve_search_terms("ignored", ["LangGraph", "RAG"]) == ["LangGraph", "RAG"]


def test_resolve_search_terms_falls_back_to_single_query():
    assert _resolve_search_terms("AI agent MCP", None) == ["AI agent MCP"]


def test_merge_hits_dedupes_by_object_id():
    now = int(datetime.now(timezone.utc).timestamp())
    merged = _merge_hits([
        _hit("1", "A", 10, now - 100),
        _hit("1", "A newer", 20, now),
        _hit("2", "B", 5, now),
    ])
    assert len(merged) == 2
    by_id = {h["objectID"]: h for h in merged}
    assert by_id["1"]["points"] == 20


def test_filter_hits_applies_points_and_freshness():
    now = int(datetime.now(timezone.utc).timestamp())
    old = now - 3600 * 24 * 30
    hits = [
        _hit("1", "fresh high", 30, now - 3600),
        _hit("2", "fresh low", 5, now - 7200),
        _hit("3", "stale high", 50, old),
    ]
    out = _filter_hits(hits, points_min=20, freshness_hours=168, limit=10)
    assert [h["objectID"] for h in out] == ["1"]


@patch("briefing_tools.hn_algolia._search_term")
def test_fetch_hn_algolia_merges_multi_query_results(mock_search):
    now = int(datetime.now(timezone.utc).timestamp())

    def side_effect(term, **kwargs):
        if term == "LangGraph":
            return [_hit("1", "LangGraph post", 25, now - 100)]
        if term == "RAG":
            return [_hit("2", "RAG post", 22, now - 200)]
        return []

    mock_search.side_effect = side_effect

    items = fetch_hn_algolia(
        queries=["LangGraph", "RAG"],
        points_min=20,
        hits_per_page=10,
        freshness_hours=168,
    )
    assert len(items) == 2
    assert items[0]["title"] == "LangGraph post"
    assert "HN 25 points" in items[0]["description"]
    assert items[0]["url"].startswith("https://")
