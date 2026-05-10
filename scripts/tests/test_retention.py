"""run 目录清理测试"""

from conftest import *  # noqa
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from briefing_tools import config as cfg_mod
from briefing_tools import retention
from briefing_tools.retention import cleanup_runs


class TestCleanupRuns(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runs = Path(self.tmp.name) / "runs"
        self.runs.mkdir()
        self.p1 = patch.object(cfg_mod, "RUNS_DIR", self.runs)
        self.p2 = patch.object(retention, "RUNS_DIR", self.runs)
        self.p1.start()
        self.p2.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()
        self.tmp.cleanup()

    def _mkday(self, name: str):
        d = self.runs / name
        d.mkdir()
        (d / "pool.jsonl").write_text("{}")
        return d

    def test_remove_old(self):
        # 2026-05-10 是"今天"，30 天前是 2026-04-10
        self._mkday("2026-01-01")  # 很老
        self._mkday("2026-05-09")  # 最近
        self._mkday("2026-03-01")  # 中间（会被清）

        result = cleanup_runs(days=30)
        self.assertEqual(result["removed"], 2)
        self.assertEqual(result["kept"], 1)

    def test_days_zero_noop(self):
        self._mkday("2026-01-01")
        result = cleanup_runs(days=0)
        self.assertEqual(result["removed"], 0)

    def test_ignore_non_date_dirs(self):
        (self.runs / "not-a-date").mkdir()
        self._mkday("2026-01-01")
        result = cleanup_runs(days=30)
        self.assertEqual(result["removed"], 1)
        self.assertTrue((self.runs / "not-a-date").exists())

    def test_runs_dir_not_exist(self):
        import shutil
        shutil.rmtree(self.runs)
        result = cleanup_runs(days=30)
        self.assertEqual(result["removed"], 0)


if __name__ == "__main__":
    unittest.main()
