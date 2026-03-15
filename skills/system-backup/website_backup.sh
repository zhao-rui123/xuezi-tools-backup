#!/bin/bash
#
# 网站备份脚本
# 整合自 website-backup 和 website-restore
#

SERVER_IP="106.54.25.161"
SERVER_PASS="Zr123456"
WEBSITE_DIR="/usr/share/nginx/html"
BACKUP_DIR="/tmp"
DATE=$(date +%Y-%m-%d)

echo "============================================================"
echo "🌐 网站备份 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# 在服务器上执行备份
echo -e "\n📦 正在备份网站..."
sshpass -p $SERVER_PASS ssh root@$SERVER_IP "
cd $WEBSITE_DIR

# 打包备份（排除 downloads 目录下的 tar.gz 文件，避免循环备份）
tar -czvf /tmp/xuezi-tools-backup-${DATE}.tar.gz \
  --exclude='downloads/*.tar.gz' \
  --exclude='node_modules' \
  --exclude='.git' \
  .

echo '备份完成: /tmp/xuezi-tools-backup-${DATE}.tar.gz'
ls -lh /tmp/xuezi-tools-backup-${DATE}.tar.gz
" 2>/dev/null

# 下载备份到本地
echo -e "\n📥 正在下载备份..."
if sshpass -p $SERVER_PASS scp root@$SERVER_IP:/tmp/xuezi-tools-backup-${DATE}.tar.gz $BACKUP_DIR/ 2>/dev/null; then
    echo "  ✅ 备份下载成功: $BACKUP_DIR/xuezi-tools-backup-${DATE}.tar.gz"
    
    # 显示备份大小
    ls -lh $BACKUP_DIR/xuezi-tools-backup-${DATE}.tar.gz
else
    echo "  ❌ 备份下载失败"
    exit 1
fi

# 可选：上传到坚果云（如果有配置）
if [ -f "$HOME/.nutstore_config" ]; then
    echo -e "\n☁️  上传到坚果云..."
    # 这里可以添加坚果云上传命令
    echo "  ℹ️  坚果云上传功能待配置"
fi

echo -e "\n============================================================"
echo "✅ 网站备份完成"
echo "============================================================"
echo ""
echo "备份文件: $BACKUP_DIR/xuezi-tools-backup-${DATE}.tar.gz"
echo "恢复命令: bash ~/.openclaw/workspace/skills/system-backup/website_restore.sh $BACKUP_DIR/xuezi-tools-backup-${DATE}.tar.gz"
