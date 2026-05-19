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

---

### 第二条头条

正文...

→ [原文](https://example.com/headline2)

---

## ⚡ 快讯

- **Anthropic**: 一句话 → [link1](https://anthropic.com/x)
- **Google**: 一句话 → [link2](https://google.com/x)
- **Meta**: 一句话 → [link3](https://meta.com/x)
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
        # VALID_MD 含 5 个外链
        self.assertEqual(result.get("registered"), 5)
        self.assertEqual(result.get("total_urls"), 5)

    def test_skip_invalid_briefing(self):
        """损坏的 md 不应污染 published-index"""
        topic_dir = self.base / "ai-agent" / "2026" / "05"
        topic_dir.mkdir(parents=True)
        (topic_dir / "2026-05-10.md").write_text(INCOMPLETE_MD, encoding="utf-8")

        result = register_published("ai-agent", "2026-05-10", retention_days=60)
        self.assertEqual(result.get("registered"), 0)
        self.assertIn("error", result)
        self.assertIn("invalid", result["error"])

    def test_register_idempotent(self):
        """重复 register 同一份未变的 md：第二次新增 0 条，无 warning"""
        topic_dir = self.base / "ai-agent" / "2026" / "05"
        topic_dir.mkdir(parents=True)
        (topic_dir / "2026-05-10.md").write_text(VALID_MD, encoding="utf-8")

        r1 = register_published("ai-agent", "2026-05-10", retention_days=60)
        self.assertEqual(r1["registered"], 5)
        self.assertNotIn("warning", r1)

        r2 = register_published("ai-agent", "2026-05-10", retention_days=60)
        # 已注册的 URL 跳过
        self.assertEqual(r2["registered"], 0)
        self.assertNotIn("warning", r2)
        # hash 应当不变
        self.assertEqual(r1["file_hash"], r2["file_hash"])

    def test_register_detects_file_change(self):
        """register 之后改动 md 内容，再 register 应给 warning"""
        topic_dir = self.base / "ai-agent" / "2026" / "05"
        topic_dir.mkdir(parents=True)
        f = topic_dir / "2026-05-10.md"
        f.write_text(VALID_MD, encoding="utf-8")
        register_published("ai-agent", "2026-05-10", retention_days=60)

        # 改动内容（追加一段）
        f.write_text(VALID_MD + "\n\n额外段落", encoding="utf-8")
        r = register_published("ai-agent", "2026-05-10", retention_days=60)
        self.assertIn("warning", r)
        self.assertIn("changed", r["warning"])


if __name__ == "__main__":
    unittest.main()
