"""Bark 推送"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from .config import REPO_ROOT, TOPIC_ICONS, TOPIC_NAMES
from .storage import briefing_file, today_str

BLOG_SITE_URL = "https://walterwang0x01.github.io/portfolio"


def briefing_github_url(topic: str, date_str: str | None = None) -> str:
    ds = date_str or today_str()
    return f"{BLOG_SITE_URL}/briefing/#{topic}/{ds}"


def get_bark_url() -> str | None:
    url = os.environ.get("BARK_URL", "").strip()
    if not url:
        candidates = [
            REPO_ROOT.parent / "personal-brand-agent" / ".env",
            REPO_ROOT.parent / "Brand Agent" / ".env",
            REPO_ROOT / "🤖 Brand Agent" / ".env",
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


def push_bark(
    bark_url: str, title: str, body: str, group: str = "AI简报", open_url: str = "",
    timeout: int = 10, retries: int = 2,
) -> bool:
    """推送 Bark 通知，带指数退避重试（模式同 http.py 的 http_get）。

    网络超时 / 5xx 视为临时错误重试；4xx（配置错误等）不重试。
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
    backoffs = [2, 5, 10]
    last_err: Exception | None = None
    for attempt in range(1 + retries):
        try:
            req = urllib.request.Request(
                url, data=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("code") == 200:
                    print(f"  ✅ Bark 推送成功：{title}")
                    return True
                print(f"  ❌ Bark 推送失败：{result}")
                return False
        except urllib.error.HTTPError as e:
            last_err = e
            if 400 <= e.code < 500 and e.code not in (408, 429):
                break
        except Exception as e:
            last_err = e
        if attempt < retries:
            print(f"  ⚠️  Bark 推送超时/异常，{backoffs[attempt]}s 后重试（{attempt + 1}/{retries}）：{last_err}")
            time.sleep(backoffs[min(attempt, len(backoffs) - 1)])
    print(f"  ❌ Bark 推送异常（已重试 {retries} 次）：{last_err}")
    return False


def count_briefing_items(content: str) -> int:
    lines = content.splitlines()
    count = 0
    in_table = False
    for line in lines:
        stripped = line.strip()
        if re.match(r"^#{1,3}\s*📈", stripped) or re.match(r"^#{1,3}\s*📊", stripped):
            break
        if stripped.startswith("#"):
            in_table = False
            if re.match(r"^###\s+", stripped):
                title_body = stripped[3:].strip()
                if not re.match(r"^[📌⚡📦🤖🛠🔒💰📜💬🚀🆕🔺🔻]", title_body):
                    count += 1
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                in_table = True
                continue
            if set(stripped.replace("|", "").strip()) <= set("-: "):
                continue
            count += 1
            continue
        else:
            in_table = False
        if re.match(r"^-\s+\*\*", stripped):
            count += 1
    return count


def extract_briefing_summary(topic: str) -> tuple[str, str, str] | None:
    filepath = briefing_file(topic)
    if not filepath.exists():
        return None
    content = filepath.read_text(encoding="utf-8")
    icon = TOPIC_ICONS.get(topic, "📰")
    name = TOPIC_NAMES.get(topic, topic)
    today = datetime.now().strftime("%m-%d")

    headlines = re.findall(r"^### \d+\. (.+)$", content, re.MULTILINE)
    if not headlines:
        headlines = re.findall(r"^### (.+)$", content, re.MULTILINE)

    m = re.search(r"最终收录：(\d+) 条", content)
    if not m:
        m = re.search(r"评分筛选后收录\s*\|\s*(\d+)\s*条", content)
    count = m.group(1) if m else str(count_briefing_items(content))

    source_m = re.search(r"采集源：(\d+) 个", content)
    source_count = source_m.group(1) if source_m else ""

    title = f"{icon} {name} {today}｜{count} 条收录"
    lines = []
    for i, h in enumerate(headlines[:5], 1):
        short = h[:80] + ("…" if len(h) > 80 else "")
        lines.append(f"{i}. {short}")
    if not lines:
        lines.append("详见完整简报")
    total = len(headlines)
    if total > 5:
        lines.append(f"\n…共 {total} 条要闻")
    if source_count:
        lines.append(f"📡 {source_count} 个源采集")
    lines.append("👆 点击查看完整简报")

    return title, "\n".join(lines), briefing_github_url(topic)
