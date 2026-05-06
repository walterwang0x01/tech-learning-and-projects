#!/usr/bin/env python3
"""技术笔记 Spec 任务完成后的自动验证（零 LLM）.

场景：postTaskExecution 事件触发。事件本身不带具体任务路径，
Kiro 会把 spec 任务的上下文作为 KIRO_TOOL_INPUT 传入。

策略：
1. 先做 PROJECT_KEY 短路：当前工作区不在 tech-learning-and-projects 则直接退出
2. 检查有无未提交变更；无变更则静默退出
3. 按项目类型选执行验证：
   - pyproject.toml 存在 → 尝试 `ruff check`（如已安装）
   - scripts/doc-lint.sh 存在且有 .md 变更 → 运行它
4. 任何问题写到 stdout 作为 WARNING（非阻断）

设计原则：事件频率低但成本固定在 LLM 不划算，改为本地几十毫秒的脚本即可。
需要语义判断时再在 prompt 里手动升级。
"""
from __future__ import annotations

import os
import subprocess  # noqa: S404
import sys

PROJECT_KEY = "tech-learning-and-projects"


def _in_project() -> bool:
    cwd = os.path.abspath(os.getcwd())
    return PROJECT_KEY in cwd


def _changed_files() -> list[str]:
    """返回未暂存 + 已暂存的变更文件相对路径列表."""
    try:
        out = subprocess.run(  # noqa: S603
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if out.returncode != 0:
        return []
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def _has_tool(name: str) -> bool:
    try:
        out = subprocess.run(  # noqa: S603, S607
            ["which", name], capture_output=True, text=True, timeout=3, check=False
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return out.returncode == 0 and bool(out.stdout.strip())


def _run_ruff(paths: list[str]) -> str | None:
    if not _has_tool("ruff"):
        return None
    py_paths = [p for p in paths if p.endswith(".py") and os.path.isfile(p)]
    if not py_paths:
        return None
    try:
        out = subprocess.run(  # noqa: S603, S607
            ["ruff", "check", *py_paths],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        tail = out.stdout.strip().splitlines()[-5:]
        return "ruff 发现问题：" + " | ".join(tail)
    return None


def _run_doc_lint(paths: list[str]) -> str | None:
    script = "scripts/doc-lint.sh"
    if not os.path.isfile(script):
        return None
    md_paths = [p for p in paths if p.endswith(".md")]
    if not md_paths:
        return None
    try:
        out = subprocess.run(  # noqa: S603
            ["bash", script, "learning-notes"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        tail = out.stdout.strip().splitlines()[-5:]
        return "doc-lint 发现问题：" + " | ".join(tail)
    return None


def main() -> int:
    if not _in_project():
        return 0
    changed = _changed_files()
    if not changed:
        return 0
    warnings: list[str] = []
    for check in (_run_ruff, _run_doc_lint):
        msg = check(changed)
        if msg:
            warnings.append(msg)
    if warnings:
        print("WARNING: " + "；".join(warnings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
