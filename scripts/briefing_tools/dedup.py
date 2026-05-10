"""去重工具：Jaccard、shingle、相似度判断"""

from __future__ import annotations

import re


def _tokens(text: str) -> set[str]:
    return set(re.sub(r"[^\w\s]", "", text.lower()).split())


def title_similarity(a: str, b: str) -> float:
    """词集合 Jaccard"""
    sa, sb = _tokens(a), _tokens(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def title_in(candidate: str, pool: list[str], threshold: float = 0.6) -> bool:
    for p in pool:
        if title_similarity(candidate, p) > threshold:
            return True
    return False


# ============================================
# Shingle-based 语义去重（title+description 前 200 字）
# ============================================

def _shingles(text: str, n: int = 3) -> set[str]:
    """生成字符 n-gram 集合，CJK + 英文都能用"""
    text = re.sub(r"\s+", " ", text.lower())
    if len(text) < n:
        return {text}
    return {text[i:i + n] for i in range(len(text) - n + 1)}


def shingle_similarity(a: str, b: str, n: int = 3) -> float:
    sa, sb = _shingles(a, n), _shingles(b, n)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def semantic_duplicate(a: dict, b: dict, threshold: float = 0.85) -> bool:
    """基于 title+description 前 200 字的 shingle 判同一事件"""
    text_a = (a.get("title", "") + " " + a.get("description", ""))[:200]
    text_b = (b.get("title", "") + " " + b.get("description", ""))[:200]
    return shingle_similarity(text_a, text_b) >= threshold


def dedup_semantic(items: list[dict], threshold: float = 0.85) -> tuple[list[dict], list[dict]]:
    """对条目列表做语义去重。保留较高分数或较早的一条。"""
    kept: list[dict] = []
    removed: list[dict] = []
    for it in items:
        dup_idx = None
        for i, k in enumerate(kept):
            if semantic_duplicate(it, k, threshold):
                dup_idx = i
                break
        if dup_idx is None:
            kept.append(it)
        else:
            # 比较分数：保留更高分的
            existing = kept[dup_idx]
            score_new = (it.get("score") or {}).get("total", 0)
            score_old = (existing.get("score") or {}).get("total", 0)
            if score_new > score_old:
                removed.append({**existing, "dedup_reason": f"语义相似 → 被更高分覆盖"})
                kept[dup_idx] = it
            else:
                removed.append({**it, "dedup_reason": "语义相似"})
    return kept, removed
