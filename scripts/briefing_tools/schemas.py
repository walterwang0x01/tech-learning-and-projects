"""简报采集数据模型。纯标准库 dataclass + 手写 validator。

提供 from_dict / to_dict / validate，兼容 JSONL 读写。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


class ValidationError(ValueError):
    """Schema 校验失败"""


# ========== PoolItem ==========

@dataclass
class PoolItem:
    """ingest 产物：原始采集条目"""
    title: str
    url: str
    published: str = ""
    description: str = ""
    source: str = ""
    source_topic_hints: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "PoolItem":
        _require(d, ["title", "url"], "PoolItem")
        return cls(
            title=str(d["title"]),
            url=str(d["url"]),
            published=str(d.get("published", "")),
            description=str(d.get("description", ""))[:2000],
            source=str(d.get("source", "")),
            source_topic_hints=list(d.get("source_topic_hints", []) or []),
        )

    def to_dict(self) -> dict:
        return asdict(self)


# ========== ScoreBreakdown ==========

@dataclass
class ScoreBreakdown:
    freshness: int
    primacy: int
    relevance: int
    utility: int
    total: int

    @classmethod
    def from_dict(cls, d: dict) -> "ScoreBreakdown":
        _require(d, ["freshness", "primacy", "relevance", "utility", "total"], "ScoreBreakdown")
        return cls(
            freshness=int(d["freshness"]),
            primacy=int(d["primacy"]),
            relevance=int(d["relevance"]),
            utility=int(d["utility"]),
            total=int(d["total"]),
        )

    def to_dict(self) -> dict:
        return asdict(self)


# ========== ClassifiedItem ==========

@dataclass
class ClassifiedItem:
    """classify 产物：带 tags + score"""
    title: str
    url: str
    published: str
    description: str
    source: str
    source_topic_hints: list[str]
    tags: list[str]
    main_topic: str | None
    score: ScoreBreakdown

    @classmethod
    def from_dict(cls, d: dict) -> "ClassifiedItem":
        _require(d, ["title", "url", "tags", "score"], "ClassifiedItem")
        return cls(
            title=str(d["title"]),
            url=str(d["url"]),
            published=str(d.get("published", "")),
            description=str(d.get("description", "")),
            source=str(d.get("source", "")),
            source_topic_hints=list(d.get("source_topic_hints", []) or []),
            tags=list(d.get("tags", []) or []),
            main_topic=d.get("main_topic"),
            score=ScoreBreakdown.from_dict(d["score"]),
        )

    def to_dict(self) -> dict:
        out = asdict(self)
        return out


# ========== 工具 ==========

def _require(d: dict, keys: list[str], where: str) -> None:
    missing = [k for k in keys if k not in d]
    if missing:
        raise ValidationError(f"{where}: missing keys {missing} in {list(d.keys())[:10]}")


def validate_pool_item(d: Any) -> PoolItem:
    if not isinstance(d, dict):
        raise ValidationError(f"PoolItem: expected dict, got {type(d).__name__}")
    return PoolItem.from_dict(d)


def validate_classified_item(d: Any) -> ClassifiedItem:
    if not isinstance(d, dict):
        raise ValidationError(f"ClassifiedItem: expected dict, got {type(d).__name__}")
    return ClassifiedItem.from_dict(d)
