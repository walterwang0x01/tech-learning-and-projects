"""finalize 收尾报告测试

这些是「人每天唯一会看的输出」，逻辑不复杂但错了会让静默失败溜过去，
所以对分支和去重做基本约束。
"""

from conftest import *  # noqa
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from briefing_tools import cli
from briefing_tools import config as cfg_mod
from briefing_tools import storage
from briefing_tools.storage import atomic_write, atomic_write_json, url_hash

MD = """# 测试简报 — 2026-05-10

> Author: Walter Wang

## 📌 头条

### 头条一

正文。

→ [来源 A](https://a.example/post)

## ⚡ 快讯

- **X**：一条 → [来源 B](https://b.example/post)
- **Y**：两条 → [来源 C](https://c.example/post)
- **Z**：三条 → [来源 D](https://d.example/post)
"""


def _capture(fn, *args, **kwargs) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn(*args, **kwargs)
    return buf.getvalue()


class TestPrintActionItems(unittest.TestCase):
    def test_all_clear(self):
        out = _capture(cli._print_action_items, [], {}, [])
        self.assertIn("无需人工介入", out)

    def test_cross_topic_shown_with_advice(self):
        rows = [("ai-agent", {
            "url": "https://x.example/p", "kind": "cross_topic",
            "where": "global-tech 2026-05-10",
        })]
        out = _capture(cli._print_action_items, rows, {}, [])
        self.assertIn("跨主题 1 条", out)
        self.assertIn("https://x.example/p", out)
        self.assertIn("建议删掉一边", out)
        self.assertNotIn("无需人工介入", out)

    def test_cross_day_shows_stale_article_hint(self):
        """跨天提示必须包含「旧文当新闻」这条，那是实际踩过的坑"""
        rows = [("ai-agent", {
            "url": "https://x.example/p", "kind": "cross_day",
            "where": "global-tech 2026-05-01",
        })]
        out = _capture(cli._print_action_items, rows, {}, [])
        self.assertIn("跨天 1 条", out)
        self.assertIn("核对原文发布日期", out)

    def test_cross_day_truncated(self):
        rows = [
            ("ai-agent", {"url": f"https://x{i}.example/p", "kind": "cross_day",
                          "where": "global-tech 2026-05-01"})
            for i in range(8)
        ]
        out = _capture(cli._print_action_items, rows, {}, [], max_show=5)
        self.assertIn("另有 3 条跨天复用", out)

    def test_index_issues(self):
        issues = {
            "missing": [{"key": "ai-agent/2026-05-01"}],
            "hash_drift": [{"key": "china-tech/2026-05-02"}],
            "orphan": [{"key": "global-tech/2026-04-01"}],
        }
        out = _capture(cli._print_action_items, [], issues, [])
        self.assertIn("缺失登记 1", out)
        self.assertIn("hash 漂移 1", out)
        self.assertIn("孤儿记录 1", out)
        self.assertIn("doctor --fix", out)

    def test_baseline_anomaly(self):
        baselines = [
            {"topic": "ai-agent", "anomaly": True, "message": "候选数 10 / 基线 90（11%）偏低"},
            {"topic": "china-tech", "anomaly": False, "message": "正常"},
        ]
        out = _capture(cli._print_action_items, [], {}, baselines)
        self.assertIn("基线异常", out)
        self.assertIn("偏低", out)
        self.assertNotIn("china-tech", out)


class TestZeroYield(unittest.TestCase):
    """抓取成功但零产出：HTTP/解析都不报错，全链路唯一能看见它的地方"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runs = Path(self.tmp.name) / "runs"
        self.runs.mkdir()
        self.patches = [
            patch.object(cfg_mod, "RUNS_DIR", self.runs),
            patch.object(cli, "RUNS_DIR", self.runs),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def _metrics(self, date: str, sources: list[tuple[str, bool, int]]):
        d = self.runs / date
        d.mkdir(parents=True, exist_ok=True)
        (d / "metrics.json").write_text(json.dumps({
            "sources": [
                {"name": n, "ok": ok, "count": c} for n, ok, c in sources
            ]
        }), encoding="utf-8")

    def test_no_zero_yield(self):
        self._metrics("2026-08-03", [("A", True, 10), ("B", True, 5)])
        self.assertEqual(cli._collect_zero_yield("2026-08-03"), [])

    def test_failed_source_not_counted(self):
        """抓取失败的源走熔断那条路，不算零产出"""
        self._metrics("2026-08-03", [("A", False, 0)])
        self.assertEqual(cli._collect_zero_yield("2026-08-03"), [])

    def test_missing_metrics(self):
        self.assertEqual(cli._collect_zero_yield("2026-08-03"), [])

    def test_gap_days_not_counted_as_zero_runs(self):
        """中间没采集的日子（周末）不该算进零产出次数 —— 否则会误报成源坏了"""
        self._metrics("2026-08-03", [("arXiv", True, 0)])
        self._metrics("2026-07-31", [("arXiv", True, 282)])  # 08-01/02 无 run 目录
        got = cli._collect_zero_yield("2026-08-03")
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["last_yield_date"], "2026-07-31")
        self.assertEqual(got[0]["days_ago"], 3)
        self.assertEqual(got[0]["zero_runs"], 0)

    def test_consecutive_zero_runs_counted(self):
        self._metrics("2026-08-03", [("X", True, 0)])
        self._metrics("2026-08-02", [("X", True, 0)])
        self._metrics("2026-08-01", [("X", True, 0)])
        self._metrics("2026-07-31", [("X", True, 40)])
        got = cli._collect_zero_yield("2026-08-03")
        self.assertEqual(got[0]["zero_runs"], 2)
        self.assertEqual(got[0]["days_ago"], 3)

    def test_never_yielded_in_window(self):
        self._metrics("2026-08-03", [("Dead", True, 0)])
        self._metrics("2026-08-02", [("Dead", True, 0)])
        got = cli._collect_zero_yield("2026-08-03")
        self.assertIsNone(got[0]["last_yield_date"])

    def test_printed_hint_distinguishes_gap_from_failure(self):
        gap = [{"name": "arXiv", "last_yield_date": "2026-07-31", "days_ago": 3,
                "zero_runs": 0, "lookback": 7}]
        out = _capture(cli._print_action_items, [], {}, [], zero_yield=gap)
        self.assertIn("上次有产出 2026-07-31", out)
        self.assertIn("无其他零产出记录", out)
        self.assertNotIn("值得查", out)

        broken = [{"name": "X", "last_yield_date": "2026-07-31", "days_ago": 3,
                   "zero_runs": 2, "lookback": 7}]
        out2 = _capture(cli._print_action_items, [], {}, [], zero_yield=broken)
        self.assertIn("已零产出 2 次", out2)
        self.assertIn("值得查", out2)

    def test_all_clear_message_mentions_zero_yield(self):
        out = _capture(cli._print_action_items, [], {}, [], zero_yield=[])
        self.assertIn("无源零产出", out)


class TestFormatStatus(unittest.TestCase):
    def _report(self, **extra) -> dict:
        base = {
            "date": "2026-05-10",
            "topics": {
                "ai-agent": {"status": "✅", "latest": "2026-05-10", "days_ago": 0,
                             "total": 10, "this_week": 1, "this_month": 5},
            },
            "index_size": 100,
            "index_updated": "2026-05-10 10:00",
            "run": {"exists": False},
            "baselines": [],
        }
        base.update(extra)
        return base

    def test_item_counts_rendered(self):
        out = cli._format_status(self._report(item_counts={
            "ai-agent": 19, "china-tech": 17, "global-tech": 19,
        }))
        self.assertIn("今日简报条目", out)
        self.assertIn("共 55 条", out)

    def test_no_item_counts_section_when_absent(self):
        out = cli._format_status(self._report())
        self.assertNotIn("今日简报条目", out)

    def test_suggestion_section_omitted_when_nothing_todo(self):
        """三个主题都采完时不该留一个空的「建议」标题"""
        out = cli._format_status(self._report())
        self.assertNotIn("💡 建议", out)

    def test_suggestion_section_shown_when_stale(self):
        out = cli._format_status(self._report(topics={
            "ai-agent": {"status": "❌", "latest": "2026-05-01", "days_ago": 9,
                         "total": 10, "this_week": 0, "this_month": 5},
        }))
        self.assertIn("💡 建议", out)
        self.assertIn("需要采集", out)


class TestCollectUrlReuse(unittest.TestCase):
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
        atomic_write_json(self.index, {"items": {}})

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def _write_md(self, topic: str, content: str = MD):
        p = self.base / topic / "2026" / "05" / "2026-05-10.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(p, content)

    def test_cross_topic_deduped_to_one_row(self):
        """同一 URL 在两个主题各命中一次，只应汇报一条"""
        self._write_md("ai-agent")
        self._write_md("china-tech")
        rows = cli._collect_url_reuse(["ai-agent", "china-tech"], "2026-05-10")
        urls = [r["url"] for _, r in rows]
        self.assertEqual(len(urls), len(set(urls)))
        self.assertEqual(len(urls), 4)  # 两份 md 内容相同，4 个 URL 全撞

    def test_no_reuse_returns_empty(self):
        self._write_md("ai-agent")
        rows = cli._collect_url_reuse(["ai-agent"], "2026-05-10")
        self.assertEqual(rows, [])

    def test_cross_day_reported_per_topic(self):
        self._write_md("ai-agent")
        atomic_write_json(self.index, {"items": {
            url_hash("https://a.example/post"): {
                "url": "https://a.example/post", "topic": "global-tech",
                "date": "2026-05-01",
            }
        }})
        rows = cli._collect_url_reuse(["ai-agent"], "2026-05-10")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1]["kind"], "cross_day")


if __name__ == "__main__":
    unittest.main()
