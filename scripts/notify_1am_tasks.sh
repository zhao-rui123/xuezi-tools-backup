#!/bin/bash
# 凌晨1点定时任务完成通知脚本
# 由crontab调用，发送飞书通知

FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_TOKEN"
USER_ID="ou_5a7b7ec0339ffe0c1d5bb6c5bc162579"

# 获取当前日期
DATE=$(date +"%Y-%m-%d")
TIME=$(date +"%H:%M")

# 检查各任务日志
GRAPH_LOG="/tmp/ums-graph.log"
KB_LOG="/tmp/kb-integration.log"
UMS_LOG="/tmp/ums-daily.log"

# 检查知识图谱任务
if tail -5 "$GRAPH_LOG" 2>/dev/null | grep -q "完成"; then
    GRAPH_STATUS="✅ 完成"
else
    GRAPH_STATUS="❌ 失败"
fi

# 检查知识同步任务
if tail -5 "$KB_LOG" 2>/dev/null | grep -q "完成"; then
    KB_STATUS="✅ 完成"
else
    KB_STATUS="❌ 失败"
fi

# 检查统一记忆归档任务
if tail -5 "$UMS_LOG" 2>/dev/null | grep -q "完成"; then
    UMS_STATUS="✅ 完成"
else
    UMS_STATUS="❌ 失败"
fi

# 构建消息
MESSAGE="🤖 凌晨1点定时任务完成通知

📅 日期: $DATE
⏰ 时间: $TIME

📋 任务执行状态:
• 知识图谱自动更新: $GRAPH_STATUS
• 每日知识同步: $KB_STATUS  
• 统一记忆归档: $UMS_STATUS

所有任务已完成！"

# 使用OpenClaw的message工具发送通知
# 注意: 此脚本需要在OpenClaw Agent环境中运行
# 或者配置飞书Webhook

# 方案1: 如果有飞书Webhook
# curl -X POST "$FEISHU_WEBHOOK" \
#     -H "Content-Type: application/json" \
#     -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"$MESSAGE\"}}"

# 方案2: 创建通知文件，等待Agent处理
NOTIFICATION_FILE="/tmp/kilo_notification_1am_$(date +%H%M%S).json"
echo "{
  \"chat_id\": \"oc_b14195eb990ab57ea573e696758ae3d5\",
  \"user_id\": \"$USER_ID\",
  \"message\": \"$MESSAGE\",
  \"type\": \"定时任务通知\",
  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
}" > "$NOTIFICATION_FILE"

echo "✅ 通知文件已创建: $NOTIFICATION_FILE"
echo "📤 消息内容:"
echo "$MESSAGE"
