"""published-index 和 run 目录管理，含原子写入"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

from .config import BASE_DIR, PUBLISHED_INDEX, RUNS_DIR, TOPICS
from .http import normalize_url


def url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def topic_dir(topic: str, date_str: str | None = None) -> Path:
    dt = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
    return BASE_DIR / topic / str(dt.year) / f"{dt.month:02d}"


def briefing_file(topic: str, date_str: str | None = None) -> Path:
    ds = date_str or today_str()
    return topic_dir(topic, ds) / f"{ds}.md"


def run_dir(date_str: str | None = None) -> Path:
    ds = date_str or today_str()
    return RUNS_DIR / ds


# ============================================
# 原子写入
# ============================================

def atomic_write(path: Path, text: str, encoding: str = "utf-8") -> None:
    """tmp → fsync → rename，保证读侧永远不看到半写入状态"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding=encoding) as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def atomic_write_json(path: Path, obj, indent: int | None = 2) -> None:
    atomic_write(path, json.dumps(obj, ensure_ascii=False, indent=indent))


def atomic_write_jsonl(path: Path, items: list[dict]) -> None:
    lines = [json.dumps(it, ensure_ascii=False) for it in items]
    atomic_write(path, "\n".join(lines) + ("\n" if lines else ""))


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                # 跳过损坏行（不应该发生，但防御性）
                continue
    return items


# ============================================
# Published Index（已写入简报的 URL）
# ============================================

def load_published_index() -> dict:
    if PUBLISHED_INDEX.exists():
        try:
            return json.loads(PUBLISHED_INDEX.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"items": {}, "updated": ""}
    return {"items": {}, "updated": ""}


def save_published_index(index: dict) -> None:
    index["updated"] = now_str()
    atomic_write_json(PUBLISHED_INDEX, index)


def cleanup_published_index(index: dict, days: int) -> dict:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    index["items"] = {k: v for k, v in index["items"].items() if v.get("date", "") >= cutoff}
    return index


# ============================================
# md 解析工具（提取 URL / 标题 / 校验）
# ============================================

_URL_RE = re.compile(r"\]\((https?://[^\s)]+)\)")
_H3_RE = re.compile(r"^### (.+)$", re.MULTILINE)
_TABLE_RE = re.compile(r"^\|\s*([^|]+)\s*\|[^|]+\|[^|]+\|$", re.MULTILINE)


def extract_urls_from_md(path: Path) -> set[str]:
    if not path.exists():
        return set()
    content = path.read_text(encoding="utf-8")
    return {normalize_url(m) for m in _URL_RE.findall(content)}


def extract_titles_from_md(path: Path) -> list[str]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    titles = list(_H3_RE.findall(content))
    for t in _TABLE_RE.findall(content):
        t = t.strip()
        if t and not set(t) <= set("-: "):
            titles.append(t)
    return titles


def validate_briefing_md(path: Path, strict: bool = True) -> tuple[bool, str]:
    """简报 md 校验。返回 (ok, reason)。

    内部委托给 md_lint.lint_briefing，做完整结构级检查：
    - 文件存在 + 非空 + H1 / 外链
    - strict=True（默认）：头条章节（1-2 条 + 每条之间 ---）/ 快讯章节（≥ 3 条）/ 表格列数一致
    - strict=False：只查 H1 + 外链（用于历史归档兼容）

    多个错误时 reason 是分号分隔的拼接字符串，便于一次修复。
    """
    from .md_lint import lint_briefing
    ok, errs = lint_briefing(path, strict=strict)
    if ok:
        return True, "ok"
    return False, "; ".join(errs)


# ============================================
# URL 复用检查
# ============================================

def check_url_reuse(topic: str, date_str: str, path: Path | None = None) -> list[dict]:
    """检查一份简报 md 里的 URL 有没有被收录过。

    candidates 阶段的 published_before / not_main_topic 两层过滤只作用于候选集，
    而 curate 时 web search 补充进来的链接从未进过候选集，因此完全绕过去重。
    这个函数补上那条路径，在 render / finalize 阶段查。

    只报告不阻断：跨天引用同一篇原文有时是合理的（原文有更新、换视角展开），
    硬拦会逼着去找次优来源。判断留给人或 curate agent。

    返回 [{"url", "kind", "where"}]，kind 为 cross_day 或 cross_topic。
    """
    p = path or briefing_file(topic, date_str)
    urls = extract_urls_from_md(p)
    if not urls:
        return []

    findings: list[dict] = []
    published = load_published_index()["items"]
    for u in sorted(urls):
        rec = published.get(url_hash(u))
        # 同日期的记录跳过：可能是自己上次 register 留下的，也可能是今日其他主题
        # 已登记（此时 index 里只留一条），后者由下面的跨主题检查负责，不重复报
        if rec and rec.get("date") != date_str:
            findings.append({
                "url": u,
                "kind": "cross_day",
                "where": f"{rec.get('topic', '?')} {rec.get('date', '?')}",
            })

    # 今日其他主题。并行 curate 时先 render 的看不到后 render 的，
    # 所以这层在 render 阶段只能部分命中，finalize 阶段才是完整的。
    for other in TOPICS:
        if other == topic:
            continue
        other_urls = extract_urls_from_md(briefing_file(other, date_str))
        for u in sorted(urls & other_urls):
            findings.append({"url": u, "kind": "cross_topic", "where": f"{other} {date_str}"})

    return findings


# ============================================
# Register：把 md 里的 URL 登记到 published-index
# ============================================

def register_published(topic: str, date_str: str | None = None, retention_days: int = 60) -> dict:
    ds = date_str or today_str()
    f = briefing_file(topic, ds)
    if not f.exists():
        return {"topic": topic, "date": ds, "registered": 0, "error": "briefing file not found"}

    ok, reason = validate_briefing_md(f)
    if not ok:
        return {"topic": topic, "date": ds, "registered": 0, "error": f"invalid briefing file: {reason}"}

    urls = extract_urls_from_md(f)
    file_hash = hashlib.sha256(f.read_bytes()).hexdigest()[:16]

    index = cleanup_published_index(load_published_index(), retention_days)

    # 幂等性 + hash 漂移检测
    file_hashes = index.setdefault("file_hashes", {})
    key = f"{topic}/{ds}"
    prev_hash = file_hashes.get(key)
    hash_changed = prev_hash is not None and prev_hash != file_hash

    added = 0
    for u in urls:
        if not u:
            continue
        uh = url_hash(u)
        if uh in index["items"]:
            continue
        index["items"][uh] = {"url": u, "title": "", "topic": topic, "date": ds}
        added += 1

    file_hashes[key] = file_hash
    save_published_index(index)

    result = {
        "topic": topic, "date": ds, "registered": added, "total_urls": len(urls),
        "file_hash": file_hash,
    }
    if hash_changed:
        result["warning"] = (
            f"file content changed since last register (prev={prev_hash}, now={file_hash})。"
            f"建议运行 `python3 scripts/briefing-tools.py index --topic {topic}` 同步 README"
        )
    return result


def doctor_check_index_consistency(auto_fix: bool = False, retention_days: int = 60) -> dict:
    """检查 md 与 published-index 的一致性。

    扫描 `learning-notes/_briefings/{topic}/YYYY/MM/*.md`，对比
    `.published-index.json` 的 `file_hashes`，找出三类不一致：

    - missing: md 在文件系统但 file_hashes 没记录（最常见，subagent 中断造成）
    - hash_drift: md 已修改但 file_hashes 还是旧 hash（手动改了 md 但忘了 register）
    - orphan: file_hashes 有记录但 md 文件已不存在（删除了文件）

    auto_fix=True 时对 missing 和 hash_drift 自动跑 register_published 修复，
    orphan 只报告不删（删除是用户决策）。返回各类问题的清单和修复结果。
    """
    issues = {"missing": [], "hash_drift": [], "orphan": [], "fixed": []}

    index = load_published_index()
    file_hashes = index.get("file_hashes", {})

    # 扫文件系统
    md_keys: set[str] = set()
    for topic in TOPICS:
        topic_base = BASE_DIR / topic
        if not topic_base.exists():
            continue
        for md_file in topic_base.rglob("*.md"):
            if md_file.name == "README.md":
                continue
            m = re.match(r"(\d{4}-\d{2}-\d{2})", md_file.stem)
            if not m:
                continue  # 跳过 weekly 等非日报文件
            date_str = m.group(1)
            key = f"{topic}/{date_str}"
            md_keys.add(key)

            actual_hash = hashlib.sha256(md_file.read_bytes()).hexdigest()[:16]
            recorded = file_hashes.get(key)

            if recorded is None:
                issues["missing"].append({"key": key, "topic": topic, "date": date_str, "actual": actual_hash})
            elif recorded != actual_hash:
                issues["hash_drift"].append({
                    "key": key, "topic": topic, "date": date_str,
                    "recorded": recorded, "actual": actual_hash,
                })

    # 反向找孤儿：file_hashes 有但 md 没了
    for key in file_hashes:
        if key not in md_keys:
            try:
                topic, date_str = key.split("/", 1)
            except ValueError:
                continue
            issues["orphan"].append({"key": key, "topic": topic, "date": date_str})

    if auto_fix:
        for problem in issues["missing"] + issues["hash_drift"]:
            r = register_published(problem["topic"], problem["date"], retention_days=retention_days)
            if "error" not in r:
                issues["fixed"].append({
                    "key": problem["key"],
                    "registered": r.get("registered", 0),
                    "total_urls": r.get("total_urls", 0),
                })
            elif "invalid briefing file" in r.get("error", ""):
                # strict 校验失败的旧格式 md：lenient 通过就只补 file_hash，不动 items
                f = briefing_file(problem["topic"], problem["date"])
                ok_lenient, _ = validate_briefing_md(f, strict=False)
                if ok_lenient:
                    backfilled = _backfill_file_hash_only(problem["topic"], problem["date"])
                    if backfilled:
                        issues["fixed"].append({
                            "key": problem["key"],
                            "registered": 0,
                            "total_urls": 0,
                            "backfilled_legacy": True,
                        })

    return issues


def _backfill_file_hash_only(topic: str, date_str: str) -> bool:
    """只补 file_hashes，不动 items。

    用于历史 md：URL 已经通过 v1 旧路径登记到 items，但当时 register
    还没引入 file_hashes 字段。strict 校验对历史格式 fail 时调用此函数
    只把当前 hash 写进去，避免 doctor 永远报警。
    """
    f = briefing_file(topic, date_str)
    if not f.exists():
        return False
    file_hash = hashlib.sha256(f.read_bytes()).hexdigest()[:16]
    index = load_published_index()
    file_hashes = index.setdefault("file_hashes", {})
    file_hashes[f"{topic}/{date_str}"] = file_hash
    save_published_index(index)
    return True


def rebuild_published_index(days: int = 60) -> dict:
    """扫描历史 md 重建 index。

    历史文件可能用旧格式（"今日要闻"等），所以走 lenient 校验：只查 H1 + 外链。
    """
    index = {"items": {}, "updated": ""}
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    total_files = 0
    total_urls = 0
    for topic in TOPICS:
        topic_base = BASE_DIR / topic
        if not topic_base.exists():
            continue
        for md_file in topic_base.rglob("*.md"):
            if md_file.name == "README.md":
                continue
            m = re.match(r"(\d{4}-\d{2}-\d{2})", md_file.stem)
            if not m:
                continue
            date_str = m.group(1)
            if date_str < cutoff:
                continue
            ok, _reason = validate_briefing_md(md_file, strict=False)
            if not ok:
                continue
            total_files += 1
            for u in extract_urls_from_md(md_file):
                if not u:
                    continue
                uh = url_hash(u)
                if uh in index["items"]:
                    if date_str < index["items"][uh]["date"]:
                        index["items"][uh]["date"] = date_str
                        index["items"][uh]["topic"] = topic
                    continue
                index["items"][uh] = {"url": u, "title": "", "topic": topic, "date": date_str}
                total_urls += 1
    save_published_index(index)
    return {"files_scanned": total_files, "urls_registered": total_urls}
