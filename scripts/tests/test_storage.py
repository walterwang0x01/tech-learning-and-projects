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
    doctor_check_index_consistency,
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

        # 冻结时间：否则 fixture 日期一旦超出 retention_days 窗口，
        # 第一次登记的记录会被 cleanup_published_index 立刻清掉，幂等断言失效
        with frozen_now(storage, "2026-05-10"):
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


class TestDoctorCheckIndexConsistency(unittest.TestCase):
    """doctor 一致性检查：md 与 published-index 的 file_hashes 是否一致"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.p_cfg_base = patch.object(cfg_mod, "BASE_DIR", self.base)
        self.p_cfg_idx = patch.object(cfg_mod, "PUBLISHED_INDEX", self.base / ".published-index.json")
        self.p_st_base = patch.object(storage, "BASE_DIR", self.base)
        self.p_st_idx = patch.object(storage, "PUBLISHED_INDEX", self.base / ".published-index.json")
        for p in (self.p_cfg_base, self.p_cfg_idx, self.p_st_base, self.p_st_idx):
            p.start()

    def tearDown(self):
        for p in (self.p_cfg_base, self.p_cfg_idx, self.p_st_base, self.p_st_idx):
            p.stop()
        self.tmp.cleanup()

    def _write_md(self, topic: str, date_str: str, content: str = VALID_MD) -> Path:
        year, month = date_str[:4], date_str[5:7]
        d = self.base / topic / year / month
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"{date_str}.md"
        f.write_text(content, encoding="utf-8")
        return f

    def test_all_clean(self):
        """注册过的 md，doctor 不应报问题"""
        self._write_md("ai-agent", "2026-05-10")
        register_published("ai-agent", "2026-05-10")

        issues = doctor_check_index_consistency(auto_fix=False)
        self.assertEqual(issues["missing"], [])
        self.assertEqual(issues["hash_drift"], [])
        self.assertEqual(issues["orphan"], [])

    def test_detects_missing(self):
        """md 存在但 file_hashes 没记录 → missing"""
        self._write_md("ai-agent", "2026-05-10")
        # 不跑 register

        issues = doctor_check_index_consistency(auto_fix=False)
        self.assertEqual(len(issues["missing"]), 1)
        self.assertEqual(issues["missing"][0]["key"], "ai-agent/2026-05-10")
        self.assertEqual(issues["hash_drift"], [])

    def test_detects_hash_drift(self):
        """注册后改 md → hash_drift"""
        f = self._write_md("ai-agent", "2026-05-10")
        register_published("ai-agent", "2026-05-10")
        f.write_text(VALID_MD + "\n\n新增段落", encoding="utf-8")

        issues = doctor_check_index_consistency(auto_fix=False)
        self.assertEqual(issues["missing"], [])
        self.assertEqual(len(issues["hash_drift"]), 1)
        self.assertEqual(issues["hash_drift"][0]["key"], "ai-agent/2026-05-10")

    def test_detects_orphan(self):
        """register 之后删 md → orphan"""
        f = self._write_md("ai-agent", "2026-05-10")
        register_published("ai-agent", "2026-05-10")
        f.unlink()

        issues = doctor_check_index_consistency(auto_fix=False)
        self.assertEqual(issues["missing"], [])
        self.assertEqual(len(issues["orphan"]), 1)
        self.assertEqual(issues["orphan"][0]["key"], "ai-agent/2026-05-10")

    def test_auto_fix_resolves_missing(self):
        """auto_fix=True 应当跑 register 把 missing 补上"""
        self._write_md("ai-agent", "2026-05-10")

        issues = doctor_check_index_consistency(auto_fix=True)
        self.assertEqual(len(issues["missing"]), 1)
        self.assertEqual(len(issues["fixed"]), 1)
        self.assertEqual(issues["fixed"][0]["key"], "ai-agent/2026-05-10")
        # 修复后再查应该干净
        issues2 = doctor_check_index_consistency(auto_fix=False)
        self.assertEqual(issues2["missing"], [])
        self.assertEqual(issues2["hash_drift"], [])

    def test_auto_fix_resolves_drift(self):
        """auto_fix=True 应当对 hash_drift 重新 register"""
        f = self._write_md("ai-agent", "2026-05-10")
        register_published("ai-agent", "2026-05-10")
        f.write_text(VALID_MD + "\n\n新增段落", encoding="utf-8")

        issues = doctor_check_index_consistency(auto_fix=True)
        self.assertEqual(len(issues["hash_drift"]), 1)
        self.assertEqual(len(issues["fixed"]), 1)
        # 再查无问题
        issues2 = doctor_check_index_consistency(auto_fix=False)
        self.assertEqual(issues2["hash_drift"], [])

    def test_skips_readme_and_weekly(self):
        """README.md 和 *-weekly.md 不应被纳入检查"""
        # 写一个普通日报
        self._write_md("ai-agent", "2026-05-10")
        register_published("ai-agent", "2026-05-10")
        # 加 README 和 weekly
        (self.base / "ai-agent" / "README.md").write_text("# index\n", encoding="utf-8")
        weekly = self.base / "ai-agent" / "2026" / "05"
        weekly.mkdir(parents=True, exist_ok=True)
        (weekly / "2026-W18-weekly.md").write_text(VALID_MD, encoding="utf-8")

        issues = doctor_check_index_consistency(auto_fix=False)
        self.assertEqual(issues["missing"], [])  # weekly 用 W 前缀，不匹配 YYYY-MM-DD

    def test_backfill_legacy_md(self):
        """旧格式 md（strict 校验 fail 但 lenient 通过）应只补 file_hash"""
        # INCOMPLETE_MD 只有 H1，strict 必 fail；但下面这个旧格式有 H1 + 链接，lenient 通过
        legacy_md = (
            "# 旧版简报 — 2026-04-01\n\n"
            "## 今日要闻\n\n"
            "1. 第一条 → [link](https://example.com/a)\n"
            "2. 第二条 → [link2](https://example.com/b)\n"
        )
        self._write_md("ai-agent", "2026-04-01", content=legacy_md)

        issues = doctor_check_index_consistency(auto_fix=True)
        self.assertEqual(len(issues["missing"]), 1)
        # 应该被 backfill 而不是普通 register
        self.assertEqual(len(issues["fixed"]), 1)
        self.assertTrue(issues["fixed"][0].get("backfilled_legacy"))

        # 再查应该干净
        issues2 = doctor_check_index_consistency(auto_fix=False)
        self.assertEqual(issues2["missing"], [])

    def test_truly_invalid_md_not_fixed(self):
        """连 lenient 都 fail 的 md（如缺 H1）不应被修复，留下 missing 让用户处理"""
        broken = "## subheader only\nno h1, no link\n"
        self._write_md("ai-agent", "2026-04-02", content=broken)

        issues = doctor_check_index_consistency(auto_fix=True)
        self.assertEqual(len(issues["missing"]), 1)
        self.assertEqual(len(issues["fixed"]), 0)


if __name__ == "__main__":
    unittest.main()
