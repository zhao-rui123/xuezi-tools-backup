# AI Coder

安全的 Python CLI 工具，统一调用本地 Claude Code 和韩国 Codex。

## 功能

- **双平台支持**：本地 Claude (MiniMax/Opus) + 韩国 Codex (GPT-5.4)
- **安全设计**：防命令注入、严格 SSH 验证、输入净化
- **Session 管理**：创建、关闭、状态查询
- **后台模式**：`--no-wait` 不阻塞执行
- **Skills 支持**：OMC/OMX 技能调用
- **自动重试**：失败自动重试
- **健康检查**：`ai-coder doctor` 诊断工具

## 安装

```bash
cd ~/.openclaw/workspace/ai_coder
pip3 install -e .
```

## 使用

```bash
# 本地执行（默认）
python3 -m ai_coder exec "任务" -s session名 --wait

# 韩国执行
python3 -m ai_coder exec "任务" -p kr -s session名 --wait

# 健康检查
python3 -m ai_coder doctor
```

## 配置

### 环境变量

```bash
# 韩国服务器（使用 -p kr 时必须）
export AI_CODER_KR_HOST="43.108.18.71"
export AI_CODER_KR_USER="ccuser"
export AI_CODER_KR_SSH_KEY="~/.ssh/id_ed25519"
```

## 命令

| 命令 | 说明 |
|------|------|
| `doctor` | 健康检查 |
| `exec` | 执行单次任务 |
| `session-new NAME` | 创建 session |
| `session-close NAME` | 关闭 session |
| `status -s NAME` | 查询状态 |
| `skills` | 列出 skills |

## 子 Agent 调用

```python
sessions_spawn({
    "task": "cd ~/.openclaw/workspace/ai_coder && python3 -m ai_coder exec '任务' -s SESSION --wait",
    "runtime": "subagent",
    "runTimeoutSeconds": 300
})
```
