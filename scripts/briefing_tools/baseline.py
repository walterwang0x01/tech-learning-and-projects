"""Metrics 基线分析

对比当日候选数与近 7 天均值，低于 50% 视为异常（可能源故障 / 分类规则破损）。
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from .config import RUNS_DIR, TOPICS

# 候选数低于均值这个比例时告警
LOW_RATIO_THRESHOLD = 0.5
# 用最近多少天计算基线
BASELINE_DAYS = 7
# 至少有几天的数据才计算基线（防止冷启动)
MIN_BASELINE_SAMPLES = 3


def _load_stats(run_dir: Path, topic: str) -> int | None:
    """读 candidates.{topic}.stats.json 取 kept 数。返回 None 表示当日没数据。"""
    path = run_dir / f"candidates.{topic}.stats.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("stats", {}).get("kept")
    except (json.JSONDecodeError, OSError):
        return None


def _historical_kept(topic: str, today: datetime, days: int = BASELINE_DAYS) -> list[int]:
    """收集最近 N 天该主题的候选数（不含今天）"""
    samples = []
    for i in range(1, days + 1):
        d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        rd = RUNS_DIR / d
        kept = _load_stats(rd, topic)
        if kept is not None:
            samples.append(kept)
    return samples


def check_topic_baseline(topic: str, today: datetime | None = None) -> dict:
    """对单个主题做基线检查。返回:
    {
        "topic": str,
        "today_kept": int | None,
        "baseline_avg": float | None,
        "baseline_samples": int,
        "ratio": float | None,       # today / avg
        "anomaly": bool,
        "message": str,
    }
    """
    today = today or datetime.now()
    rd = RUNS_DIR / today.strftime("%Y-%m-%d")
    today_kept = _load_stats(rd, topic)
    history = _historical_kept(topic, today)

    result: dict = {
        "topic": topic,
        "today_kept": today_kept,
        "baseline_avg": None,
        "baseline_samples": len(history),
        "ratio": None,
        "anomaly": False,
        "message": "",
    }

    if today_kept is None:
        result["message"] = "今日候选集尚未生成"
        return result
    if len(history) < MIN_BASELINE_SAMPLES:
        result["message"] = f"基线样本不足（{len(history)} < {MIN_BASELINE_SAMPLES}），跳过比对"
        return result

    avg = sum(history) / len(history)
    result["baseline_avg"] = avg
    if avg <= 0:
        result["message"] = "历史均值为 0，无法比对"
        return result

    ratio = today_kept / avg
    result["ratio"] = ratio
    if ratio < LOW_RATIO_THRESHOLD:
        result["anomaly"] = True
        result["message"] = (
            f"候选数 {today_kept} 仅为基线 {avg:.0f} 的 {ratio * 100:.0f}%（< {LOW_RATIO_THRESHOLD * 100:.0f}%），"
            f"可能是 RSS 源故障 / 分类规则误伤"
        )
    else:
        result["message"] = f"候选数 {today_kept} / 基线 {avg:.0f}（{ratio * 100:.0f}%）正常"
    return result


def check_all_baselines(today: datetime | None = None) -> list[dict]:
    """对全部主题做基线检查"""
    return [check_topic_baseline(t, today) for t in TOPICS]
