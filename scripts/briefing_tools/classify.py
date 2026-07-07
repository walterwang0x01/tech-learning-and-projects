"""Classify：规则打标 + 评分（+ 可选 LLM）"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime

from .config import Config, TOPICS, get_api_key, get_llm_classify_model, get_openai_api_base
from .http import hours_since_published


# ============================================
# 关键词匹配（带词边界，ASCII 走 \b，中文/短语走子串）
# ============================================

def kw_hit(keyword: str, haystack: str) -> bool:
    k = keyword.lower()
    if any(ord(c) > 127 for c in k):
        return k in haystack
    if " " in k or k.startswith(" ") or k.endswith(" "):
        return k in haystack
    return re.search(r"\b" + re.escape(k) + r"\b", haystack) is not None


# ============================================
# 评分（可覆盖 primacy）
# ============================================

_DEFAULT_HIGH_PRIMACY = [
    "blog", "research", "openai", "anthropic", "google ai", "huggingface",
    "github blog", "aws blog", "cloudflare", "kubernetes", "langchain",
]
_MID_PRIMACY = ["arxiv", "infoq", "量子位", "36氪", "开源中国", "极客公园"]
_LOW_PRIMACY_HN = ["hn ", "hacker news", "techcrunch", "verge", "ars technica", "wired"]


def score_primacy(source: str, tags: list[str], cfg: Config) -> int:
    s = source.lower()
    # per-topic override（取第一个命中的 topic）
    for tag in tags:
        overrides = cfg.score_overrides.get(tag, {}).get("primacy_sources", {})
        for key, weight in overrides.items():
            if key.lower() in s:
                return int(weight)
    # 默认规则
    if any(k in s for k in _DEFAULT_HIGH_PRIMACY):
        return 5
    if any(k in s for k in _MID_PRIMACY):
        return 4
    if any(k in s for k in _LOW_PRIMACY_HN):
        return 3
    return 2


_PREFERRED = ["langgraph", "mcp", "crewai", "python", "typescript", "rag", "agentic"]
_ACTION_SIGNALS = ["release", "launches", "open source", "开源", "发布", "上线", "announces"]


def score_item(item: dict, tags: list[str], cfg: Config, now: datetime | None = None) -> dict:
    title_desc = (item.get("title", "") + " " + item.get("description", "")).lower()

    # freshness
    hrs = hours_since_published(item.get("published", ""), now)
    if hrs is None:
        freshness = 3
    elif hrs <= 48:
        freshness = 5
    elif hrs <= 168:
        freshness = 3
    else:
        freshness = 1

    # primacy（带 per-topic override）
    primacy = score_primacy(item.get("source", ""), tags, cfg)

    # relevance
    relevance = 3
    if any(kw_hit(k, title_desc) for k in _PREFERRED):
        relevance = 5

    # utility
    utility = 3
    if any(kw_hit(k, title_desc) for k in _ACTION_SIGNALS) or re.search(r"\bv\d+\.\d+", title_desc):
        utility = 4

    # 噪声惩罚
    if any(kw_hit(k, title_desc) for k in cfg.noise_keywords):
        relevance = max(1, relevance - 2)
        utility = max(1, utility - 2)

    total = freshness + primacy + relevance + utility
    return {
        "freshness": freshness,
        "primacy": primacy,
        "relevance": relevance,
        "utility": utility,
        "total": total,
    }


# ============================================
# 分类（规则 / LLM）
# ============================================

def classify_rule(item: dict, cfg: Config) -> list[str]:
    """规则分类：
    1. 关键词命中优先（只匹配 title + description，不匹配 source 字段）
    2. 关键词完全未命中时用 source hint 兜底
       — follow-builders/x 推文不打 hint，避免无关节推误入 ai-agent
    """
    haystack = (item.get("title", "") + " " + item.get("description", "")).lower()
    tags: set[str] = set()
    for topic, rules in cfg.classify_rules.items():
        for kw in rules.get("keywords", []):
            if kw_hit(kw, haystack):
                tags.add(topic)
                break
    if not tags:
        source = item.get("source", "")
        if source.startswith("follow-builders/x/"):
            return []
        hints = item.get("source_topic_hints", []) or []
        tags.update(hints)
    return sorted(tags)


def decide_main_topic(tags: list[str], priority: list[str]) -> str | None:
    """根据 priority 列表决定 main topic。未命中时返回 None。"""
    for t in priority:
        if t in tags:
            return t
    return tags[0] if tags else None


# ============================================
# LLM 分类（可选，默认关闭）
# ============================================

class LLMClassifyError(RuntimeError):
    pass


_CLASSIFY_SYSTEM_PROMPT = (
    "You tag news articles with topic tags. "
    "Tags are a subset of: ai-agent, china-tech, global-tech. "
    "A single article can carry multiple tags. "
    "Respond ONLY with JSON: {\"results\":[{\"idx\":0,\"tags\":[\"...\"]}, ...]}. "
    "Use 'ai-agent' for content about LLMs, AI frameworks, agents, MCP, RAG, prompt engineering. "
    "Use 'china-tech' for content about Chinese tech companies/products/policy. "
    "Use 'global-tech' for general global tech, programming languages, cloud, devtools, security. "
    "If nothing fits, return empty tags []."
)


def _build_labeled_items(items: list[dict]) -> list[dict]:
    return [
        {
            "idx": i,
            "title": (it.get("title") or "")[:180],
            "source": it.get("source") or "",
            "desc": (it.get("description") or "")[:300],
        }
        for i, it in enumerate(items)
    ]


def _parse_classify_json(text: str, provider: str) -> dict:
    try:
        s = text.strip()
        if s.startswith("```"):
            s = re.sub(r"^```(?:json)?\s*", "", s)
            s = re.sub(r"\s*```$", "", s)
        return json.loads(s)
    except json.JSONDecodeError:
        raise LLMClassifyError(f"{provider} response not JSON: {text[:200]}")


def _tags_from_results(data: dict, n: int) -> list[list[str]]:
    results: dict[int, list[str]] = {}
    for r in data.get("results", []):
        idx = int(r.get("idx", -1))
        tags = [t for t in (r.get("tags") or []) if t in TOPICS]
        if idx >= 0:
            results[idx] = tags
    return [results.get(i, []) for i in range(n)]


def classify_llm_batch(items: list[dict], cfg: Config, batch_size: int = 40) -> list[list[str]]:
    """用 LLM 批量分类。失败时抛错让调用方退回规则。"""
    provider = cfg.llm_classify.provider
    if provider == "anthropic":
        api_key = get_api_key("anthropic")
        if not api_key:
            raise LLMClassifyError("ANTHROPIC_API_KEY not set")
        classify_fn = lambda chunk: _anthropic_classify(chunk, cfg.llm_classify.model, api_key)
    elif provider == "openai":
        api_key = get_api_key("openai")
        if not api_key:
            raise LLMClassifyError("OPENAI_API_KEY not set")
        api_base = get_openai_api_base(cfg)
        model = get_llm_classify_model(cfg)
        classify_fn = lambda chunk: _openai_classify(chunk, model, api_key, api_base)
    else:
        raise LLMClassifyError(f"Unsupported provider: {provider}")

    all_tags: list[list[str]] = []
    for i in range(0, len(items), batch_size):
        chunk = items[i:i + batch_size]
        all_tags.extend(classify_fn(chunk))
    return all_tags


def _anthropic_classify(items: list[dict], model: str, api_key: str) -> list[list[str]]:
    """单批次调用 Claude Messages API，返回每条的 tags 列表。"""
    labeled = _build_labeled_items(items)
    user = "Tag these:\n" + json.dumps(labeled, ensure_ascii=False)
    payload = {
        "model": model,
        "max_tokens": 4000,
        "system": _CLASSIFY_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as e:
        raise LLMClassifyError(f"Anthropic API error: {e}")

    text = ""
    for block in body.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "")
    data = _parse_classify_json(text, "Anthropic")
    return _tags_from_results(data, len(items))


def _openai_classify(items: list[dict], model: str, api_key: str, api_base: str) -> list[list[str]]:
    """单批次调用 OpenAI 兼容 chat/completions（含 llm-gw），返回每条的 tags 列表。"""
    labeled = _build_labeled_items(items)
    user = "Tag these:\n" + json.dumps(labeled, ensure_ascii=False)
    payload = {
        "model": model,
        "max_tokens": 4000,
        "messages": [
            {"role": "system", "content": _CLASSIFY_SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ],
    }
    url = f"{api_base}/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as e:
        raise LLMClassifyError(f"OpenAI API error: {e}")

    choices = body.get("choices") or []
    if not choices:
        raise LLMClassifyError(f"OpenAI API empty choices: {str(body)[:200]}")
    text = (choices[0].get("message") or {}).get("content") or ""
    data = _parse_classify_json(text, "OpenAI")
    return _tags_from_results(data, len(items))


# ============================================
# 入口
# ============================================

def run_classify(items: list[dict], cfg: Config) -> list[dict]:
    """
    产出 classified 条目：
    - tags（规则 + 可选 LLM 补标）
    - main_topic（根据 priority）
    - score 细目
    """
    tag_lists = [classify_rule(it, cfg) for it in items]

    if cfg.llm_classify.enabled:
        if cfg.llm_classify.borderline_only:
            borderline_idx = [i for i, tags in enumerate(tag_lists) if not tags]
            if borderline_idx:
                try:
                    borderline_items = [items[i] for i in borderline_idx]
                    llm_tags = classify_llm_batch(borderline_items, cfg)
                    for idx, tags in zip(borderline_idx, llm_tags):
                        tag_lists[idx] = tags
                    print(f"  🤖 LLM 补标 {len(borderline_idx)} 条边界条目")
                except LLMClassifyError as e:
                    print(f"  ⚠️  LLM 边界补标失败，保留规则结果: {e}")
        else:
            try:
                tag_lists = classify_llm_batch(items, cfg)
            except LLMClassifyError as e:
                print(f"  ⚠️  LLM 分类失败，退回规则: {e}")
                tag_lists = [classify_rule(it, cfg) for it in items]

    out = []
    for it, tags in zip(items, tag_lists):
        # 非 follow-builders/x 条目：LLM/规则都没命中时走 source hint 兜底
        if not tags and not (it.get("source", "").startswith("follow-builders/x/")):
            tags = list(it.get("source_topic_hints", []) or [])
        main = decide_main_topic(tags, cfg.main_topic_priority)
        score = score_item(it, tags, cfg)
        new_item = dict(it)
        new_item["tags"] = sorted(set(tags))
        new_item["main_topic"] = main
        new_item["score"] = score
        out.append(new_item)
    return out
