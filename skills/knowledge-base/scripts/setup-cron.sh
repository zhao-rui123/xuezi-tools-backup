#!/bin/bash
#
# 知识库整合系统 - 自动化任务配置脚本
# Knowledge-Memory Integration Cron Setup
#

set -e

echo "📚 知识库整合系统自动化任务配置"
echo "=================================="
echo ""

# 检查目录
WORKSPACE="$HOME/.openclaw/workspace"
KB_DIR="$WORKSPACE/skills/knowledge-base"

# 添加到 crontab 的任务
echo "📋 将添加以下定时任务："
echo ""
echo "1. 每日知识同步 (每天 01:00)"
echo "   分析昨日记忆 → 提取知识 → 同步到知识库 → 联动进化"
echo ""
echo "2. 每周知识库维护 (每周一 05:00)"
echo "   整理索引、归档旧文件、生成统计"
echo ""
echo "3. 每月知识审计 (每月 2号 06:00)"
echo "   完整性检查、重复内容清理、索引优化"
echo ""

# 创建临时 cron 文件
TEMP_CRON=$(mktemp)

# 导出当前 crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || echo "# 新建 crontab" > "$TEMP_CRON"

# 检查是否已存在知识库整合任务
if grep -q "knowledge_memory_integration" "$TEMP_CRON"; then
    echo "⚠️ 已存在知识库整合任务，更新配置..."
    # 删除旧的任务行
    grep -v "knowledge_memory_integration" "$TEMP_CRON" > "$TEMP_CRON.tmp" || true
    mv "$TEMP_CRON.tmp" "$TEMP_CRON"
fi

echo "" >> "$TEMP_CRON"
echo "# ===== Knowledge-Memory Integration Tasks =====" >> "$TEMP_CRON"
echo "# 每日知识同步" >> "$TEMP_CRON"
echo "0 1 * * * /usr/bin/python3 $KB_DIR/scripts/knowledge_memory_integration.py daily-sync >> /tmp/kb-integration.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"
echo "# 每周知识库维护 (已有)" >> "$TEMP_CRON"
# weekly-maintenance.sh 已在现有 crontab 中
echo "" >> "$TEMP_CRON"
echo "# 每月知识审计" >> "$TEMP_CRON"
echo "0 6 2 * * /usr/bin/python3 $KB_DIR/scripts/knowledge_memory_integration.py monthly-audit >> /tmp/kb-audit.log 2>&1" >> "$TEMP_CRON"

# 导入新的 crontab
crontab "$TEMP_CRON"

# 清理
rm "$TEMP_CRON"

echo "✅ 知识库整合系统任务已添加"
echo ""
echo "配置完成！"
