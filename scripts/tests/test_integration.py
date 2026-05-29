"""端到端集成测试：用 fixture 数据跑完 classify → candidates"""

from conftest import *  # noqa
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from briefing_tools import config as cfg_mod, storage
from briefing_tools.candidates import build_candidates
from briefing_tools.classify import run_classify
from briefing_tools.config import (
    CircuitBreakerCfg,
    Config,
    LLMClassifyCfg,
    SemanticDedupCfg,
)

FIXTURE_POOL = [
    {
        "title": "OpenAI Codex for Chrome 发布",
        "url": "https://openai.com/index/unlocking-the-codex-harness",
        "published": "Fri, 09 May 2026 14:30:00 +0000",
        "description": "OpenAI launches Codex as a Chrome extension",
        "source": "OpenAI Blog",
        "source_topic_hints": ["ai-agent"],
    },
    {
        "title": "Dirty Frag 漏洞曝光",
        "url": "https://oschina.net/news/dirty-frag",
        "published": "Fri, 09 May 2026 12:00:00 +0000",
        "description": "Local privilege escalation CVE pending",
        "source": "开源中国",
        "source_topic_hints": ["china-tech"],
    },
    {
        "title": "Rust 1.86 release",
        "url": "https://blog.rust-lang.org/2026-rust-186",
        "published": "Fri, 09 May 2026 10:00:00 +0000",
        "description": "New features and standard library improvements",
        "source": "GitHub Blog",
        "source_topic_hints": ["global-tech"],
    },
    {
        "title": "DeepSeek V4.1 即将发布",
        "url": "https://infoq.cn/deepseek-v41",
        "published": "Fri, 09 May 2026 08:00:00 +0000",
        "description": "DeepSeek 承诺加快迭代节奏",
        "source": "InfoQ CN",
        "source_topic_hints": ["china-tech"],
    },
]


def _make_cfg() -> Config:
    # 用真实配置（浓缩版）
    return Config(
        freshness_hours=72,  # fixture 数据都在 48-72h 之间
        published_index_retention_days=60,
        run_retention_days=30,
        circuit_breaker=CircuitBreakerCfg(),
        main_topic_priority=["ai-agent", "china-tech", "global-tech"],
        rss_sources=[],
        classify_rules={
            "ai-agent": {"keywords": ["openai", "deepseek", "codex", "llm", "langchain"]},
            "china-tech": {"keywords": ["deepseek", "开源中国", "infoq", "百度"]},
            "global-tech": {"keywords": ["rust", "cve", "chrome", "release"]},
        },
        noise_keywords=[],
        score_overrides={
            "china-tech": {"primacy_sources": {"开源中国": 5}},
        },
        llm_classify=LLMClassifyCfg(),
        semantic_dedup=SemanticDedupCfg(),
        raw={},
    )


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.p_cfg_base = patch.object(cfg_mod, "BASE_DIR", self.base)
        self.p_cfg_idx = patch.object(cfg_mod, "PUBLISHED_INDEX", self.base / ".published-index.json")
        self.p_st_base = patch.object(storage, "BASE_DIR", self.base)
        self.p_st_idx = patch.object(storage, "PUBLISHED_INDEX", self.base / ".published-index.json")
        self.p_cfg_base.start()
        self.p_cfg_idx.start()
        self.p_st_base.start()
        self.p_st_idx.start()

    def tearDown(self):
        self.p_cfg_base.stop()
        self.p_cfg_idx.stop()
        self.p_st_base.stop()
        self.p_st_idx.stop()
        self.tmp.cleanup()

    def test_classify_and_split(self):
        cfg = _make_cfg()
        classified = run_classify(FIXTURE_POOL, cfg)
        # Codex / OpenAI 应归 ai-agent，可能同时带 global-tech（chrome / release）
        codex = next(c for c in classified if "Codex" in c["title"])
        self.assertIn("ai-agent", codex["tags"])
        # Dirty Frag 不应有 ai-agent（即使 "rag" 存在）
        dirty = next(c for c in classified if "Dirty Frag" in c["title"])
        self.assertNotIn("ai-agent", dirty["tags"])
        # Rust 发布
        rust = next(c for c in classified if "Rust" in c["title"])
        self.assertIn("global-tech", rust["tags"])
        # DeepSeek 同时是 AI 和中国
        deepseek = next(c for c in classified if "DeepSeek" in c["title"])
        self.assertIn("ai-agent", deepseek["tags"])
        self.assertIn("china-tech", deepseek["tags"])
        # main_topic 按 priority（ai-agent 优先）
        self.assertEqual(deepseek["main_topic"], "ai-agent")

    def test_candidates_no_cross_pollution(self):
        """关键回归：三个主题各自的候选集应不互相污染。
        Dirty Frag 没有中国语境信号（标题/描述里只有 CVE 字样），
        虽然来自 OSChina，但不该被算成 china-tech——这是我们 2026-05 修掉的污染 bug。"""
        cfg = _make_cfg()
        classified = run_classify(FIXTURE_POOL, cfg)

        ai = build_candidates(classified, "ai-agent", "2026-05-10", cfg, min_score=10)
        cn = build_candidates(classified, "china-tech", "2026-05-10", cfg, min_score=10)
        gl = build_candidates(classified, "global-tech", "2026-05-10", cfg, min_score=10)

        ai_titles = {it["title"] for it in ai["items"]}
        cn_titles = {it["title"] for it in cn["items"]}
        gl_titles = {it["title"] for it in gl["items"]}

        self.assertIn("OpenAI Codex for Chrome 发布", ai_titles)
        # CVE 内容归 global-tech，不归 china-tech（即使 source 是开源中国）
        self.assertIn("Dirty Frag 漏洞曝光", gl_titles)
        self.assertNotIn("Dirty Frag 漏洞曝光", cn_titles)
        self.assertIn("Rust 1.86 release", gl_titles)
        # DeepSeek 两个主题都能看到
        self.assertIn("DeepSeek V4.1 即将发布", ai_titles)
        self.assertIn("DeepSeek V4.1 即将发布", cn_titles)

    def test_require_main_topic_disambiguates(self):
        """开启 require_main_topic 后，DeepSeek 只进入 ai-agent（因为 priority）"""
        cfg = _make_cfg()
        classified = run_classify(FIXTURE_POOL, cfg)

        cn = build_candidates(
            classified, "china-tech", "2026-05-10", cfg,
            min_score=10, require_main_topic=True,
        )
        cn_titles = {it["title"] for it in cn["items"]}
        # DeepSeek main_topic 是 ai-agent，所以 china-tech 不收
        self.assertNotIn("DeepSeek V4.1 即将发布", cn_titles)


if __name__ == "__main__":
    unittest.main()
