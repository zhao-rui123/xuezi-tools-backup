#!/bin/bash
# 定时更新小龙虾之家Token数据

API_SERVER="106.54.25.161"
DATA_FILE="/opt/lobster-home/data/stats.json"

# 获取当前token使用量（从OpenClaw状态）
# 注意：这里使用估算值，实际应该从OpenClaw API获取
# 由于权限限制，我们创建一个手动更新接口

echo "更新Token数据脚本"
echo "用法: $0 <token数>"
echo ""
echo "示例: $0 9500"

if [ -z "$1" ]; then
    echo "错误: 请提供token数量"
    exit 1
fi

TOKEN_COUNT=$1

# 通过SSH更新服务器数据
sshpass -p 'Zr123456' ssh root@$API_SERVER "
cd /opt/lobster-home/data

# 读取当前数据
python3 << PYEOF
import json
from datetime import datetime

with open('stats.json', 'r') as f:
    data = json.load(f)

# 更新今日token
data['today']['tokens_used'] = $TOKEN_COUNT
data['today']['date'] = datetime.now().strftime('%Y-%m-%d')

with open('stats.json', 'w') as f:
    json.dump(data, f)

print(f'✅ Token已更新: $TOKEN_COUNT')
PYEOF
"

echo "数据已同步到服务器"
