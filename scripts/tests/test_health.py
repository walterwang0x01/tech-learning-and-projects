"""源健康 + 熔断测试"""

from conftest import *  # noqa
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from briefing_tools import config as cfg_mod
from briefing_tools import health
from briefing_tools.health import (
    is_source_tripped,
    load_health,
    record_source_result,
    reset_source,
    should_probe,
    tripped_sources,
)


class TestHealth(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        fake_health = Path(self.tmp.name) / "source-health.json"
        self.p1 = patch.object(cfg_mod, "SOURCE_HEALTH_FILE", fake_health)
        self.p2 = patch.object(health, "SOURCE_HEALTH_FILE", fake_health)
        self.p1.start()
        self.p2.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()
        self.tmp.cleanup()

    def test_initial_empty(self):
        data = load_health()
        self.assertEqual(data.get("sources"), {})

    def test_record_success(self):
        record_source_result("Src1", ok=True)
        data = load_health()
        self.assertEqual(data["sources"]["Src1"]["consecutive_failures"], 0)
        self.assertTrue(data["sources"]["Src1"]["last_ok_date"])

    def test_record_failure_once_per_day(self):
        record_source_result("Src2", ok=False)
        record_source_result("Src2", ok=False)  # 同一天，不应重复计数
        data = load_health()
        self.assertEqual(data["sources"]["Src2"]["consecutive_failures"], 1)

    def test_success_resets(self):
        record_source_result("Src3", ok=False)
        record_source_result("Src3", ok=True)
        data = load_health()
        self.assertEqual(data["sources"]["Src3"]["consecutive_failures"], 0)

    def test_is_tripped(self):
        # 连续 3 天失败：用伪造数据
        import json
        from briefing_tools.storage import atomic_write_json
        atomic_write_json(cfg_mod.SOURCE_HEALTH_FILE, {
            "sources": {"Trip1": {"consecutive_failures": 3}}
        })
        self.assertTrue(is_source_tripped("Trip1", threshold_days=3))
        self.assertFalse(is_source_tripped("Trip1", threshold_days=4))
        self.assertFalse(is_source_tripped("NotExist", threshold_days=3))

    def test_reset(self):
        from briefing_tools.storage import atomic_write_json
        atomic_write_json(cfg_mod.SOURCE_HEALTH_FILE, {
            "sources": {"R1": {"consecutive_failures": 5}}
        })
        self.assertTrue(is_source_tripped("R1", threshold_days=3))
        reset_source("R1")
        self.assertFalse(is_source_tripped("R1", threshold_days=3))


class TestHalfOpenProbe(unittest.TestCase):
    """熔断源的 half-open 自愈试探"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        fake_health = Path(self.tmp.name) / "source-health.json"
        self.p1 = patch.object(cfg_mod, "SOURCE_HEALTH_FILE", fake_health)
        self.p2 = patch.object(health, "SOURCE_HEALTH_FILE", fake_health)
        self.p1.start()
        self.p2.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()
        self.tmp.cleanup()

    def _write(self, name: str, last_fail: str, failures: int = 3):
        from briefing_tools.storage import atomic_write_json
        atomic_write_json(cfg_mod.SOURCE_HEALTH_FILE, {
            "sources": {name: {
                "consecutive_failures": failures,
                "last_fail_date": last_fail,
            }}
        })

    def test_not_yet_due(self):
        """距最后失败不足 retry_after_days，不试探"""
        self._write("S", "2026-05-08")
        with frozen_now(health, "2026-05-10"):  # 只过了 2 天
            self.assertFalse(should_probe("S", retry_after_days=7))

    def test_due_exactly(self):
        """刚好满 retry_after_days，放行试探"""
        self._write("S", "2026-05-03")
        with frozen_now(health, "2026-05-10"):  # 正好 7 天
            self.assertTrue(should_probe("S", retry_after_days=7))

    def test_long_overdue(self):
        self._write("S", "2026-01-01")
        with frozen_now(health, "2026-05-10"):
            self.assertTrue(should_probe("S", retry_after_days=7))

    def test_disabled_by_zero(self):
        """retry_after_days=0 表示关闭试探"""
        self._write("S", "2026-01-01")
        with frozen_now(health, "2026-05-10"):
            self.assertFalse(should_probe("S", retry_after_days=0))

    def test_no_record_or_bad_date(self):
        self.assertFalse(should_probe("NotExist", retry_after_days=7))
        self._write("S", "")
        self.assertFalse(should_probe("S", retry_after_days=7))
        self._write("S", "not-a-date")
        self.assertFalse(should_probe("S", retry_after_days=7))

    def test_probe_success_heals_source(self):
        """试探成功后 consecutive_failures 归零，源自动恢复"""
        self._write("S", "2026-01-01", failures=5)
        self.assertTrue(is_source_tripped("S", threshold_days=2))
        record_source_result("S", ok=True)
        self.assertFalse(is_source_tripped("S", threshold_days=2))

    def test_probe_failure_reschedules(self):
        """试探失败后 last_fail_date 刷新为今天，于是要再等一个完整周期"""
        self._write("S", "2026-01-01", failures=5)
        record_source_result("S", ok=False)
        last_fail = load_health()["sources"]["S"]["last_fail_date"]
        self.assertEqual(last_fail, datetime.now().strftime("%Y-%m-%d"))
        # 刚失败过，立刻再问就不该试探
        self.assertFalse(should_probe("S", retry_after_days=7))
        self.assertTrue(is_source_tripped("S", threshold_days=2))


if __name__ == "__main__":
    unittest.main()
