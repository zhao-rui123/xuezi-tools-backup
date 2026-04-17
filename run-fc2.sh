#!/bin/bash
pkill -f 'feishu-claude' 2>/dev/null
sleep 1
cd /root/feishu-claude-code
source /root/.nvm/nvm.sh
nvm use 20
nohup node dist/index.js > /root/feishu-claude-code.log 2>&1 &
echo "Started with Node $(node --version)"
