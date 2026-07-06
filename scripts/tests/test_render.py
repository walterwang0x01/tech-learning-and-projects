"""render 集成测试：JSON → md → lint → skeleton diff"""

from conftest import *  # noqa
import tempfile
import unittest
from pathlib import Path

from briefing_tools.doc_schema import BriefingDoc
from briefing_tools.md_lint import lint_briefing
from briefing_tools.render import render_briefing
from briefing_tools.skeleton import diff_skeleton, extract_skeleton


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "scripts" / "tests" / "fixtures" / "briefings"


def _link(label="原文", url="https://example.com/x") -> dict:
    return {"label": label, "url": url}


def _headline(title, body="正文段落，3-5 句叙述。") -> dict:
    return {"title": title, "body": body, "links": [_link()]}


def _brief(subject="主体", text="一句话描述", url="https://example.com/y") -> dict:
    return {"subject": subject, "text": text, "links": [{"label": "x", "url": url}]}


def _ai_doc() -> dict:
    return {
        "topic": "ai-agent",
        "date": "2026-05-19",
        "h1": "AI Agent 简报 — 2026-05-19",
        "subtitle": "每日精选 AI Agent 领域最值得关注的动态。5 分钟读完。",
        "headlines": [_headline("头条 1"), _headline("头条 2")],
        "briefs": [
            _brief("A", url="https://a.com/1"),
            _brief("B", url="https://b.com/2"),
            _brief("C", url="https://c.com/3"),
        ],
        "extra_sections": [{
            "title": "📦 项目 & 论文",
            "columns": ["项目", "描述", "链接"],
            "rows": [{"cells": ["Foo", "一句话"], "link": _link("→", "https://github.com/x/y")}],
        }],
        "trends": [
            {"icon": "🆕", "text": "趋势 A"},
            {"icon": "🔺", "text": "趋势 B"},
        ],
    }


def _china_doc() -> dict:
    d = _ai_doc()
    d["topic"] = "china-tech"
    d["h1"] = "🇨🇳 国内科技简报 — 2026-05-19"
    d["extra_sections"] = [{
        "title": "🤖 大模型动态",
        "columns": ["公司", "动态", "链接"],
        "rows": [{"cells": ["A 公司", "做了什么"], "link": _link("→", "https://example.com/llm")}],
    }]
    return d


def _global_doc() -> dict:
    d = _ai_doc()
    d["topic"] = "global-tech"
    d["h1"] = "🌍 国际科技简报 — 2026-05-19"
    d["extra_sections"] = [{
        "title": "🛠 值得关注",
        "columns": ["项目", "动态", "链接"],
        "rows": [{"cells": ["X", "干了啥"], "link": _link("→", "https://example.com/proj")}],
    }]
    return d


class TestRenderEndToEnd(unittest.TestCase):
    def _render_to_temp(self, doc_dict: dict) -> Path:
        doc = BriefingDoc.from_dict(doc_dict)
        md = render_briefing(doc)
        f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        f.write(md)
        f.close()
        return Path(f.name)

    def test_ai_agent_passes_lint_and_skeleton(self):
        p = self._render_to_temp(_ai_doc())
        try:
            ok, errs = lint_briefing(p)
            self.assertTrue(ok, f"lint errors: {errs}")
            golden = FIXTURE_DIR / "ai-agent.golden.md"
            diffs = diff_skeleton(extract_skeleton(p), extract_skeleton(golden))
            self.assertEqual(diffs, [])
        finally:
            p.unlink()

    def test_china_tech_passes_lint_and_skeleton(self):
        p = self._render_to_temp(_china_doc())
        try:
            ok, errs = lint_briefing(p)
            self.assertTrue(ok, f"lint errors: {errs}")
            golden = FIXTURE_DIR / "china-tech.golden.md"
            diffs = diff_skeleton(extract_skeleton(p), extract_skeleton(golden))
            self.assertEqual(diffs, [])
        finally:
            p.unlink()

    def test_global_tech_passes_lint_and_skeleton(self):
        p = self._render_to_temp(_global_doc())
        try:
            ok, errs = lint_briefing(p)
            self.assertTrue(ok, f"lint errors: {errs}")
            golden = FIXTURE_DIR / "global-tech.golden.md"
            diffs = diff_skeleton(extract_skeleton(p), extract_skeleton(golden))
            self.assertEqual(diffs, [])
        finally:
            p.unlink()

    def test_optional_sections_markdown(self):
        doc = _ai_doc()
        doc["optional_sections"] = [
            {"type": "markdown", "content": "**Paper X** — one line. → [arXiv](https://arxiv.org/abs/1234)"}
        ]
        rendered = render_briefing(BriefingDoc.from_dict(doc))
        self.assertIn("**Paper X**", rendered)
        self.assertIn("arXiv", rendered)


if __name__ == "__main__":
    unittest.main()
