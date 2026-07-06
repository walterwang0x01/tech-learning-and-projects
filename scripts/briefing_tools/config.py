"""读取 .kiro/briefings/config.json，提供类型化访问"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_CONFIG = REPO_ROOT / ".kiro" / "briefings" / "config.json"

BASE_DIR = REPO_ROOT / "learning-notes" / "briefings"
PUBLISHED_INDEX = BASE_DIR / ".published-index.json"
LEGACY_INDEX = BASE_DIR / ".dedup-index.json"
SOURCE_HEALTH_FILE = REPO_ROOT / ".kiro_tmp" / "briefings" / "source-health.json"
RUNS_DIR = REPO_ROOT / ".kiro_tmp" / "briefings" / "runs"

TOPICS = ["ai-agent", "china-tech", "global-tech"]
TOPIC_NAMES = {"ai-agent": "AI Agent", "china-tech": "国内科技", "global-tech": "国际科技"}
TOPIC_ICONS = {"ai-agent": "🤖", "china-tech": "🇨🇳", "global-tech": "🌍"}


@dataclass
class CircuitBreakerCfg:
    fail_threshold_days: int = 3
    skip_when_tripped: bool = True


@dataclass
class LLMClassifyCfg:
    enabled: bool = False
    borderline_only: bool = False  # 仅对规则未命中任何 tag 的条目调 LLM
    provider: str = "anthropic"
    model: str = "claude-3-5-haiku-20241022"


@dataclass
class SemanticDedupCfg:
    enabled: bool = False
    threshold: float = 0.85


@dataclass
class FollowBuildersCfg:
    """zarazhangrui/follow-builders 中心化 feed 配置"""
    enabled: bool = False
    feed_base_url: str = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main"
    feeds: list[str] = field(default_factory=lambda: ["x", "podcasts"])
    timeout: int = 20
    x_min_likes: int = 50
    x_max_per_author: int = 2
    podcast_description_chars: int = 300


@dataclass
class Config:
    freshness_hours: int
    published_index_retention_days: int
    run_retention_days: int
    circuit_breaker: CircuitBreakerCfg
    main_topic_priority: list[str]
    rss_sources: list[dict]
    classify_rules: dict  # topic -> {"keywords": [...]}
    noise_keywords: list[str]
    score_overrides: dict  # topic -> {"primacy_sources": {sub: weight}}
    llm_classify: LLMClassifyCfg
    semantic_dedup: SemanticDedupCfg
    follow_builders: FollowBuildersCfg = field(default_factory=FollowBuildersCfg)
    # candidates 阶段每个 topic 的 top-N 上限。key 是 topic 名，"_default" 兜底，
    # 不同 topic 的候选池规模差距很大（ai-agent 通常远多于 china/global-tech），
    # 一刀切会让信息密集主题损失太多候选。CLI --top-n 显式指定时覆盖此配置。
    candidates_top_n: dict[str, int] = field(default_factory=lambda: {"_default": 60})
    raw: dict = field(default_factory=dict, repr=False)

    def resolve_top_n(self, topic: str) -> int:
        """返回某 topic 的 candidates top-N。
        优先 per-topic 配置 → _default 配置 → 硬编码 60。
        """
        if topic in self.candidates_top_n:
            return self.candidates_top_n[topic]
        return self.candidates_top_n.get("_default", 60)


_cached: Config | None = None


def load_config(path: Path | None = None, force_reload: bool = False) -> Config:
    """读取 config.json，默认缓存结果"""
    global _cached
    if _cached is not None and not force_reload and path is None:
        return _cached

    p = path or DEFAULT_CONFIG
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {p}")
    raw = json.loads(p.read_text(encoding="utf-8"))

    cb = raw.get("source_circuit_breaker", {})
    llm = raw.get("llm_classify", {})
    sem = raw.get("semantic_dedup", {})
    fb = raw.get("follow_builders", {})
    top_n_raw = raw.get("candidates_top_n", {})
    # 容错：candidates_top_n 必须是 dict，否则用默认；非数字 value 静默丢弃
    top_n_cfg: dict[str, int] = {"_default": 60}
    if isinstance(top_n_raw, dict):
        for k, v in top_n_raw.items():
            if k.startswith("_") and k != "_default":
                continue  # 跳过 _comment 之类的注释字段
            try:
                top_n_cfg[k] = int(v)
            except (TypeError, ValueError):
                continue

    cfg = Config(
        freshness_hours=int(raw.get("freshness_hours", 48)),
        published_index_retention_days=int(raw.get("published_index_retention_days", 60)),
        run_retention_days=int(raw.get("run_retention_days", 30)),
        circuit_breaker=CircuitBreakerCfg(
            fail_threshold_days=int(cb.get("fail_threshold_days", 3)),
            skip_when_tripped=bool(cb.get("skip_when_tripped", True)),
        ),
        main_topic_priority=list(raw.get("main_topic_rules", {}).get("priority", TOPICS)),
        rss_sources=list(raw.get("rss_sources", [])),
        classify_rules=dict(raw.get("classify_rules", {})),
        noise_keywords=list(raw.get("noise_keywords", [])),
        score_overrides=dict(raw.get("score_overrides", {})),
        llm_classify=LLMClassifyCfg(
            enabled=bool(llm.get("enabled", False)),
            borderline_only=bool(llm.get("borderline_only", False)),
            provider=str(llm.get("provider", "anthropic")),
            model=str(llm.get("model", "claude-3-5-haiku-20241022")),
        ),
        semantic_dedup=SemanticDedupCfg(
            enabled=bool(sem.get("enabled", False)),
            threshold=float(sem.get("threshold", 0.85)),
        ),
        follow_builders=FollowBuildersCfg(
            enabled=bool(fb.get("enabled", False)),
            feed_base_url=str(fb.get(
                "feed_base_url",
                "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main",
            )),
            feeds=list(fb.get("feeds", ["x", "podcasts"])),
            timeout=int(fb.get("timeout", 20)),
            x_min_likes=int(fb.get("x_min_likes", 20)),
            x_max_per_author=int(fb.get("x_max_per_author", 3)),
            podcast_description_chars=int(fb.get("podcast_description_chars", 800)),
        ),
        candidates_top_n=top_n_cfg,
        raw=raw,
    )
    if path is None:
        _cached = cfg
    return cfg


def get_api_key(provider: str) -> str | None:
    """从 env 读 API key"""
    env_map = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
    }
    return os.environ.get(env_map.get(provider, ""), "").strip() or None
