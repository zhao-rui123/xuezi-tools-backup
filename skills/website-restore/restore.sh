#!/bin/bash
# 从坚果云恢复网站到腾讯云

WEBDAV_URL="https://dav.jianguoyun.com/dav/OpenClaw/website-backup/"
USERNAME="1034440765@qq.com"
PASSWORD="azevrhj4j6igpt9q"
BACKUP_FILE="xuezi-tools-full-backup-20260224_134314.tar.gz"

echo "=========================================="
echo "  雪子的智能工具包 - 网站恢复脚本"
echo "=========================================="
echo ""

echo "[1/5] 正在下载备份..."
curl -u "${USERNAME}:${PASSWORD}" \
  -o /tmp/${BACKUP_FILE} \
  "${WEBDAV_URL}${BACKUP_FILE}"

if [ $? -ne 0 ]; then
    echo "下载失败！请检查网络和认证信息"
    exit 1
fi
echo "下载完成"
echo ""

echo "[2/5] 正在备份当前网站..."
cd /usr/share/nginx/html
tar -czvf /tmp/xuezi-tools-backup-before-restore-$(date +%Y%m%d).tar.gz --exclude='*.tar.gz' .
echo "当前网站已备份到: /tmp/xuezi-tools-backup-before-restore-$(date +%Y%m%d).tar.gz"
echo ""

echo "[3/5] 正在恢复网站..."
find . -not -name '*.tar.gz' -not -name '.' -not -name '..' -delete
tar -xzvf /tmp/${BACKUP_FILE} -C /usr/share/nginx/html/
chmod -R 755 /usr/share/nginx/html/*
chmod 644 /usr/share/nginx/html/*/index.html
echo "恢复完成"
echo ""

echo "[4/5] 重启Nginx..."
nginx -t && nginx -s reload
echo ""

echo "[5/5] 验证网站..."
echo "主站: http://106.54.25.161/"
echo "电价查询: http://106.54.25.161/electricity/"
echo "电气接线图: http://106.54.25.161/electrical/"
echo "股票筛选: http://106.54.25.161/stock8090/"
echo ""
echo "=========================================="
echo "  恢复完成！"
echo "=========================================="
