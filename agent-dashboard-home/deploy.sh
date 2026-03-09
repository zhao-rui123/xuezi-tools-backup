#!/bin/bash
# 部署小龙虾之家到云服务器

set -e

LOCAL_DIR="/Users/zhaoruicn/.openclaw/workspace/agent-dashboard-home"
REMOTE_HOST="root@106.54.25.161"
REMOTE_DIR="/usr/share/nginx/html/agent-home"
PASSWORD="Zr123456"

echo "🏠 部署小龙虾之家（四室两厅）..."
echo ""

# 创建远程目录
echo "📁 创建远程目录..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $REMOTE_HOST "mkdir -p $REMOTE_DIR/{css,js,data}"

# 上传文件
echo "📤 上传文件..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/index.html" $REMOTE_HOST:$REMOTE_DIR/
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/css/style.css" $REMOTE_HOST:$REMOTE_DIR/css/
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/js/dashboard.js" $REMOTE_HOST:$REMOTE_DIR/js/

# 设置权限
echo "🔐 设置权限..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $REMOTE_HOST "chmod -R 755 $REMOTE_DIR"

echo ""
echo "🎉 部署成功！"
echo ""
echo "🏠 访问地址: http://106.54.25.161/agent-home/"
echo ""
echo "房子结构:"
echo "  🛏️ 卧室      🎮 游戏室"
echo "  📺 客厅      💻 工作室"
echo "  🍽️ 餐厅      🚽 卫生间"
echo "         ↓"
echo "      🏃 运动场"
