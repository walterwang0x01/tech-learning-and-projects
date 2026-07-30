"""ingest 源筛选测试：enabled 开关 / 熔断 / half-open 试探三分支"""

from conftest import *  # noqa
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from briefing_tools import config as cfg_mod
from briefing_tools import health
from briefing_tools.ingest import partition_sources
from briefing_tools.storage import atomic_write_json


def _src(name: str, **kw) -> dict:
    return {"name": name, "url": f"https://{name}/feed", **kw}


class TestPartitionSources(unittest.TestCase):
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

    def _health(self, mapping: dict):
        """mapping: name -> (consecutive_failures, last_fail_date)"""
        atomic_write_json(cfg_mod.SOURCE_HEALTH_FILE, {
            "sources": {
                n: {"consecutive_failures": f, "last_fail_date": d}
                for n, (f, d) in mapping.items()
            }
        })

    def test_all_healthy(self):
        sources = [_src("A"), _src("B")]
        active, tripped, disabled, probing = partition_sources(
            sources, skip_tripped=True, threshold=2, retry_after_days=7)
        self.assertEqual([s["name"] for s in active], ["A", "B"])
        self.assertEqual((tripped, disabled, probing), ([], [], []))

    def test_disabled_source_never_fetched(self):
        """enabled=false 的源不采，也不算熔断"""
        sources = [_src("A"), _src("Dead", enabled=False)]
        active, tripped, disabled, probing = partition_sources(
            sources, skip_tripped=True, threshold=2, retry_after_days=7)
        self.assertEqual([s["name"] for s in active], ["A"])
        self.assertEqual(disabled, ["Dead"])
        self.assertEqual(tripped, [])

    def test_disabled_takes_precedence_over_probe(self):
        """已停用的源即便早该试探，也不参与 half-open"""
        self._health({"Dead": (5, "2020-01-01")})
        sources = [_src("Dead", enabled=False)]
        active, tripped, disabled, probing = partition_sources(
            sources, skip_tripped=True, threshold=2, retry_after_days=7)
        self.assertEqual(active, [])
        self.assertEqual(disabled, ["Dead"])
        self.assertEqual(probing, [])

    def test_tripped_skipped_when_not_due(self):
        self._health({"Flaky": (3, "2026-05-09")})
        sources = [_src("Flaky")]
        with frozen_now(health, "2026-05-10"):  # 只过 1 天
            active, tripped, disabled, probing = partition_sources(
                sources, skip_tripped=True, threshold=2, retry_after_days=7)
        self.assertEqual(active, [])
        self.assertEqual(tripped, ["Flaky"])
        self.assertEqual(probing, [])

    def test_tripped_probed_when_due(self):
        """到期的熔断源进入 active，并被标记为 probing"""
        self._health({"Flaky": (3, "2026-05-01")})
        sources = [_src("Flaky")]
        with frozen_now(health, "2026-05-10"):  # 9 天 > 7
            active, tripped, disabled, probing = partition_sources(
                sources, skip_tripped=True, threshold=2, retry_after_days=7)
        self.assertEqual([s["name"] for s in active], ["Flaky"])
        self.assertEqual(probing, ["Flaky"])
        self.assertEqual(tripped, [])

    def test_probe_disabled_keeps_source_tripped(self):
        """retry_after_days=0 时退回旧行为：熔断源永久跳过"""
        self._health({"Flaky": (3, "2020-01-01")})
        sources = [_src("Flaky")]
        active, tripped, disabled, probing = partition_sources(
            sources, skip_tripped=True, threshold=2, retry_after_days=0)
        self.assertEqual(active, [])
        self.assertEqual(tripped, ["Flaky"])
        self.assertEqual(probing, [])

    def test_skip_tripped_false_ignores_breaker(self):
        """skip_when_tripped=false 时熔断不生效，源照常采集"""
        self._health({"Flaky": (9, "2026-05-09")})
        sources = [_src("Flaky")]
        active, tripped, disabled, probing = partition_sources(
            sources, skip_tripped=False, threshold=2, retry_after_days=7)
        self.assertEqual([s["name"] for s in active], ["Flaky"])
        self.assertEqual(tripped, [])

    def test_mixed(self):
        self._health({
            "Tripped": (3, "2026-05-09"),   # 熔断未到期
            "Due": (3, "2026-04-01"),       # 熔断已到期 → 试探
        })
        sources = [_src("OK"), _src("Tripped"), _src("Due"), _src("Off", enabled=False)]
        with frozen_now(health, "2026-05-10"):
            active, tripped, disabled, probing = partition_sources(
                sources, skip_tripped=True, threshold=2, retry_after_days=7)
        self.assertEqual([s["name"] for s in active], ["OK", "Due"])
        self.assertEqual(tripped, ["Tripped"])
        self.assertEqual(disabled, ["Off"])
        self.assertEqual(probing, ["Due"])


if __name__ == "__main__":
    unittest.main()
