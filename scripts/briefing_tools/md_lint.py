"""简报 md 格式校验（结构级）

设计原则：
- 只查结构，不查内容质量
- 每条规则独立、可断言、有清晰错误信息
- 返回 (ok, reasons[]) ：失败时给出全部问题，方便一次修干净

校验范围：
- H1 / 元信息行
- 章节存在性（头条 / 快讯 必备，其他可选）
- 头条结构（数量 1-2、每条后有 `---` 分隔）
- 快讯条数（≥ 3）
- 表格列数一致
- 至少 1 个外链
"""

from __future__ import annotations

import re
from pathlib import Path

# 必需章节（H2 标题里出现这些关键字之一即视为存在）
SECTION_HEADLINES = ["头条", "要闻", "Headlines"]
SECTION_BRIEFS = ["快讯", "速读", "Briefs"]

# 头条数量上下限
HEADLINE_MIN = 1
HEADLINE_MAX = 2

# 快讯条数下限
BRIEF_MIN = 3

# 正则
RE_H1 = re.compile(r"^# .+$", re.MULTILINE)
RE_H2 = re.compile(r"^## (.+)$", re.MULTILINE)
RE_H3 = re.compile(r"^### (.+)$", re.MULTILINE)
RE_HR = re.compile(r"^---\s*$", re.MULTILINE)
RE_LINK = re.compile(r"\]\((https?://[^\s)]+)\)")
# bullet list item: 行首 `- ` 或 `* `
RE_BULLET = re.compile(r"^\s*[-*] ", re.MULTILINE)
# table row: 行首 `|` 且至少两个 `|`
RE_TABLE_ROW = re.compile(r"^\|.+\|$", re.MULTILINE)


def _section_present(content: str, keywords: list[str]) -> bool:
    """章节是否存在：H2 行里命中任一关键字"""
    for h2 in RE_H2.findall(content):
        for kw in keywords:
            if kw in h2:
                return True
    return False


def _slice_section(content: str, keywords: list[str]) -> str | None:
    """取出章节正文（从匹配的 H2 到下一个 H2 之间）"""
    lines = content.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = re.match(r"^## (.+)$", line)
        if m and any(kw in m.group(1) for kw in keywords):
            start = i + 1
            break
    if start is None:
        return None
    # 找下一个 H2
    end = len(lines)
    for j in range(start, len(lines)):
        if re.match(r"^## ", lines[j]):
            end = j
            break
    return "\n".join(lines[start:end])


def _count_headlines(headline_section: str) -> tuple[int, list[int]]:
    """数头条 H3 数量，返回 (count, line_indices)（行号 0-indexed，相对 section）"""
    indices = []
    for i, line in enumerate(headline_section.splitlines()):
        if line.startswith("### "):
            indices.append(i)
    return len(indices), indices


def _check_headline_separators(headline_section: str) -> list[str]:
    """检查每个头条 H3 之后到下一个 H3（或章节结束）之间是否有 `---`"""
    lines = headline_section.splitlines()
    h3_lines = [i for i, line in enumerate(lines) if line.startswith("### ")]
    if not h3_lines:
        return []
    errors = []
    boundaries = h3_lines + [len(lines)]
    for i in range(len(h3_lines)):
        start = boundaries[i]
        end = boundaries[i + 1]
        block = lines[start:end]
        # 是否包含 `---`（仅独占一行的水平线）
        has_hr = any(re.match(r"^---\s*$", line) for line in block[1:])
        if not has_hr:
            title = lines[h3_lines[i]][4:].strip()
            errors.append(f"headline #{i + 1} ({title!r}) 缺少 `---` 分隔线")
    return errors


def _count_briefs(brief_section: str) -> int:
    """数快讯 bullet 数量（仅顶层 bullet，不含表格）"""
    count = 0
    for line in brief_section.splitlines():
        if RE_BULLET.match(line) and not line.lstrip().startswith("|"):
            count += 1
    return count


def _check_table_columns(content: str) -> list[str]:
    """检查每个表格的列数一致性（rough check：每行 `|` 数量相同）"""
    errors = []
    lines = content.splitlines()
    in_table = False
    table_start = -1
    expected_cols = -1
    for i, line in enumerate(lines):
        if RE_TABLE_ROW.match(line):
            cols = line.count("|")
            if not in_table:
                in_table = True
                table_start = i + 1  # 1-indexed
                expected_cols = cols
            elif cols != expected_cols:
                errors.append(
                    f"table at line {table_start}: column count mismatch (expected {expected_cols}, got {cols} at line {i + 1})"
                )
        else:
            in_table = False
            expected_cols = -1
    return errors


def lint_briefing(path: Path, strict: bool = True) -> tuple[bool, list[str]]:
    """完整校验，返回 (ok, errors)。ok=True 时 errors 为空。

    Args:
        path: 简报 md 路径
        strict: 严格模式（默认）。False 时只查 H1 + 外链（用于历史归档）。
    """
    if not path.exists():
        return False, ["file not found"]
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        return False, ["empty file"]

    errors: list[str] = []

    # H1（始终查）
    if not content.lstrip().startswith("# "):
        errors.append("missing H1 header (第一行必须是 `# 标题`)")

    # 至少一个外链（始终查）
    if not RE_LINK.search(content):
        errors.append("no external links")

    # 严格模式才查结构
    if strict:
        # 必需章节
        if not _section_present(content, SECTION_HEADLINES):
            errors.append("missing section: 头条/要闻")
        if not _section_present(content, SECTION_BRIEFS):
            errors.append("missing section: 快讯/速读")

        # 头条结构
        head_section = _slice_section(content, SECTION_HEADLINES)
        if head_section is not None:
            n, _ = _count_headlines(head_section)
            if n < HEADLINE_MIN:
                errors.append(f"headlines too few: got {n}, need ≥ {HEADLINE_MIN}")
            elif n > HEADLINE_MAX:
                errors.append(f"headlines too many: got {n}, max {HEADLINE_MAX}")
            # 分隔符检查
            errors.extend(_check_headline_separators(head_section))

        # 快讯条数
        brief_section = _slice_section(content, SECTION_BRIEFS)
        if brief_section is not None:
            n = _count_briefs(brief_section)
            if n < BRIEF_MIN:
                errors.append(f"briefs too few: got {n}, need ≥ {BRIEF_MIN}")

        # 表格列数
        errors.extend(_check_table_columns(content))

    return (len(errors) == 0), errors
