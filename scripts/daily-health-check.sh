#!/bin/bash

# 每日健康检查报告
# 检查 OpenClaw 系统、云服务器、备份状态
# 发送报告到飞书

# 设置环境变量（cron 环境需要）
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"
export HOME="/Users/zhaoruicn"

REPORT_FILE="/tmp/daily-health-report-$(date '+%Y%m%d').txt"
FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/8c3b0f1e-2d4a-4b5c-9e6f-7a8b9c0d1e2f"

echo "📊 每日健康检查报告" > "$REPORT_FILE"
echo "日期: $(date '+%Y-%m-%d %H:%M')" >> "$REPORT_FILE"
echo "================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# ===== 1. OpenClaw 状态 =====
echo "🔧 OpenClaw 状态" >> "$REPORT_FILE"

# Gateway 状态
if pgrep -f "openclaw" > /dev/null; then
    echo "  ✅ Gateway: 运行中" >> "$REPORT_FILE"
else
    echo "  ❌ Gateway: 未运行" >> "$REPORT_FILE"
fi

# 磁盘空间
disk_usage=$(df -h "$HOME" | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    echo "  ✅ 磁盘空间: ${disk_usage}%" >> "$REPORT_FILE"
else
    echo "  ⚠️ 磁盘空间: ${disk_usage}% (偏高)" >> "$REPORT_FILE"
fi

# 会话文件数量
session_count=$(ls ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | wc -l)
echo "  ℹ️ 活跃会话: $session_count 个" >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"

# ===== 2. 云服务器状态 =====
echo "☁️ 云服务器 (106.54.25.161)" >> "$REPORT_FILE"

# 检查服务器可访问性
if sshpass -p 'Zr123456' ssh -o ConnectTimeout=5 root@106.54.25.161 "echo ok" > /dev/null 2>&1; then
    echo "  ✅ 服务器: 可访问" >> "$REPORT_FILE"
    
    # 磁盘空间
    server_disk=$(sshpass -p 'Zr123456' ssh root@106.54.25.161 "df -h / | tail -1 | awk '{print \$5}' | sed 's/%//'" 2>/dev/null)
    if [ "$server_disk" -lt 80 ]; then
        echo "  ✅ 磁盘空间: ${server_disk}%" >> "$REPORT_FILE"
    else
        echo "  ⚠️ 磁盘空间: ${server_disk}% (偏高)" >> "$REPORT_FILE"
    fi
    
    # Nginx 状态
    if sshpass -p 'Zr123456' ssh root@106.54.25.161 "systemctl is-active nginx" > /dev/null 2>&1; then
        echo "  ✅ Nginx: 运行中" >> "$REPORT_FILE"
    else
        echo "  ❌ Nginx: 未运行" >> "$REPORT_FILE"
    fi
else
    echo "  ❌ 服务器: 无法访问" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"

# ===== 3. 备份状态 =====
echo "💾 备份状态" >> "$REPORT_FILE"

# 本地备份
if [ -d "/Volumes/cu/ocu/memory" ]; then
    backup_count=$(ls /Volumes/cu/ocu/memory/*.md 2>/dev/null | wc -l)
    latest_backup=$(ls -t /Volumes/cu/ocu/memory/*.md 2>/dev/null | head -1 | xargs basename)
    echo "  ✅ 本地备份: $backup_count 个文件" >> "$REPORT_FILE"
    echo "  ℹ️ 最新备份: $latest_backup" >> "$REPORT_FILE"
else
    echo "  ❌ 本地备份: 磁盘未挂载" >> "$REPORT_FILE"
fi

# GitHub 备份
cd ~/.openclaw/workspace
if git rev-parse --git-dir > /dev/null 2>&1; then
    last_commit=$(git log -1 --format="%h %s" 2>/dev/null)
    echo "  ✅ GitHub: $last_commit" >> "$REPORT_FILE"
else
    echo "  ❌ GitHub: 未初始化" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"

# ===== 4. 今日统计 =====
echo "📈 今日统计" >> "$REPORT_FILE"

# 记忆文件
today_file="$HOME/.openclaw/workspace/memory/$(date '+%Y-%m-%d').md"
if [ -f "$today_file" ]; then
    lines=$(wc -l < "$today_file")
    echo "  ✅ 今日记忆: $lines 行" >> "$REPORT_FILE"
else
    echo "  ℹ️ 今日记忆: 未创建" >> "$REPORT_FILE"
fi

# Git 变更
changes=$(git status --short 2>/dev/null | wc -l)
if [ "$changes" -gt 0 ]; then
    echo "  ℹ️ 未提交变更: $changes 个文件" >> "$REPORT_FILE"
else
    echo "  ✅ 工作区: 已同步" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "================================" >> "$REPORT_FILE"
echo "报告生成时间: $(date '+%H:%M:%S')" >> "$REPORT_FILE"

# 发送报告到飞书
FEISHU_USER="ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"
NOTIFY_SCRIPT="/Users/zhaoruicn/.openclaw/workspace/scripts/feishu-notify.sh"

# 构建简洁的报告消息
report_summary=$(cat <<EOF
📊 每日健康检查报告 ($(date '+%Y-%m-%d %H:%M'))

🔧 OpenClaw 状态
$(grep "Gateway:" "$REPORT_FILE")
$(grep "磁盘空间:" "$REPORT_FILE" | head -1)

☁️ 云服务器 (106.54.25.161)
$(grep "服务器:" "$REPORT_FILE")
$(grep "Nginx:" "$REPORT_FILE")

💾 备份状态
$(grep "本地备份:" "$REPORT_FILE")
$(grep "GitHub:" "$REPORT_FILE")

📈 今日统计
$(grep "今日记忆:" "$REPORT_FILE")
$(grep "未提交变更:" "$REPORT_FILE" || grep "工作区:" "$REPORT_FILE")
EOF
)

# 发送消息
if [ -x "$NOTIFY_SCRIPT" ]; then
    "$NOTIFY_SCRIPT" send "$report_summary"
else
    echo "警告: 通知脚本不存在或不可执行"
fi

# 输出报告
cat "$REPORT_FILE"

# 保留最近7天的报告
find /tmp -name "daily-health-report-*.txt" -mtime +7 -delete 2>/dev/null
