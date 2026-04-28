#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 4 ]; then
  echo "Usage: $0 <agent: claude|codex> <task_name> <workdir> <prompt_file_or_dash> [log_file]"
  exit 1
fi

AGENT="$1"
TASK_NAME="$2"
WORKDIR="$3"
PROMPT_SRC="$4"
LOG_FILE="${5:-$HOME/.openclaw/workspace/logs/${TASK_NAME}.log}"
STATE_DIR="$HOME/.openclaw/workspace/logs/agent-screen"
mkdir -p "$(dirname "$LOG_FILE")" "$STATE_DIR"

META_FILE="$STATE_DIR/${TASK_NAME}.meta"
PROMPT_FILE="$STATE_DIR/${TASK_NAME}.prompt.txt"

if [ "$PROMPT_SRC" = "-" ]; then
  cat > "$PROMPT_FILE"
else
  cp "$PROMPT_SRC" "$PROMPT_FILE"
fi

case "$AGENT" in
  claude)
    RUN_CMD="claude --permission-mode bypassPermissions --print \"\$(cat '$PROMPT_FILE')\""
    PATTERN='claude --permission-mode bypassPermissions --print'
    ;;
  codex)
    RUN_CMD="export https_proxy=http://127.0.0.1:1087 http_proxy=http://127.0.0.1:1087; codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox \"\$(cat '$PROMPT_FILE')\""
    PATTERN='codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox'
    ;;
  *)
    echo "Unsupported agent: $AGENT"
    exit 1
    ;;
esac

cat > "$META_FILE" <<EOF
AGENT='$AGENT'
TASK_NAME='$TASK_NAME'
WORKDIR='$WORKDIR'
LOG_FILE='$LOG_FILE'
PROMPT_FILE='$PROMPT_FILE'
PATTERN='$PATTERN'
STARTED_AT='$(date '+%Y-%m-%d %H:%M:%S')'
EOF

screen -dmS "$TASK_NAME" bash -lc "cd '$WORKDIR' && $RUN_CMD > '$LOG_FILE' 2>&1"

echo "started task=$TASK_NAME agent=$AGENT"
echo "log=$LOG_FILE"
echo "meta=$META_FILE"
echo "screen=$TASK_NAME"
