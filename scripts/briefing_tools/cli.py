"""CLI 入口"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from .candidates import build_candidates
from .classify import run_classify
from .config import (
    BASE_DIR,
    LEGACY_INDEX,
    PUBLISHED_INDEX,
    REPO_ROOT,
    RUNS_DIR,
    SOURCE_HEALTH_FILE,
    TOPIC_ICONS,
    TOPIC_NAMES,
    TOPICS,
    load_config,
    get_llm_classify_model,
)
from .health import (
    is_source_tripped,
    load_health,
    reset_source,
    should_probe,
    tripped_sources,
)
from .http import http_get
from .ingest import run_ingest
from .notify import (
    briefing_github_url,
    count_briefing_items,
    extract_briefing_summary,
    get_bark_url,
    push_bark,
)
from .retention import cleanup_runs
from .schemas import validate_classified_item, validate_pool_item
from .storage import (
    atomic_write,
    atomic_write_json,
    atomic_write_jsonl,
    briefing_file,
    check_url_reuse,
    doctor_check_index_consistency,
    load_published_index,
    now_str,
    read_jsonl,
    rebuild_published_index,
    register_published,
    run_dir,
    today_str,
    validate_briefing_md,
)


# ============================================
# v2 主命令
# ============================================

def cmd_ingest(args):
    cfg = load_config()
    print(f"📡 开始一次性采集 {len(cfg.rss_sources)} 个源")
    items, metrics, tripped = run_ingest(cfg)

    rd = run_dir()
    rd.mkdir(parents=True, exist_ok=True)
    atomic_write_jsonl(rd / "pool.jsonl", items)

    metrics_data = {
        "stage": "ingest",
        "at": now_str(),
        "sources": metrics,
        "total_items": len(items),
        "tripped_sources": tripped,
    }
    atomic_write_json(rd / "metrics.json", metrics_data)
    print(f"💾 pool 写入: {rd / 'pool.jsonl'} ({len(items)} 条)")
    print(f"📊 metrics: {rd / 'metrics.json'}")

    failed = [m["name"] for m in metrics if not m["ok"]]
    if failed:
        print(f"⚠️  本次失败源 ({len(failed)}): {', '.join(failed)}")


def cmd_classify(args):
    cfg = load_config()
    rd = run_dir()
    pool_path = rd / "pool.jsonl"
    if not pool_path.exists():
        print(f"❌ pool 不存在: {pool_path}", file=sys.stderr)
        print("   请先运行: python3 scripts/briefing-tools.py ingest", file=sys.stderr)
        sys.exit(1)

    # Validate input
    items = []
    skipped = 0
    for raw in read_jsonl(pool_path):
        try:
            pi = validate_pool_item(raw)
            items.append(pi.to_dict())
        except Exception as e:
            skipped += 1
            print(f"  ⚠️  跳过损坏条目: {e}", file=sys.stderr)
    if skipped:
        print(f"  🛡  schema 校验跳过 {skipped} 条损坏数据")

    if cfg.llm_classify.enabled:
        mode = "边界补标" if cfg.llm_classify.borderline_only else "全量"
        print(f"  🤖 LLM 分类已启用 ({mode}): {cfg.llm_classify.provider}/{get_llm_classify_model(cfg)}")

    classified = run_classify(items, cfg)
    atomic_write_jsonl(rd / "classified.jsonl", classified)

    # tag 分布统计
    counts = {t: 0 for t in TOPICS}
    counts["(none)"] = 0
    main_counts = {t: 0 for t in TOPICS}
    main_counts["(none)"] = 0
    for it in classified:
        if not it["tags"]:
            counts["(none)"] += 1
        for t in it["tags"]:
            counts[t] = counts.get(t, 0) + 1
        mt = it.get("main_topic") or "(none)"
        main_counts[mt] = main_counts.get(mt, 0) + 1

    print(f"💾 classified 写入: {rd / 'classified.jsonl'} ({len(classified)} 条)")
    print("📊 tag 分布（多标签）:")
    for t, c in counts.items():
        print(f"   {t}: {c}")
    print("📊 main_topic 分布:")
    for t, c in main_counts.items():
        print(f"   {t}: {c}")


def cmd_candidates(args):
    cfg = load_config()
    rd = run_dir()
    classified_path = rd / "classified.jsonl"
    if not classified_path.exists():
        print(f"❌ classified 不存在: {classified_path}", file=sys.stderr)
        sys.exit(1)

    classified = []
    for raw in read_jsonl(classified_path):
        try:
            ci = validate_classified_item(raw)
            classified.append(ci.to_dict())
        except Exception as e:
            print(f"  ⚠️  跳过损坏条目: {e}", file=sys.stderr)

    topics = [args.topic] if args.topic != "all" else TOPICS
    # CLI 显式传 --require-main-topic / --no-require-main-topic 时覆盖配置，否则按 config 走
    require_main = (
        cfg.candidates_require_main_topic
        if getattr(args, "require_main_topic", None) is None
        else args.require_main_topic
    )
    for t in topics:
        # CLI --top-n 显式传值覆盖配置；否则按 per-topic 配置取
        topic_top_n = args.top_n if args.top_n is not None else cfg.resolve_top_n(t)
        result = build_candidates(
            classified, t, today_str(), cfg,
            min_score=args.min_score,
            require_main_topic=require_main,
            top_n=topic_top_n,
        )
        out_path = rd / f"candidates.{t}.jsonl"
        atomic_write_jsonl(out_path, result["items"])
        atomic_write_json(rd / f"candidates.{t}.stats.json", {"stats": result["stats"]})
        print(f"📦 {t}: 保留 {result['stats']['kept']}/{result['stats']['input']} 条")
        print(f"   过滤明细: {result['stats']['filtered']}")
        print(f"   候选集: {out_path}")


def cmd_register(args):
    cfg = load_config()
    topics = [args.topic] if args.topic != "all" else TOPICS
    for t in topics:
        result = register_published(t, args.date, retention_days=cfg.published_index_retention_days)
        if "error" in result:
            print(f"⚠️  {t} ({result['date']}): {result['error']}")
        else:
            print(f"📋 {t} ({result['date']}): 新增 {result['registered']}/{result['total_urls']} URLs")
            if "warning" in result:
                print(f"   ⚠️  {result['warning']}")


def cmd_rebuild_index(args):
    print(f"🔄 扫描最近 {args.days} 天的简报文件…")
    result = rebuild_published_index(days=args.days)
    print(f"✅ 扫描 {result['files_scanned']} 个 md 文件，登记 {result['urls_registered']} 个 URL")


def cmd_doctor(args):
    """检查 published-index 与 md 文件的一致性，可选自动修复"""
    cfg = load_config()
    issues = doctor_check_index_consistency(
        auto_fix=args.fix,
        retention_days=cfg.published_index_retention_days,
    )

    miss = issues["missing"]
    drift = issues["hash_drift"]
    orph = issues["orphan"]
    fixed = issues["fixed"]

    print(f"## 🩺 简报索引一致性检查\n")
    print(f"- ❓ 缺失登记 (md 存在但无 file_hash): {len(miss)}")
    print(f"- 🔀 hash 漂移 (md 修改但未重新 register): {len(drift)}")
    print(f"- 👻 孤儿记录 (file_hash 存在但 md 已删): {len(orph)}")

    if miss:
        print("\n### 缺失登记")
        for p in miss:
            print(f"  - {p['key']} (hash={p['actual']})")
    if drift:
        print("\n### hash 漂移")
        for p in drift:
            print(f"  - {p['key']} (recorded={p['recorded']}, actual={p['actual']})")
    if orph:
        print("\n### 孤儿记录（不会自动删，需手动确认）")
        for p in orph:
            print(f"  - {p['key']}")

    if args.fix:
        if fixed:
            normal = [f for f in fixed if not f.get("backfilled_legacy")]
            legacy = [f for f in fixed if f.get("backfilled_legacy")]
            print(f"\n✅ 自动修复 {len(fixed)} 条:")
            for f in normal:
                print(f"  - {f['key']}: 新增 {f['registered']}/{f['total_urls']} URLs")
            for f in legacy:
                print(f"  - {f['key']}: 仅补 file_hash（旧格式 md，items 已通过 v1 路径登记）")
        else:
            print("\n（无需修复）")
    else:
        if miss or drift:
            print("\n💡 加 --fix 自动跑 register_published 修复 missing 和 hash_drift")

    # 退出码：有问题但没修复时退 1，便于 CI/hook 用
    has_unresolved = (miss or drift) and not args.fix
    if has_unresolved or orph:
        sys.exit(1)


def cmd_validate(args):
    """校验一个简报 md 是否符合"已完成"的格式要求"""
    path = Path(args.path)
    strict = not getattr(args, "lenient", False)
    ok, reason = validate_briefing_md(path, strict=strict)
    if ok:
        print(f"✅ {path}: valid")
        sys.exit(0)
    else:
        print(f"❌ {path}: {reason}", file=sys.stderr)
        sys.exit(1)


def cmd_compare_skeleton(args):
    """对比简报章节骨架与金标准 fixture"""
    from .skeleton import diff_skeleton, extract_skeleton

    path = Path(args.path)
    if not path.exists():
        print(f"❌ 简报文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    fixtures_dir = REPO_ROOT / "scripts" / "tests" / "fixtures" / "briefings"
    golden_path = fixtures_dir / f"{args.topic}.golden.md"
    if not golden_path.exists():
        print(f"❌ 金标准 fixture 不存在: {golden_path}", file=sys.stderr)
        sys.exit(1)

    actual = extract_skeleton(path)
    golden = extract_skeleton(golden_path)
    diffs = diff_skeleton(actual, golden)

    if not diffs:
        print(f"✅ {path}: skeleton matches {args.topic}.golden.md")
        sys.exit(0)
    else:
        print(f"❌ {path}: skeleton diff vs golden", file=sys.stderr)
        for d in diffs:
            print(f"  - {d}", file=sys.stderr)
        sys.exit(1)


def cmd_render(args):
    """从 BriefingDoc JSON 渲染 md，并自动跑 validate + skeleton 校验"""
    from .doc_schema import BriefingDoc, DocValidationError
    from .render import render_briefing
    from .skeleton import diff_skeleton, extract_skeleton

    json_path = Path(args.json)
    if not json_path.exists():
        print(f"❌ JSON 文件不存在: {json_path}", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        doc = BriefingDoc.from_dict(data)
    except DocValidationError as e:
        print(f"❌ schema 校验失败: {e}", file=sys.stderr)
        sys.exit(1)

    md = render_briefing(doc)
    out = Path(args.out) if args.out else briefing_file(doc.topic, doc.date)
    atomic_write(out, md)
    print(f"💾 已渲染: {out}")

    # 自动 validate
    ok, reason = validate_briefing_md(out)
    if not ok:
        print(f"❌ 渲染产物未通过 validate: {reason}", file=sys.stderr)
        sys.exit(2)

    # 自动 skeleton 对比
    fixtures_dir = REPO_ROOT / "scripts" / "tests" / "fixtures" / "briefings"
    golden_path = fixtures_dir / f"{doc.topic}.golden.md"
    if golden_path.exists():
        diffs = diff_skeleton(extract_skeleton(out), extract_skeleton(golden_path))
        if diffs:
            print(f"❌ skeleton diff vs golden:", file=sys.stderr)
            for d in diffs:
                print(f"  - {d}", file=sys.stderr)
            sys.exit(3)

    print("✅ validate + skeleton 全部通过")

    # URL 复用检查：web search 补充的链接不经候选集，绕过了所有去重
    reuse = check_url_reuse(doc.topic, doc.date, path=out)
    if reuse:
        print(f"\n⚠️  {len(reuse)} 条 URL 此前已收录，请判断是否换掉：")
        for r in reuse:
            tag = "跨天" if r["kind"] == "cross_day" else "跨主题"
            print(f"     [{tag}] {r['url']}")
            print(f"            已用于 {r['where']}")
        print("     同一原文若有实质新进展可保留，仅换个说法则应改选来源。")


def cmd_cleanup(args):
    cfg = load_config()
    days = args.days if args.days is not None else cfg.run_retention_days
    result = cleanup_runs(days)
    print(f"🧹 run 目录清理: removed={result['removed']} kept={result['kept']} cutoff={result.get('cutoff', '?')}")


def cmd_run_all(args):
    cfg = load_config()
    print("=" * 60)
    print("Stage 1: ingest")
    print("=" * 60)
    cmd_ingest(args)
    print()
    print("=" * 60)
    print("Stage 2: classify")
    print("=" * 60)
    cmd_classify(args)
    print()
    print("=" * 60)
    print("Stage 3: candidates (all topics)")
    print("=" * 60)
    args.topic = "all"
    args.min_score = getattr(args, "min_score", 12)
    # None = 交给 cmd_candidates 读 config.candidates_require_main_topic
    args.require_main_topic = getattr(args, "require_main_topic", None)
    # None = 按 config.candidates_top_n 的 per-topic 配置走，cmd_candidates 内部解析
    args.top_n = getattr(args, "top_n", None)
    cmd_candidates(args)
    print()
    print("=" * 60)
    print("Stage 4: cleanup old runs")
    print("=" * 60)
    args.days = cfg.run_retention_days
    cmd_cleanup(args)
    print()
    print("✅ 流水线完成")


def _probe_hint(src: dict, retry_after_days: int) -> str:
    """熔断源的 half-open 试探提示。让自愈机制对用户可见，
    否则看到熔断告警会以为必须人工 health-reset。"""
    if retry_after_days <= 0:
        return "，自愈试探已关闭，需人工 health-reset"
    if should_probe(src["name"], retry_after_days):
        return " → 下次采集会 half-open 试探"
    last_fail = src.get("last_fail_date", "")
    try:
        elapsed = (datetime.now() - datetime.strptime(last_fail, "%Y-%m-%d")).days
    except ValueError:
        return ""
    return f" → {max(retry_after_days - elapsed, 0)} 天后自动试探"


def _disabled_source_names(cfg) -> set[str]:
    """config 里 enabled=false 的源。这些源不参与采集，也不该出现在熔断告警里
    （它们永远"连续失败"，反复提醒等于噪音）。"""
    return {s["name"] for s in cfg.rss_sources if not s.get("enabled", True)}


def cmd_health(args):
    """查看源健康状态"""
    cfg = load_config()
    threshold = cfg.circuit_breaker.fail_threshold_days
    data = load_health()
    sources = data.get("sources", {})
    disabled = _disabled_source_names(cfg)

    if disabled:
        print(f"## ⏸  已停用源（config enabled=false，不参与采集）: {', '.join(sorted(disabled))}\n")

    retry_after = cfg.circuit_breaker.retry_after_days
    tripped = [s for s in tripped_sources(threshold) if s["name"] not in disabled]
    if tripped:
        print(f"## 🚨 熔断源（连续失败 ≥ {threshold} 天）")
        for s in tripped:
            print(f"  - {s['name']}: {s['consecutive_failures']} 天连续失败（最后失败于 {s.get('last_fail_date', '?')}）"
                  f"{_probe_hint(s, retry_after)}")
    else:
        print(f"## ✅ 暂无熔断源（阈值: {threshold} 天）")

    print("\n## 📡 全部源状态")
    print("| 源 | 最近成功 | 最近失败 | 连续失败 | 总运行次数 |")
    print("|----|----------|----------|----------|-----------|")
    for name in sorted(sources.keys()):
        s = sources[name]
        print(f"| {name} | {s.get('last_ok_date', '—')} | {s.get('last_fail_date', '—')} | "
              f"{s.get('consecutive_failures', 0)} | {s.get('total_runs', 0)} |")


def cmd_curate_status(args):
    """列出今日 curate 状态：哪些主题缺简报、候选集路径、基线/熔断异常"""
    date = args.date or today_str()
    rd = RUNS_DIR / date
    missing = []
    done = []
    for t in TOPICS:
        fp = briefing_file(t, date)
        if fp.exists():
            done.append(t)
        else:
            missing.append(t)

    print(f"## 📋 Curate 状态 — {date}\n")
    if done:
        print("### ✅ 已完成")
        for t in done:
            print(f"- {TOPIC_NAMES.get(t, t)}: {briefing_file(t, date)}")
    if missing:
        print("\n### ⏳ 待 curate")
        for t in missing:
            cand = rd / f"candidates.{t}.jsonl"
            print(f"- {TOPIC_NAMES.get(t, t)}")
            print(f"  - prompt: `.kiro/briefings/prompts/curate.{t}.md` + `_shared.md`")
            print(f"  - 候选集: {cand if cand.exists() else '（需先 run-all）'}")
    else:
        print("\n✅ 三份简报今日均已存在")

    report = _collect_status()
    if report.get("tripped_sources"):
        print(f"\n🚨 熔断源: {', '.join(report['tripped_sources'])}")
    anomalies = [b for b in report.get("baselines", []) if b.get("anomaly")]
    if anomalies:
        print("\n🚨 基线异常")
        for b in anomalies:
            print(f"- {TOPIC_NAMES.get(b['topic'], b['topic'])}: {b['message']}")

    if args.json:
        print(json.dumps({
            "date": date,
            "done": done,
            "missing": missing,
            "run_dir": str(rd) if rd.exists() else None,
        }, ensure_ascii=False, indent=2))


def _warn_stale_index(max_show: int = 5) -> None:
    """finalize 收尾时只读扫一遍全量索引一致性。

    finalize 只 register 本次 topic/date，历史遗漏（subagent 中断没跑
    register、手动改过 md）不会被发现，一直累积到跨天去重开始漏判。
    这里只提醒不自动修：批量改写历史索引应当由人确认后跑 `doctor --fix`。
    """
    cfg = load_config()
    issues = doctor_check_index_consistency(
        auto_fix=False,
        retention_days=cfg.published_index_retention_days,
    )
    miss, drift, orph = issues["missing"], issues["hash_drift"], issues["orphan"]
    if not (miss or drift or orph):
        return

    print(
        f"\n⚠️  索引一致性（历史遗留）：缺失登记 {len(miss)} / "
        f"hash 漂移 {len(drift)} / 孤儿记录 {len(orph)}"
    )
    fixable = miss + drift
    for p in fixable[:max_show]:
        print(f"     - {p['key']}")
    if len(fixable) > max_show:
        print(f"     …另有 {len(fixable) - max_show} 条")
    if fixable:
        print("     修复: python3 scripts/briefing-tools.py doctor --fix")
    if orph:
        print(f"     孤儿记录需手动确认: python3 scripts/briefing-tools.py doctor")


def _warn_url_reuse(topics: list[str], date: str) -> None:
    """finalize 收尾时汇总 URL 复用情况。

    render 阶段的同一检查在并行 curate 下只能部分命中跨主题重复——先 render 的
    那份看不到还没写出来的其他主题。finalize 只跑一次且三份 md 都已落盘，
    这里才是完整视图。只报告不阻断，让人决定改不改。
    """
    seen: set[tuple[str, str]] = set()
    rows: list[tuple[str, dict]] = []
    for t in topics:
        for r in check_url_reuse(t, date):
            # 跨主题重复会在两个 topic 各报一次，去重成一条
            key = tuple(sorted([t, r["where"].split()[0]])) if r["kind"] == "cross_topic" else (t, "")
            dedup_key = (r["url"], "|".join(key))
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            rows.append((t, r))
    if not rows:
        return

    cross_topic = [(t, r) for t, r in rows if r["kind"] == "cross_topic"]
    cross_day = [(t, r) for t, r in rows if r["kind"] == "cross_day"]
    print(f"\n⚠️  URL 复用：跨主题 {len(cross_topic)} 条 / 跨天 {len(cross_day)} 条")
    for t, r in cross_topic:
        print(f"     [跨主题] {r['url']}")
        print(f"              {t} 与 {r['where']} 同时收录")
    for t, r in cross_day[:5]:
        print(f"     [跨天]   {r['url']}")
        print(f"              今日 {t}，此前 {r['where']}")
    if len(cross_day) > 5:
        print(f"     …另有 {len(cross_day) - 5} 条跨天复用")
    print("     这些链接来自 curate 阶段的 web search 补充，不经候选集过滤。")


def cmd_finalize(args):
    """curate 完成后统一收尾：register → 索引一致性提醒 → index → notify"""
    date = args.date or today_str()
    topics = [args.topic] if args.topic != "all" else TOPICS

    for t in topics:
        fp = briefing_file(t, date)
        if not fp.exists():
            print(f"⚠️  跳过 {t}: 简报不存在 {fp}")
            continue
        result = register_published(t, date)
        if "error" in result:
            print(f"⚠️  register {t}: {result['error']}")
        else:
            print(f"📋 register {t}: 新增 {result['registered']}/{result['total_urls']} URLs")

    _warn_stale_index()
    _warn_url_reuse(topics, date)

    cmd_index(args)
    if not args.skip_notify:
        cmd_notify(args)
    cmd_status(argparse.Namespace(json=False, check_sources=False))
    print("\n✅ finalize 完成")


def cmd_health_reset(args):
    reset_source(args.name)
    print(f"✅ 已重置源健康状态: {args.name}")


# ============================================
# Status 面板
# ============================================

def _collect_status() -> dict:
    today = datetime.now()
    report = {"date": today_str(), "topics": {}}
    for topic in TOPICS:
        topic_base = BASE_DIR / topic
        if not topic_base.exists():
            report["topics"][topic] = {
                "status": "🆕", "latest": None,
                "total": 0, "this_week": 0, "this_month": 0,
            }
            continue
        md_files = sorted(
            [f for f in topic_base.rglob("*.md") if f.name != "README.md"],
            reverse=True,
        )
        dates = []
        for f in md_files:
            m = re.match(r"(\d{4}-\d{2}-\d{2})", f.stem)
            if m:
                dates.append(m.group(1))
        latest = dates[0] if dates else None
        days_ago = None
        status = "🆕"
        if latest:
            try:
                days_ago = (today - datetime.strptime(latest, "%Y-%m-%d")).days
                status = "✅" if days_ago == 0 else ("⚠️" if days_ago == 1 else "❌")
            except ValueError:
                pass
        week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        month_start = today.strftime("%Y-%m-01")
        report["topics"][topic] = {
            "status": status,
            "latest": latest,
            "days_ago": days_ago,
            "total": len(dates),
            "this_week": sum(1 for d in dates if d >= week_start),
            "this_month": sum(1 for d in dates if d >= month_start),
        }

    if PUBLISHED_INDEX.exists():
        idx = load_published_index()
        report["index_size"] = len(idx.get("items", {}))
        report["index_updated"] = idx.get("updated", "")
    else:
        report["index_size"] = 0
        report["index_updated"] = "未创建"

    # 今日 run 状态
    rd = run_dir()
    report["run"] = {
        "exists": rd.exists(),
        "dir": str(rd) if rd.exists() else None,
        "stages": [],
    }
    if rd.exists():
        for name in ["pool.jsonl", "classified.jsonl"]:
            p = rd / name
            if p.exists():
                try:
                    lines = sum(1 for _ in p.open())
                except Exception:
                    lines = 0
                report["run"]["stages"].append({"file": name, "items": lines})
        for topic in TOPICS:
            p = rd / f"candidates.{topic}.jsonl"
            if p.exists():
                try:
                    lines = sum(1 for _ in p.open())
                except Exception:
                    lines = 0
                report["run"]["stages"].append({"file": p.name, "items": lines})

    # 熔断源（排除主动停用的，它们永远失败，报了也无从处理）
    cfg = load_config()
    _disabled = _disabled_source_names(cfg)
    report["disabled_sources"] = sorted(_disabled)
    report["tripped_sources"] = [
        s["name"] for s in tripped_sources(cfg.circuit_breaker.fail_threshold_days)
        if s["name"] not in _disabled
    ]

    # 基线对比（近 7 天均值）
    from .baseline import check_all_baselines
    report["baselines"] = check_all_baselines()

    return report


def _format_status(report: dict) -> str:
    lines = [f"## 📊 简报采集状态 — {report['date']}\n"]
    lines.append("| 主题 | 最近采集 | 距今 | 状态 | 本周/本月/总计 |")
    lines.append("|------|----------|------|------|---------------|")
    for topic, info in report["topics"].items():
        n = TOPIC_NAMES.get(topic, topic)
        latest = info["latest"] or "从未采集"
        days = f"{info['days_ago']} 天" if info["days_ago"] is not None else "-"
        counts = f"{info['this_week']}/{info['this_month']}/{info['total']}"
        lines.append(f"| {n} | {latest} | {days} | {info['status']} | {counts} |")
    lines.append(f"\n已发布索引: {report['index_size']} 条 (更新于 {report['index_updated']})")

    if report.get("tripped_sources"):
        lines.append(f"\n🚨 熔断源: {', '.join(report['tripped_sources'])}")
        lines.append(
            "   💡 源恢复后可执行: "
            "`python3 scripts/briefing-tools.py health-reset \"源名称\"`"
        )

    if report.get("run", {}).get("exists"):
        lines.append(f"\n### 🏃 今日运行状态 ({report['run']['dir']})")
        for stage in report["run"]["stages"]:
            lines.append(f"- {stage['file']}: {stage['items']} 条")

    # 基线异常
    anomalies = [b for b in report.get("baselines", []) if b.get("anomaly")]
    if anomalies:
        lines.append("\n### 🚨 基线异常")
        for b in anomalies:
            n = TOPIC_NAMES.get(b["topic"], b["topic"])
            lines.append(f"- **{n}**：{b['message']}")
    elif report.get("baselines"):
        # 全部正常时也展示一行汇总，便于快速扫
        normals = [b for b in report["baselines"] if b.get("ratio") is not None and not b["anomaly"]]
        if normals:
            lines.append("\n### 📉 基线对比（近 7 天均值）")
            for b in normals:
                n = TOPIC_NAMES.get(b["topic"], b["topic"])
                lines.append(f"- {n}：{b['message']}")

    lines.append("\n### 💡 建议")
    for topic, info in report["topics"].items():
        n = TOPIC_NAMES.get(topic, topic)
        if info["status"] in ("❌", "🆕"):
            lines.append(f"- 🔴 **{n}** 需要采集")
        elif info["status"] == "⚠️":
            lines.append(f"- 🟡 **{n}** 建议今天更新")
    return "\n".join(lines)


def cmd_status(args):
    report = _collect_status()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_format_status(report))

    if args.check_sources:
        cfg = load_config()
        print("\n## 🔗 采集源健康检查\n")
        print("| 源名称 | topic_hints | 状态 | 耗时 |")
        print("|--------|-------------|------|------|")
        for src in cfg.rss_sources:
            t0 = time.time()
            result = http_get(src["url"], timeout=10)
            elapsed = time.time() - t0
            status = "✅ 可用" if result else "❌ 不可达"
            hints = ",".join(src.get("topic_hints", []))
            print(f"| {src['name']} | {hints} | {status} | {elapsed:.1f}s |")


# ============================================
# index / notify / show-rules
# ============================================

def cmd_index(args):
    topics = [args.topic] if args.topic != "all" else TOPICS
    for t in topics:
        print(f"📋 同步索引: {t}")
        _sync_readme(t)
    lines = ["# 📰 简报中心", "", "| 主题 | 目录 |", "|------|------|"]
    for t in TOPICS:
        lines.append(f"| {TOPIC_NAMES[t]}简报 | [{t}/]({t}/) |")
    atomic_write(BASE_DIR / "README.md", "\n".join(lines) + "\n")
    print("  ✅ 已更新顶层 README")


def _sync_readme(topic: str):
    topic_base = BASE_DIR / topic
    readme = topic_base / "README.md"
    if not topic_base.exists():
        print(f"  目录不存在: {topic_base}")
        return
    entries = []
    for year_dir in sorted(topic_base.iterdir(), reverse=True):
        if not year_dir.is_dir() or year_dir.name.startswith("."):
            continue
        for month_dir in sorted(year_dir.iterdir(), reverse=True):
            if not month_dir.is_dir():
                continue
            for md_file in sorted(month_dir.iterdir(), reverse=True):
                if md_file.suffix == ".md" and md_file.name != "README.md":
                    rel = md_file.relative_to(topic_base)
                    entries.append({
                        "date": md_file.stem,
                        "path": str(rel),
                        "is_weekly": "weekly" in md_file.stem.lower(),
                    })
    lines = [
        f"# 📰 {TOPIC_NAMES.get(topic, topic)}简报",
        "",
        f"> 共 {len(entries)} 篇 | 最近更新: {entries[0]['date'] if entries else '无'}",
        "",
        "| 日期 | 类型 | 链接 |",
        "|------|------|------|",
    ]
    for e in entries:
        t = "📅 周报" if e["is_weekly"] else "📰 日报"
        lines.append(f"| {e['date']} | {t} | [{e['date']}]({e['path']}) |")
    atomic_write(readme, "\n".join(lines) + "\n")
    print(f"  ✅ 已更新 {readme} ({len(entries)} 条)")


def cmd_notify(args):
    bark_url = get_bark_url()
    if not bark_url:
        print("❌ 未配置 BARK_URL，跳过推送")
        return

    topics = [args.topic] if args.topic != "all" else TOPICS
    if args.topic == "all":
        all_lines = []
        total_count = 0
        first_url = ""
        for t in topics:
            summary = extract_briefing_summary(t)
            if summary:
                _, body, gh_url = summary
                if not first_url:
                    first_url = gh_url
                icon = TOPIC_ICONS.get(t, "📰")
                name = TOPIC_NAMES.get(t, t)
                fp = briefing_file(t)
                if fp.exists():
                    content = fp.read_text(encoding="utf-8")
                    m = re.search(r"最终收录：(\d+) 条", content)
                    if not m:
                        m = re.search(r"评分筛选后收录\s*\|\s*(\d+)\s*条", content)
                    c = int(m.group(1)) if m else count_briefing_items(content)
                    total_count += c
                all_lines.append(f"{icon} {name}")
                all_lines.append(body)
                all_lines.append("")
        if all_lines:
            today = datetime.now().strftime("%m-%d")
            title = f"📰 今日简报 {today}｜共 {total_count} 条"
            body = "\n".join(all_lines).strip()
            push_bark(bark_url, title, body, open_url=first_url)
        else:
            print("⚠️ 今天没有简报文件，跳过推送")
    else:
        summary = extract_briefing_summary(args.topic)
        if summary:
            title, body, gh_url = summary
            push_bark(bark_url, title, body, open_url=gh_url)
        else:
            print(f"⚠️ 今天没有 {args.topic} 简报文件，跳过推送")


def cmd_show_rules(args):
    rules_path = REPO_ROOT / ".kiro" / "steering" / "briefing-rules.md"
    if not rules_path.exists():
        print(f"❌ 未找到规则文件: {rules_path}", file=sys.stderr)
        sys.exit(1)
    print(rules_path.read_text(encoding="utf-8"))


# ============================================
# v1 兼容
# ============================================

def cmd_collect(args):
    """[v1 兼容] 单主题采集"""
    cfg = load_config()
    print(f"📡 [v1] 单主题采集: {args.topic}")
    sources = [s for s in cfg.rss_sources if args.topic in s.get("topic_hints", [])]

    # 临时把 config 的 rss_sources 替换为子集，复用 run_ingest
    original = cfg.rss_sources
    try:
        cfg.rss_sources = sources
        items, _, _ = run_ingest(cfg)
    finally:
        cfg.rss_sources = original

    for it in items:
        it.pop("source_topic_hints", None)
    output = {
        "topic": args.topic,
        "collected_at": now_str(),
        "total": len(items),
        "items": items,
    }
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(
            json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"💾 已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_dedup(args):
    """[v1 兼容] 旧 dedup 接口"""
    from .dedup import title_in
    from .storage import extract_titles_from_md, extract_urls_from_md, url_hash

    if args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        data = json.load(sys.stdin)
    items = data.get("items", [])
    print(f"🔍 [v1 兼容] 去重: {len(items)} 条输入 (主题: {args.topic})")

    published = load_published_index()["items"]
    other_titles = []
    other_urls = set()
    for ot in TOPICS:
        if ot == args.topic:
            continue
        f = briefing_file(ot)
        other_titles.extend(extract_titles_from_md(f))
        other_urls |= extract_urls_from_md(f)

    kept, removed, seen_titles = [], [], []
    for item in items:
        uh = url_hash(item.get("url", ""))
        reason = None
        if uh in published:
            reason = f"已在 {published[uh].get('date', '?')} 简报中发布"
        elif item.get("url") in other_urls:
            reason = "今日其他主题已收录（URL）"
        elif title_in(item.get("title", ""), other_titles, 0.5):
            reason = "今日其他主题已收录（标题相似）"
        elif title_in(item.get("title", ""), seen_titles, 0.6):
            reason = "批次内标题相似"
        if reason:
            item["dedup_reason"] = reason
            removed.append(item)
        else:
            kept.append(item)
            seen_titles.append(item.get("title", ""))

    print(f"  ✅ 保留: {len(kept)} 条")
    print(f"  ❌ 去重: {len(removed)} 条")
    output = {
        "topic": args.topic,
        "deduped_at": now_str(),
        "kept": len(kept),
        "removed": len(removed),
        "items": kept,
        "removed_items": removed,
    }
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(
            json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"💾 已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


# ============================================
# Main
# ============================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="简报工具集 v3 — 管道式采集（含测试/熔断/事务性）")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ingest", help="一次采集全部源")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("classify", help="规则打标 + 评分（可选 LLM）")
    p.set_defaults(func=cmd_classify)

    p = sub.add_parser("candidates", help="按主题分流候选集")
    p.add_argument("--topic", default="all", choices=TOPICS + ["all"])
    p.add_argument("--min-score", type=int, default=12)
    p.add_argument("--require-main-topic", action=argparse.BooleanOptionalAction, default=None,
                   help="只保留 main_topic 等于本主题的条目")
    p.add_argument("--top-n", type=int, default=None,
                   help="按 score 降序最多保留 N 条（0=不截断）。"
                        "未传时按 config.candidates_top_n 的 per-topic 配置取值")
    p.set_defaults(func=cmd_candidates)

    p = sub.add_parser("register", help="把已写入简报的 URL 登记到 published-index")
    p.add_argument("--topic", default="all", choices=TOPICS + ["all"])
    p.add_argument("--date", help="YYYY-MM-DD，默认今天")
    p.set_defaults(func=cmd_register)

    p = sub.add_parser("rebuild-index", help="从历史 md 文件重建 published-index")
    p.add_argument("--days", type=int, default=60)
    p.set_defaults(func=cmd_rebuild_index)

    p = sub.add_parser("doctor", help="检查 published-index 与 md 文件一致性")
    p.add_argument("--fix", action="store_true", help="对 missing/hash_drift 自动 register 修复")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("validate", help="校验简报 md 是否是有效完成状态")
    p.add_argument("path", help="简报 md 路径")
    p.add_argument("--lenient", action="store_true",
                   help="宽松模式，只查 H1 + 外链（用于历史归档兼容）")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("compare-skeleton", help="对比简报章节骨架与金标准 fixture")
    p.add_argument("--topic", required=True, choices=TOPICS)
    p.add_argument("path", help="简报 md 路径")
    p.set_defaults(func=cmd_compare_skeleton)

    p = sub.add_parser("render", help="把 BriefingDoc JSON 渲染为 md（推荐流程）")
    p.add_argument("--json", required=True, help="结构化简报 JSON 路径")
    p.add_argument("--out", help="输出 md 路径，默认按 topic+date 自动定")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("cleanup", help="清理旧 run 目录")
    p.add_argument("--days", type=int, default=None, help="默认读 config.run_retention_days")
    p.set_defaults(func=cmd_cleanup)

    p = sub.add_parser("run-all", help="一键跑 ingest → classify → candidates → cleanup")
    p.set_defaults(func=cmd_run_all)

    p = sub.add_parser("health", help="查看源健康状态 / 熔断情况")
    p.set_defaults(func=cmd_health)

    p = sub.add_parser("health-reset", help="重置某个源的健康计数")
    p.add_argument("name", help="源名称")
    p.set_defaults(func=cmd_health_reset)

    p = sub.add_parser("curate-status", help="今日 curate 进度与候选集路径")
    p.add_argument("--date", help="YYYY-MM-DD，默认今天")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_curate_status)

    p = sub.add_parser("finalize", help="curate 后统一 register + index + notify")
    p.add_argument("--topic", default="all", choices=TOPICS + ["all"])
    p.add_argument("--date", help="YYYY-MM-DD，默认今天")
    p.add_argument("--skip-notify", action="store_true", help="不推 Bark")
    p.set_defaults(func=cmd_finalize)

    # v1 兼容
    p = sub.add_parser("collect", help="[v1] 单主题采集")
    p.add_argument("--topic", required=True, choices=TOPICS)
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_collect)

    p = sub.add_parser("dedup", help="[v1 兼容] 对采集结果去重")
    p.add_argument("--topic", required=True, choices=TOPICS)
    p.add_argument("--input", "-i")
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_dedup)

    # 通用
    p = sub.add_parser("status", help="简报采集状态面板")
    p.add_argument("--json", action="store_true")
    p.add_argument("--check-sources", action="store_true")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("index", help="同步 README 索引")
    p.add_argument("--topic", default="all", choices=TOPICS + ["all"])
    p.set_defaults(func=cmd_index)

    p = sub.add_parser("notify", help="推送简报摘要到 Bark")
    p.add_argument("--topic", default="all", choices=TOPICS + ["all"])
    p.set_defaults(func=cmd_notify)

    p = sub.add_parser("show-rules", help="输出 briefing-rules.md")
    p.set_defaults(func=cmd_show_rules)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
