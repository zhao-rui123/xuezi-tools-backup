# AI Coder 快速参考

## 一键执行

```bash
# 本地（Opus/MiniMax）
python3 -m ai_coder exec "任务" -p local

# 韩国（Codex GPT-5.4）
python3 -m ai_coder exec "任务" -p kr
```

## Session 管理

```bash
# 创建
python3 -m ai_coder session-new NAME -p local

# 关闭
python3 -m ai_coder session-close NAME -p local

# 状态
python3 -m ai_coder status -p local -s NAME
```

## 后台模式

```bash
# 不等待，立即返回
python3 -m ai_coder exec "任务" -p local --no-wait
```

## 子 Agent 调用（推荐）

```python
sessions_spawn({
    "task": "python3 -m ai_coder exec '任务' -p local --wait",
    "runtime": "subagent",
    "runTimeoutSeconds": 300
})
```

## 环境变量

```bash
export AI_CODER_KR_HOST="43.108.18.71"
export AI_CODER_KR_USER="ccuser"
export AI_CODER_SSH_KEY="~/.ssh/id_ed25519"
```

## 测试

```bash
python3 -m pytest tests/ -v
```
