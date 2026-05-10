"""storage 事务性 + md 校验测试"""

from conftest import *  # noqa
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from briefing_tools import config as cfg_mod
from briefing_tools import storage
from briefing_tools.storage import (
    atomic_write,
    atomic_write_json,
    atomic_write_jsonl,
    register_published,
    validate_briefing_md,
)


class TestAtomicWrite(unittest.TestCase):
    def test_atomic_write_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "out.txt"
            atomic_write(p, "hello")
            self.assertEqual(p.read_text(), "hello")
            # 临时文件已清理
            self.assertFalse((p.with_suffix(p.suffix + ".tmp")).exists())

    def test_atomic_write_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "out.json"
            atomic_write_json(p, {"a": 1, "b": [2, 3]})
            self.assertEqual(json.loads(p.read_text()), {"a": 1, "b": [2, 3]})

    def test_atomic_write_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "out.jsonl"
            atomic_write_jsonl(p, [{"x": 1}, {"y": 2}])
            lines = p.read_text().strip().split("\n")
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0]), {"x": 1})
            self.assertEqual(json.loads(lines[1]), {"y": 2})

    def test_overwrite_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "out.txt"
            atomic_write(p, "first")
            atomic_write(p, "second")
            self.assertEqual(p.read_text(), "second")


VALID_MD = """# AI Agent 简报 — 2026-05-10

> Author: Walter Wang

## 📌 头条

### OpenAI Codex for Chrome

一段自然语言描述...

→ [原文](https://openai.com/index/unlocking-the-codex-harness/)

## ⚡ 快讯

- **Anthropic**: something → [link](https://anthropic.com/x)
"""

INCOMPLETE_MD = "# AI Agent 简报\n\n"  # 只有 H1，无 ### 无链接


class TestValidateBriefingMd(unittest.TestCase):
    def test_valid(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(VALID_MD)
            p = Path(f.name)
        try:
            ok, reason = validate_briefing_md(p)
            self.assertTrue(ok, reason)
        finally:
            p.unlink()

    def test_missing_h1(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("## subheader only\nno h1")
            p = Path(f.name)
        try:
            ok, reason = validate_briefing_md(p)
            self.assertFalse(ok)
            self.assertIn("H1", reason)
        finally:
            p.unlink()

    def test_missing_h3(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(INCOMPLETE_MD)
            p = Path(f.name)
        try:
            ok, reason = validate_briefing_md(p)
            self.assertFalse(ok)
        finally:
            p.unlink()

    def test_not_exists(self):
        ok, reason = validate_briefing_md(Path("/does/not/exist.md"))
        self.assertFalse(ok)
        self.assertIn("not found", reason)


class TestRegisterPublished(unittest.TestCase):
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

    def test_register_valid_briefing(self):
        # 写入合法 md
        topic_dir = self.base / "ai-agent" / "2026" / "05"
        topic_dir.mkdir(parents=True)
        (topic_dir / "2026-05-10.md").write_text(VALID_MD, encoding="utf-8")

        result = register_published("ai-agent", "2026-05-10", retention_days=60)
        self.assertEqual(result.get("registered"), 2)
        self.assertEqual(result.get("total_urls"), 2)

    def test_skip_invalid_briefing(self):
        """损坏的 md 不应污染 published-index"""
        topic_dir = self.base / "ai-agent" / "2026" / "05"
        topic_dir.mkdir(parents=True)
        (topic_dir / "2026-05-10.md").write_text(INCOMPLETE_MD, encoding="utf-8")

        result = register_published("ai-agent", "2026-05-10", retention_days=60)
        self.assertEqual(result.get("registered"), 0)
        self.assertIn("error", result)
        self.assertIn("invalid", result["error"])


if __name__ == "__main__":
    unittest.main()
