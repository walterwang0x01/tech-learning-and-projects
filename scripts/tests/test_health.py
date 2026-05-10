"""源健康 + 熔断测试"""

from conftest import *  # noqa
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from briefing_tools import config as cfg_mod
from briefing_tools import health
from briefing_tools.health import (
    is_source_tripped,
    load_health,
    record_source_result,
    reset_source,
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


if __name__ == "__main__":
    unittest.main()
