"""skeleton 提取与 diff 测试 + 金标准 fixture 自验"""

from conftest import *  # noqa
import tempfile
import unittest
from pathlib import Path

from briefing_tools import skeleton as sk
from briefing_tools.md_lint import lint_briefing


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "scripts" / "tests" / "fixtures" / "briefings"


def _write(content: str) -> Path:
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


class TestExtractSkeleton(unittest.TestCase):
    def test_basic(self):
        p = _write(
            "# Title\n\n"
            "## A\n\n### h1\n\ntext\n\n### h2\n\ntext\n\n"
            "## B\n\n- item1\n- item2\n\n"
            "## C\n\n| col1 | col2 |\n|---|---|\n| a | b |\n"
        )
        try:
            s = sk.extract_skeleton(p)
            self.assertTrue(s["has_h1"])
            names = sk.section_names(s)
            self.assertEqual(names, ["A", "B", "C"])
            # A 有 2 个 H3
            self.assertEqual(s["sections"][0]["h3_count"], 2)
            # B 有 2 个 bullet
            self.assertEqual(s["sections"][1]["bullet_count"], 2)
            # C 有 3 行表格
            self.assertEqual(s["sections"][2]["table_rows"], 3)
        finally:
            p.unlink()


class TestDiffSkeleton(unittest.TestCase):
    def test_identical(self):
        sk_a = {"has_h1": True, "sections": [{"name": "A"}, {"name": "B"}]}
        sk_b = {"has_h1": True, "sections": [{"name": "A"}, {"name": "B"}]}
        self.assertEqual(sk.diff_skeleton(sk_a, sk_b), [])

    def test_missing_section(self):
        actual = {"has_h1": True, "sections": [{"name": "A"}]}
        golden = {"has_h1": True, "sections": [{"name": "A"}, {"name": "B"}]}
        diffs = sk.diff_skeleton(actual, golden)
        self.assertTrue(any("B" in d for d in diffs))

    def test_extra_section_ok(self):
        """actual 多出 golden 没有的章节是允许的（safety 板块等）"""
        actual = {"has_h1": True, "sections": [
            {"name": "A"}, {"name": "B"}, {"name": "Extra"}, {"name": "C"},
        ]}
        golden = {"has_h1": True, "sections": [{"name": "A"}, {"name": "B"}, {"name": "C"}]}
        self.assertEqual(sk.diff_skeleton(actual, golden), [])

    def test_order_mismatch(self):
        actual = {"has_h1": True, "sections": [{"name": "B"}, {"name": "A"}]}
        golden = {"has_h1": True, "sections": [{"name": "A"}, {"name": "B"}]}
        diffs = sk.diff_skeleton(actual, golden)
        self.assertTrue(any("order" in d for d in diffs))


class TestGoldenFixturesAreValid(unittest.TestCase):
    """金标准 fixture 本身必须能通过 lint（自检）"""

    def test_global_tech_golden_passes_lint(self):
        ok, errs = lint_briefing(FIXTURE_DIR / "global-tech.golden.md")
        self.assertTrue(ok, errs)

    def test_china_tech_golden_passes_lint(self):
        ok, errs = lint_briefing(FIXTURE_DIR / "china-tech.golden.md")
        self.assertTrue(ok, errs)

    def test_ai_agent_golden_passes_lint(self):
        ok, errs = lint_briefing(FIXTURE_DIR / "ai-agent.golden.md")
        self.assertTrue(ok, errs)


if __name__ == "__main__":
    unittest.main()
