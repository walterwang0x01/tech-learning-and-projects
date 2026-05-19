"""md_lint 强化校验测试"""

from conftest import *  # noqa
import tempfile
import unittest
from pathlib import Path

from briefing_tools.md_lint import lint_briefing


def _write(content: str) -> Path:
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


VALID = """# AI Agent 简报 — 2026-05-19

> Author: Walter Wang

## 📌 头条

### Headline 1

Body text.

→ [link1](https://example.com/1)

---

### Headline 2

Body text.

→ [link2](https://example.com/2)

---

## ⚡ 快讯

- **A**: text → [link3](https://example.com/3)
- **B**: text → [link4](https://example.com/4)
- **C**: text → [link5](https://example.com/5)
"""


class TestLintBriefing(unittest.TestCase):
    def _check(self, content: str, strict: bool = True):
        p = _write(content)
        try:
            return lint_briefing(p, strict=strict)
        finally:
            p.unlink()

    def test_valid(self):
        ok, errs = self._check(VALID)
        self.assertTrue(ok, errs)
        self.assertEqual(errs, [])

    def test_missing_h1(self):
        content = VALID.replace("# AI Agent 简报 — 2026-05-19", "no title")
        ok, errs = self._check(content)
        self.assertFalse(ok)
        self.assertTrue(any("H1" in e for e in errs))

    def test_no_external_links(self):
        # 把所有 https URL 替换掉（保留 ] 和 ( 让结构看起来像但 URL 不合法）
        content = VALID.replace("https://", "/local/")
        ok, errs = self._check(content)
        self.assertFalse(ok)
        self.assertTrue(any("external link" in e for e in errs))

    def test_missing_headline_section(self):
        content = VALID.replace("## 📌 头条", "## 其他东西")
        ok, errs = self._check(content)
        self.assertFalse(ok)
        self.assertTrue(any("头条" in e or "要闻" in e for e in errs))

    def test_missing_brief_section(self):
        content = VALID.replace("## ⚡ 快讯", "## 其他东西")
        ok, errs = self._check(content)
        self.assertFalse(ok)
        self.assertTrue(any("快讯" in e or "速读" in e for e in errs))

    def test_too_few_headlines(self):
        # 删掉第二条头条（连带 --- 和正文）
        content = """# T

## 📌 头条

(空)

## ⚡ 快讯

- A → [a](https://a.com)
- B → [b](https://b.com)
- C → [c](https://c.com)
"""
        ok, errs = self._check(content)
        self.assertFalse(ok)
        self.assertTrue(any("headlines too few" in e for e in errs))

    def test_too_many_headlines(self):
        content = """# T

## 📌 头条

### H1

→ [a](https://a.com)

---

### H2

→ [b](https://b.com)

---

### H3

→ [c](https://c.com)

---

## ⚡ 快讯

- A → [a](https://a.com)
- B → [b](https://b.com)
- C → [c](https://c.com)
"""
        ok, errs = self._check(content)
        self.assertFalse(ok)
        self.assertTrue(any("too many" in e for e in errs))

    def test_headline_missing_separator(self):
        # 第一条头条后没有 ---
        content = """# T

## 📌 头条

### H1

正文

→ [a](https://a.com)

### H2

正文

→ [b](https://b.com)

---

## ⚡ 快讯

- A → [a1](https://a1.com)
- B → [b1](https://b1.com)
- C → [c1](https://c1.com)
"""
        ok, errs = self._check(content)
        self.assertFalse(ok)
        self.assertTrue(any("分隔线" in e for e in errs))

    def test_too_few_briefs(self):
        content = """# T

## 📌 头条

### H1

→ [a](https://a.com)

---

## ⚡ 快讯

- only one → [b](https://b.com)
- second → [c](https://c.com)
"""
        ok, errs = self._check(content)
        self.assertFalse(ok)
        self.assertTrue(any("briefs too few" in e for e in errs))

    def test_lenient_skips_structure(self):
        """lenient 模式只查 H1 + 外链，不查章节"""
        content = """# 老格式简报

## 🔥 今日要闻

正文 → [link](https://example.com)
"""
        ok, errs = self._check(content, strict=False)
        self.assertTrue(ok, errs)

    def test_strict_catches_old_format(self):
        """strict 模式要拦截老格式（要闻视为头条 OK，但缺快讯）"""
        content = """# 老格式简报

## 🔥 今日要闻

### 头条1

正文 → [link](https://example.com)

---

### 头条2

正文 → [link2](https://example.com/2)

---
"""
        ok, errs = self._check(content, strict=True)
        # 没快讯
        self.assertFalse(ok)
        self.assertTrue(any("快讯" in e or "速读" in e for e in errs))

    def test_recognizes_headline_keyword_alternatives(self):
        """要闻 / Headlines 都视为头条章节"""
        content = """# T

## 🔥 今日要闻

### H1

→ [a](https://a.com)

---

### H2

→ [b](https://b.com)

---

## 速读

- A → [c](https://c.com)
- B → [d](https://d.com)
- C → [e](https://e.com)
"""
        ok, errs = self._check(content)
        self.assertTrue(ok, errs)


if __name__ == "__main__":
    unittest.main()
