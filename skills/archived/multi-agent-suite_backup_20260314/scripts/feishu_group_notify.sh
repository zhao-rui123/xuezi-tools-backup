#!/bin/bash
#
# 飞书群聊通知脚本
# 发送消息到群聊:  YOUR_CHAT_ID_HERE
#

CHAT_ID=" YOUR_CHAT_ID_HERE"
MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
    echo "用法: $0 '消息内容'"
    exit 1
fi

# 记录日志
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 发送消息到群聊 $CHAT_ID" >> /tmp/kilo_notifications.log
echo "消息: $MESSAGE" >> /tmp/kilo_notifications.log

# 这里需要配置飞书的app_id和app_secret来获取access_token
# 目前先输出到日志，后续可以配置实际的飞书API调用

echo "✅ 消息已记录（群聊: $CHAT_ID）"
echo "消息内容:"
echo "$MESSAGE"
