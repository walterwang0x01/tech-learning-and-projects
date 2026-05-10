"""URL 归一化测试"""

from conftest import *  # noqa
import unittest

from briefing_tools.http import normalize_url


class TestNormalizeUrl(unittest.TestCase):
    def test_strip_fragment(self):
        self.assertEqual(normalize_url("https://example.com/page#section"), "https://example.com/page")

    def test_strip_utm(self):
        self.assertEqual(
            normalize_url("https://example.com/x?utm_source=rss&utm_medium=feed"),
            "https://example.com/x",
        )

    def test_keep_real_params(self):
        # 非追踪参数保留
        self.assertEqual(
            normalize_url("https://example.com/x?id=123&utm_source=rss"),
            "https://example.com/x?id=123",
        )

    def test_strip_ref_like(self):
        self.assertEqual(
            normalize_url("https://example.com/?ref=hn&id=1"),
            "https://example.com/?id=1",
        )

    def test_strip_trailing_slash(self):
        self.assertEqual(
            normalize_url("https://example.com/article/"),
            "https://example.com/article",
        )

    def test_keep_root_slash(self):
        self.assertEqual(normalize_url("https://example.com/"), "https://example.com/")

    def test_empty(self):
        self.assertEqual(normalize_url(""), "")
        self.assertEqual(normalize_url("   "), "")

    def test_whitespace_trim(self):
        self.assertEqual(normalize_url("  https://example.com/x  "), "https://example.com/x")


if __name__ == "__main__":
    unittest.main()
