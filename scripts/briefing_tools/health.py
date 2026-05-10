"""源健康记录 + 熔断"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from .config import SOURCE_HEALTH_FILE
from .storage import atomic_write_json


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def load_health() -> dict:
    if SOURCE_HEALTH_FILE.exists():
        try:
            return json.loads(SOURCE_HEALTH_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"sources": {}}
    return {"sources": {}}


def save_health(data: dict) -> None:
    atomic_write_json(SOURCE_HEALTH_FILE, data)


def record_source_result(source_name: str, ok: bool) -> None:
    """记录一次源抓取结果"""
    data = load_health()
    src = data["sources"].setdefault(source_name, {
        "last_ok_date": "",
        "last_fail_date": "",
        "consecutive_failures": 0,
        "total_runs": 0,
    })
    src["total_runs"] = src.get("total_runs", 0) + 1
    today = _today()
    if ok:
        src["last_ok_date"] = today
        src["consecutive_failures"] = 0
    else:
        src["last_fail_date"] = today
        # 同一天多次失败只算一次连续失败
        if src.get("_last_fail_accounted", "") != today:
            src["consecutive_failures"] = src.get("consecutive_failures", 0) + 1
            src["_last_fail_accounted"] = today
    save_health(data)


def is_source_tripped(source_name: str, threshold_days: int) -> bool:
    """检查源是否触发熔断"""
    data = load_health()
    src = data["sources"].get(source_name, {})
    return src.get("consecutive_failures", 0) >= threshold_days


def reset_source(source_name: str) -> None:
    data = load_health()
    if source_name in data["sources"]:
        data["sources"][source_name]["consecutive_failures"] = 0
        data["sources"][source_name].pop("_last_fail_accounted", None)
        save_health(data)


def tripped_sources(threshold_days: int) -> list[dict]:
    data = load_health()
    return [
        {"name": name, **src}
        for name, src in data["sources"].items()
        if src.get("consecutive_failures", 0) >= threshold_days
    ]
