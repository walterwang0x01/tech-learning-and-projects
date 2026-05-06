#!/usr/bin/env python3
"""技术笔记文档格式兜底检查（零 LLM）.

事前约束：`doc-maintenance.md` steering 已要求 agent 写 learning-notes/ 下
的 .md 时遵守格式（# 标题开头、> Author: Walter Wang）。

本脚本是事后兜底：在 write 操作前或 fileCreated 后，用纯字符串检查是否
真的按规则写了。发现问题输出 WARNING，不阻断工具调用。

输入来源（KIRO_TOOL_INPUT）：
- preToolUse write: 包含 path 和 content/newStr（即将写入的内容）
- fileCreated:      只包含 path，需要读文件

约定：stdout 静默表示 OK，输出 WARNING: <原因> 表示提醒但仍放行。
"""
from __future__ import annotations

import json
import os
import sys

PROJECT_KEY = "tech-learning-and-projects"
SCOPE_PREFIX = "learning-notes/"
AUTHOR_MARK = "> Author: Walter Wang"
SKIP_BASENAMES = {
    "README.md",
    ".update-log.md",
    ".audit-progress.md",
}


def _resolve_content(data: dict, path: str) -> str | None:
    """优先用 tool_input 里的新内容，fileCreated 场景回退到读文件."""
    for key in ("content", "newStr", "text"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return None


def _should_skip(path: str) -> bool:
    if not path:
        return True
    # 跨项目短路
    if PROJECT_KEY not in os.path.abspath(path):
        return True
    if not path.endswith(".md"):
        return True
    if SCOPE_PREFIX not in path:
        return True
    basename = os.path.basename(path)
    if basename in SKIP_BASENAMES:
        return True
    return False


def main() -> int:
    raw = os.environ.get("KIRO_TOOL_INPUT", "")
    if not raw:
        return 0
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    path = data.get("path") or data.get("targetFile") or ""
    if not isinstance(path, str) or _should_skip(path):
        return 0

    content = _resolve_content(data, path)
    if content is None:
        return 0

    problems: list[str] = []
    stripped = content.lstrip()
    if not stripped.startswith("# "):
        problems.append("缺少一级标题（需以 `# ` 开头）")
    if AUTHOR_MARK not in content:
        problems.append(f"缺少 `{AUTHOR_MARK}` 标记")

    if problems:
        print("WARNING: " + "；".join(problems))
    return 0


if __name__ == "__main__":
    sys.exit(main())
