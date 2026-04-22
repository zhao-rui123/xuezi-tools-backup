#!/usr/bin/env bash

set -uo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JOB_DIR="${SCREEN_JOB_DIR:-$WORKSPACE/.screen-jobs}"
STATE_DIR="${SCREEN_NOTIFIER_STATE_DIR:-$SCRIPT_DIR/state}"
RUNTIME_DIR="${SCREEN_NOTIFIER_RUNTIME_DIR:-$SCRIPT_DIR/runtime}"
CHECK_INTERVAL="${SCREEN_NOTIFIER_INTERVAL:-30}"
GROUP_ID="${SCREEN_NOTIFIER_GROUP_ID:-oc_b14195eb990ab57ea573e696758ae3d5}"
LOG_FILE="${SCREEN_NOTIFIER_LOG:-$WORKSPACE/logs/screen-notifier/daemon.log}"

mkdir -p "$JOB_DIR" "$STATE_DIR" "$RUNTIME_DIR" "$(dirname "$LOG_FILE")"

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG_FILE" >/dev/null
}

require_cmd() {
    local cmd="$1"
    command -v "$cmd" >/dev/null 2>&1 || {
        log "missing command: $cmd"
        exit 1
    }
}

json_escape() {
    python3 - "$1" <<'PY'
import json
import sys
print(json.dumps(sys.argv[1], ensure_ascii=False))
PY
}

parse_json_field() {
    python3 - "$1" "$2" <<'PY'
import json
import sys

payload = sys.argv[1]
field = sys.argv[2]
try:
    data = json.loads(payload)
except Exception:
    print("")
    raise SystemExit(0)

value = data
for part in field.split("."):
    if isinstance(value, dict):
        value = value.get(part, "")
    else:
        value = ""
        break

if value is None:
    value = ""
print(value)
PY
}

send_feishu_message() {
    local title="$1"
    local body="$2"

    if [[ -z "${FEISHU_APP_ID:-}" || -z "${FEISHU_APP_SECRET:-}" ]]; then
        log "FEISHU_APP_ID/FEISHU_APP_SECRET not set, skip notify"
        return 1
    fi

    local token_resp token
    token_resp="$(
        curl -fsS --retry 2 --retry-delay 1 \
            -H 'Content-Type: application/json; charset=utf-8' \
            -X POST \
            -d "{\"app_id\":\"${FEISHU_APP_ID}\",\"app_secret\":\"${FEISHU_APP_SECRET}\"}" \
            'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' 2>&1
    )" || {
        log "failed to get tenant_access_token: $token_resp"
        return 1
    }

    token="$(parse_json_field "$token_resp" "tenant_access_token")"
    if [[ -z "$token" ]]; then
        log "tenant_access_token missing: $token_resp"
        return 1
    fi

    local text_payload payload resp code body_file
    text_payload="【${title}】"$'\n\n'"${body}"
    payload="$(python3 - "$GROUP_ID" "$text_payload" <<'PY'
import json
import sys

receive_id = sys.argv[1]
text = sys.argv[2]
print(json.dumps({
    "receive_id": receive_id,
    "msg_type": "text",
    "content": json.dumps({"text": text}, ensure_ascii=False),
}, ensure_ascii=False))
PY
)"

    body_file="$(mktemp)"
    code="$(
        curl -sS -o "$body_file" -w '%{http_code}' \
            -H "Authorization: Bearer ${token}" \
            -H 'Content-Type: application/json; charset=utf-8' \
            -X POST \
            -d "$payload" \
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    )"
    resp="$(cat "$body_file")"
    rm -f "$body_file"

    if [[ "$code" != "200" ]]; then
        log "feishu send failed, http=$code resp=$resp"
        return 1
    fi

    if [[ "$(parse_json_field "$resp" "code")" != "0" ]]; then
        log "feishu send failed, resp=$resp"
        return 1
    fi

    log "feishu notification sent: $title"
    return 0
}

screen_exists() {
    local name="$1"
    local escaped
    escaped="$(printf '%s' "$name" | sed 's/[][(){}.^$+*?|\\/]/\\&/g')"
    screen -list 2>/dev/null | grep -Eq "[[:space:]][0-9]+\\.${escaped}[[:space:]]"
}

sanitize_name() {
    printf '%s' "$1" | tr '/ ' '__' | tr -cd '[:alnum:]_.-'
}

build_summary() {
    local log_path="$1"
    if [[ ! -f "$log_path" ]]; then
        printf '日志文件不存在：%s' "$log_path"
        return 0
    fi

    python3 - "$log_path" <<'PY'
import os
import re
import sys
from collections import deque

path = sys.argv[1]
lines = deque(maxlen=40)

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    for raw in f:
        text = raw.strip()
        if not text:
            continue
        text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        lines.append(text)

if not lines:
    print("日志为空")
    raise SystemExit(0)

priority = []
normal = []
keywords = ("error", "failed", "exception", "traceback", "warning", "warn", "success", "done", "completed", "finished")

for line in lines:
    lower = line.lower()
    if any(k in lower for k in keywords):
        priority.append(line)
    else:
        normal.append(line)

picked = []
for seq in (priority[-6:], normal[-6:]):
    for item in seq:
        if item not in picked:
            picked.append(item)

summary = " | ".join(picked[-8:])
summary = summary[:900]
print(summary)
PY
}

notify_job_done() {
    local screen_name="$1"
    local log_path="$2"
    local desc="$3"
    local finished_at summary title body

    finished_at="$(date '+%Y-%m-%d %H:%M:%S %Z')"
    summary="$(build_summary "$log_path")"
    title="screen任务完成通知"
    body=$(
        cat <<EOF
任务名: $screen_name
完成时间: $finished_at
任务描述: $desc
输出摘要: $summary
日志路径: $log_path
EOF
    )

    send_feishu_message "$title" "$body"
}

process_job_file() {
    local job_file="$1"
    local line screen_name log_path desc job_id state_file lock_file

    [[ -f "$job_file" ]] || return 0
    line="$(head -n 1 "$job_file" 2>/dev/null || true)"
    [[ -n "$line" ]] || {
        log "empty job file: $job_file"
        return 0
    }

    IFS='|' read -r screen_name log_path desc <<<"$line"
    if [[ -z "${screen_name:-}" || -z "${log_path:-}" || -z "${desc:-}" ]]; then
        log "invalid job file format: $job_file"
        return 0
    fi

    job_id="$(sanitize_name "$screen_name")"
    state_file="$STATE_DIR/${job_id}.sent"
    lock_file="$RUNTIME_DIR/${job_id}.lock"

    if [[ -f "$state_file" ]]; then
        rm -f "$job_file"
        return 0
    fi

    if screen_exists "$screen_name"; then
        # Screen still running, reset tracking
        rm -f "$RUNTIME_DIR/${job_id}.was_running"
        return 0
    fi

    # Screen not found - only consider complete if we saw it running before
    local was_running_file="$RUNTIME_DIR/${job_id}.was_running"
    if [[ -f "$was_running_file" ]]; then
        # We've seen this screen running before, and now it's gone = really done
        rm -f "$was_running_file"
    else
        # Never saw this screen running - might be transient, wait and check again
        touch "$was_running_file"
        return 0
    fi

    if ! mkdir "$lock_file" 2>/dev/null; then
        return 0
    fi

    if notify_job_done "$screen_name" "$log_path" "$desc"; then
        printf '%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" >"$state_file"
        rm -f "$job_file"
        log "job completed and notified: $screen_name"
    else
        log "notify failed, will retry: $screen_name"
    fi

    rmdir "$lock_file" 2>/dev/null || true
}

run_once() {
    require_cmd screen
    require_cmd curl
    require_cmd python3

    shopt -s nullglob
    local file
    for file in "$JOB_DIR"/*; do
        [[ -f "$file" ]] || continue
        process_job_file "$file"
    done
    shopt -u nullglob
}

run_daemon() {
    log "screen notifier daemon started, interval=${CHECK_INTERVAL}s, job_dir=$JOB_DIR"
    while true; do
        run_once
        sleep "$CHECK_INTERVAL"
    done
}

usage() {
    cat <<EOF
Usage:
  $(basename "$0") daemon
  $(basename "$0") once

Environment:
  FEISHU_APP_ID
  FEISHU_APP_SECRET
  SCREEN_NOTIFIER_INTERVAL
  SCREEN_NOTIFIER_GROUP_ID
  SCREEN_JOB_DIR
EOF
}

main() {
    local mode="${1:-daemon}"
    case "$mode" in
        daemon) run_daemon ;;
        once) run_once ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
