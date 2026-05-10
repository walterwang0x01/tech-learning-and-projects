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
    provider: str = "anthropic"
    model: str = "claude-3-5-haiku-20241022"


@dataclass
class SemanticDedupCfg:
    enabled: bool = False
    threshold: float = 0.85


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
    raw: dict = field(repr=False)


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
            provider=str(llm.get("provider", "anthropic")),
            model=str(llm.get("model", "claude-3-5-haiku-20241022")),
        ),
        semantic_dedup=SemanticDedupCfg(
            enabled=bool(sem.get("enabled", False)),
            threshold=float(sem.get("threshold", 0.85)),
        ),
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
