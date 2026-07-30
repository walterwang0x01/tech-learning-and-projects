"""notify 条目计数测试

count_briefing_items 决定 Bark 推送标题里的「共 N 条」。它按结构识别条目，
所以每新增一种正文区块写法（列表 / 表格 / 自由块），都要在这里补一个 case，
否则推送数字会静默偏小。
"""

from conftest import *  # noqa
import unittest

from briefing_tools.notify import count_briefing_items

HEADER = "# AI Agent 简报 — 2026-05-10\n\n> Author: Walter Wang\n\n"


class TestCountBriefingItems(unittest.TestCase):
    def test_headline_h3(self):
        md = HEADER + "## 📌 头条\n\n### 第一条头条\n\n正文。\n\n### 第二条头条\n\n正文。\n"
        self.assertEqual(count_briefing_items(md), 2)

    def test_section_emoji_h3_not_counted(self):
        """带 emoji 前缀的 H3 是区块标题，不是条目"""
        md = HEADER + "### ⚡ 快讯\n\n### 📦 项目\n"
        self.assertEqual(count_briefing_items(md), 0)

    def test_bullet_items(self):
        md = HEADER + "## ⚡ 快讯\n\n- **OpenAI**：发布了东西 → [链接](https://a)\n- **Google**：也发布了 → [链接](https://b)\n"
        self.assertEqual(count_briefing_items(md), 2)

    def test_plain_bullet_not_counted(self):
        """不以 **加粗** 开头的普通列表项不算条目"""
        md = HEADER + "## ⚡ 快讯\n\n- 这只是一句说明\n- 这也是\n"
        self.assertEqual(count_briefing_items(md), 0)

    def test_table_rows_exclude_header(self):
        md = (HEADER + "## 📦 项目\n\n| 项目 | 描述 | 链接 |\n|------|------|------|\n"
              "| A | 描述 A | [→](https://a) |\n| B | 描述 B | [→](https://b) |\n")
        self.assertEqual(count_briefing_items(md), 2)

    def test_free_block_items(self):
        """自由块：**标题** — 描述（论文 / 延伸阅读等不走列表或表格的区块）"""
        md = (HEADER + "## 📦 论文\n\n"
              "**Semalith v1.4** — 184M 参数的安全分类器。→ [arXiv](https://a)\n\n"
              "**ACM** — 长时程上下文管理。→ [arXiv](https://b)\n")
        self.assertEqual(count_briefing_items(md), 2)

    def test_free_block_needs_description(self):
        """只有加粗标题没有破折号描述的，不算条目（避免把强调文本误计）"""
        md = HEADER + "## 📌 说明\n\n**注意**\n\n**重点**\n"
        self.assertEqual(count_briefing_items(md), 0)

    def test_bullet_and_free_block_not_double_counted(self):
        """`- **X** — ...` 只能算一次，不能同时命中列表与自由块两条规则"""
        md = HEADER + "## ⚡ 快讯\n\n- **OpenAI** — 发布了东西 → [链接](https://a)\n"
        self.assertEqual(count_briefing_items(md), 1)

    def test_stops_at_trend_section(self):
        """趋势区（📈）之后的内容不计入条目数"""
        md = (HEADER + "## ⚡ 快讯\n\n- **A**：一条 → [链接](https://a)\n\n"
              "## 📈 趋势\n\n- **不该被数到的趋势** → 说明\n"
              "**这条自由块也不该被数到** — 说明\n")
        self.assertEqual(count_briefing_items(md), 1)

    def test_mixed_full_briefing(self):
        """混合结构：2 头条 + 2 快讯 + 2 表格行 + 2 自由块 = 8"""
        md = (HEADER
              + "## 📌 头条\n\n### 头条一\n\n正文\n\n### 头条二\n\n正文\n\n"
              + "## ⚡ 快讯\n\n- **A**：一条 → [链接](https://a)\n- **B**：两条 → [链接](https://b)\n\n"
              + "## 📦 项目 & 论文\n\n| 项目 | 描述 | 链接 |\n|------|------|------|\n"
              + "| P1 | 描述 | [→](https://c) |\n| P2 | 描述 | [→](https://d) |\n\n"
              + "**论文一** — 摘要。→ [arXiv](https://e)\n\n"
              + "**论文二** — 摘要。→ [arXiv](https://f)\n\n"
              + "## 📈 趋势\n\n- 🔺 某个趋势\n")
        self.assertEqual(count_briefing_items(md), 8)


if __name__ == "__main__":
    unittest.main()
