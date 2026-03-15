#!/bin/bash
# 修复看板API脚本
# 在服务器上执行: bash fix_dashboard_apis.sh

echo "=== 修复看板API ==="

# 1. 重启小龙虾之家API (5000)
echo "1. 重启小龙虾之家API..."
pkill -f api_simple.py
sleep 1
cd /opt/lobster-home
nohup python3 api_simple.py > /var/log/lobster-api.log 2>&1 &
sleep 2
echo "   状态: $(curl -s http://localhost:5000/api/status 2>/dev/null | head -c 50)"

# 2. 检查服务器监控API (5001)
echo ""
echo "2. 检查服务器监控API..."
echo "   状态: $(curl -s http://localhost:5001/api/server/realtime 2>/dev/null | head -c 50)"

# 3. 修复备份监控API (5002)
echo ""
echo "3. 修复备份监控API..."
pkill -f backup_status.py
sleep 1

cat > /opt/server-monitor/backup_api.py << 'PYEOF'
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)

@app.route('/api/backup/status')
def get_status():
    today = datetime.now().strftime('%Y%m%d')
    backup_dir = Path('/Volumes/cu/ocu/full-backups')
    
    # 查找今日备份文件
    files = list(backup_dir.glob(f'openclaw-backup-{today}*.tar.gz')) if backup_dir.exists() else []
    
    if files:
        size_mb = files[0].stat().st_size / (1024*1024)
        size_str = f'{size_mb:.0f}MB' if size_mb < 1024 else f'{size_mb/1024:.1f}GB'
        return jsonify({
            'status': 'success',
            'message': '✅ 今日备份成功',
            'backup_size': size_str,
            'last_backup_time': '22:00',
            'next_backup': '明天 22:00'
        })
    else:
        return jsonify({
            'status': 'pending',
            'message': '⏳ 等待备份',
            'backup_size': '未知',
            'next_backup': '今天 22:00'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
PYEOF

cd /opt/server-monitor
nohup python3 backup_api.py > /var/log/backup-api.log 2>&1 &
sleep 2
echo "   状态: $(curl -s http://localhost:5002/api/backup/status 2>/dev/null | head -c 100)"

echo ""
echo "=== 修复完成 ==="
echo "测试看板: http://106.54.25.161/dashboard/"
