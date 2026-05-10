"""分类 + 评分回归测试"""

from conftest import *  # noqa
import unittest

from briefing_tools.classify import classify_rule, decide_main_topic, kw_hit, score_item
from briefing_tools.config import Config, CircuitBreakerCfg, LLMClassifyCfg, SemanticDedupCfg


def _make_cfg(**overrides) -> Config:
    base = {
        "freshness_hours": 48,
        "published_index_retention_days": 60,
        "run_retention_days": 30,
        "circuit_breaker": CircuitBreakerCfg(),
        "main_topic_priority": ["ai-agent", "china-tech", "global-tech"],
        "rss_sources": [],
        "classify_rules": {
            "ai-agent": {"keywords": ["llm", "ai agent", "rag", "langchain"]},
            "china-tech": {"keywords": ["百度", "阿里", "国产"]},
            "global-tech": {"keywords": ["rust", "kubernetes", "cve"]},
        },
        "noise_keywords": ["sponsored"],
        "score_overrides": {
            "china-tech": {"primacy_sources": {"开源中国": 5}},
        },
        "llm_classify": LLMClassifyCfg(),
        "semantic_dedup": SemanticDedupCfg(),
        "raw": {},
    }
    base.update(overrides)
    return Config(**base)


class TestKeywordMatcher(unittest.TestCase):
    def test_word_boundary_ascii(self):
        # 防止 "rag" 误命中 "Frag"
        self.assertTrue(kw_hit("rag", "using rag here"))
        self.assertFalse(kw_hit("rag", "dirty frag vuln"))

    def test_word_boundary_hyphenated(self):
        # "0-day" 是固定短语，不应该匹配 "today"
        self.assertTrue(kw_hit("cve", "cve 2026 disclosed"))
        self.assertFalse(kw_hit("cve", "nothing here"))

    def test_chinese_substring(self):
        # 中文走子串
        self.assertTrue(kw_hit("国产", "国产大模型发布"))
        self.assertTrue(kw_hit("百度", "百度文心 5.1"))

    def test_phrase_with_space(self):
        # 带空格短语走子串
        self.assertTrue(kw_hit("ai agent", "building an ai agent system"))
        self.assertFalse(kw_hit("ai agent", "ai-agent framework"))  # 不同字符


class TestClassifyRule(unittest.TestCase):
    def setUp(self):
        self.cfg = _make_cfg()

    def test_dirty_frag_is_not_ai(self):
        """回归：Dirty Frag 这种包含子串 'rag' 的不应归入 ai-agent"""
        item = {
            "title": "Dirty Frag 漏洞：主流 Linux 提权",
            "description": "CVE 编号即将发布",
            "source": "开源中国",
        }
        tags = classify_rule(item, self.cfg)
        self.assertNotIn("ai-agent", tags)
        # 命中 "cve" 应该归入 global-tech
        self.assertIn("global-tech", tags)

    def test_deepseek_is_both(self):
        """DeepSeek 同时是 AI 和中国科技"""
        # 扩展规则：DeepSeek 作为 ai-agent 和 china-tech 的关键词
        cfg = _make_cfg(classify_rules={
            "ai-agent": {"keywords": ["llm", "deepseek"]},
            "china-tech": {"keywords": ["百度", "deepseek"]},
            "global-tech": {"keywords": ["rust"]},
        })
        item = {
            "title": "DeepSeek V4.1 发布",
            "description": "",
            "source": "量子位",
        }
        tags = classify_rule(item, cfg)
        self.assertIn("ai-agent", tags)
        self.assertIn("china-tech", tags)

    def test_source_hint_fallback(self):
        """关键词完全未命中时，source hint 兜底"""
        item = {
            "title": "Totally unrelated topic",
            "description": "",
            "source": "Wired AI",
            "source_topic_hints": ["ai-agent"],
        }
        tags = classify_rule(item, self.cfg)
        self.assertEqual(tags, ["ai-agent"])

    def test_hint_not_overriding_keywords(self):
        """关键词命中后，source hint 不应再强塞别的 topic"""
        item = {
            "title": "Rust 1.86 released",
            "description": "",
            "source": "Wired AI",
            "source_topic_hints": ["ai-agent"],
        }
        tags = classify_rule(item, self.cfg)
        self.assertIn("global-tech", tags)
        self.assertNotIn("ai-agent", tags)

    def test_no_match_no_hint(self):
        item = {
            "title": "Random content",
            "description": "",
            "source": "Unknown",
            "source_topic_hints": [],
        }
        self.assertEqual(classify_rule(item, self.cfg), [])


class TestMainTopic(unittest.TestCase):
    def test_priority_order(self):
        priority = ["ai-agent", "china-tech", "global-tech"]
        self.assertEqual(decide_main_topic(["china-tech", "ai-agent"], priority), "ai-agent")
        self.assertEqual(decide_main_topic(["global-tech", "china-tech"], priority), "china-tech")
        self.assertEqual(decide_main_topic(["global-tech"], priority), "global-tech")
        self.assertIsNone(decide_main_topic([], priority))


class TestScoreItem(unittest.TestCase):
    def setUp(self):
        self.cfg = _make_cfg()

    def test_primacy_override_for_china_tech(self):
        """开源中国 在 china-tech 下 primacy=5（配置覆盖）"""
        item = {
            "title": "百度发布文心 5.1",
            "description": "最新大模型",
            "published": "",
            "source": "开源中国",
        }
        score = score_item(item, ["china-tech"], self.cfg)
        self.assertEqual(score["primacy"], 5)

    def test_noise_penalty(self):
        item = {
            "title": "sponsored content",
            "description": "",
            "published": "",
            "source": "Random",
        }
        score = score_item(item, ["global-tech"], self.cfg)
        self.assertLessEqual(score["relevance"], 1)

    def test_action_signal(self):
        item = {
            "title": "Rust 1.85 release",
            "description": "",
            "published": "",
            "source": "Rust Blog",
        }
        score = score_item(item, ["global-tech"], self.cfg)
        # "release" 应该触发 utility=4
        self.assertEqual(score["utility"], 4)


if __name__ == "__main__":
    unittest.main()
