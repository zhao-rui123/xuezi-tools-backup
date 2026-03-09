#!/bin/bash
# 部署脚本 v2.0 - 上传小龙虾房子看板到云服务器

set -e

LOCAL_DIR="/Users/zhaoruicn/.openclaw/workspace/agent-dashboard-v2"
REMOTE_HOST="root@106.54.25.161"
REMOTE_DIR="/usr/share/nginx/html/agent-dashboard"
PASSWORD="Zr123456"

echo "🏠 部署小龙虾房子看板 v2.0..."
echo ""

# 检查本地目录
if [ ! -d "$LOCAL_DIR" ]; then
    echo "❌ 错误: 本地目录不存在 $LOCAL_DIR"
    exit 1
fi

# 创建远程目录
echo "📁 创建远程目录..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $REMOTE_HOST "mkdir -p $REMOTE_DIR/{css,js,data}"

# 上传文件
echo "📤 上传文件..."

# 上传 HTML
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/index.html" $REMOTE_HOST:$REMOTE_DIR/

# 上传 CSS
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/css/style.css" $REMOTE_HOST:$REMOTE_DIR/css/

# 上传 JS
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/js/dashboard.js" $REMOTE_HOST:$REMOTE_DIR/js/

# 设置权限
echo "🔐 设置权限..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $REMOTE_HOST "chmod -R 755 $REMOTE_DIR && chmod 644 $REMOTE_DIR/index.html $REMOTE_DIR/css/*.css $REMOTE_DIR/js/*.js"

echo ""
echo "🎉 部署成功！"
echo ""
echo "访问地址: http://106.54.25.161/agent-dashboard/"
echo ""
echo "🏠 房子结构:"
echo "  📚 书房(思考)  💻 工作室(工作)  🎮 游戏室(娱乐)"
echo "  🛏️ 休息室(休息)  🚽 卫生间(摸鱼)  🍜 厨房(吃饭)"
echo "  🏃 操场(运动/高强度工作)"
