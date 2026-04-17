# AI Coder Skill

安全调用 Claude Code 和 Codex 的统一 CLI 工具。

## 功能

- 本地 Claude (MiniMax/Opus) 调用
- 韩国 Codex (GPT-5.4) 调用
- Session 管理（创建、关闭、状态查询）
- 后台模式（--no-wait）
- Skills 支持（OMC/OMX）

## 安装

```bash
pip3 install click paramiko
```

## 配置

```bash
# 韩国服务器（必须）
export AI_CODER_KR_HOST="43.108.18.71"
export AI_CODER_KR_USER="ccuser"
export AI_CODER_SSH_KEY="~/.ssh/id_ed25519"
```

## 使用方式

### 方式一：直接执行（测试用）

```bash
cd ~/.openclaw/workspace/ai_coder
python3 -m ai_coder exec "任务" -p local
```

### 方式二：子 Agent 执行（推荐）

```python
sessions_spawn({
    "task": "cd ~/.openclaw/workspace && PYTHONPATH=/Users/zhaoruicn/.openclaw/workspace/ai_coder python3 -m ai_coder exec '任务' -p local --wait",
    "runtime": "subagent",
    "runTimeoutSeconds": 300
})
```

**推荐原因：**
- 不阻塞主对话
- 支持并行执行
- 超时控制

## 命令

| 命令 | 说明 |
|------|------|
| `exec` | 执行单次任务 |
| `session-new` | 创建 session |
| `session-close` | 关闭 session |
| `status` | 查询状态 |
| `skills` | 列出 skills |
| `skill` | 执行 skill |

## 选项

| 选项 | 说明 |
|------|------|
| `-p, --provider` | local 或 kr |
| `-s, --session` | session 名称 |
| `--wait/--no-wait` | 是否等待结果 |
| `--timeout` | 超时秒数 |

## 示例

### 本地架构设计

```python
sessions_spawn({
    "task": "python3 -m ai_coder exec '设计 Flask API 架构' -p local -s arch --wait",
    "runtime": "subagent"
})
```

### 韩国代码实现

```python
sessions_spawn({
    "task": "python3 -m ai_coder exec '实现代码' -p kr -s dev --wait",
    "runtime": "subagent"
})
```

### 后台执行

```python
sessions_spawn({
    "task": "python3 -m ai_coder exec '长任务' -p kr -s bg --no-wait",
    "runtime": "subagent"
})
```

## 安全

- 输入净化（危险字符检测）
- SSH RejectPolicy 严格验证
- 无 shell 字符串拼接
- 配置懒加载

## 测试

```bash
cd ~/.openclaw/workspace/ai_coder
python3 -m pytest tests/ -v
```

## 文档

- `README.md` - 完整文档
- `docs/ai_coder_architecture_opus.md` - 架构设计
