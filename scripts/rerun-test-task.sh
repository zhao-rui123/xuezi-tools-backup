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
  echo "meta missing: $META_FILE"
  exit 2
fi

# shellcheck disable=SC1090
source "$META_FILE"

case "$TASK_NAME" in
  cc-min-test|cc-wrapper-test|codex-wrapper-test) ;;
  *)
    echo "task not allowed for rerun: $TASK_NAME"
    exit 3
    ;;
esac

if [ ! -f "$PROMPT_FILE" ]; then
  echo "prompt missing: $PROMPT_FILE"
  exit 4
fi

NEW_TASK_NAME="${TASK_NAME}-rerun-$(date '+%m%d-%H%M%S')"

bash "$HOME/.openclaw/workspace/scripts/agent-screen-run.sh" \
  "$AGENT" \
  "$NEW_TASK_NAME" \
  "$WORKDIR" \
  "$PROMPT_FILE"
