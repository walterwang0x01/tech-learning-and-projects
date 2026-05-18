#!/usr/bin/env bash
# 在 Kiro 中循环执行「追踪知识库更新」hook（10 次），遇 traffic/限流则等待后继续，结束后 push。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK_FILE="$REPO_ROOT/.kiro/hooks/tool-doc-update-check.kiro.hook"
UPDATE_LOG="$REPO_ROOT/learning-notes/.update-log.md"
LOG_DIR="$REPO_ROOT/.kiro_tmp/doc-update-runs"
RUN_TAG="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOG_DIR/run-$RUN_TAG.log"
KIRO_AGENT_LOG="${KIRO_AGENT_LOG:-$HOME/Library/Application Support/Kiro/logs}"

TOTAL_RUNS="${TOTAL_RUNS:-10}"
# 已手动完成的轮次（例如手动点了 2 次 hook，则 SKIP_COMPLETED=2，脚本再跑 8 次）
SKIP_COMPLETED="${SKIP_COMPLETED:-0}"
MAX_RETRIES_PER_RUN="${MAX_RETRIES_PER_RUN:-8}"
TRAFFIC_BACKOFF_SEC="${TRAFFIC_BACKOFF_SEC:-180}"
IDLE_SEC="${IDLE_SEC:-180}"
MAX_WAIT_PER_RUN_SEC="${MAX_WAIT_PER_RUN_SEC:-3600}"

mkdir -p "$LOG_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

find_q_client_log() {
  local latest="" latest_mtime=0 f mtime
  while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    mtime=$(stat -f %m "$f" 2>/dev/null || echo 0)
    if [[ "$mtime" -gt "$latest_mtime" ]]; then
      latest_mtime=$mtime
      latest=$f
    fi
  done < <(find "$KIRO_AGENT_LOG" -path '*/kiro.kiroAgent/q-client.log' -type f 2>/dev/null)
  [[ -n "$latest" ]] && echo "$latest"
}

kiro_is_running() {
  pgrep -f '/Applications/Kiro.app/Contents/MacOS/Electron' >/dev/null 2>&1 \
    || pgrep -f 'Kiro Helper' >/dev/null 2>&1
}

ensure_kiro_running() {
  if kiro_is_running; then
    return 0
  fi
  log "Kiro 未运行，正在启动..."
  open -a Kiro "$REPO_ROOT" || true
  local i
  for i in $(seq 1 24); do
    sleep 5
    if kiro_is_running; then
      log "Kiro 已启动 (等待 $((i * 5))s)"
      return 0
    fi
  done
  log "ERROR: Kiro 启动超时 (120s)"
  return 1
}

extract_prompt() {
  python3 - "$HOOK_FILE" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    print(json.load(f)["then"]["prompt"])
PY
}

update_log_lines() {
  [[ -f "$UPDATE_LOG" ]] && wc -l <"$UPDATE_LOG" | tr -d ' ' || echo 0
}

log_has_traffic() {
  local log_path="$1"
  [[ -n "$log_path" && -f "$log_path" ]] || return 1
  tail -n 30 "$log_path" 2>/dev/null \
    | grep -qiE 'high traffic|ThrottlingException|INSUFFICIENT_MODEL_CAPACITY|rate.?limit|429|too many requests|请稍后|限流'
}

log_is_idle() {
  local log_path="$1"
  local idle_threshold="$2"
  [[ -n "$log_path" && -f "$log_path" ]] || return 0
  local now mtime age
  now=$(date +%s)
  mtime=$(stat -f %m "$log_path" 2>/dev/null || stat -c %Y "$log_path" 2>/dev/null)
  age=$((now - mtime))
  [[ $age -ge $idle_threshold ]]
}

has_new_learning_notes_changes() {
  local marker="$1"
  find "$REPO_ROOT/learning-notes" -type f -newer "$marker" 2>/dev/null | head -1 | grep -q .
}

wait_for_agent_completion() {
  local run_idx="$1"
  local baseline_lines="$2"
  local marker="$3"
  local qlog
  qlog="$(find_q_client_log)"
  log "等待第 ${run_idx} 次 agent 完成 (baseline update-log lines=${baseline_lines})"
  [[ -n "$qlog" ]] && log "监控日志: $qlog" || log "WARN: 未找到 q-client.log"

  local start_ts now elapsed saw_activity=0
  start_ts=$(date +%s)

  while true; do
    now=$(date +%s)
    elapsed=$((now - start_ts))
    if [[ $elapsed -gt $MAX_WAIT_PER_RUN_SEC ]]; then
      log "WARN: 第 ${run_idx} 次等待超时 (${MAX_WAIT_PER_RUN_SEC}s)，继续下一轮"
      return 0
    fi

    if has_new_learning_notes_changes "$marker"; then
      saw_activity=1
    fi

    if [[ -n "$qlog" ]] && log_has_traffic "$qlog"; then
      log "检测到 traffic/限流，${TRAFFIC_BACKOFF_SEC}s 后继续等待..."
      sleep "$TRAFFIC_BACKOFF_SEC"
      continue
    fi

    local current_lines
    current_lines="$(update_log_lines)"
    if [[ "$current_lines" -gt "$((baseline_lines + 8))" ]]; then
      if [[ -n "$qlog" ]] && ! log_is_idle "$qlog" 60; then
        sleep 30
        continue
      fi
      log "第 ${run_idx} 次完成：update-log ${baseline_lines} -> ${current_lines} 行"
      return 0
    fi

    if [[ $saw_activity -eq 1 ]] && [[ -n "$qlog" ]] && log_is_idle "$qlog" "$IDLE_SEC"; then
      log "第 ${run_idx} 次完成：派发后有新文件写入且 agent 空闲 ${IDLE_SEC}s"
      return 0
    fi

    if [[ $elapsed -gt 600 ]] && [[ $saw_activity -eq 0 ]] && log_is_idle "$qlog" "$IDLE_SEC"; then
      log "WARN: 第 ${run_idx} 次派发后 10 分钟仍无新写入，可能 traffic 阻塞"
      return 1
    fi

    sleep 30
  done
}

dispatch_kiro_chat() {
  local run_idx="$1"
  local out_file="$LOG_DIR/run${run_idx}-dispatch.log"
  local prompt
  prompt="$(extract_prompt)"

  log "派发第 ${run_idx} 次 kiro chat -> $out_file"
  (
    cd "$REPO_ROOT"
    kiro chat --reuse-window --mode agent "$prompt"
  ) >"$out_file" 2>&1 || true
}

run_one_iteration() {
  local run_idx="$1"
  local attempt="$2"
  local baseline_lines marker
  baseline_lines="$(update_log_lines)"
  marker="$(mktemp "${LOG_DIR}/.run${run_idx}-marker.XXXXXX")"
  touch "$marker"

  until ensure_kiro_running; do
    log "第 ${run_idx} 次：等待 Kiro..."
    sleep 30
  done
  dispatch_kiro_chat "$run_idx"
  wait_for_agent_completion "$run_idx" "$baseline_lines" "$marker"
  rm -f "$marker"
}

git_push_changes() {
  cd "$REPO_ROOT"
  if [[ -z "$(git status --porcelain learning-notes/)" ]]; then
    log "learning-notes 无变更，跳过 push"
    return 0
  fi

  log "提交并 push learning-notes 变更..."
  git add learning-notes/
  git commit -m "$(cat <<EOF
docs: 知识库批量更新（${TOTAL_RUNS} 轮「追踪知识库更新」${RUN_TAG}）

EOF
)" || log "WARN: commit 失败"
  git push origin HEAD
  log "已 push 到 origin"
}

main() {
  log "=== 开始 | TOTAL_RUNS=$TOTAL_RUNS | RUN_TAG=$RUN_TAG ==="
  log "LOG=$LOG_FILE"

  if [[ ! -f "$HOOK_FILE" ]]; then
    log "ERROR: 找不到 $HOOK_FILE"
    exit 1
  fi

  until ensure_kiro_running; do
    log "等待 Kiro 可用，30s 后重试..."
    sleep 30
  done

  # 若 Kiro 正在跑上一轮，先等到空闲
  local qlog
  qlog="$(find_q_client_log)"
  if [[ -n "$qlog" ]] && ! log_is_idle "$qlog" 60; then
    log "Kiro agent 仍在活动，先等待空闲..."
    while ! log_is_idle "$qlog" "$IDLE_SEC"; do
      if log_has_traffic "$qlog"; then
        log "traffic 中，${TRAFFIC_BACKOFF_SEC}s 后重试..."
        sleep "$TRAFFIC_BACKOFF_SEC"
      else
        sleep 30
      fi
    done
    log "Kiro 已空闲，开始正式循环"
  fi

  local completed=$SKIP_COMPLETED
  log "已完成基线: ${SKIP_COMPLETED} 轮（手动或此前），目标共 ${TOTAL_RUNS} 轮"
  while [[ $completed -lt $TOTAL_RUNS ]]; do
    local run_idx=$((completed + 1))
    local attempt=1
    local ok=0

    while [[ $attempt -le $MAX_RETRIES_PER_RUN ]]; do
      if run_one_iteration "$run_idx" "$attempt"; then
        ok=1
        break
      fi
      log "第 ${run_idx} 次尝试 ${attempt} 未成功，30s 后重试..."
      sleep 30
      attempt=$((attempt + 1))
    done

    completed=$((completed + 1))
    if [[ $ok -eq 0 ]]; then
      log "WARN: 第 ${run_idx} 次未确认成功，仍计入进度 (${completed}/${TOTAL_RUNS})"
    fi
    sleep 15
  done

  log "=== ${TOTAL_RUNS} 轮结束，执行 git push ==="
  git_push_changes || true
  log "=== DONE ==="
}

main "$@"
