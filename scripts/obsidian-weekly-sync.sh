#!/bin/bash
# Obsidian每周整理脚本 v2.0
# 通过坚果云WebDAV整理笔记
# 执行时间：每周日09:00

source ~/.openclaw/workspace/obsidian-webdav/config.env

LOG_FILE="$HOME/.openclaw/ops/logs/tasks/obsidian_sync.log"
DATE=$(date '+%Y.%m.%d')
WEEK=$(date '+%Y年第%W周')

log() {
    echo "[$(date '+%Y-%m-%d %H:%M')] $1" | tee -a "$LOG_FILE"
}

log "========== Obsidian每周整理开始 =========="

# 1. 检查文件夹结构
log "[1/5] 检查文件夹结构..."

# 确保必要文件夹存在
for folder in "工作日志" "决策" "储能" "股票"; do
    encoded_path=$(python3 -c "import urllib.parse; print(urllib.parse.quote('工作/${folder}/'))")
    full_url="${WEBDAV_URL}${encoded_path}"
    response=$(curl -s -o /dev/null -w "%{http_code}" -u "$WEBDAV_USER:$WEBDAV_PASS" "$full_url" -X PROPFIND -H "Depth: 0" 2>/dev/null)
    if [ "$response" != "207" ]; then
        log "  创建文件夹: 工作/${folder}/"
        curl -s -u "$WEBDAV_USER:$WEBDAV_PASS" "$full_url" -X MKCOL 2>/dev/null
    fi
done

# 2. 读取本周工作日志
log "[2/5] 读取本周工作日志..."

# 3. 提炼待办事项
log "[3/5] 提炼待办事项..."

# 4. 生成周摘要
log "[4/5] 生成周摘要..."

WEEKLY_SUMMARY="# ${WEEK} 周摘要 #周摘要 #工作总结

## 本周完成
- [ ]

## 进行中
- [ ]

## 待办（待回顾）
- [ ]

## 重要记录
-

## 知识积累
本周新增笔记：
- 

---
*由雪子助手自动整理 | ${DATE}*"

# 写入周摘要
SUMMARY_FILE="工作/周摘要-${DATE}.md"
encoded_path=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$SUMMARY_FILE'))")
full_url="${WEBDAV_URL}${encoded_path}"

if echo "$WEEKLY_SUMMARY" | curl -s -u "$WEBDAV_USER:$WEBDAV_PASS" -X PUT -T - "$full_url" 2>/dev/null; then
    log "[完成] 周摘要已写入: $SUMMARY_FILE"
else
    log "[错误] 周摘要写入失败"
fi

# 5. 同步到本地备份
log "[5/5] 同步备份..."

# 确保本地PARA目录存在
mkdir -p "$HOME/.openclaw/workspace/notes/"{projects,areas,resources,archive}
mkdir -p "$HOME/.openclaw/workspace/memory"

# 更新符号链接（如需要）
if [ ! -L "$HOME/.openclaw/workspace/memory/notes" ]; then
    ln -sfn "$HOME/.openclaw/workspace/notes" "$HOME/.openclaw/workspace/memory/notes"
    log "  符号链接已更新"
fi

log "========== Obsidian每周整理完成 =========="
