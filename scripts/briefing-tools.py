#!/usr/bin/env python3
"""
简报工具集 — 为 Kiro hooks 提供确定性的采集、去重、状态查询、推送能力。

子命令:
  collect   多源采集原始素材，输出 JSON
  dedup     对采集结果去重（URL hash + 标题相似度 + 跨简报）
  status    输出简报采集状态面板
  index     同步 README 索引
  notify    推送简报摘要到 Bark（iOS 推送通知）

设计原则:
  - 纯标准库，零外部依赖
  - 确定性操作（采集、去重、文件管理、推送）由脚本完成
  - 智能判断（评分、摘要、趋势）留给 Kiro agent

使用方式:
  python3 scripts/briefing-tools.py collect --topic ai-agent
  python3 scripts/briefing-tools.py dedup --input raw.json --topic ai-agent
  python3 scripts/briefing-tools.py status
  python3 scripts/briefing-tools.py index --topic ai-agent
  python3 scripts/briefing-tools.py notify --topic all
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

# ============================================
# 配置
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent / "learning-notes" / "briefings"
INDEX_FILE = BASE_DIR / ".dedup-index.json"

# RSS 源配置（按主题分组，timeout 字段可选，覆盖默认 15 秒）
RSS_SOURCES = {
    "ai-agent": [
        {"name": "LangChain Blog", "url": "https://blog.langchain.com/rss.xml"},
        {"name": "Anthropic Research", "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml", "timeout": 30},
        {"name": "Anthropic News", "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml", "timeout": 30},
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
        {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/"},
        {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml"},
        {"name": "Wired AI", "url": "https://www.wired.com/feed/tag/ai/latest/rss"},
        {"name": "Hacker News AI", "url": "https://hnrss.org/newest?q=AI+agent+OR+MCP+OR+LLM&points=30"},
        {"name": "Hacker News AI 关键词", "url": "https://hnrss.org/newest?q=LangGraph+OR+CrewAI+OR+Claude+OR+RAG+OR+function+calling+OR+context+engineering&points=20"},
        {"name": "arXiv AI", "url": "https://rss.arxiv.org/rss/cs.AI"},
    ],
    "china-tech": [
        {"name": "36氪", "url": "https://36kr.com/feed"},
        {"name": "InfoQ CN", "url": "https://www.infoq.cn/feed"},
        {"name": "极客公园", "url": "https://www.geekpark.net/rss"},
        {"name": "量子位", "url": "https://www.qbitai.com/feed"},
        {"name": "开源中国", "url": "https://www.oschina.net/news/rss"},
        {"name": "少数派", "url": "https://sspai.com/feed"},
        {"name": "Hacker News 中国科技", "url": "https://hnrss.org/newest?q=DeepSeek+OR+Qwen+OR+Baidu+AI+OR+China+AI&points=10"},
    ],
    "global-tech": [
        {"name": "Hacker News Top", "url": "https://hnrss.org/frontpage?count=30"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
        {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
        {"name": "GitHub Blog", "url": "https://github.blog/feed/"},
        {"name": "Product Hunt", "url": "https://www.producthunt.com/feed"},
        {"name": "AWS Blog", "url": "https://aws.amazon.com/blogs/aws/feed/"},
        {"name": "Cloudflare Blog", "url": "https://blog.cloudflare.com/rss/"},
        {"name": "Kubernetes Blog", "url": "https://kubernetes.io/feed.xml"},
        {"name": "Hacker News 开发者", "url": "https://hnrss.org/newest?q=Rust+OR+TypeScript+OR+Kubernetes+OR+AWS+OR+security+vulnerability&points=20"},
    ],
}

# 条目时效过滤：只保留最近 N 小时内发布的条目（0 表示不过滤）
FRESHNESS_HOURS = 48


# ============================================
# 工具函数
# ============================================

def url_hash(url: str) -> str:
    """URL 的短 hash，用于去重索引"""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def title_similarity(a: str, b: str) -> float:
    """基于词集合的 Jaccard 相似度"""
    clean_fn = lambda s: set(re.sub(r"[^\w\s]", "", s.lower()).split())
    sa, sb = clean_fn(a), clean_fn(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def topic_dir(topic: str) -> Path:
    """获取主题的当日输出目录"""
    now = datetime.now()
    return BASE_DIR / topic / str(now.year) / f"{now.month:02d}"


def http_get(url: str, timeout: int = 10, retries: int = 1) -> str | None:
    """标准库 HTTP GET，带错误处理和自动重试"""
    import time as _time
    for attempt in range(1 + retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "BriefingTools/1.0 (Walter's Knowledge Base)"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < retries:
                _time.sleep(3)
                continue
            log_error(f"HTTP GET 失败: {url} — {e}")
            return None


def log_error(msg: str):
    """追加错误到 .errors.log"""
    log_file = BASE_DIR / ".errors.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{now_str()}] {msg}\n")
    print(f"  ⚠️  {msg}", file=sys.stderr)


# ============================================
# 去重索引管理
# ============================================

def load_index() -> dict:
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"items": {}, "updated": ""}


def save_index(index: dict):
    index["updated"] = now_str()
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def cleanup_index(index: dict, days: int = 30) -> dict:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    index["items"] = {
        k: v for k, v in index["items"].items()
        if v.get("date", "") >= cutoff
    }
    return index


# ============================================
# RSS 解析（纯标准库）
# ============================================

def parse_rss(xml_text: str, source_name: str) -> list[dict]:
    """用标准库解析 RSS/Atom feed"""
    items = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        log_error(f"RSS 解析失败 ({source_name}): {e}")
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # RSS 2.0
    for item in root.iter("item"):
        title = _text(item, "title") or ""
        link = _text(item, "link") or ""
        pub_date = _text(item, "pubDate") or ""
        description = _text(item, "description") or ""
        if title and link:
            items.append({
                "title": title.strip(),
                "url": link.strip(),
                "published": pub_date.strip(),
                "description": _clean_html(description)[:500],
                "source": source_name,
            })

    # Atom
    if not items:
        for entry in root.iter(f"{{{ns['atom']}}}entry"):
            title = _text(entry, f"{{{ns['atom']}}}title") or ""
            link_el = entry.find(f"{{{ns['atom']}}}link[@rel='alternate']")
            if link_el is None:
                link_el = entry.find(f"{{{ns['atom']}}}link")
            link = link_el.get("href", "") if link_el is not None else ""
            pub_date = (
                _text(entry, f"{{{ns['atom']}}}published")
                or _text(entry, f"{{{ns['atom']}}}updated")
                or ""
            )
            summary = _text(entry, f"{{{ns['atom']}}}summary") or ""
            if title and link:
                items.append({
                    "title": title.strip(),
                    "url": link.strip(),
                    "published": pub_date.strip(),
                    "description": _clean_html(summary)[:500],
                    "source": source_name,
                })

    return items


def _text(el, tag, ns=None):
    child = el.find(tag, ns) if ns else el.find(tag)
    return child.text if child is not None and child.text else None


def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def _parse_pub_date(date_str: str) -> datetime | None:
    """尝试解析 RSS/Atom 中常见的日期格式"""
    if not date_str:
        return None
    # 常见格式列表
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",      # RFC 822: Thu, 01 May 2026 16:08:53 +0000
        "%a, %d %b %Y %H:%M:%S %Z",      # RFC 822 with timezone name
        "%Y-%m-%dT%H:%M:%S%z",            # ISO 8601: 2026-05-01T18:01:53-04:00
        "%Y-%m-%dT%H:%M:%SZ",             # ISO 8601 UTC
        "%Y-%m-%d %H:%M:%S  %z",          # 36氪格式: 2026-05-02 17:37:20  +0800
        "%Y-%m-%d %H:%M:%S %z",           # 标准: 2026-05-02 17:37:20 +0800
        "%a, %d %b %Y %H:%M:%S GMT",      # OpenAI: Thu, 30 Apr 2026 20:25:12 GMT
        "%Y-%m-%dT%H:%M:%S.%f%z",         # 带毫秒的 ISO 8601
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def _filter_by_freshness(items: list[dict], hours: int) -> list[dict]:
    """按发布时间过滤条目，只保留最近 N 小时内的。无法解析日期的条目保留（宁可多不可漏）。"""
    if hours <= 0:
        return items
    now = datetime.now()
    cutoff_naive = now - timedelta(hours=hours)
    try:
        cutoff_aware = now.astimezone() - timedelta(hours=hours)
    except Exception:
        cutoff_aware = None
    result = []
    for item in items:
        pub_dt = _parse_pub_date(item.get("published", ""))
        if pub_dt is None:
            # 无法解析日期，保留
            result.append(item)
        else:
            try:
                # 统一比较：如果 pub_dt 有时区信息用 aware 比较，否则用 naive
                if pub_dt.tzinfo is not None and cutoff_aware is not None:
                    if pub_dt >= cutoff_aware:
                        result.append(item)
                else:
                    # naive 比较
                    pub_naive = pub_dt.replace(tzinfo=None)
                    if pub_naive >= cutoff_naive:
                        result.append(item)
            except Exception:
                # 比较失败，保留
                result.append(item)
    return result


# ============================================
# 采集主入口（并发）
# ============================================

def _fetch_one_source(src: dict) -> tuple[str, list[dict], float, bool]:
    """采集单个 RSS 源，返回 (源名称, 条目列表, 耗时, 是否成功)"""
    import time as _time
    name = src["name"]
    timeout = src.get("timeout", 15)
    t0 = _time.time()
    xml_text = http_get(src["url"], timeout=timeout)
    elapsed = _time.time() - t0
    if xml_text:
        items = parse_rss(xml_text, name)
        return name, items, elapsed, True
    return name, [], elapsed, False


def collect_topic(topic: str) -> list[dict]:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time as _time

    sources = RSS_SOURCES.get(topic, [])
    all_items = []
    results = []

    # 并发采集所有 RSS 源
    t_start = _time.time()
    with ThreadPoolExecutor(max_workers=min(len(sources), 8)) as pool:
        futures = {pool.submit(_fetch_one_source, src): src for src in sources}
        for future in as_completed(futures):
            name, items, elapsed, ok = future.result()
            results.append((name, items, elapsed, ok))

    # 按配置顺序输出结果（方便阅读）
    source_order = {src["name"]: i for i, src in enumerate(sources)}
    results.sort(key=lambda r: source_order.get(r[0], 999))

    for name, items, elapsed, ok in results:
        if ok:
            print(f"  📡 {name}: {len(items)} 条 ({elapsed:.1f}s)")
            all_items.extend(items)
        else:
            print(f"  ⚠️  {name}: 失败 ({elapsed:.1f}s)")

    total_elapsed = _time.time() - t_start

    # 按时效过滤
    before = len(all_items)
    all_items = _filter_by_freshness(all_items, FRESHNESS_HOURS)
    filtered = before - len(all_items)
    if filtered > 0:
        print(f"  🕐 时效过滤: {filtered} 条超过 {FRESHNESS_HOURS}h 已排除")

    print(f"  ⏱  总耗时: {total_elapsed:.1f}s（并发）")
    return all_items


# ============================================
# 去重
# ============================================

def dedup_items(
    items: list[dict], topic: str
) -> tuple[list[dict], list[dict]]:
    """
    去重:
    1. URL hash 精确去重（跨天）
    2. 标题相似度 > 0.6（同一事件不同报道）
    3. 跨简报去重（今天其他主题已收录的）
    """
    index = cleanup_index(load_index())

    # 加载今天其他主题的标题
    other_titles = []
    for ot in ["ai-agent", "china-tech", "global-tech"]:
        if ot == topic:
            continue
        today_file = topic_dir(ot) / f"{today_str()}.md"
        if today_file.exists():
            content = today_file.read_text(encoding="utf-8")
            other_titles.extend(
                re.findall(r"^### (.+)$", content, re.MULTILINE)
            )

    kept, removed, seen_titles = [], [], []

    for item in items:
        uh = url_hash(item["url"])
        reason = None

        # URL 精确去重
        if uh in index["items"]:
            reason = (
                f"URL 重复 (首次: {index['items'][uh].get('date', '?')})"
            )

        # 标题相似度（历史索引）
        if not reason:
            for entry in index["items"].values():
                if title_similarity(item["title"], entry.get("title", "")) > 0.6:
                    reason = f"标题相似: {entry['title'][:40]}..."
                    break

        # 批次内去重
        if not reason:
            for st in seen_titles:
                if title_similarity(item["title"], st) > 0.6:
                    reason = f"批次内重复: {st[:40]}..."
                    break

        # 跨简报去重
        if not reason:
            for ot in other_titles:
                if title_similarity(item["title"], ot) > 0.5:
                    reason = f"跨简报重复: {ot[:40]}..."
                    break

        if reason:
            item["dedup_reason"] = reason
            removed.append(item)
        else:
            kept.append(item)
            seen_titles.append(item["title"])
            index["items"][uh] = {
                "title": item["title"],
                "source": item.get("source", ""),
                "topic": topic,
                "date": today_str(),
            }

    save_index(index)
    return kept, removed


# ============================================
# 状态面板
# ============================================

def get_status() -> dict:
    today = datetime.now()
    report = {"date": today_str(), "topics": {}}

    for topic in ["ai-agent", "china-tech", "global-tech"]:
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
            match = re.match(r"(\d{4}-\d{2}-\d{2})", f.stem)
            if match:
                dates.append(match.group(1))

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

    if INDEX_FILE.exists():
        idx = load_index()
        report["index_size"] = len(idx.get("items", {}))
        report["index_updated"] = idx.get("updated", "")
    else:
        report["index_size"] = 0
        report["index_updated"] = "未创建"

    return report


def format_status(report: dict) -> str:
    names = {"ai-agent": "AI Agent", "china-tech": "国内科技", "global-tech": "国际科技"}
    lines = [f"## 📊 简报采集状态 — {report['date']}\n"]
    lines.append("| 主题 | 最近采集 | 距今 | 状态 | 本周/本月/总计 |")
    lines.append("|------|----------|------|------|---------------|")
    for topic, info in report["topics"].items():
        n = names.get(topic, topic)
        latest = info["latest"] or "从未采集"
        days = f"{info['days_ago']} 天" if info["days_ago"] is not None else "-"
        counts = f"{info['this_week']}/{info['this_month']}/{info['total']}"
        lines.append(f"| {n} | {latest} | {days} | {info['status']} | {counts} |")
    lines.append(f"\n去重索引: {report['index_size']} 条 (更新于 {report['index_updated']})")
    lines.append("\n### 💡 建议")
    for topic, info in report["topics"].items():
        n = names.get(topic, topic)
        if info["status"] in ("❌", "🆕"):
            lines.append(f"- 🔴 **{n}** 需要采集")
        elif info["status"] == "⚠️":
            lines.append(f"- 🟡 **{n}** 建议今天更新")
    return "\n".join(lines)


# ============================================
# 索引同步
# ============================================

def sync_readme_index(topic: str):
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

    names = {
        "ai-agent": "AI Agent 简报",
        "china-tech": "国内科技简报",
        "global-tech": "国际科技简报",
    }
    lines = [
        f"# 📰 {names.get(topic, topic)}",
        "",
        f"> 共 {len(entries)} 篇 | 最近更新: {entries[0]['date'] if entries else '无'}",
        "",
        "| 日期 | 类型 | 链接 |",
        "|------|------|------|",
    ]
    for e in entries:
        t = "📅 周报" if e["is_weekly"] else "📰 日报"
        lines.append(f"| {e['date']} | {t} | [{e['date']}]({e['path']}) |")

    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✅ 已更新 {readme} ({len(entries)} 条)")


# ============================================
# CLI
# ============================================

def cmd_collect(args):
    print(f"📡 开始采集: {args.topic}")
    items = collect_topic(args.topic)
    print(f"\n📊 采集完成: {len(items)} 条原始素材")
    output = {
        "topic": args.topic,
        "collected_at": now_str(),
        "total": len(items),
        "items": items,
    }
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_dedup(args):
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    items = data.get("items", [])
    print(f"🔍 去重: {len(items)} 条输入 (主题: {args.topic})")
    kept, removed = dedup_items(items, args.topic)
    print(f"  ✅ 保留: {len(kept)} 条")
    print(f"  ❌ 去重: {len(removed)} 条")
    if removed:
        print("\n  去重详情:")
        for item in removed:
            print(f"    - {item['title'][:50]}... → {item.get('dedup_reason', '?')}")
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
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到: {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_status(args):
    report = get_status()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_status(report))

    if args.check_sources:
        print("\n## 🔗 采集源健康检查\n")
        print("| 主题 | 源名称 | 状态 | 耗时 |")
        print("|------|--------|------|------|")
        for topic, sources in RSS_SOURCES.items():
            for src in sources:
                import time as _time
                t0 = _time.time()
                result = http_get(src["url"], timeout=10)
                elapsed = _time.time() - t0
                if result:
                    status = "✅ 可用"
                else:
                    status = "❌ 不可达"
                print(f"| {topic} | {src['name']} | {status} | {elapsed:.1f}s |")


def cmd_index(args):
    topics = (
        [args.topic]
        if args.topic != "all"
        else ["ai-agent", "china-tech", "global-tech"]
    )
    for t in topics:
        print(f"📋 同步索引: {t}")
        sync_readme_index(t)

    # 顶层 README
    names = {
        "ai-agent": "AI Agent 简报",
        "china-tech": "国内科技简报",
        "global-tech": "国际科技简报",
    }
    lines = ["# 📰 简报中心", "", "| 主题 | 目录 |", "|------|------|"]
    for t in ["ai-agent", "china-tech", "global-tech"]:
        lines.append(f"| {names[t]} | [{t}/]({t}/) |")
    (BASE_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✅ 已更新顶层 README")


# ============================================
# Bark 推送
# ============================================

TOPIC_NAMES = {
    "ai-agent": "AI Agent",
    "china-tech": "国内科技",
    "global-tech": "国际科技",
}

TOPIC_ICONS = {
    "ai-agent": "🤖",
    "china-tech": "🇨🇳",
    "global-tech": "🌍",
}

# 博客站点地址，用于生成简报的在线阅读链接
BLOG_SITE_URL = "https://walterhandsome.github.io/portfolio"
GITHUB_REPO = "https://github.com/WalterHandsome/tech-learning-and-projects"
GITHUB_BRANCH = "main"


def briefing_github_url(topic: str, date_str: str | None = None) -> str:
    """生成简报文件对应的博客站点在线阅读链接"""
    ds = date_str or today_str()
    return f"{BLOG_SITE_URL}/briefing.html#{topic}/{ds}"


def get_bark_url() -> str | None:
    """从环境变量获取 Bark 推送地址"""
    url = os.environ.get("BARK_URL", "").strip()
    if not url:
        # 尝试从 Brand Agent 的 .env 读取
        candidates = [
            Path(__file__).resolve().parent.parent.parent / "personal-brand-agent" / ".env",
            Path(__file__).resolve().parent.parent.parent / "Brand Agent" / ".env",
            Path(__file__).resolve().parent.parent / "🤖 Brand Agent" / ".env",
        ]
        for env_path in candidates:
            if env_path.exists():
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("BARK_URL=") and "你的key" not in line:
                        url = line.split("=", 1)[1].strip()
                        break
            if url:
                break
    return url or None


def push_bark(bark_url: str, title: str, body: str, group: str = "AI简报", open_url: str = "") -> bool:
    """通过 Bark 推送通知到 iOS 设备（纯标准库实现）

    Args:
        open_url: 点击通知后跳转的链接（可选）
    """
    url = bark_url.rstrip("/") + "/"
    data = {
        "title": title,
        "body": body,
        "group": group,
        "icon": "https://github.githubassets.com/favicons/favicon.svg",
        "level": "timeSensitive",
    }
    if open_url:
        data["url"] = open_url
    payload = json.dumps(data).encode("utf-8")
    try:
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 200:
                print(f"  ✅ Bark 推送成功：{title}")
                return True
            print(f"  ❌ Bark 推送失败：{result}")
            return False
    except Exception as e:
        print(f"  ❌ Bark 推送异常：{e}")
        return False


def count_briefing_items(content: str) -> int:
    """按简报正文内容统计收录条目数（适配 TLDR 风格简报）

    规则：
    - 统计头条下的 `### ` 标题（排除形如 "### 📌 头条" 这类分组标题）
    - 统计快讯/安全/融资等板块的 `- **` 一级列表条目
    - 统计项目/论文/大模型动态等板块的表格数据行（排除表头与分隔行）
    - 遇到「📈 趋势」或「📊 本期统计」则停止，避免把趋势条目算进去
    """
    lines = content.splitlines()
    count = 0
    in_table = False

    for line in lines:
        stripped = line.strip()

        # 遇到趋势或统计板块即停止
        if re.match(r"^#{1,3}\s*📈", stripped) or re.match(r"^#{1,3}\s*📊", stripped):
            break

        # 其它标题重置表格状态
        if stripped.startswith("#"):
            in_table = False
            # 头条下的 ### 条目计 1，但要排除 emoji 分组标题（如 "### 📌 头条"）
            if re.match(r"^###\s+", stripped):
                title_body = stripped[3:].strip()
                if not re.match(r"^[📌⚡📦🤖🛠🔒💰📜💬🚀🆕🔺🔻]", title_body):
                    count += 1
            continue

        # 表格：表头进入表格态后跳过表头与分隔行，其余行计数
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
                continue  # 表头
            if set(stripped.replace("|", "").strip()) <= set("-: "):
                continue  # 分隔行
            count += 1
            continue
        else:
            in_table = False

        # 一级列表条目（快讯、安全动态等）
        if re.match(r"^-\s+\*\*", stripped):
            count += 1

    return count


def extract_briefing_summary(topic: str) -> tuple[str, str, str] | None:
    """从当天简报文件提取推送摘要，返回 (title, body, github_url) 或 None

    设计原则（参考 iOS 推送最佳实践）：
    - 标题 ≤ 40 字符，确保锁屏不截断
    - 正文前 2 行（约 80 字符）在锁屏预览可见，用于抓眼球
    - 展开后显示完整 5 条要闻 + 统计摘要
    - 每条标题 ≤ 80 字符，保留足够语义
    - 点击通知跳转 GitHub 查看完整简报
    """
    filepath = topic_dir(topic) / f"{today_str()}.md"
    if not filepath.exists():
        return None

    content = filepath.read_text(encoding="utf-8")
    icon = TOPIC_ICONS.get(topic, "📰")
    name = TOPIC_NAMES.get(topic, topic)
    today = datetime.now().strftime("%m-%d")

    # 提取要闻标题（### 开头的行）
    headlines = re.findall(r"^### \d+\. (.+)$", content, re.MULTILINE)
    if not headlines:
        headlines = re.findall(r"^### (.+)$", content, re.MULTILINE)

    # 提取收录数：优先读显式写明的数字（旧格式），否则按实际条目统计（新 TLDR 格式）
    count_match = re.search(r"最终收录：(\d+) 条", content)
    if not count_match:
        count_match = re.search(r"评分筛选后收录\s*\|\s*(\d+)\s*条", content)
    if count_match:
        count = count_match.group(1)
    else:
        count = str(count_briefing_items(content))

    # 提取来源数
    source_match = re.search(r"采集源：(\d+) 个", content)
    source_count = source_match.group(1) if source_match else ""

    title = f"{icon} {name} {today}｜{count} 条收录"

    lines = []
    # 展示前 5 条要闻，每条最多 80 字符
    for i, h in enumerate(headlines[:5], 1):
        short = h[:80] + ("…" if len(h) > 80 else "")
        lines.append(f"{i}. {short}")

    if not lines:
        lines.append("详见完整简报")

    # 底部统计行
    total = len(headlines)
    if total > 5:
        lines.append(f"\n…共 {total} 条要闻")
    if source_count:
        lines.append(f"📡 {source_count} 个源采集")
    lines.append("👆 点击查看完整简报")

    body = "\n".join(lines)
    gh_url = briefing_github_url(topic)
    return title, body, gh_url


def cmd_notify(args):
    """推送简报摘要到 Bark"""
    bark_url = get_bark_url()
    if not bark_url:
        print("❌ 未配置 BARK_URL，跳过推送")
        print("   设置方式：export BARK_URL=https://api.day.app/你的key")
        return

    topics = (
        [args.topic]
        if args.topic != "all"
        else ["ai-agent", "china-tech", "global-tech"]
    )

    if args.topic == "all":
        # 合并推送：三个简报合成一条通知
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
                # 提取收录数
                filepath = topic_dir(t) / f"{today_str()}.md"
                if filepath.exists():
                    content = filepath.read_text(encoding="utf-8")
                    m = re.search(r"最终收录：(\d+) 条", content)
                    if not m:
                        m = re.search(r"评分筛选后收录\s*\|\s*(\d+)\s*条", content)
                    c = int(m.group(1)) if m else 0
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
        # 单主题推送
        summary = extract_briefing_summary(args.topic)
        if summary:
            title, body, gh_url = summary
            push_bark(bark_url, title, body, open_url=gh_url)
        else:
            print(f"⚠️ 今天没有 {args.topic} 简报文件，跳过推送")


def main():
    parser = argparse.ArgumentParser(description="简报工具集")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("collect", help="多源采集原始素材")
    p.add_argument("--topic", required=True, choices=["ai-agent", "china-tech", "global-tech"])
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_collect)

    p = sub.add_parser("dedup", help="对采集结果去重")
    p.add_argument("--topic", required=True, choices=["ai-agent", "china-tech", "global-tech"])
    p.add_argument("--input", "-i")
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_dedup)

    p = sub.add_parser("status", help="简报采集状态面板")
    p.add_argument("--json", action="store_true")
    p.add_argument("--check-sources", action="store_true", help="检查所有 RSS 源是否可达")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("index", help="同步 README 索引")
    p.add_argument("--topic", default="all", choices=["ai-agent", "china-tech", "global-tech", "all"])
    p.set_defaults(func=cmd_index)

    p = sub.add_parser("notify", help="推送简报摘要到 Bark")
    p.add_argument("--topic", default="all", choices=["ai-agent", "china-tech", "global-tech", "all"])
    p.set_defaults(func=cmd_notify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
