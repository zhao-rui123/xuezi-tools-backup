#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <task_name>"
  exit 1
fi

TASK_NAME="$1"
OUT=$(bash "$HOME/.openclaw/workspace/scripts/rerun-test-task.sh" "$TASK_NAME")

NEW_TASK=$(printf '%s
' "$OUT" | awk -F'=' '/^started task=/{print $2}' | awk '{print $1}')
LOG_FILE=$(printf '%s
' "$OUT" | awk -F'=' '/^log=/{print $2}')
META_FILE=$(printf '%s
' "$OUT" | awk -F'=' '/^meta=/{print $2}')
SCREEN_NAME=$(printf '%s
' "$OUT" | awk -F'=' '/^screen=/{print $2}')

cat <<EOF
✅ 已触发重跑
- 原任务: $TASK_NAME
- 新任务: ${NEW_TASK:-unknown}
- 日志: ${LOG_FILE:-unknown}
- Meta: ${META_FILE:-unknown}
- Screen: ${SCREEN_NAME:-unknown}
EOF
