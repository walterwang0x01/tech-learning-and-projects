"""结构化简报文档 schema

subagent 把精选结果写成 JSON 后，由 render 模块渲染为 md。
这样格式由模板保证，不再依赖 LLM 服从 prompt。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class DocValidationError(ValueError):
    pass


@dataclass
class Link:
    label: str
    url: str

    @classmethod
    def from_dict(cls, d: Any) -> Link:
        if not isinstance(d, dict):
            raise DocValidationError(f"Link 必须是 dict，得到 {type(d).__name__}")
        if "label" not in d or "url" not in d:
            raise DocValidationError(f"Link 缺字段: {d}")
        if not str(d["url"]).startswith(("http://", "https://")):
            raise DocValidationError(f"Link.url 必须是 http(s) 开头: {d['url']}")
        return cls(label=str(d["label"]), url=str(d["url"]))


@dataclass
class Headline:
    title: str
    body: str
    links: list[Link]

    @classmethod
    def from_dict(cls, d: Any) -> Headline:
        if not isinstance(d, dict):
            raise DocValidationError(f"Headline 必须是 dict")
        title = str(d.get("title", "")).strip()
        body = str(d.get("body", "")).strip()
        if not title:
            raise DocValidationError("Headline.title 不能为空")
        if not body:
            raise DocValidationError("Headline.body 不能为空")
        if len(title) > 60:
            raise DocValidationError(f"Headline.title 过长（{len(title)} 字 > 60）: {title}")
        links = [Link.from_dict(x) for x in d.get("links", [])]
        if not links:
            raise DocValidationError(f"Headline 至少需要 1 个 link: {title}")
        return cls(title=title, body=body, links=links)


@dataclass
class Brief:
    subject: str
    text: str
    links: list[Link]

    @classmethod
    def from_dict(cls, d: Any) -> Brief:
        subject = str(d.get("subject", "")).strip()
        text = str(d.get("text", "")).strip()
        if not subject:
            raise DocValidationError("Brief.subject 不能为空")
        if not text:
            raise DocValidationError("Brief.text 不能为空")
        links = [Link.from_dict(x) for x in d.get("links", [])]
        if not links:
            raise DocValidationError(f"Brief 至少需要 1 个 link: {subject}")
        return cls(subject=subject, text=text, links=links)


@dataclass
class TableRow:
    cells: list[str]
    link: Link | None = None

    @classmethod
    def from_dict(cls, d: Any) -> TableRow:
        cells = [str(c) for c in d.get("cells", [])]
        if not cells:
            raise DocValidationError("TableRow.cells 不能为空")
        link_raw = d.get("link")
        link = Link.from_dict(link_raw) if link_raw else None
        return cls(cells=cells, link=link)


@dataclass
class TableSection:
    title: str  # 不含 H2 前缀
    columns: list[str]
    rows: list[TableRow] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Any) -> TableSection:
        title = str(d.get("title", "")).strip()
        columns = [str(c) for c in d.get("columns", [])]
        if not title:
            raise DocValidationError("TableSection.title 不能为空")
        if len(columns) < 2:
            raise DocValidationError("TableSection.columns 至少 2 列")
        rows = [TableRow.from_dict(r) for r in d.get("rows", [])]
        # 列数检查
        for i, r in enumerate(rows):
            if r.link is None and len(r.cells) != len(columns):
                raise DocValidationError(
                    f"TableSection {title!r} 第 {i + 1} 行列数 {len(r.cells)} ≠ 表头 {len(columns)}"
                )
            # 带 link 的最后一列被 link 占用，前面 cells 数量是 len(columns)-1
            if r.link is not None and len(r.cells) != len(columns) - 1:
                raise DocValidationError(
                    f"TableSection {title!r} 第 {i + 1} 行（带 link）非 link 列数 {len(r.cells)} ≠ 表头 {len(columns) - 1}"
                )
        return cls(title=title, columns=columns, rows=rows)


@dataclass
class TrendItem:
    icon: str  # 🆕 / 🔺 / 🔻
    text: str

    @classmethod
    def from_dict(cls, d: Any) -> TrendItem:
        icon = str(d.get("icon", "")).strip()
        text = str(d.get("text", "")).strip()
        if icon not in {"🆕", "🔺", "🔻"}:
            raise DocValidationError(f"TrendItem.icon 必须是 🆕/🔺/🔻，得到 {icon!r}")
        if not text:
            raise DocValidationError("TrendItem.text 不能为空")
        return cls(icon=icon, text=text)


@dataclass
class BriefingDoc:
    """完整简报文档"""
    topic: str
    date: str  # YYYY-MM-DD
    h1: str  # 不含 `# ` 前缀
    subtitle: str
    headlines: list[Headline]
    briefs: list[Brief]
    extra_sections: list[TableSection] = field(default_factory=list)
    optional_sections: list[dict] = field(default_factory=list)  # 灵活预留
    trends: list[TrendItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Any) -> BriefingDoc:
        if not isinstance(d, dict):
            raise DocValidationError("BriefingDoc 必须是 dict")
        for k in ("topic", "date", "h1", "subtitle"):
            if not d.get(k):
                raise DocValidationError(f"BriefingDoc.{k} 缺失")

        headlines = [Headline.from_dict(x) for x in d.get("headlines", [])]
        if not (1 <= len(headlines) <= 2):
            raise DocValidationError(f"headlines 数量必须是 1-2，得到 {len(headlines)}")

        briefs = [Brief.from_dict(x) for x in d.get("briefs", [])]
        if len(briefs) < 3:
            raise DocValidationError(f"briefs 数量必须 ≥ 3，得到 {len(briefs)}")

        extra_sections = [TableSection.from_dict(x) for x in d.get("extra_sections", [])]
        trends = [TrendItem.from_dict(x) for x in d.get("trends", [])]

        return cls(
            topic=str(d["topic"]),
            date=str(d["date"]),
            h1=str(d["h1"]),
            subtitle=str(d["subtitle"]),
            headlines=headlines,
            briefs=briefs,
            extra_sections=extra_sections,
            optional_sections=list(d.get("optional_sections", [])),
            trends=trends,
        )
