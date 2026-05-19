"""把 BriefingDoc 渲染成符合 lint 规范的 markdown

不引入 jinja2，纯 Python 字符串拼接。设计目标：
- 输出永远满足 md_lint 严格模式
- 输出永远满足 skeleton 与金标准 fixture 对齐
- 章节顺序固定，调用方无法干扰
"""

from __future__ import annotations

from .doc_schema import (
    BriefingDoc,
    Brief,
    Headline,
    Link,
    TableRow,
    TableSection,
    TrendItem,
)


def _format_links(links: list[Link]) -> str:
    """[label1](url1) / [label2](url2) ..."""
    return " / ".join(f"[{l.label}]({l.url})" for l in links)


def _format_headline(h: Headline) -> str:
    parts = [
        f"### {h.title}",
        "",
        h.body.strip(),
        "",
        f"→ {_format_links(h.links)}",
        "",
        "---",
    ]
    return "\n".join(parts)


def _format_brief(b: Brief) -> str:
    """- **subject**：text → [link](url)"""
    return f"- **{b.subject}**：{b.text} → {_format_links(b.links)}"


def _format_table(section: TableSection) -> str:
    cols = section.columns
    header = "| " + " | ".join(cols) + " |"
    sep = "|" + "|".join(["------"] * len(cols)) + "|"
    rows: list[str] = [header, sep]
    for r in section.rows:
        if r.link is not None:
            cells = list(r.cells) + [f"[→]({r.link.url})"]
        else:
            cells = list(r.cells)
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([f"## {section.title}", "", *rows])


def _format_trend(t: TrendItem) -> str:
    return f"- {t.icon} {t.text}"


def render_briefing(doc: BriefingDoc) -> str:
    """渲染完整 markdown"""
    lines: list[str] = [
        f"# {doc.h1}",
        "",
        "> Author: Walter Wang",
        f"> {doc.subtitle}",
        "",
        "## 📌 头条",
        "",
    ]
    for h in doc.headlines:
        lines.append(_format_headline(h))
        lines.append("")

    lines.extend(["## ⚡ 快讯", ""])
    for b in doc.briefs:
        lines.append(_format_brief(b))
    lines.append("")

    for section in doc.extra_sections:
        lines.append(_format_table(section))
        lines.append("")

    if doc.trends:
        lines.extend(["## 📈 趋势", ""])
        for t in doc.trends:
            lines.append(_format_trend(t))
        lines.append("")

    # 去掉末尾多余空行
    text = "\n".join(lines).rstrip() + "\n"
    return text
