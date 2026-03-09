#!/bin/bash
# 部署小龙虾之家完整版（前端+后端API）

set -e

LOCAL_DIR="/Users/zhaoruicn/.openclaw/workspace/my-lobster-home"
REMOTE_HOST="root@106.54.25.161"
REMOTE_DIR="/usr/share/nginx/html/my-home"
API_DIR="/opt/lobster-home"
PASSWORD="Zr123456"

echo "🏠 部署小龙虾之家完整版..."
echo ""

# 1. 部署前端文件
echo "📁 1. 部署前端文件..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $REMOTE_HOST "mkdir -p $REMOTE_DIR/{css,js,data}"

sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/index.html" $REMOTE_HOST:$REMOTE_DIR/
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/css/style.css" $REMOTE_HOST:$REMOTE_DIR/css/
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/js/dashboard.js" $REMOTE_HOST:$REMOTE_DIR/js/

# 2. 部署后端API
echo "📦 2. 部署后端API..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $REMOTE_HOST "mkdir -p $API_DIR"

sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/api_server.py" $REMOTE_HOST:$API_DIR/
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_DIR/lobster_client.py" $REMOTE_HOST:$API_DIR/

# 3. 安装依赖并启动服务
echo "🚀 3. 安装依赖并启动API服务..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $REMOTE_HOST "
    # 安装Flask
    pip3 install flask flask-cors -q 2>/dev/null || echo 'Flask已安装'
    
    # 创建数据目录
    mkdir -p $API_DIR/data
    
    # 停止旧服务
    pkill -f 'api_server.py' 2>/dev/null || true
    
    # 启动新服务
    cd $API_DIR
    nohup python3 api_server.py > /tmp/lobster_api.log 2>&1 &
echo 'API服务已启动'
    
    sleep 2
    
    # 检查服务状态
    if pgrep -f 'api_server.py' > /dev/null; then
        echo '✅ API服务运行正常'
    else
        echo '❌ API服务启动失败，查看日志: /tmp/lobster_api.log'
    fi
"

# 4. 设置权限
echo "🔐 4. 设置权限..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $REMOTE_HOST "chmod -R 755 $REMOTE_DIR $API_DIR"

echo ""
echo "🎉 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "  前端: http://106.54.25.161/my-home/"
echo "  API: http://106.54.25.161:5000/api/status"
echo ""
echo "📊 API接口:"
echo "  GET  /api/status      - 获取当前状态"
echo "  POST /api/task/start  - 开始任务"
echo "  POST /api/task/complete - 完成任务"
echo "  GET  /api/summary     - 获取每日总结"
echo ""
echo "🧪 测试命令:"
echo "  curl http://106.54.25.161:5000/api/status"
