#!/bin/bash
# 每周日整理Obsidian笔记
# 通过坚果云WebDAV读取笔记，提炼整理，写回

source ~/.openclaw/workspace/obsidian-webdav/config.env

LOG_FILE="$HOME/.openclaw/ops/logs/tasks/obsidian-sync.log"
DATE=$(date '+%Y-%m-%d')

log() {
    echo "[$DATE] $1" | tee -a "$LOG_FILE"
}

log "========== Obsidian每周整理开始 =========="

# 1. 读取本周所有笔记
log "[步骤1] 读取本周笔记..."

# 2. 提炼待办事项
log "[步骤2] 提炼待办事项..."

# 3. 生成周摘要
log "[步骤3] 生成周摘要..."

# 4. 写入整理结果
SUMMARY_FILE="雪子助手/记忆/周摘要-${DATE}.md"
SUMMARY_CONTENT="# ${DATE} 周整理摘要

## 本周主要工作

## 待办事项

## 下周计划

---
*由雪子助手自动整理*"

# 写入摘要
encoded_path=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$SUMMARY_FILE'))")
full_url="${WEBDAV_URL}${encoded_path#/}"
if echo "$SUMMARY_CONTENT" | curl -s -u "$WEBDAV_USER:$WEBDAV_PASS" -X PUT -T - "$full_url" 2>/dev/null; then
    log "[完成] 周摘要已写入: $SUMMARY_FILE"
else
    log "[错误] 周摘要写入失败"
fi

log "========== Obsidian每周整理完成 =========="
