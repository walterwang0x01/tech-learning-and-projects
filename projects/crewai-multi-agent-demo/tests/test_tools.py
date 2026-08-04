"""自定义工具测试"""

import os
import tempfile
from unittest.mock import patch

from app.tools.custom_tools import save_article, word_count, keyword_density, OUTPUT_DIR


class TestSaveArticle:
    """save_article 工具测试"""

__author__ = "Walter Wang"

    def test_save_article_creates_file(self, sample_article: str):
        """测试文章保存功能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.tools.custom_tools.OUTPUT_DIR", tmpdir):
                # 重新导入以使用 mock 路径
                from pathlib import Path

                mock_dir = Path(tmpdir)
                result = save_article.run(filename="test-article.md", content=sample_article)
                # 验证返回消息包含保存路径
                assert "保存到" in result

    def test_save_article_adds_md_extension(self):
        """测试自动添加 .md 扩展名"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.tools.custom_tools.OUTPUT_DIR", tmpdir):
                from pathlib import Path

                result = save_article.run(filename="test", content="# Test")
                assert ".md" in result

    def test_save_article_sanitizes_filename(self):
        """测试文件名安全处理"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.tools.custom_tools.OUTPUT_DIR", tmpdir):
                result = save_article.run(
                    filename="bad/file name!.md", content="# Test"
                )
                assert "保存到" in result


class TestWordCount:
    """word_count 工具测试"""

    def test_chinese_text(self):
        """测试中文字数统计"""
        result = word_count.run(text="你好世界")
        assert "中文字符: 4" in result

    def test_english_text(self):
        """测试英文字数统计"""
        result = word_count.run(text="hello world")
        assert "英文单词: 2" in result

    def test_mixed_text(self, sample_article: str):
        """测试中英文混合文本"""
        result = word_count.run(text=sample_article)
        assert "总字数" in result
        assert "中文字符" in result
        assert "英文单词" in result

    def test_empty_text(self):
        """测试空文本"""
        result = word_count.run(text="")
        assert "总字数: 0" in result


class TestKeywordDensity:
    """keyword_density 工具测试"""

    def test_keyword_found(self, sample_article: str, sample_keyword: str):
        """测试关键词密度分析"""
        result = keyword_density.run(text=sample_article, keyword=sample_keyword)
        assert "AI Agent" in result
        assert "出现次数" in result
        assert "关键词密度" in result

    def test_keyword_not_found(self, sample_article: str):
        """测试关键词未出现的情况"""
        result = keyword_density.run(text=sample_article, keyword="区块链")
        assert "出现次数: 0" in result

    def test_case_insensitive(self):
        """测试大小写不敏感"""
        text = "Python is great. python is popular. PYTHON rocks."
        result = keyword_density.run(text=text, keyword="python")
        assert "出现次数: 3" in result

    def test_empty_text(self):
        """测试空文本"""
        result = keyword_density.run(text="", keyword="test")
        assert "出现次数: 0" in result
