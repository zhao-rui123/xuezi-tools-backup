#!/bin/bash

# OpenClaw 系统维护脚本
# 清理日志、会话文件、检查磁盘空间

LOG_DIR="$HOME/.openclaw/logs"
SESSION_DIR="$HOME/.openclaw/agents/main/sessions"
BACKUP_DIR="/Volumes/cu/ocu/system-maintenance"
DATE_STR=$(date '+%Y%m%d')

# 确保备份目录存在
mkdir -p "$BACKUP_DIR/logs"

echo "========== OpenClaw 系统维护 =========="
echo "开始时间: $(date)"

# 1. 轮转日志
echo "[1/4] 轮转日志文件..."
if [ -f "$LOG_DIR/gateway.log" ]; then
    mv "$LOG_DIR/gateway.log" "$BACKUP_DIR/logs/gateway.log.$DATE_STR.bak"
    touch "$LOG_DIR/gateway.log"
    echo "  ✅ gateway.log 已轮转"
fi

if [ -f "$LOG_DIR/gateway.err.log" ]; then
    mv "$LOG_DIR/gateway.err.log" "$BACKUP_DIR/logs/gateway.err.log.$DATE_STR.bak"
    touch "$LOG_DIR/gateway.err.log"
    echo "  ✅ gateway.err.log 已轮转"
fi

# 2. 清理孤儿会话文件
echo "[2/4] 清理孤儿会话文件..."
cd "$SESSION_DIR"
orphan_count=$(ls *.jsonl.reset.* *.jsonl.deleted.* 2>/dev/null | wc -l)
if [ "$orphan_count" -gt 0 ]; then
    rm -f *.jsonl.reset.* *.jsonl.deleted.*
    echo "  ✅ 已清理 $orphan_count 个孤儿会话文件"
else
    echo "  ℹ️ 没有孤儿会话文件需要清理"
fi

# 3. 检查磁盘空间
echo "[3/4] 检查磁盘空间..."
df -h "$HOME" | tail -1 | awk '{print "  主磁盘使用率: "$5" (可用 "$4")"}'

if [ -d "/Volumes/cu/ocu" ]; then
    df -h "/Volumes/cu/ocu" | tail -1 | awk '{print "  备份磁盘使用率: "$5" (可用 "$4")"}'
fi

# 4. 检查 OpenClaw 状态
echo "[4/4] 检查 OpenClaw 状态..."
if pgrep -f "openclaw.*gateway" > /dev/null; then
    echo "  ✅ Gateway 运行中"
else
    echo "  ⚠️ Gateway 未运行"
fi

# 清理旧备份（保留30天）
echo "[清理] 删除30天前的日志备份..."
find "$BACKUP_DIR/logs" -name "*.bak" -mtime +30 -delete 2>/dev/null
echo "  ✅ 已清理旧备份"

echo ""
echo "========== 维护完成 =========="
echo "结束时间: $(date)"
