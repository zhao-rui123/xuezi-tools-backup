#!/bin/bash
export ANTHROPIC_BASE_URL="http://localhost:3456"
export ANTHROPIC_API_KEY="dummy-key"
source /root/.nvm/nvm.sh
nvm use 20 > /dev/null 2>&1
cd /root/feishu-claude-code
exec node dist/index.js
