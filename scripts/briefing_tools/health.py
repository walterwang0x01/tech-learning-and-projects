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


def should_probe(source_name: str, retry_after_days: int) -> bool:
    """熔断源是否到了 half-open 试探时机。

    熔断源被跳过时不会调用 record_source_result，consecutive_failures 会冻结在
    触发阈值那一刻——既不增加也不归零。没有试探机制的话，源一旦熔断就永久熔断，
    哪怕上游早已恢复，也只能靠人工 health-reset 发现。

    这里按 last_fail_date 计时：距最后一次失败满 retry_after_days 就放行一次抓取。
    试探成功 → consecutive_failures 归零，自动恢复；
    试探失败 → last_fail_date 刷新为今天，于是自然形成每 retry_after_days 试一次的节奏。

    retry_after_days <= 0 表示关闭自愈试探（退回纯人工 health-reset）。
    """
    if retry_after_days <= 0:
        return False
    data = load_health()
    src = data["sources"].get(source_name, {})
    last_fail = src.get("last_fail_date", "")
    if not last_fail:
        return False
    try:
        last_fail_dt = datetime.strptime(last_fail, "%Y-%m-%d")
    except ValueError:
        return False
    return (datetime.now() - last_fail_dt).days >= retry_after_days


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
