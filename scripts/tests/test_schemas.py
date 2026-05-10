"""Schema 校验测试"""

from conftest import *  # noqa
import unittest

from briefing_tools.schemas import (
    ValidationError,
    validate_classified_item,
    validate_pool_item,
)


class TestValidatePoolItem(unittest.TestCase):
    def test_valid_minimal(self):
        item = validate_pool_item({"title": "t", "url": "https://example.com/x"})
        self.assertEqual(item.title, "t")
        self.assertEqual(item.url, "https://example.com/x")

    def test_missing_required(self):
        with self.assertRaises(ValidationError):
            validate_pool_item({"title": "only title"})

    def test_not_a_dict(self):
        with self.assertRaises(ValidationError):
            validate_pool_item("hello")

    def test_description_truncation(self):
        item = validate_pool_item({
            "title": "t", "url": "https://x",
            "description": "A" * 5000,
        })
        self.assertLessEqual(len(item.description), 2000)

    def test_roundtrip(self):
        original = {
            "title": "t", "url": "https://x",
            "published": "Fri, 09 May 2026 10:00:00 +0000",
            "description": "desc", "source": "s",
            "source_topic_hints": ["ai-agent"],
        }
        item = validate_pool_item(original)
        d = item.to_dict()
        # 所有核心字段保留
        self.assertEqual(d["title"], "t")
        self.assertEqual(d["source_topic_hints"], ["ai-agent"])


class TestValidateClassifiedItem(unittest.TestCase):
    def test_valid(self):
        raw = {
            "title": "t", "url": "https://x",
            "tags": ["ai-agent"],
            "score": {"freshness": 5, "primacy": 4, "relevance": 3, "utility": 3, "total": 15},
        }
        item = validate_classified_item(raw)
        self.assertEqual(item.tags, ["ai-agent"])
        self.assertEqual(item.score.total, 15)

    def test_score_missing_field(self):
        raw = {
            "title": "t", "url": "https://x",
            "tags": [],
            "score": {"freshness": 5, "primacy": 4, "relevance": 3},  # missing utility, total
        }
        with self.assertRaises(ValidationError):
            validate_classified_item(raw)

    def test_main_topic_optional(self):
        raw = {
            "title": "t", "url": "https://x",
            "tags": ["global-tech"],
            "score": {"freshness": 5, "primacy": 3, "relevance": 3, "utility": 3, "total": 14},
        }
        item = validate_classified_item(raw)
        self.assertIsNone(item.main_topic)


if __name__ == "__main__":
    unittest.main()
