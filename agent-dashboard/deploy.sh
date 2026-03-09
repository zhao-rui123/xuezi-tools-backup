#!/bin/bash
# 部署脚本 - 上传任务看板到云服务器

set -e

# 配置
LOCAL_DIR="/Users/zhaoruicn/.openclaw/workspace/agent-dashboard"
REMOTE_HOST="root@106.54.25.161"
REMOTE_DIR="/usr/share/nginx/html/agent-dashboard"
PASSWORD="Zr123456"

echo "🦞 部署小龙虾任务看板..."
echo ""

# 检查本地目录
if [ ! -d "$LOCAL_DIR" ]; then
    echo "❌ 错误: 本地目录不存在 $LOCAL_DIR"
    exit 1
fi

# 创建远程目录
echo "📁 创建远程目录..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $REMOTE_HOST "mkdir -p $REMOTE_DIR/{css,js,assets,data}"

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

# 验证部署
echo "✅ 验证部署..."
DEPLOYED=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $REMOTE_HOST "ls -la $REMOTE_DIR/" 2>/dev/null || echo "FAILED")

if echo "$DEPLOYED" | grep -q "index.html"; then
    echo ""
    echo "🎉 部署成功！"
    echo ""
    echo "访问地址:"
    echo "  http://106.54.25.161/agent-dashboard/"
    echo ""
else
    echo ""
    echo "⚠️ 部署可能有问题，请手动检查"
    exit 1
fi
