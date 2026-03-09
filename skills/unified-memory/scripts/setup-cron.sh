#!/bin/bash
#
# 统一记忆系统 - 自动化任务配置脚本
# Unified Memory System Cron Setup
#

set -e

echo "🧠 统一记忆系统自动化任务配置"
echo "================================"
echo ""

# 检查目录
WORKSPACE="$HOME/.openclaw/workspace"
UMS_DIR="$WORKSPACE/skills/unified-memory"

# 添加到 crontab 的任务
echo "📋 将添加以下定时任务："
echo ""
echo "1. 每日记忆归档 (每天 00:30)"
echo "   自动归档昨日记忆到 permanent 目录"
echo ""
echo "2. 知识图谱自动更新 (每天 01:00)"
echo "   从最新记忆更新知识图谱"
echo ""
echo "3. 月度深度分析 (每月 1号 02:00)"
echo "   执行月度记忆分析和主题提取"
echo ""

# 创建临时 cron 文件
TEMP_CRON=$(mktemp)

# 导出当前 crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || echo "# 新建 crontab" > "$TEMP_CRON"

# 检查是否已存在 UMS 任务
if grep -q "unified-memory" "$TEMP_CRON"; then
    echo "⚠️ 已存在统一记忆系统任务，跳过添加"
else
    echo "" >> "$TEMP_CRON"
    echo "# ===== Unified Memory System Tasks =====" >> "$TEMP_CRON"
    echo "# 每日记忆归档" >> "$TEMP_CRON"
    echo "30 0 * * * /usr/bin/python3 $UMS_DIR/unified_memory.py daily >> /tmp/ums-daily.log 2>&1" >> "$TEMP_CRON"
    echo "" >> "$TEMP_CRON"
    echo "# 知识图谱自动更新" >> "$TEMP_CRON"
    echo "0 1 * * * /usr/bin/python3 $UMS_DIR/knowledge_graph.py build --memory-dir $WORKSPACE/memory >> /tmp/ums-graph.log 2>&1" >> "$TEMP_CRON"
    echo "" >> "$TEMP_CRON"
    echo "# 月度深度分析 (由 system-maintenance 统一管理)" >> "$TEMP_CRON"
    # 月度分析已包含在现有 crontab 中
    
    # 导入新的 crontab
    crontab "$TEMP_CRON"
    echo "✅ 统一记忆系统任务已添加"
fi

# 清理
rm "$TEMP_CRON"

echo ""
echo "📊 当前 crontab 中的统一记忆任务："
crontab -l | grep "unified-memory" || echo "   无"
echo ""
echo "配置完成！"
