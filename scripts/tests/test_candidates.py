"""candidates 阶段测试：多主题筛选、main_topic、跨主题去重"""

from conftest import *  # noqa
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from briefing_tools import config as cfg_mod
from briefing_tools.candidates import build_candidates
from briefing_tools.config import (
    CircuitBreakerCfg,
    Config,
    LLMClassifyCfg,
    SemanticDedupCfg,
)


def _make_cfg(**overrides) -> Config:
    base = {
        "freshness_hours": 48,
        "published_index_retention_days": 60,
        "run_retention_days": 30,
        "circuit_breaker": CircuitBreakerCfg(),
        "main_topic_priority": ["ai-agent", "china-tech", "global-tech"],
        "rss_sources": [],
        "classify_rules": {},
        "noise_keywords": [],
        "score_overrides": {},
        "llm_classify": LLMClassifyCfg(),
        "semantic_dedup": SemanticDedupCfg(),
        "raw": {},
    }
    base.update(overrides)
    return Config(**base)


def _item(title, url, tags, score_total=15, main_topic=None):
    return {
        "title": title,
        "url": url,
        "published": "",
        "description": "",
        "source": "test",
        "source_topic_hints": [],
        "tags": tags,
        "main_topic": main_topic,
        "score": {"freshness": 5, "primacy": 5, "relevance": 3, "utility": 2, "total": score_total},
    }


class TestBuildCandidates(unittest.TestCase):
    def setUp(self):
        # 使用临时目录隔离 BASE_DIR / PUBLISHED_INDEX
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.patcher_base = patch.object(cfg_mod, "BASE_DIR", self.base)
        self.patcher_idx = patch.object(cfg_mod, "PUBLISHED_INDEX", self.base / ".published-index.json")
        self.patcher_base.start()
        self.patcher_idx.start()
        # storage 模块的常量也要 patch（它持有 config 常量的引用）
        from briefing_tools import storage
        self.p1 = patch.object(storage, "BASE_DIR", self.base)
        self.p2 = patch.object(storage, "PUBLISHED_INDEX", self.base / ".published-index.json")
        self.p1.start()
        self.p2.start()

    def tearDown(self):
        self.patcher_base.stop()
        self.patcher_idx.stop()
        self.p1.stop()
        self.p2.stop()
        self.tmp.cleanup()

    def test_topic_filter(self):
        items = [
            _item("A", "https://a", ["ai-agent"], 15),
            _item("B", "https://b", ["global-tech"], 15),
            _item("C", "https://c", ["ai-agent", "global-tech"], 15),
        ]
        result = build_candidates(items, "ai-agent", "2026-05-10", _make_cfg())
        kept_urls = {it["url"] for it in result["items"]}
        self.assertEqual(kept_urls, {"https://a", "https://c"})

    def test_min_score(self):
        items = [
            _item("A", "https://a", ["ai-agent"], 11),
            _item("B", "https://b", ["ai-agent"], 15),
        ]
        result = build_candidates(items, "ai-agent", "2026-05-10", _make_cfg(), min_score=12)
        kept_urls = {it["url"] for it in result["items"]}
        self.assertEqual(kept_urls, {"https://b"})
        self.assertEqual(result["stats"]["filtered"]["low_score"], 1)

    def test_published_before(self):
        # 往 published-index 里写入 A 的 URL
        from briefing_tools.storage import save_published_index, url_hash
        idx = {"items": {
            url_hash("https://a"): {"url": "https://a", "topic": "ai-agent", "date": "2026-05-01"}
        }, "updated": ""}
        save_published_index(idx)

        items = [
            _item("A", "https://a", ["ai-agent"], 15),
            _item("B", "https://b", ["ai-agent"], 15),
        ]
        result = build_candidates(items, "ai-agent", "2026-05-10", _make_cfg())
        kept_urls = {it["url"] for it in result["items"]}
        self.assertEqual(kept_urls, {"https://b"})
        self.assertEqual(result["stats"]["filtered"]["published_before"], 1)

    def test_require_main_topic(self):
        items = [
            _item("A", "https://a", ["ai-agent", "global-tech"], 15, main_topic="ai-agent"),
            _item("B", "https://b", ["ai-agent"], 15, main_topic="ai-agent"),
            _item("C", "https://c", ["global-tech", "ai-agent"], 15, main_topic="global-tech"),
        ]
        # 对于 global-tech 开启 require_main_topic，则只有 main_topic==global-tech 的 C 进入
        result = build_candidates(items, "global-tech", "2026-05-10", _make_cfg(), require_main_topic=True)
        kept_urls = {it["url"] for it in result["items"]}
        self.assertEqual(kept_urls, {"https://c"})
        self.assertEqual(result["stats"]["filtered"]["not_main_topic"], 1)

    def test_sorted_by_score_desc(self):
        items = [
            _item("A", "https://a", ["ai-agent"], 13),
            _item("B", "https://b", ["ai-agent"], 18),
            _item("C", "https://c", ["ai-agent"], 15),
        ]
        result = build_candidates(items, "ai-agent", "2026-05-10", _make_cfg())
        totals = [it["score"]["total"] for it in result["items"]]
        self.assertEqual(totals, [18, 15, 13])

    def test_top_n_truncation(self):
        items = [
            _item(f"T{i}", f"https://t{i}", ["ai-agent"], 13 + i)
            for i in range(10)
        ]
        result = build_candidates(items, "ai-agent", "2026-05-10", _make_cfg(), top_n=3)
        self.assertEqual(len(result["items"]), 3)
        # 截断按 score 降序：T9(22), T8(21), T7(20)
        urls = [it["url"] for it in result["items"]]
        self.assertEqual(urls, ["https://t9", "https://t8", "https://t7"])
        self.assertEqual(result["stats"]["filtered"]["top_n_truncated"], 7)

    def test_top_n_zero_no_truncation(self):
        items = [_item("A", "https://a", ["ai-agent"], 15)]
        result = build_candidates(items, "ai-agent", "2026-05-10", _make_cfg(), top_n=0)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["stats"]["filtered"]["top_n_truncated"], 0)


if __name__ == "__main__":
    unittest.main()
