"""Ingest：一次采集全部源"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import Config
from .follow_builders import fetch_follow_builders
from .health import is_source_tripped, record_source_result
from .hn_algolia import fetch_hn_algolia
from .http import filter_by_freshness, http_get, parse_rss
from .supplements import run_supplements


def _cap_items(items: list[dict], max_items: int | None) -> list[dict]:
    if max_items is None or max_items <= 0 or len(items) <= max_items:
        return items
    return items[:max_items]


def _fetch_one(src: dict) -> tuple[dict, list[dict], float, bool]:
    timeout = src.get("timeout", 15)
    retries = src.get("retries", 3)
    t0 = time.time()
    xml_text = None
    urls = [src["url"]]
    fallback = src.get("fallback_url")
    if fallback:
        urls.append(fallback)

    for url in urls:
        xml_text = http_get(url, timeout=timeout, retries=retries)
        if xml_text:
            break

    elapsed = time.time() - t0
    if xml_text:
        items = parse_rss(xml_text, src["name"])
        items = _cap_items(items, src.get("max_items"))
        hints = src.get("topic_hints", [])
        for it in items:
            it["source_topic_hints"] = hints
        return src, items, elapsed, True

    # Algolia HN 备用（hnrss 502/超时时）
    algolia = src.get("algolia_fallback")
    if algolia:
        fb_items = fetch_hn_algolia(
            algolia.get("query", ""),
            queries=algolia.get("queries"),
            tags=algolia.get("tags", "story"),
            points_min=algolia.get("points_min"),
            hits_per_page=int(algolia.get("hits_per_page", 30)),
            freshness_hours=int(algolia.get("freshness_hours", 168)),
            max_pages_per_query=int(algolia.get("max_pages_per_query", 2)),
            timeout=timeout,
        )
        if fb_items:
            hints = src.get("topic_hints", [])
            for it in fb_items:
                it["source"] = f"{src['name']} (Algolia)"
                it["source_topic_hints"] = hints
            elapsed = time.time() - t0
            print(
                f"  🔁 Algolia 备用: {src['name']} → {len(fb_items)} 条",
                file=sys.stderr,
            )
            return src, fb_items, elapsed, True

    return src, [], elapsed, False


def run_ingest(cfg: Config) -> tuple[list[dict], list[dict], list[str]]:
    """
    返回 (items, per_source_metrics, tripped_source_names)
    - 熔断的源会被跳过
    - 每次抓取结果记入 health
    """
    sources = cfg.rss_sources
    skip_tripped = cfg.circuit_breaker.skip_when_tripped
    threshold = cfg.circuit_breaker.fail_threshold_days

    active: list[dict] = []
    tripped: list[str] = []
    for src in sources:
        if skip_tripped and is_source_tripped(src["name"], threshold):
            tripped.append(src["name"])
            continue
        active.append(src)

    if tripped:
        print(f"  🚨 熔断跳过 {len(tripped)} 个源: {', '.join(tripped)}")

    metrics: list[dict] = []
    all_items: list[dict] = []
    t_start = time.time()

    if active:
        with ThreadPoolExecutor(max_workers=min(len(active), 8)) as pool:
            futures = {pool.submit(_fetch_one, src): src for src in active}
            for future in as_completed(futures):
                src, items, elapsed, ok = future.result()
                record_source_result(src["name"], ok)
                metrics.append({
                    "name": src["name"],
                    "url": src["url"],
                    "count": len(items),
                    "elapsed_sec": round(elapsed, 2),
                    "ok": ok,
                })
                if ok:
                    all_items.extend(items)

    # follow-builders 中心化 feed（X 推文 + 播客 transcript）
    if cfg.follow_builders.enabled:
        fb_t0 = time.time()
        fb_items, fb_metrics = fetch_follow_builders(cfg.follow_builders)
        for m in fb_metrics:
            record_source_result(m["name"], m["ok"])
        metrics.extend(fb_metrics)
        all_items.extend(fb_items)
        feed_breakdown = ", ".join(
            f"{m['name'].split('/')[-1]}={m['count']}" for m in fb_metrics
        )
        print(
            f"  🔗 follow-builders: {len(fb_items)} 条 ({feed_breakdown})，"
            f"耗时 {time.time() - fb_t0:.1f}s"
        )

    # 补充采集层（B站 / V2EX 等，无 Cookie 社区源）
    sup_items, sup_metrics = run_supplements(cfg)
    if sup_metrics:
        for m in sup_metrics:
            record_source_result(m["name"], m["ok"])
        metrics.extend(sup_metrics)
        all_items.extend(sup_items)
        breakdown = ", ".join(f"{m['name']}={m['count']}" for m in sup_metrics)
        print(f"  📎 supplement: {len(sup_items)} 条 ({breakdown})")

    # 本 run 内按 URL/title 去重
    seen = set()
    deduped: list[dict] = []
    for it in all_items:
        key = it["url"] or (it["title"], it.get("source", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)

    before = len(deduped)
    deduped = filter_by_freshness(deduped, cfg.freshness_hours)
    filtered = before - len(deduped)
    print(
        f"  ⏱  采集完成: {len(deduped)} 条（去重后），"
        f"过滤 {filtered} 条超时效，总耗时 {time.time() - t_start:.1f}s"
    )
    return deduped, metrics, tripped
