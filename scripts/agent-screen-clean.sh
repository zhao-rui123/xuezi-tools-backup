#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <task_name>"
  exit 1
fi

TASK_NAME="$1"
STATE_DIR="$HOME/.openclaw/workspace/logs/agent-screen"
META_FILE="$STATE_DIR/${TASK_NAME}.meta"

if [ ! -f "$META_FILE" ]; then
  echo "Meta file not found: $META_FILE"
  exit 1
fi

# shellcheck disable=SC1090
source "$META_FILE"

echo "Cleaning task=$TASK_NAME agent=$AGENT"

# 1) 先关 screen 壳子
screen -S "$TASK_NAME" -X quit >/dev/null 2>&1 || true
sleep 1

# 2) 再清对应 agent 主进程
if [ -n "${PATTERN:-}" ]; then
  pkill -f "$PATTERN" >/dev/null 2>&1 || true
fi

# 3) 清理与该工作目录绑定的 bash/login 包装层
pkill -f "bash -lc cd $WORKDIR &&" >/dev/null 2>&1 || true
pkill -f "login -pflq .*bash -lc cd $WORKDIR &&" >/dev/null 2>&1 || true
sleep 2

echo "--- remaining related processes ---"
ps aux | egrep "$PATTERN|bash -lc cd $WORKDIR &&|login -pflq .*bash -lc cd $WORKDIR &&" | grep -v grep || true

echo "--- memory snapshot ---"
OC=$(ps aux | awk '/openclaw-gateway/ && !/grep/ {print int($6/1024)}')
echo "openclaw=${OC}MB"
