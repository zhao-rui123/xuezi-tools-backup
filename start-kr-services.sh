#!/bin/bash
# 启动韩国服务器上的所有服务
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 20 > /dev/null 2>&1

# 启动 CCR
nohup ccr start > /tmp/ccr.log 2>&1 &
sleep 3

# 启动 feishu-claude-code
cd /root/feishu-claude-code
nohup npm start > /root/feishu-claude-code.log 2>&1 &

echo "服务启动完成"
echo "CCR PID: $(pgrep -f 'ccr start')"
echo "Feishu PID: $(pgrep -f 'feishu-claude-code')"
