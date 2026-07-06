"""follow-builders feed 采集与归一化测试（无网络）"""

from conftest import *  # noqa
import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from briefing_tools.config import FollowBuildersCfg
from briefing_tools.follow_builders import (
    FEED_FRESHNESS_HOURS,
    FEED_STALE_THRESHOLD_HOURS,
    _feed_is_stale,
    _normalize_iso,
    fetch_follow_builders,
    items_from_blogs,
    items_from_podcasts,
    items_from_x,
)
from briefing_tools.http import filter_by_freshness
from briefing_tools.schemas import validate_pool_item


# ==========================================================
# 时间戳归一化
# ==========================================================

class TestNormalizeISO(unittest.TestCase):
    def test_z_suffix_replaced(self):
        self.assertEqual(
            _normalize_iso("2026-05-10T07:06:29.000Z"),
            "2026-05-10T07:06:29.000+00:00",
        )

    def test_offset_preserved(self):
        self.assertEqual(
            _normalize_iso("2026-05-10T07:06:29+08:00"),
            "2026-05-10T07:06:29+08:00",
        )

    def test_empty(self):
        self.assertEqual(_normalize_iso(""), "")
        self.assertEqual(_normalize_iso(None), "")


# ==========================================================
# X feed 归一化
# ==========================================================

class TestItemsFromX(unittest.TestCase):
    def setUp(self):
        self.cfg = FollowBuildersCfg(
            enabled=True,
            x_min_likes=50,
            x_max_per_author=2,
        )
        self.feed = {
            "x": [
                {
                    "name": "Swyx",
                    "handle": "swyx",
                    "tweets": [
                        # 长推，应入选（即使 likes 未达阈值）
                        {
                            "text": "AI agent " + "A" * 240,
                            "url": "https://x.com/swyx/status/1",
                            "createdAt": "2026-05-10T07:06:29.000Z",
                            "likes": 10,
                        },
                        # 含链接 + AI 信号，应入选
                        {
                            "text": "new MCP release https://example.com/paper",
                            "url": "https://x.com/swyx/status/2",
                            "createdAt": "2026-05-10T08:00:00.000Z",
                            "likes": 5,
                        },
                        # 高 likes + AI 信号，应入选
                        {
                            "text": "short hot take on Claude Codex",
                            "url": "https://x.com/swyx/status/3",
                            "createdAt": "2026-05-10T09:00:00.000Z",
                            "likes": 100,
                        },
                        # 低信号，应过滤（无 AI 关键词）
                        {
                            "text": "boring update about football",
                            "url": "https://x.com/swyx/status/4",
                            "createdAt": "2026-05-10T09:05:00.000Z",
                            "likes": 5,
                        },
                        # 短 @ 回复，应过滤
                        {
                            "text": "@someone haha",
                            "url": "https://x.com/swyx/status/5",
                            "createdAt": "2026-05-10T09:10:00.000Z",
                            "likes": 50,
                        },
                    ],
                },
            ]
        }

    def test_basic_shape(self):
        items = items_from_x(self.feed, self.cfg)
        # cap=2，命中的 3 条里按 likes 取 Top-2
        self.assertEqual(len(items), 2)
        for it in items:
            self.assertIn("title", it)
            self.assertIn("url", it)
            self.assertIn("published", it)
            self.assertEqual(it["source_topic_hints"], [])
            self.assertTrue(it["source"].startswith("follow-builders/x/@"))
            # per-feed freshness override
            self.assertEqual(it["freshness_override_hours"], FEED_FRESHNESS_HOURS["x"])

    def test_long_tweet_admitted_without_likes(self):
        # 专门验证"长文"准入独立于 likes
        cfg = FollowBuildersCfg(x_min_likes=100, x_max_per_author=5)
        feed = {
            "x": [{
                "name": "A", "handle": "a",
                "tweets": [{"text": "x" * 200 + " AI agent framework", "url": "https://x.com/a/1",
                            "createdAt": "", "likes": 0}]
            }]
        }
        items = items_from_x(feed, cfg)
        self.assertEqual(len(items), 1)

    def test_link_tweet_admitted_without_likes(self):
        cfg = FollowBuildersCfg(x_min_likes=100, x_max_per_author=5)
        feed = {
            "x": [{
                "name": "A", "handle": "a",
                "tweets": [{"text": "look at this LLM paper https://example.com", "url": "https://x.com/a/1",
                            "createdAt": "", "likes": 0}]
            }]
        }
        items = items_from_x(feed, cfg)
        self.assertEqual(len(items), 1)

    def test_low_signal_tweet_filtered(self):
        items = items_from_x(self.feed, self.cfg)
        urls = {it["url"] for it in items}
        self.assertNotIn("https://x.com/swyx/status/4", urls)

    def test_reply_filter(self):
        items = items_from_x(self.feed, self.cfg)
        urls = {it["url"] for it in items}
        self.assertNotIn("https://x.com/swyx/status/5", urls)

    def test_per_author_cap(self):
        cfg = FollowBuildersCfg(x_min_likes=0, x_max_per_author=1)
        feed = {
            "x": [
                {
                    "name": "A",
                    "handle": "a",
                    "tweets": [
                        {"text": "first valid long tweet about AI agents", "url": "https://x.com/a/1", "createdAt": "", "likes": 10},
                        {"text": "second valid long tweet on MCP release", "url": "https://x.com/a/2", "createdAt": "", "likes": 50},
                        {"text": "third valid long tweet Claude Codex", "url": "https://x.com/a/3", "createdAt": "", "likes": 30},
                    ],
                }
            ]
        }
        items = items_from_x(feed, cfg)
        self.assertEqual(len(items), 1)
        # 选 likes 最高的
        self.assertEqual(items[0]["url"], "https://x.com/a/2")

    def test_iso_normalized(self):
        items = items_from_x(self.feed, self.cfg)
        self.assertTrue(items[0]["published"].endswith("+00:00"))

    def test_non_ai_tweet_filtered_even_with_likes(self):
        feed = {
            "x": [{
                "name": "A", "handle": "a",
                "tweets": [{
                    "text": "Happy birthday America!",
                    "url": "https://x.com/a/99",
                    "createdAt": "", "likes": 500,
                }],
            }]
        }
        self.assertEqual(items_from_x(feed, self.cfg), [])

    def test_empty_tweets_skipped(self):
        feed = {"x": [{"name": "X", "handle": "x", "tweets": []}]}
        self.assertEqual(items_from_x(feed, self.cfg), [])


# ==========================================================
# Podcasts feed 归一化
# ==========================================================

class TestItemsFromPodcasts(unittest.TestCase):
    def setUp(self):
        self.cfg = FollowBuildersCfg(podcast_description_chars=100)

    def test_basic_shape(self):
        feed = {
            "podcasts": [
                {
                    "source": "podcast",
                    "name": "Latent Space",
                    "title": "Episode X",
                    "url": "https://example.com/ep-x",
                    "publishedAt": "2026-05-08T17:05:00.000Z",
                    "transcript": "A" * 500,
                }
            ]
        }
        items = items_from_podcasts(feed, self.cfg)
        self.assertEqual(len(items), 1)
        it = items[0]
        self.assertTrue(it["title"].startswith("[Podcast] "))
        self.assertEqual(it["source"], "follow-builders/podcast/Latent Space")
        self.assertEqual(it["source_topic_hints"], ["ai-agent"])
        self.assertEqual(len(it["description"]), 100)
        self.assertTrue(it["published"].endswith("+00:00"))
        # per-feed override，podcasts 用 336h
        self.assertEqual(it["freshness_override_hours"], FEED_FRESHNESS_HOURS["podcasts"])

    def test_missing_title_or_url_skipped(self):
        feed = {"podcasts": [
            {"url": "", "title": "no url"},
            {"url": "https://x", "title": ""},
        ]}
        self.assertEqual(items_from_podcasts(feed, self.cfg), [])


# ==========================================================
# fetch_follow_builders 集成（mock HTTP）
# ==========================================================

class TestFetchFollowBuilders(unittest.TestCase):
    def test_disabled_returns_empty(self):
        cfg = FollowBuildersCfg(enabled=False)
        items, metrics = fetch_follow_builders(cfg)
        self.assertEqual(items, [])
        self.assertEqual(metrics, [])

    def test_happy_path(self):
        cfg = FollowBuildersCfg(enabled=True, feeds=["x", "podcasts"], x_min_likes=0)
        fresh = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        x_payload = json.dumps({
            "generatedAt": fresh,
            "x": [{"name": "A", "handle": "a", "tweets": [
                {"text": "long enough tweet about LangGraph agents", "url": "https://x.com/a/1",
                 "createdAt": "2026-05-10T07:00:00.000Z", "likes": 100},
            ]}]
        })
        p_payload = json.dumps({
            "generatedAt": fresh,
            "podcasts": [
                {"name": "Pod", "title": "Ep", "url": "https://e.com/1",
                 "publishedAt": "2026-05-08T00:00:00.000Z", "transcript": "hello"}
            ]
        })
        responses = {
            "feed-x.json": x_payload,
            "feed-podcasts.json": p_payload,
        }

        def fake_http_get(url, timeout=10, retries=1):
            for k, v in responses.items():
                if url.endswith(k):
                    return v
            return None

        with patch("briefing_tools.follow_builders.http_get", side_effect=fake_http_get):
            items, metrics = fetch_follow_builders(cfg)
        self.assertEqual(len(items), 2)
        self.assertEqual(len(metrics), 2)
        self.assertTrue(all(m["ok"] for m in metrics))

    def test_fetch_failure_records_metric(self):
        cfg = FollowBuildersCfg(enabled=True, feeds=["x"])
        with patch("briefing_tools.follow_builders.http_get", return_value=None):
            items, metrics = fetch_follow_builders(cfg)
        self.assertEqual(items, [])
        self.assertEqual(len(metrics), 1)
        self.assertFalse(metrics[0]["ok"])

    def test_stale_feed_marked_not_ok(self):
        """上游停更（generatedAt 超过 48h）视为失败，让熔断接管"""
        cfg = FollowBuildersCfg(enabled=True, feeds=["x"])
        stale_time = datetime.now(timezone.utc) - timedelta(hours=72)
        stale_payload = json.dumps({
            "generatedAt": stale_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "x": [{"name": "A", "handle": "a", "tweets": [
                {"text": "x" * 300, "url": "https://x.com/a/1",
                 "createdAt": "2026-05-10T07:00:00.000Z", "likes": 999},
            ]}]
        })
        with patch("briefing_tools.follow_builders.http_get", return_value=stale_payload):
            items, metrics = fetch_follow_builders(cfg)
        self.assertEqual(items, [])
        self.assertEqual(len(metrics), 1)
        self.assertFalse(metrics[0]["ok"])
        self.assertEqual(metrics[0].get("reason"), "stale")


# ==========================================================
# 上游 stale 守卫单元
# ==========================================================

class TestFeedStaleGuard(unittest.TestCase):
    def _ts(self, hours_ago: float) -> str:
        dt = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def test_fresh_feed_ok(self):
        self.assertFalse(_feed_is_stale(self._ts(1)))

    def test_edge_under_threshold(self):
        self.assertFalse(_feed_is_stale(self._ts(FEED_STALE_THRESHOLD_HOURS - 0.5)))

    def test_edge_over_threshold(self):
        self.assertTrue(_feed_is_stale(self._ts(FEED_STALE_THRESHOLD_HOURS + 1)))

    def test_missing_timestamp_not_stale(self):
        # 没提供 generatedAt 时不应误判为停更
        self.assertFalse(_feed_is_stale(None))
        self.assertFalse(_feed_is_stale(""))

    def test_malformed_timestamp_not_stale(self):
        self.assertFalse(_feed_is_stale("not a date"))


# ==========================================================
# per-item freshness override 集成到 filter_by_freshness
# ==========================================================

class TestPerItemFreshness(unittest.TestCase):
    def test_override_extends_window(self):
        """podcast 条目带 336h override，即使全局 48h 也应保留"""
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=200)).strftime(
            "%Y-%m-%dT%H:%M:%S+00:00"
        )
        items = [{
            "title": "old podcast", "url": "https://e.com/1",
            "published": old_ts,
            "freshness_override_hours": 336,
        }]
        kept = filter_by_freshness(items, hours=48)
        self.assertEqual(len(kept), 1)

    def test_override_shortens_window(self):
        """带 x 36h override 时，全局 72h 也不能救活 40h 前的推文"""
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=40)).strftime(
            "%Y-%m-%dT%H:%M:%S+00:00"
        )
        items = [{
            "title": "old tweet", "url": "https://x.com/1",
            "published": old_ts,
            "freshness_override_hours": 36,
        }]
        kept = filter_by_freshness(items, hours=72)
        self.assertEqual(len(kept), 0)

    def test_no_override_uses_global(self):
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=200)).strftime(
            "%Y-%m-%dT%H:%M:%S+00:00"
        )
        items = [{
            "title": "rss article", "url": "https://r.com/1",
            "published": old_ts,
        }]
        kept = filter_by_freshness(items, hours=48)
        self.assertEqual(len(kept), 0)


# ==========================================================
# PoolItem schema roundtrip（override 字段）
# ==========================================================

class TestPoolItemOverride(unittest.TestCase):
    def test_roundtrip_with_override(self):
        d = {
            "title": "t", "url": "https://x.com/1",
            "freshness_override_hours": 336,
        }
        pi = validate_pool_item(d)
        self.assertEqual(pi.freshness_override_hours, 336)
        out = pi.to_dict()
        self.assertEqual(out["freshness_override_hours"], 336)

    def test_roundtrip_without_override_drops_key(self):
        """不带 override 的 RSS 条目 to_dict 应不落 None 字段，保持 JSONL 干净"""
        d = {"title": "t", "url": "https://x.com/1"}
        pi = validate_pool_item(d)
        self.assertIsNone(pi.freshness_override_hours)
        out = pi.to_dict()
        self.assertNotIn("freshness_override_hours", out)


if __name__ == "__main__":
    unittest.main()
