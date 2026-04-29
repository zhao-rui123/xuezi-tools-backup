#!/bin/bash
# 清理本地超 2 小时且不在活跃 screen 体系下的 codex/claude 进程
# 只处理本机残留，不尝试判断远程机器上的会话

set -euo pipefail

LOG_FILE="$HOME/.openclaw/ops/logs/tasks/codex-claude-orphan-clean.log"
mkdir -p "$(dirname "$LOG_FILE")"

NOW_TS=$(date '+%Y-%m-%d %H:%M:%S')
MAX_AGE_SECONDS_DEFAULT=$((2 * 60 * 60))
MAX_AGE_SECONDS=${MAX_AGE_SECONDS_OVERRIDE:-$MAX_AGE_SECONDS_DEFAULT}

log() {
  printf '[%s] %s\n' "$NOW_TS" "$1" >> "$LOG_FILE"
}

# 收集本地 screen 相关 PID：screen 本身 + 它的直接子进程
collect_protected_pids() {
  local pids=()
  while IFS= read -r spid; do
    [[ -z "$spid" ]] && continue
    pids+=("$spid")
    while IFS= read -r cpid; do
      [[ -n "$cpid" ]] && pids+=("$cpid")
    done < <(pgrep -P "$spid" || true)
  done < <(pgrep -x screen || true)

  if ((${#pids[@]} > 0)); then
    printf '%s\n' "${pids[@]}" | sort -u
  fi
}

is_protected_pid() {
  local target="$1"
  local pid
  for pid in "${PROTECTED_PIDS[@]:-}"; do
    [[ "$pid" == "$target" ]] && return 0
  done
  return 1
}

# shellcheck disable=SC2207
PROTECTED_PIDS=($(collect_protected_pids))

log "start protected_pids=${PROTECTED_PIDS[*]:-none} max_age_seconds=$MAX_AGE_SECONDS"

FOUND=0
KILLED=0
SKIPPED=0

while IFS= read -r pid; do
  [[ -z "$pid" ]] && continue
  FOUND=$((FOUND + 1))

  # 进程已不存在则跳过
  if ! kill -0 "$pid" 2>/dev/null; then
    SKIPPED=$((SKIPPED + 1))
    log "skip pid=$pid reason=not_exists"
    continue
  fi

  etimes=$(ps -p "$pid" -o etime= 2>/dev/null | awk '{gsub(/^ +| +$/,"",$0); split($0,a,":"); if (index($0,"-")>0) {split(a[1],d,"-"); days=d[1]+0; hours=a[2]+0; mins=a[3]+0; secs=a[4]+0; print days*86400+hours*3600+mins*60+secs} else if (length(a)==3) {print (a[1]+0)*3600+(a[2]+0)*60+(a[3]+0)} else if (length(a)==2) {print (a[1]+0)*60+(a[2]+0)} else {print a[1]+0}}' || true)
  comm=$(ps -o comm= -p "$pid" 2>/dev/null | sed 's/^ *//' || true)
  args=$(ps -o args= -p "$pid" 2>/dev/null || true)
  ppid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ' || true)

  if [[ -z "$etimes" ]]; then
    SKIPPED=$((SKIPPED + 1))
    log "skip pid=$pid reason=no_etimes comm=$comm"
    continue
  fi

  if (( etimes < MAX_AGE_SECONDS )); then
    SKIPPED=$((SKIPPED + 1))
    log "skip pid=$pid reason=young age=${etimes}s comm=$comm"
    continue
  fi

  # 保护：在活跃 screen 树里
  if is_protected_pid "$pid" || { [[ -n "$ppid" ]] && is_protected_pid "$ppid"; }; then
    SKIPPED=$((SKIPPED + 1))
    log "skip pid=$pid reason=screen_protected age=${etimes}s comm=$comm ppid=$ppid"
    continue
  fi

  # 只杀本次脚本目标：codex / claude / 其明显子命令
  if echo "$args" | grep -Eiq '(^|[ /])(codex|claude)( |$)|Claude Code'; then
    if kill "$pid" 2>/dev/null; then
      KILLED=$((KILLED + 1))
      log "killed pid=$pid age=${etimes}s comm=$comm ppid=$ppid args=$args"
    else
      SKIPPED=$((SKIPPED + 1))
      log "skip pid=$pid reason=kill_failed age=${etimes}s comm=$comm args=$args"
    fi
  else
    SKIPPED=$((SKIPPED + 1))
    log "skip pid=$pid reason=no_match age=${etimes}s comm=$comm args=$args"
  fi

done < <(ps -axo pid=,args= | grep -Ei '(^|[ /])(codex|claude)( |$)|Claude Code' | grep -vE 'grep|codex-claude-orphan-clean\.sh' | awk '{print $1}')

log "done found=$FOUND killed=$KILLED skipped=$SKIPPED"
echo "found=$FOUND killed=$KILLED skipped=$SKIPPED"
