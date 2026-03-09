#!/bin/bash
#
# 自我进化系统 - 自动化任务配置脚本
# Self-Evolution System Cron Setup
#

set -e

echo "🧬 自我进化系统自动化任务配置"
echo "================================"
echo ""

# 检查目录
WORKSPACE="$HOME/.openclaw/workspace"
SE_DIR="$WORKSPACE/skills/self-improvement"

# 添加到 crontab 的任务
echo "📋 将添加以下定时任务："
echo ""
echo "1. 每日自我进化 (每天 23:00)"
echo "   执行交互分析、优化建议、等级更新"
echo ""
echo "2. 每周进化回顾 (每周日 22:00)"
echo "   生成周报、分析模式、调整目标"
echo ""
echo "3. 每月深度进化 (每月 1号 08:00)"
echo "   生成月报、长期规划调整、知识整合"
echo ""

# 创建临时 cron 文件
TEMP_CRON=$(mktemp)

# 导出当前 crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || echo "# 新建 crontab" > "$TEMP_CRON"

# 检查是否已存在自我进化任务
if grep -q "evolution_triggers.py" "$TEMP_CRON"; then
    echo "⚠️ 已存在自我进化任务，更新配置..."
    # 删除旧的任务行
    grep -v "evolution_triggers.py" "$TEMP_CRON" > "$TEMP_CRON.tmp" || true
    mv "$TEMP_CRON.tmp" "$TEMP_CRON"
fi

echo "" >> "$TEMP_CRON"
echo "# ===== Self-Evolution System Tasks =====" >> "$TEMP_CRON"
echo "# 每日自我进化" >> "$TEMP_CRON"
echo "0 23 * * * /usr/bin/python3 $SE_DIR/triggers/evolution_triggers.py daily >> /tmp/evolution-daily.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"
echo "# 每周进化回顾" >> "$TEMP_CRON"
echo "0 22 * * 0 /usr/bin/python3 $SE_DIR/triggers/evolution_triggers.py weekly >> /tmp/evolution-weekly.log 2>&1" >> "$TEMP_CRON"
echo "" >> "$TEMP_CRON"
echo "# 每月深度进化" >> "$TEMP_CRON"
echo "0 8 1 * * /usr/bin/python3 $SE_DIR/triggers/evolution_triggers.py monthly >> /tmp/evolution-monthly.log 2>&1" >> "$TEMP_CRON"

# 导入新的 crontab
crontab "$TEMP_CRON"

# 清理
rm "$TEMP_CRON"

echo "✅ 自我进化系统任务已添加"
echo ""
echo "📊 当前 crontab 中的自我进化任务："
crontab -l | grep -A1 "Self-Evolution" || echo "   已配置"
echo ""
echo "配置完成！"
