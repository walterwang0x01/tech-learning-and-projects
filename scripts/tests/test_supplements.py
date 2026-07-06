"""补充采集层测试（无网络）"""

from conftest import *  # noqa
import json
import unittest
from unittest.mock import patch

from briefing_tools.config import Config, CircuitBreakerCfg, LLMClassifyCfg, SemanticDedupCfg
from briefing_tools.supplements import fetch_bilibili_search, fetch_v2ex, run_supplements


def _cfg_with_supplements(**supp_overrides) -> Config:
    supp = {
        "enabled": True,
        "bilibili": {
            "enabled": True,
            "queries": ["DeepSeek"],
            "max_per_query": 2,
            "topic_hints": ["china-tech"],
        },
        "v2ex": {
            "enabled": True,
            "include_hot": True,
            "nodes": ["ai"],
            "max_per_node": 2,
            "topic_hints": ["ai-agent"],
        },
    }
    supp.update(supp_overrides)
    return Config(
        freshness_hours=48,
        published_index_retention_days=60,
        run_retention_days=30,
        circuit_breaker=CircuitBreakerCfg(),
        main_topic_priority=["ai-agent", "china-tech", "global-tech"],
        rss_sources=[],
        classify_rules={},
        noise_keywords=[],
        score_overrides={},
        llm_classify=LLMClassifyCfg(),
        semantic_dedup=SemanticDedupCfg(),
        raw={"supplement_sources": supp},
    )


class TestBilibiliSearch(unittest.TestCase):
    def test_parse_results(self):
        payload = json.dumps({
            "code": 0,
            "data": {
                "result": [{
                    "bvid": "BV1xx",
                    "title": "DeepSeek <em class=\"keyword\">教程</em>",
                    "description": "demo",
                    "pubdate": 1700000000,
                }]
            },
        })
        with patch("briefing_tools.supplements._fetch_json") as mock_fetch:
            mock_fetch.return_value = json.loads(payload)
            items, metric = fetch_bilibili_search(["DeepSeek"], max_per_query=3)
        self.assertEqual(len(items), 1)
        self.assertIn("bilibili.com/video/BV1xx", items[0]["url"])
        self.assertEqual(items[0]["source"], "supplement/bilibili")
        self.assertTrue(metric["ok"])


class TestV2ex(unittest.TestCase):
    def test_hot_and_node(self):
        hot = json.dumps([{
            "title": "AI topic",
            "url": "https://www.v2ex.com/t/1",
            "created": 1700000000,
            "content": "body",
            "node": {"name": "ai"},
        }])
        node = json.dumps([{
            "title": "Rust release",
            "url": "https://www.v2ex.com/t/2",
            "created": 1700000001,
            "content": "rust",
            "node": {"name": "programmer"},
        }])

        def fake_get(url, timeout=15, headers=None):
            if "hot.json" in url:
                return json.loads(hot)
            if "node_name=ai" in url:
                return json.loads(hot)
            return json.loads(node)

        with patch("briefing_tools.supplements._fetch_json", side_effect=fake_get):
            items, metric = fetch_v2ex(nodes=["programmer"], include_hot=True, max_per_node=5)
        self.assertEqual(len(items), 2)
        self.assertTrue(metric["ok"])


class TestRunSupplements(unittest.TestCase):
    def test_disabled(self):
        cfg = _cfg_with_supplements(enabled=False)
        items, metrics = run_supplements(cfg)
        self.assertEqual(items, [])
        self.assertEqual(metrics, [])


if __name__ == "__main__":
    unittest.main()
