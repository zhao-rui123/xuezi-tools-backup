#!/bin/bash

# 电价查询系统V4 - 部署脚本
# 部署到腾讯云服务器

set -e

echo "======================================"
echo "电价查询系统V4 - 部署脚本"
echo "======================================"

# 配置
SERVER_IP="106.54.25.161"
SERVER_USER="root"
SERVER_PASS="Zr123456"
REMOTE_DIR="/usr/share/nginx/html/electricity-v4"
LOCAL_DIR="/Users/zhaoruicn/.openclaw/workspace/projects/electricity-v4"

echo ""
echo "[1/5] 检查本地文件..."

# 检查必要文件
if [ ! -f "$LOCAL_DIR/index.html" ]; then
    echo "❌ 错误: index.html 不存在"
    exit 1
fi

if [ ! -f "$LOCAL_DIR/data/price-data.js" ]; then
    echo "❌ 错误: data/price-data.js 不存在"
    exit 1
fi

if [ ! -f "$LOCAL_DIR/js/app.js" ]; then
    echo "❌ 错误: js/app.js 不存在"
    exit 1
fi

if [ ! -f "$LOCAL_DIR/js/price-service.js" ]; then
    echo "❌ 错误: js/price-service.js 不存在"
    exit 1
fi

if [ ! -f "$LOCAL_DIR/css/styles.css" ]; then
    echo "❌ 错误: css/styles.css 不存在"
    exit 1
fi

echo "✅ 本地文件检查通过"

echo ""
echo "[2/5] 创建远程目录..."

sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "
    mkdir -p $REMOTE_DIR
    mkdir -p $REMOTE_DIR/data
    mkdir -p $REMOTE_DIR/js
    mkdir -p $REMOTE_DIR/css
    mkdir -p $REMOTE_DIR/api
    echo '目录创建完成'
"

echo "✅ 远程目录创建完成"

echo ""
echo "[3/5] 上传文件..."

# 上传文件
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/index.html" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/data/price-data.js" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/data/"
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/js/app.js" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/js/"
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/js/price-service.js" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/js/"
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/js/config.js" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/js/"
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/css/styles.css" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/css/"
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/api/price-data.js" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/api/"

echo "✅ 文件上传完成"

echo ""
echo "[4/5] 设置文件权限..."

sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "
    chmod -R 755 $REMOTE_DIR
    chown -R www-data:www-data $REMOTE_DIR
    echo '权限设置完成'
"

echo "✅ 文件权限设置完成"

echo ""
echo "[5/5] 验证部署..."

# 检查文件是否存在
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "
    echo '检查部署文件...'
    ls -la $REMOTE_DIR/
    echo ''
    echo '检查data目录...'
    ls -la $REMOTE_DIR/data/
    echo ''
    echo '检查js目录...'
    ls -la $REMOTE_DIR/js/
    echo ''
    echo '检查css目录...'
    ls -la $REMOTE_DIR/css/
"

echo ""
echo "======================================"
echo "✅ 部署完成!"
echo "======================================"
echo ""
echo "访问地址: http://$SERVER_IP/electricity-v4/"
echo ""
