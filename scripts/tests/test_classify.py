"""分类 + 评分回归测试"""

from conftest import *  # noqa
import json
import unittest
from unittest.mock import MagicMock, patch

from briefing_tools.classify import (
    classify_llm_batch,
    classify_rule,
    decide_main_topic,
    kw_hit,
    score_item,
)
from briefing_tools.config import Config, CircuitBreakerCfg, LLMClassifyCfg, SemanticDedupCfg, get_llm_classify_model, get_openai_api_base


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

    def test_follow_builders_x_no_hint_fallback(self):
        """follow-builders/x 无 AI 关键词时不应靠 hint 兜底进 ai-agent"""
        item = {
            "title": "Someone (@x): random life update",
            "description": "just had coffee",
            "source": "follow-builders/x/@someone",
            "source_topic_hints": [],
        }
        tags = classify_rule(item, self.cfg)
        self.assertEqual(tags, [])

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

    def test_keyword_does_not_match_source_field(self):
        """回归（2026-05 修复）：source 字段名不参与关键词匹配。
        否则站点名「开源中国」会让该源所有内容（含国际新闻）无条件命中
        china-tech 的 '中国' 关键词，造成大面积污染。"""
        cfg = _make_cfg(classify_rules={
            "ai-agent": {"keywords": ["llm"]},
            "china-tech": {"keywords": ["中国", "国产"]},
            "global-tech": {"keywords": ["rust"]},
        })
        # 内容里没有任何中国语境信号，但 source 是「开源中国」
        item = {
            "title": "Krita 6.0.2 发布",
            "description": "Open source painting tool",
            "source": "开源中国",
            "source_topic_hints": [],  # 显式不给 hint，确认完全不会进 china-tech
        }
        tags = classify_rule(item, cfg)
        self.assertNotIn("china-tech", tags)


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


class TestOpenAIClassify(unittest.TestCase):
    def test_openai_classify_batch(self):
        cfg = _make_cfg(
            llm_classify=LLMClassifyCfg(
                enabled=True,
                provider="openai",
                model="aws-bedrock/claude-haiku-4-5",
                api_base="https://llm-gw.example.com/v1",
            ),
        )
        items = [
            {"title": "MCP server for agents", "description": "", "source": "HN"},
            {"title": "华为新品发布", "description": "", "source": "36氪"},
        ]
        mock_body = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "results": [
                                {"idx": 0, "tags": ["ai-agent"]},
                                {"idx": 1, "tags": ["china-tech"]},
                            ],
                        }),
                    },
                },
            ],
        }
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_body).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("briefing_tools.classify.get_api_key", return_value="test-key"):
            with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
                tags = classify_llm_batch(items, cfg)

        self.assertEqual(tags, [["ai-agent"], ["china-tech"]])
        req = mock_open.call_args[0][0]
        self.assertEqual(req.full_url, "https://llm-gw.example.com/v1/chat/completions")
        self.assertEqual(req.get_header("Authorization"), "Bearer test-key")

    def test_get_openai_api_base_prefers_config(self):
        cfg = _make_cfg(
            llm_classify=LLMClassifyCfg(api_base="https://custom.gw/v1/"),
        )
        self.assertEqual(get_openai_api_base(cfg), "https://custom.gw/v1")

    def test_get_llm_classify_model_prefers_env(self):
        cfg = _make_cfg(
            llm_classify=LLMClassifyCfg(
                provider="openai",
                model="aws-bedrock/claude-haiku-4-5",
            ),
        )
        with patch("briefing_tools.config.get_env_var", return_value="aws-bedrock/claude-opus-4-8"):
            self.assertEqual(get_llm_classify_model(cfg), "aws-bedrock/claude-opus-4-8")


if __name__ == "__main__":
    unittest.main()
