"""run 目录清理"""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timedelta

from .config import RUNS_DIR


def cleanup_runs(days: int) -> dict:
    """删除早于 cutoff 的 run 目录。返回 {removed, kept}"""
    if days <= 0:
        return {"removed": 0, "kept": 0, "reason": "days<=0, skip"}
    if not RUNS_DIR.exists():
        return {"removed": 0, "kept": 0}

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    removed = 0
    kept = 0
    for item in RUNS_DIR.iterdir():
        if not item.is_dir():
            continue
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", item.name):
            continue
        if item.name < cutoff:
            shutil.rmtree(item, ignore_errors=True)
            removed += 1
        else:
            kept += 1
    return {"removed": removed, "kept": kept, "cutoff": cutoff}
