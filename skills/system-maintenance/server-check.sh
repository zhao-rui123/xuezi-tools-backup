#!/bin/bash
#
# 服务器快速检查脚本
# 整合自 server-monitor
#

SERVER_IP="106.54.25.161"
SERVER_PASS="Zr123456"

echo "============================================================"
echo "☁️  服务器快速检查 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# 检查可访问性
echo -e "\n📡 检查服务器可访问性..."
if ping -c 1 -W 3 $SERVER_IP > /dev/null 2>&1; then
    echo "  ✅ 服务器可访问"
else
    echo "  ❌ 服务器无法访问"
    exit 1
fi

# 检查磁盘空间
echo -e "\n💾 检查磁盘空间..."
disk_usage=$(sshpass -p $SERVER_PASS ssh root@$SERVER_IP "df -h / | tail -1 | awk '{print \$5}' | sed 's/%//'" 2>/dev/null)
if [ -n "$disk_usage" ]; then
    if [ "$disk_usage" -lt 70 ]; then
        echo "  ✅ 磁盘使用率: ${disk_usage}%"
    elif [ "$disk_usage" -lt 85 ]; then
        echo "  ⚠️  磁盘使用率: ${disk_usage}% (需关注)"
    else
        echo "  🔴 磁盘使用率: ${disk_usage}% (危险)"
    fi
else
    echo "  ❌ 无法获取磁盘信息"
fi

# 检查内存
echo -e "\n🧠 检查内存使用..."
memory_info=$(sshpass -p $SERVER_PASS ssh root@$SERVER_IP "free -h | grep Mem" 2>/dev/null)
if [ -n "$memory_info" ]; then
    echo "  $memory_info"
else
    echo "  ❌ 无法获取内存信息"
fi

# 检查 Nginx
echo -e "\n🌐 检查 Nginx 状态..."
nginx_status=$(sshpass -p $SERVER_PASS ssh root@$SERVER_IP "systemctl is-active nginx" 2>/dev/null)
if [ "$nginx_status" = "active" ]; then
    echo "  ✅ Nginx 运行中"
else
    echo "  ❌ Nginx 未运行"
fi

# 检查网站可访问性
echo -e "\n🌍 检查网站可访问性..."
if curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP/ | grep -q "200\|301\|302"; then
    echo "  ✅ 网站可访问"
else
    echo "  ❌ 网站无法访问"
fi

echo -e "\n============================================================"
echo "✅ 服务器检查完成"
echo "============================================================"
