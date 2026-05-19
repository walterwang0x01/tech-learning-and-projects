"""baseline 检查测试"""

from conftest import *  # noqa
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from briefing_tools import baseline as bl


def _write_stats(runs_dir: Path, date_str: str, topic: str, kept: int) -> None:
    rd = runs_dir / date_str
    rd.mkdir(parents=True, exist_ok=True)
    (rd / f"candidates.{topic}.stats.json").write_text(
        json.dumps({"stats": {"kept": kept}}), encoding="utf-8"
    )


class TestCheckTopicBaseline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runs_dir = Path(self.tmp.name)
        self.p_runs = patch.object(bl, "RUNS_DIR", self.runs_dir)
        self.p_runs.start()

    def tearDown(self):
        self.p_runs.stop()
        self.tmp.cleanup()

    def test_no_today_data(self):
        today = datetime(2026, 5, 19)
        result = bl.check_topic_baseline("ai-agent", today)
        self.assertIsNone(result["today_kept"])
        self.assertIn("尚未生成", result["message"])
        self.assertFalse(result["anomaly"])

    def test_insufficient_baseline_samples(self):
        today = datetime(2026, 5, 19)
        # 今日有数据
        _write_stats(self.runs_dir, "2026-05-19", "ai-agent", 100)
        # 历史只有 1 天
        _write_stats(self.runs_dir, "2026-05-18", "ai-agent", 100)
        result = bl.check_topic_baseline("ai-agent", today)
        self.assertEqual(result["today_kept"], 100)
        self.assertEqual(result["baseline_samples"], 1)
        self.assertIn("基线样本不足", result["message"])
        self.assertFalse(result["anomaly"])

    def test_normal_within_baseline(self):
        today = datetime(2026, 5, 19)
        _write_stats(self.runs_dir, "2026-05-19", "ai-agent", 100)
        for i in range(1, 8):
            d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            _write_stats(self.runs_dir, d, "ai-agent", 100)
        result = bl.check_topic_baseline("ai-agent", today)
        self.assertFalse(result["anomaly"])
        self.assertAlmostEqual(result["ratio"], 1.0)

    def test_anomaly_low(self):
        today = datetime(2026, 5, 19)
        _write_stats(self.runs_dir, "2026-05-19", "ai-agent", 30)  # 30%
        for i in range(1, 8):
            d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            _write_stats(self.runs_dir, d, "ai-agent", 100)
        result = bl.check_topic_baseline("ai-agent", today)
        self.assertTrue(result["anomaly"])
        self.assertAlmostEqual(result["ratio"], 0.3)
        self.assertIn("源故障", result["message"])

    def test_just_above_threshold_normal(self):
        today = datetime(2026, 5, 19)
        # 正好 50% 是边界，按 < threshold 判定，所以 50 视为正常
        _write_stats(self.runs_dir, "2026-05-19", "ai-agent", 50)
        for i in range(1, 8):
            d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            _write_stats(self.runs_dir, d, "ai-agent", 100)
        result = bl.check_topic_baseline("ai-agent", today)
        self.assertFalse(result["anomaly"])

    def test_zero_avg_no_division_error(self):
        today = datetime(2026, 5, 19)
        _write_stats(self.runs_dir, "2026-05-19", "ai-agent", 5)
        for i in range(1, 8):
            d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            _write_stats(self.runs_dir, d, "ai-agent", 0)
        result = bl.check_topic_baseline("ai-agent", today)
        self.assertFalse(result["anomaly"])
        self.assertIn("无法比对", result["message"])


if __name__ == "__main__":
    unittest.main()
