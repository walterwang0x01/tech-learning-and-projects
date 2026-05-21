"""config 加载测试：重点验证 candidates_top_n 的 per-topic 解析与兜底逻辑"""

from conftest import *  # noqa
import json
import tempfile
import unittest
from pathlib import Path

from briefing_tools.config import load_config


def _write_config(tmpdir: str, extra: dict) -> Path:
    """在临时目录写一份最小化合法 config.json，用 extra 覆盖/追加字段"""
    minimal = {
        "freshness_hours": 48,
        "published_index_retention_days": 60,
        "run_retention_days": 30,
        "rss_sources": [],
        "classify_rules": {},
        "noise_keywords": [],
        "score_overrides": {},
    }
    minimal.update(extra)
    p = Path(tmpdir) / "config.json"
    p.write_text(json.dumps(minimal, ensure_ascii=False), encoding="utf-8")
    return p


class TestCandidatesTopN(unittest.TestCase):
    def test_default_when_missing(self):
        """整个 candidates_top_n 字段缺失时退回硬编码默认 60"""
        with tempfile.TemporaryDirectory() as td:
            p = _write_config(td, {})
            cfg = load_config(path=p, force_reload=True)
        self.assertEqual(cfg.resolve_top_n("ai-agent"), 60)
        self.assertEqual(cfg.resolve_top_n("china-tech"), 60)
        self.assertEqual(cfg.resolve_top_n("global-tech"), 60)
        self.assertEqual(cfg.resolve_top_n("unknown-topic"), 60)

    def test_per_topic_override(self):
        """per-topic 配置覆盖 _default"""
        with tempfile.TemporaryDirectory() as td:
            p = _write_config(td, {
                "candidates_top_n": {
                    "_default": 70,
                    "ai-agent": 120,
                    "china-tech": 80,
                }
            })
            cfg = load_config(path=p, force_reload=True)
        self.assertEqual(cfg.resolve_top_n("ai-agent"), 120)
        self.assertEqual(cfg.resolve_top_n("china-tech"), 80)
        # 没显式配置的 topic 走 _default
        self.assertEqual(cfg.resolve_top_n("global-tech"), 70)

    def test_default_only(self):
        """只设了 _default 时所有 topic 都用 _default"""
        with tempfile.TemporaryDirectory() as td:
            p = _write_config(td, {"candidates_top_n": {"_default": 90}})
            cfg = load_config(path=p, force_reload=True)
        self.assertEqual(cfg.resolve_top_n("ai-agent"), 90)
        self.assertEqual(cfg.resolve_top_n("china-tech"), 90)

    def test_comment_field_ignored(self):
        """以下划线开头但非 _default 的字段（如 _comment）被忽略，不污染配置"""
        with tempfile.TemporaryDirectory() as td:
            p = _write_config(td, {
                "candidates_top_n": {
                    "_comment": "this is a comment",
                    "_default": 60,
                    "ai-agent": 100,
                }
            })
            cfg = load_config(path=p, force_reload=True)
        self.assertEqual(cfg.resolve_top_n("ai-agent"), 100)
        # _comment 不被当成 topic 名
        self.assertNotIn("_comment", cfg.candidates_top_n)

    def test_invalid_value_silently_dropped(self):
        """非数字 value 静默丢弃，不让坏配置炸整个流水线"""
        with tempfile.TemporaryDirectory() as td:
            p = _write_config(td, {
                "candidates_top_n": {
                    "_default": 60,
                    "ai-agent": "not-a-number",
                    "china-tech": None,
                    "global-tech": 100,
                }
            })
            cfg = load_config(path=p, force_reload=True)
        # 坏值被丢弃，退回 _default
        self.assertEqual(cfg.resolve_top_n("ai-agent"), 60)
        self.assertEqual(cfg.resolve_top_n("china-tech"), 60)
        # 好值保留
        self.assertEqual(cfg.resolve_top_n("global-tech"), 100)

    def test_non_dict_top_n_uses_default(self):
        """candidates_top_n 不是 dict（写成 list/数字）时用默认配置，不抛错"""
        with tempfile.TemporaryDirectory() as td:
            p = _write_config(td, {"candidates_top_n": [1, 2, 3]})
            cfg = load_config(path=p, force_reload=True)
        self.assertEqual(cfg.resolve_top_n("ai-agent"), 60)


if __name__ == "__main__":
    unittest.main()
