"""结构化简报 schema 测试"""

from conftest import *  # noqa
import unittest

from briefing_tools.doc_schema import (
    BriefingDoc,
    Brief,
    DocValidationError,
    Headline,
    Link,
    TableRow,
    TableSection,
    TrendItem,
)


def _link(label="原文", url="https://example.com/x") -> dict:
    return {"label": label, "url": url}


def _headline(title="头条 X", body="正文段落，3-5 句叙述。") -> dict:
    return {"title": title, "body": body, "links": [_link()]}


def _brief(subject="主体 X", text="一句话描述") -> dict:
    return {"subject": subject, "text": text, "links": [_link()]}


def _doc_dict() -> dict:
    return {
        "topic": "ai-agent",
        "date": "2026-05-19",
        "h1": "AI Agent 简报 — 2026-05-19",
        "subtitle": "每日精选 AI Agent 领域最值得关注的动态。5 分钟读完。",
        "headlines": [_headline("头条 1"), _headline("头条 2")],
        "briefs": [_brief("A"), _brief("B"), _brief("C")],
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


class TestLink(unittest.TestCase):
    def test_valid(self):
        l = Link.from_dict({"label": "x", "url": "https://example.com"})
        self.assertEqual(l.url, "https://example.com")

    def test_missing_field(self):
        with self.assertRaises(DocValidationError):
            Link.from_dict({"label": "x"})

    def test_invalid_url(self):
        with self.assertRaises(DocValidationError):
            Link.from_dict({"label": "x", "url": "/local/path"})


class TestHeadline(unittest.TestCase):
    def test_valid(self):
        h = Headline.from_dict(_headline())
        self.assertEqual(h.title, "头条 X")
        self.assertEqual(len(h.links), 1)

    def test_empty_title(self):
        d = _headline()
        d["title"] = "  "
        with self.assertRaises(DocValidationError):
            Headline.from_dict(d)

    def test_title_too_long(self):
        d = _headline(title="头" * 80)
        with self.assertRaises(DocValidationError):
            Headline.from_dict(d)

    def test_no_links(self):
        d = _headline()
        d["links"] = []
        with self.assertRaises(DocValidationError):
            Headline.from_dict(d)


class TestBrief(unittest.TestCase):
    def test_valid(self):
        b = Brief.from_dict(_brief())
        self.assertEqual(b.subject, "主体 X")

    def test_empty_subject(self):
        d = _brief()
        d["subject"] = ""
        with self.assertRaises(DocValidationError):
            Brief.from_dict(d)


class TestTableSection(unittest.TestCase):
    def test_valid_with_link(self):
        s = TableSection.from_dict({
            "title": "📦 项目",
            "columns": ["名称", "描述", "链接"],
            "rows": [{"cells": ["A", "一句话"], "link": _link("→", "https://x.com")}],
        })
        self.assertEqual(len(s.rows), 1)

    def test_columns_too_few(self):
        with self.assertRaises(DocValidationError):
            TableSection.from_dict({"title": "x", "columns": ["A"]})

    def test_row_column_mismatch(self):
        with self.assertRaises(DocValidationError):
            TableSection.from_dict({
                "title": "x",
                "columns": ["A", "B", "C"],
                "rows": [{"cells": ["a", "b"]}],  # 应该 3 列但只给了 2
            })


class TestTrendItem(unittest.TestCase):
    def test_valid(self):
        t = TrendItem.from_dict({"icon": "🆕", "text": "新趋势"})
        self.assertEqual(t.icon, "🆕")

    def test_invalid_icon(self):
        with self.assertRaises(DocValidationError):
            TrendItem.from_dict({"icon": "@", "text": "x"})


class TestBriefingDoc(unittest.TestCase):
    def test_valid_full(self):
        doc = BriefingDoc.from_dict(_doc_dict())
        self.assertEqual(doc.topic, "ai-agent")
        self.assertEqual(len(doc.headlines), 2)
        self.assertEqual(len(doc.briefs), 3)

    def test_too_many_headlines(self):
        d = _doc_dict()
        d["headlines"] = [_headline(f"H{i}") for i in range(3)]
        with self.assertRaises(DocValidationError):
            BriefingDoc.from_dict(d)

    def test_too_few_headlines(self):
        d = _doc_dict()
        d["headlines"] = []
        with self.assertRaises(DocValidationError):
            BriefingDoc.from_dict(d)

    def test_too_few_briefs(self):
        d = _doc_dict()
        d["briefs"] = [_brief("A"), _brief("B")]
        with self.assertRaises(DocValidationError):
            BriefingDoc.from_dict(d)

    def test_missing_required(self):
        d = _doc_dict()
        del d["h1"]
        with self.assertRaises(DocValidationError):
            BriefingDoc.from_dict(d)


if __name__ == "__main__":
    unittest.main()
