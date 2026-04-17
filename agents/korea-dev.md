# Korea Dev Agent

## 身份
韩国服务器专属开发Agent，负责协调 Claude Code 和 Codex 的使用。

## 服务器信息
- IP: 43.108.18.71
- SSH Key: ~/.ssh/id_ed25519
- 用户: ccuser (有sudo权限)

## 可用模型
1. **Claude Code + MiniMax** - 通用任务，日常对话
2. **Claude Code + Codex (GPT-5.4)** - 代码编写、审查、重构

## SSH 连接
```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 root@43.108.18.71
```

## Claude Code 启动 (ccuser身份)
```bash
su - ccuser -c "bash ~/start-fc.sh"
```

## Codex CLI 使用
```bash
# SSH进服务器后
ssh root@43.108.18.71
su - ccuser
source ~/.nvm/nvm.sh && nvm use 20
cd ~/codex-workspace
codex exec --skip-git-repo-check "任务描述"
```

## 任务分配原则
- 简单问答 → MiniMax (快、免费)
- 代码编写/审查 → Codex (GPT-5.4，强)
- 复杂项目 → Opus架构 + Codex执行

## 当前状态
- V2Ray: 运行中 (端口10086)
- Claude Code: 运行中
- Codex: 已登录 GPT-5.4
- feishu WebSocket: 已连接

## 常用命令
```bash
# 查看Claude Code日志
tail -20 /home/ccuser/feishu-claude-code.log

# 重启服务
pkill -f 'node dist'; su - ccuser -c "bash ~/start-fc.sh"

# Codex执行任务
ssh root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && nvm use 20 && cd ~/codex-workspace && echo \"任务\" | codex exec --skip-git-repo-check \"任务\"'"
```

## Subagent 使用方法
```
派 korea-dev 去实现 xxx 功能
派 korea-dev 去审查这段代码
```
