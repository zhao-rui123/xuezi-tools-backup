#!/bin/bash
# 部署温馨小家到云服务器

set -e

LOCAL_DIR="/Users/zhaoruicn/.openclaw/workspace/my-lobster-home"
REMOTE_HOST="root@106.54.25.161"
REMOTE_DIR="/usr/share/nginx/html/my-home"
PASSWORD="Zr123456"

echo "🏠 部署雪子助手的温馨小家..."
echo ""

# 创建远程目录
echo "📁 创建目录..."
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
echo "🎉 温馨小家装修完成！"
echo ""
echo "🏠 访问地址: http://106.54.25.161/my-home/"
echo ""
echo "房子布局:"
echo "  🍵 茶水室    🍳 厨房    🎮 游戏室"
echo "  🚽 卫生间·东  📺 客厅   💻 工作室"
echo "  🍽️ 餐厅"
echo "  🚽 卫生间·西  🛏️ 主卧"
echo "        ↓"
echo "    🌞 阳台运动场"
