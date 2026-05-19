"""提取简报章节骨架，用于跨日 / 跟金标准的结构对比

骨架只记录:
- H1 是否存在
- H2 章节名顺序列表
- 每个 H2 下 H3 数量
- 每个 H2 下表格行数

不记录任何文本内容，纯结构。
"""

from __future__ import annotations

import re
from pathlib import Path


RE_H1 = re.compile(r"^# (.+)$", re.MULTILINE)
RE_H2 = re.compile(r"^## (.+)$", re.MULTILINE)


def extract_skeleton(path: Path) -> dict:
    """提取章节骨架。返回:
    {
        "has_h1": bool,
        "sections": [
            {"name": "📌 头条", "h3_count": 2, "table_rows": 0, "bullet_count": 0},
            ...
        ]
    }
    """
    if not path.exists():
        return {"has_h1": False, "sections": []}
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    skeleton: dict = {
        "has_h1": bool(RE_H1.search(content)),
        "sections": [],
    }

    # 找出每个 H2 的起止行
    h2_indices: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        m = re.match(r"^## (.+)$", line)
        if m:
            h2_indices.append((i, m.group(1).strip()))

    for idx, (start, name) in enumerate(h2_indices):
        end = h2_indices[idx + 1][0] if idx + 1 < len(h2_indices) else len(lines)
        block = lines[start + 1:end]
        h3 = sum(1 for line in block if line.startswith("### "))
        # 表格行：以 `|` 开头且至少含两个 `|`
        table_rows = sum(1 for line in block if re.match(r"^\|.+\|$", line))
        # 顶层 bullet（不在表格里）
        bullets = sum(
            1 for line in block
            if re.match(r"^\s*[-*] ", line) and not line.lstrip().startswith("|")
        )
        skeleton["sections"].append({
            "name": name,
            "h3_count": h3,
            "table_rows": table_rows,
            "bullet_count": bullets,
        })

    return skeleton


def section_names(skeleton: dict) -> list[str]:
    """返回章节名顺序列表"""
    return [s["name"] for s in skeleton["sections"]]


def diff_skeleton(actual: dict, golden: dict) -> list[str]:
    """对比两份骨架，返回结构差异列表（不计较具体计数，只看章节存在与顺序）。

    用于「actual 必须包含 golden 的所有 H2 章节，且顺序一致」的弱约束。
    H3/table/bullet 的下限校验交给 md_lint。
    """
    diffs: list[str] = []
    actual_names = section_names(actual)
    golden_names = section_names(golden)

    # 1. golden 的每个章节在 actual 中必须存在
    for gname in golden_names:
        if gname not in actual_names:
            diffs.append(f"missing section: {gname}")

    # 2. 章节顺序：保留出现在 golden 中的子集，子集顺序必须与 golden 一致
    actual_subset = [n for n in actual_names if n in golden_names]
    golden_subset = [n for n in golden_names if n in actual_subset]
    if actual_subset != golden_subset:
        diffs.append(
            f"section order mismatch: actual={actual_subset!r}, expected={golden_subset!r}"
        )

    return diffs
