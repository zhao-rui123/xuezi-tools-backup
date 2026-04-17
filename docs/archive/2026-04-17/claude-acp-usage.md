# Claude Code ACP 调用指南

## 快速开始

### 1. 确保电脑上 Claude 已关闭
Claude Code 只能单实例运行，必须先关闭 GUI 版 Claude。

### 2. 创建/使用 session

```bash
# 创建新 session（推荐 --ttl 0 永久保持）
acpx claude sessions new --name my-session

# 或直接使用（自动创建临时 session）
acpx claude "任务描述" --approve-all
```

### 3. 执行命令

```bash
# 使用指定 session
acpx claude -s my-session "任务描述" --approve-all

# 长时间任务（120秒超时）
acpx claude --timeout 120 "复杂任务" --approve-all

# 永久 session + 长时间任务
acpx claude -s my-session --ttl 0 --timeout 600 "长时间任务" --approve-all
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `acpx claude sessions new --name <name>` | 创建新 session |
| `acpx claude sessions list` | 列出所有 session |
| `acpx claude sessions close <name>` | 关闭 session |
| `acpx claude -s <name> "prompt"` | 使用指定 session 执行 |
| `acpx claude status` | 查看当前状态 |

## 权限选项

| 选项 | 说明 |
|------|------|
| `--approve-all` | 自动批准所有权限请求 |
| `--approve-reads` | 自动批准读/搜索，写操作需确认 |
| `--deny-all` | 拒绝所有权限请求 |

## 当前配置

- **模型**: MiniMax-M2.7（通过 ~/.claude/settings.json 配置）
- **默认 TTL**: 300秒（5分钟空闲后关闭）
- **默认权限**: approve-all

## 切换到 Opus（未来需要时）

编辑 `~/.claude/settings.json`:
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://timesniper.club",
    "ANTHROPIC_AUTH_TOKEN": "sk-OLqePftCUT0kOGggfgGtgeMOE3km0hPXwxUf6FTpFFL7mdsJ",
    "ANTHROPIC_MODEL": "claude-opus-4-6"
  }
}
```

## OpenClaw 集成

```javascript
// 通过 sessions_spawn 调用
sessions_spawn({
  task: "任务描述",
  runtime: "acp",
  agentId: "claude",
  runTimeoutSeconds: 600
})
```

## 注意事项

1. **必须先关闭电脑的 Claude GUI**，否则 acpx 启动会失败
2. **session 默认 5分钟后关闭**，长时间任务用 `--ttl 0`
3. **模型配置在 ~/.claude/settings.json**，acpx 环境变量会被覆盖
