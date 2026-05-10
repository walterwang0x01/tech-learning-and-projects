"""去重测试"""

from conftest import *  # noqa
import unittest

from briefing_tools.dedup import (
    dedup_semantic,
    semantic_duplicate,
    shingle_similarity,
    title_in,
    title_similarity,
)


class TestTitleSimilarity(unittest.TestCase):
    def test_identical(self):
        self.assertAlmostEqual(title_similarity("Hello World", "Hello World"), 1.0)

    def test_disjoint(self):
        self.assertAlmostEqual(title_similarity("apple pie", "rust code"), 0.0)

    def test_partial(self):
        sim = title_similarity("OpenAI releases GPT-5", "OpenAI GPT-5 launched")
        self.assertGreater(sim, 0.3)
        self.assertLess(sim, 1.0)

    def test_empty(self):
        self.assertEqual(title_similarity("", "something"), 0.0)


class TestShingleSimilarity(unittest.TestCase):
    def test_chinese_near_duplicate(self):
        """中文近义标题应有较高 shingle 相似度"""
        a = "苹果发布新一代 Vision Pro 2"
        b = "Apple 推出 Vision Pro 2 头显"
        # 跨中英，shingle 分数不会太高，但高于 Jaccard
        s = shingle_similarity(a, b)
        # 共享 "Vision Pro 2"，至少有一定相似度
        self.assertGreater(s, 0.05)

    def test_english_near_duplicate(self):
        a = "OpenAI releases Codex for Chrome extension"
        b = "OpenAI launches Codex for Chrome extension"
        s = shingle_similarity(a, b)
        # 只有 releases vs launches 差异
        self.assertGreater(s, 0.6)


class TestSemanticDuplicate(unittest.TestCase):
    def test_dup_detect(self):
        a = {"title": "OpenAI releases Codex for Chrome extension", "description": ""}
        b = {"title": "OpenAI launches Codex for Chrome extension", "description": ""}
        self.assertTrue(semantic_duplicate(a, b, threshold=0.6))

    def test_not_dup(self):
        a = {"title": "OpenAI Codex Chrome", "description": ""}
        b = {"title": "Anthropic Claude Code", "description": ""}
        self.assertFalse(semantic_duplicate(a, b, threshold=0.8))


class TestDedupSemantic(unittest.TestCase):
    def test_keep_higher_score(self):
        # 用高度相似的 title + description 确保 shingle > 0.6
        items = [
            {
                "title": "OpenAI launches Codex for Chrome extension",
                "description": "OpenAI Codex is now available in Chrome",
                "score": {"total": 14},
            },
            {
                "title": "OpenAI releases Codex for Chrome extension",
                "description": "OpenAI Codex is now available in Chrome",
                "score": {"total": 17},
            },
        ]
        kept, removed = dedup_semantic(items, threshold=0.6)
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0]["score"]["total"], 17)
        self.assertEqual(len(removed), 1)


class TestTitleIn(unittest.TestCase):
    def test_cross_topic_duplicate_detected(self):
        pool = ["OpenAI Codex for Chrome", "Meta Hatch agent"]
        self.assertTrue(title_in("OpenAI releases Codex for Chrome extension", pool, 0.3))
        self.assertFalse(title_in("Rust 1.86 release", pool, 0.3))


if __name__ == "__main__":
    unittest.main()
