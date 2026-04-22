#!/usr/bin/env bash

set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
JOB_DIR="${SCREEN_JOB_DIR:-$WORKSPACE/.screen-jobs}"
DEFAULT_LOG_DIR="${SCREEN_JOB_LOG_DIR:-$WORKSPACE/logs/screen-notifier/jobs}"

mkdir -p "$JOB_DIR" "$DEFAULT_LOG_DIR"

usage() {
    cat <<EOF
Usage:
  $(basename "$0") <screen_name> <task_description> <command...>
  $(basename "$0") <screen_name> <log_path> <task_description> -- <command...>

Examples:
  $(basename "$0") demo-task "测试任务" "bash -lc 'echo hello; sleep 5; echo done'"
  $(basename "$0") demo-task "$WORKSPACE/logs/demo.log" "测试任务" -- bash -lc 'echo hello; sleep 5; echo done'
EOF
}

screen_exists() {
    local name="$1"
    local escaped
    escaped="$(printf '%s' "$name" | sed 's/[][(){}.^$+*?|\\/]/\\&/g')"
    screen -list 2>/dev/null | grep -Eq "[[:space:]][0-9]+\\.${escaped}[[:space:]]"
}

main() {
    command -v screen >/dev/null 2>&1 || {
        echo "screen 未安装" >&2
        exit 1
    }

    if [[ $# -lt 3 ]]; then
        usage
        exit 1
    fi

    local screen_name="$1"
    shift

    local log_path desc cmd
    if [[ "${2:-}" == "--" ]]; then
        log_path="$1"
        desc="$2"
        shift 3
        cmd="$*"
    else
        desc="$1"
        shift
        cmd="$*"
        log_path="$DEFAULT_LOG_DIR/${screen_name}.log"
    fi

    if [[ -z "$screen_name" || -z "$desc" || -z "$cmd" ]]; then
        usage
        exit 1
    fi

    if screen_exists "$screen_name"; then
        echo "screen 会话已存在: $screen_name" >&2
        exit 1
    fi

    mkdir -p "$(dirname "$log_path")"
    local job_file="$JOB_DIR/${screen_name}.job"
    printf '%s|%s|%s\n' "$screen_name" "$log_path" "$desc" >"$job_file"

    # Write command to temp file to avoid shell escaping issues
    local tmpcmd="/tmp/.screen_cmd_${screen_name}"
    echo "#!/bin/bash" >"$tmpcmd"
    echo "$cmd" >>"$tmpcmd"
    chmod +x "$tmpcmd"
    
    screen -dmS "$screen_name" bash -c "$tmpcmd > '$log_path' 2>&1; rm -f '$tmpcmd'"

    cat <<EOF
screen started
  name: $screen_name
  log: $log_path
  job: $job_file
  desc: $desc
EOF
}

main "$@"
