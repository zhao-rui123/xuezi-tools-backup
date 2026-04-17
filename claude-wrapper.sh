#!/bin/bash
source /root/.nvm/nvm.sh
nvm use 20 > /dev/null 2>&1
# Start CCR if not running
if ! pgrep -f 'ccr start' > /dev/null 2>&1; then
    nohup ccr start > /tmp/ccr.log 2>&1 &
    sleep 3
fi
export ANTHROPIC_BASE_URL="http://localhost:3456"
export ANTHROPIC_API_KEY="dummy-key"
exec /root/.nvm/versions/node/v20.20.2/bin/node /root/.nvm/versions/node/v20.20.2/lib/node_modules/@anthropic-ai/claude-code/cli.js "$@"
