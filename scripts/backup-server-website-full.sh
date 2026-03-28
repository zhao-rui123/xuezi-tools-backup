#!/bin/bash
# 云服务器网站完整备份脚本
# 备份所有在用的网页和程序

echo "📦 开始备份云服务器网站..."

# 服务器信息
SERVER="root@106.54.25.161"
SSH_KEY="~/.ssh/id_ed25519"
DATE=$(date +%Y%m%d_%H%M%S)
LOCAL_BACKUP="/Volumes/cu/ocu/server-backup/website-full-$DATE.tar.gz"

# 创建本地备份目录
mkdir -p $(dirname $LOCAL_BACKUP)

# 需要备份的所有项目
ITEMS="electricity electricity-price-v2 calculation.html energy-bill-v3 storage-layout-ai agent-home agent-dashboard quant-trading stock stock-v2 my-home energy-tools grid-analysis energy-storage-app landing-zhongchuanghang dashboard electrical"

# 在服务器上打包
echo "📦 正在打包..."
ssh -o ConnectTimeout=60 -i $SSH_KEY $SERVER "
    cd /usr/share/nginx/html
    tar -czf /tmp/website-full.tar.gz $ITEMS
    du -h /tmp/website-full.tar.gz
" 2>&1

# 下载备份
echo "📥 正在下载..."
scp -o ConnectTimeout=60 -i $SSH_KEY $SERVER:/tmp/website-full.tar.gz $LOCAL_BACKUP 2>&1

# 清理服务器上的临时文件
ssh -o ConnectTimeout=30 -i $SSH_KEY $SERVER "rm -f /tmp/website-full.tar.gz" 2>/dev/null

echo ""
echo "✅ 备份完成!"
echo "📁 $LOCAL_BACKUP"
echo "📊 大小: $(du -h $LOCAL_BACKUP 2>/dev/null | cut -f1)"
