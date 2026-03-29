#!/bin/bash
# 云服务器网站备份脚本
# 用法: ./backup-server-website.sh

echo "📦 开始备份云服务器网站..."

# 服务器信息
SERVER="root@106.54.25.161"
SSH_KEY="~/.ssh/id_ed25519"

# 需要备份的项目
ITEMS="electricity electricity-price-v2 calculation.html energy-bill-v3 storage-layout-ai agent-home agent-dashboard"

# 备份文件名
DATE=$(date +%Y%m%d_%H%M%S)
LOCAL_BACKUP="/Volumes/cu/ocu/server-backup/website-$DATE.tar.gz"

# 创建本地备份目录
mkdir -p $(dirname $LOCAL_BACKUP)

# 在服务器上打包
ssh -o ConnectTimeout=30 -i $SSH_KEY $SERVER "
    cd /usr/share/nginx/html
    tar -czf /tmp/website-backup.tar.gz $ITEMS
" 2>&1

# 下载备份
scp -o ConnectTimeout=30 -i $SSH_KEY $SERVER:/tmp/website-backup.tar.gz $LOCAL_BACKUP 2>&1

# 清理服务器上的临时文件
ssh -o ConnectTimeout=30 -i $SSH_KEY $SERVER "rm -f /tmp/website-backup.tar.gz" 2>/dev/null

echo "✅ 备份完成: $LOCAL_BACKUP"
echo "📊 大小: $(du -h $LOCAL_BACKUP 2>/dev/null | cut -f1)"
