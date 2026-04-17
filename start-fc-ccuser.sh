#!/bin/bash
source ~/.nvm/nvm.sh
nvm use 20 > /dev/null 2>&1
cd ~/feishu-claude-code
export ANTHROPIC_BASE_URL="http://localhost:3456"
export ANTHROPIC_API_KEY="dummy-key"
export CLAUDE_PERMISSION_MODE=bypassPermissions
exec node dist/index.js
