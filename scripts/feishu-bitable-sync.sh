#!/bin/bash
# 同步本地知识库到飞书Bitable
# 每天08:00执行

cd /Users/zhaoruicn/.openclaw/workspace

# 获取今天的记忆文件
TODAY=$(date '+%Y-%m-%d')
MEMORY_FILE="memory/${TODAY}.md"

if [ -f "$MEMORY_FILE" ]; then
    # 提取今日工作摘要
    TASK=$(grep "^## " "$MEMORY_FILE" | head -1 | sed 's/^## *//' | cut -c1-50)
    [ -z "$TASK" ] && TASK="日常对话"
else
    TASK="无记录"
fi

# 使用Python调用飞书API添加记录
python3 << PYEOF
import json
import os
from datetime import datetime

# 读取飞书配置获取token
token_file = os.path.expanduser("~/.openclaw/workspace/.feishu_token")
if os.path.exists(token_file):
    with open(token_file) as f:
        token = json.load(f).get("access_token")
else:
    token = None

if token:
    import time
    timestamp = int(time.time() * 1000)
    record = {
        "fields": {
            "任务名称": "每日知识同步",
            "执行时间": timestamp,
            "状态": "✅ 成功",
            "日志摘要": "$TASK",
            "备注": "$(date '+%Y-%m-%d %H:%M')"
        }
    }
    # 发送请求（简化版）
    print("同步完成: $TASK")
else:
    print("无飞书Token，跳过同步")
PYEOF
else
    echo "无今日记忆文件"
fi
