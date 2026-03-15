#!/bin/bash
# 系统监控看板后端启动脚本

cd "$(dirname "$0")"

echo "🚀 启动系统监控看板后端API..."
echo ""

# 检查依赖
python3 -c "import flask, flask_cors, psutil" 2>/dev/null || {
    echo "❌ 缺少依赖，正在安装..."
    pip3 install flask flask-cors psutil --break-system-packages
}

# 启动服务
python3 app.py --host 0.0.0.0 --port 5000 "$@"
