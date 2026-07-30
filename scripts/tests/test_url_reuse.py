"""check_url_reuse 测试

候选集的 published_before / not_main_topic 两层只管候选集，curate 阶段 web search
补进来的链接完全绕过去重。这个检查是那条路径上唯一的护栏，所以要测牢。
"""

from conftest import *  # noqa
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from briefing_tools import config as cfg_mod
from briefing_tools import storage
from briefing_tools.storage import (
    atomic_write,
    atomic_write_json,
    check_url_reuse,
    url_hash,
)

MD = """# 测试简报 — 2026-05-10

> Author: Walter Wang

## 📌 头条

### 头条一

正文。

→ [来源 A](https://a.example/post) / [来源 B](https://b.example/post)

## ⚡ 快讯

- **X**：一条 → [来源 C](https://c.example/post)
- **Y**：两条 → [来源 D](https://d.example/post)
- **Z**：三条 → [来源 E](https://e.example/post)
"""


class TestCheckUrlReuse(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name) / "briefings"
        self.index = self.base / ".published-index.json"
        self.patches = [
            patch.object(cfg_mod, "BASE_DIR", self.base),
            patch.object(storage, "BASE_DIR", self.base),
            patch.object(cfg_mod, "PUBLISHED_INDEX", self.index),
            patch.object(storage, "PUBLISHED_INDEX", self.index),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def _write_md(self, topic: str, date: str = "2026-05-10", content: str = MD):
        p = self.base / topic / "2026" / "05" / f"{date}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(p, content)
        return p

    def _write_index(self, mapping: dict):
        """mapping: url -> (topic, date)"""
        atomic_write_json(self.index, {
            "items": {
                url_hash(u): {"url": u, "topic": t, "date": d}
                for u, (t, d) in mapping.items()
            }
        })

    def test_no_reuse(self):
        self._write_md("ai-agent")
        self._write_index({})
        self.assertEqual(check_url_reuse("ai-agent", "2026-05-10"), [])

    def test_missing_file(self):
        self._write_index({})
        self.assertEqual(check_url_reuse("ai-agent", "2026-05-10"), [])

    def test_cross_day_detected(self):
        self._write_md("ai-agent")
        self._write_index({"https://a.example/post": ("global-tech", "2026-05-01")})
        found = check_url_reuse("ai-agent", "2026-05-10")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["kind"], "cross_day")
        self.assertIn("global-tech 2026-05-01", found[0]["where"])

    def test_same_topic_cross_day_detected(self):
        """同主题跨天复用也要报——往往意味着把旧文当新闻"""
        self._write_md("ai-agent")
        self._write_index({"https://b.example/post": ("ai-agent", "2026-04-20")})
        found = check_url_reuse("ai-agent", "2026-05-10")
        self.assertEqual([f["kind"] for f in found], ["cross_day"])

    def test_own_registration_not_flagged(self):
        """自己今天登记的记录不算复用，否则每次 re-register 都会误报"""
        self._write_md("ai-agent")
        self._write_index({
            "https://a.example/post": ("ai-agent", "2026-05-10"),
            "https://b.example/post": ("ai-agent", "2026-05-10"),
        })
        self.assertEqual(check_url_reuse("ai-agent", "2026-05-10"), [])

    def test_same_date_other_topic_not_double_reported(self):
        """今日其他主题已登记时只报 cross_topic，不重复报 cross_day"""
        self._write_md("ai-agent")
        self._write_md("global-tech")
        self._write_index({"https://a.example/post": ("global-tech", "2026-05-10")})
        found = check_url_reuse("ai-agent", "2026-05-10")
        kinds = [f["kind"] for f in found]
        self.assertNotIn("cross_day", kinds)
        self.assertEqual(kinds.count("cross_topic"), 5)  # 两份 md 内容相同，5 个 URL 全撞

    def test_cross_topic_detected(self):
        self._write_md("ai-agent")
        self._write_md("china-tech", content=MD.replace("a.example", "z.example"))
        self._write_index({})
        found = check_url_reuse("ai-agent", "2026-05-10")
        self.assertTrue(found)
        self.assertTrue(all(f["kind"] == "cross_topic" for f in found))
        # a.example 被换成 z.example，所以只有其余 4 个 URL 重复
        self.assertEqual(len(found), 4)

    def test_cross_topic_ignores_other_dates(self):
        """其他主题的历史简报不参与跨主题判断，那是 cross_day 的职责"""
        self._write_md("ai-agent")
        self._write_md("china-tech", date="2026-05-09")
        self._write_index({})
        self.assertEqual(check_url_reuse("ai-agent", "2026-05-10"), [])

    def test_explicit_path(self):
        """path 参数可指向任意文件，供 render 校验刚写出的产物"""
        p = self._write_md("ai-agent", date="2026-05-11")
        self._write_index({"https://c.example/post": ("china-tech", "2026-05-01")})
        found = check_url_reuse("ai-agent", "2026-05-11", path=p)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["url"], "https://c.example/post")


if __name__ == "__main__":
    unittest.main()
