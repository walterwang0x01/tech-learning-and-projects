#!/usr/bin/env bash
# 持续监听 Kiro agent 日志，输出 traffic / 活动状态（供并行观察）
set -uo pipefail

KIRO_AGENT_LOG="${KIRO_AGENT_LOG:-$HOME/Library/Application Support/Kiro/logs}"
OUT_DIR="${1:-$(cd "$(dirname "$0")/.." && pwd)/.kiro_tmp/doc-update-runs}"
mkdir -p "$OUT_DIR"
WATCH_LOG="$OUT_DIR/kiro-watch.log"

find_qlog() {
  local latest="" latest_mtime=0 f mtime
  while IFS= read -r f; do
    mtime=$(stat -f %m "$f" 2>/dev/null || echo 0)
    if [[ "$mtime" -gt "$latest_mtime" ]]; then
      latest_mtime=$mtime
      latest=$f
    fi
  done < <(find "$KIRO_AGENT_LOG" -path '*/kiro.kiroAgent/q-client.log' -type f 2>/dev/null)
  echo "$latest"
}

log() {
  echo "[$(date '+%H:%M:%S')] $*" | tee -a "$WATCH_LOG"
}

log "=== Kiro 监听启动 ==="
last_line=0
qlog=""

while true; do
  if ! pgrep -f '/Applications/Kiro.app/Contents/MacOS/Electron' >/dev/null 2>&1; then
    log "Kiro 未运行"
    sleep 15
    continue
  fi

  new_qlog="$(find_qlog)"
  if [[ -n "$new_qlog" && "$new_qlog" != "$qlog" ]]; then
    qlog=$new_qlog
    last_line=0
    log "切换日志: $qlog"
  fi

  if [[ -z "$qlog" || ! -f "$qlog" ]]; then
    sleep 10
    continue
  fi

  total=$(wc -l <"$qlog" | tr -d ' ')
  if [[ "$total" -gt "$last_line" ]]; then
    tail -n $((total - last_line)) "$qlog" | while IFS= read -r line; do
      if echo "$line" | grep -qiE 'high traffic|ThrottlingException|INSUFFICIENT_MODEL_CAPACITY'; then
        log "⚠️ TRAFFIC: $(echo "$line" | grep -oE 'high traffic[^"]*|ThrottlingException[^"]*' | head -1)"
      elif echo "$line" | grep -q 'GenerateAssistantResponseCommand'; then
        log "🔄 Agent 正在生成回复..."
      elif echo "$line" | grep -qE 'Replaced text|Appended the text|fs_write'; then
        log "📝 正在写入文件..."
      fi
    done
    last_line=$total
  fi

  mtime=$(stat -f %m "$qlog" 2>/dev/null || echo 0)
  now=$(date +%s)
  idle=$((now - mtime))
  if [[ $idle -ge 180 ]]; then
    log "💤 Agent 空闲 ${idle}s"
    sleep 60
  else
    sleep 15
  fi
done
