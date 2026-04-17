#!/bin/bash
pkill -f 'feishu-claude' 2>/dev/null
sleep 1
cd /root/feishu-claude-code
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 20 > /dev/null 2>&1
nohup node dist/index.js > /root/feishu-claude-code.log 2>&1 &
echo "Started"
