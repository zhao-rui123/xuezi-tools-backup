#!/bin/bash
#
# 网站恢复脚本
# 整合自 website-backup 和 website-restore
#

SERVER_IP="106.54.25.161"
SERVER_PASS="Zr123456"
WEBSITE_DIR="/usr/share/nginx/html"

# 检查参数
if [ -z "$1" ]; then
    echo "用法: $0 <备份文件路径>"
    echo "示例: $0 /tmp/xuezi-tools-backup-2026-03-09.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "============================================================"
echo "🔄 网站恢复 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# 1. 备份当前网站（可选）
echo -e "\n💾 备份当前网站..."
CURRENT_BACKUP="/tmp/xuezi-tools-backup-before-restore-$(date +%Y%m%d).tar.gz"
sshpass -p $SERVER_PASS ssh root@$SERVER_IP "
cd $WEBSITE_DIR
tar -czvf $CURRENT_BACKUP --exclude='*.tar.gz' . 2>/dev/null
echo '当前网站已备份: $CURRENT_BACKUP'
" 2>/dev/null

# 2. 上传备份文件到服务器
echo -e "\n📤 上传备份文件到服务器..."
if sshpass -p $SERVER_PASS scp "$BACKUP_FILE" root@$SERVER_IP:/tmp/restore.tar.gz 2>/dev/null; then
    echo "  ✅ 上传成功"
else
    echo "  ❌ 上传失败"
    exit 1
fi

# 3. 在服务器上执行恢复
echo -e "\n🔄 正在恢复网站..."
sshpass -p $SERVER_PASS ssh root@$SERVER_IP "
cd $WEBSITE_DIR

echo '清空当前网站目录（保留备份文件）...'
find . -not -name '*.tar.gz' -not -name '.' -not -name '..' -delete

echo '解压备份文件...'
tar -xzvf /tmp/restore.tar.gz -C $WEBSITE_DIR/

echo '设置权限...'
chmod -R 755 $WEBSITE_DIR/*
chmod 644 $WEBSITE_DIR/*/index.html

echo '清理临时文件...'
rm -f /tmp/restore.tar.gz

echo '恢复完成'
" 2>/dev/null

# 4. 重启 Nginx
echo -e "\n🔄 重启 Nginx..."
if sshpass -p $SERVER_PASS ssh root@$SERVER_IP "nginx -t && nginx -s reload" 2>/dev/null; then
    echo "  ✅ Nginx 重启成功"
else
    echo "  ⚠️  Nginx 重启可能有问题，请手动检查"
fi

# 5. 验证恢复
echo -e "\n🔍 验证恢复..."
if curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP/ | grep -q "200\|301\|302"; then
    echo "  ✅ 网站可访问"
else
    echo "  ⚠️  网站可能无法正常访问，请检查"
fi

echo -e "\n============================================================"
echo "✅ 网站恢复完成"
echo "============================================================"
echo ""
echo "验证地址:"
echo "  - 主站: http://$SERVER_IP/"
echo "  - 电价查询: http://$SERVER_IP/electricity/"
echo "  - 电气接线图: http://$SERVER_IP/electrical/"
