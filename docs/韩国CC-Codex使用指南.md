# 韩国CC Codex 使用指南

> 本文档是雪子助手调用韩国服务器Codex的完整索引
> 更新：2026-04-18（新增full-access模式和rsync工作流）

---

## 韩国服务器信息

| 项目 | 值 |
|------|-----|
| **IP** | 43.108.18.71 |
| **用户** | ccuser |
| **SSH密钥** | ~/.ssh/id_ed25519 |
| **acpx路径** | /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx |
| **Node版本** | v18.20.8 |

---

## 核心原则：任务分类决定工作流

| 任务类型 | 工作流 | 难度 |
|---------|--------|------|
| **分析/思考类** | 直接丢给 Codex | ⭐ 简单 |
| **代码编写/修改** | rsync → Codex → rsync 回来 | ⭐⭐ 中等 |
| **复杂debug/重构** | rsync → Codex → rsync 回来 | ⭐⭐⭐ 复杂 |

---

## 一、分析/思考类任务（直接调用）

**适用场景：**
- 代码审查
- 架构设计建议
- 需求分析
- 文档撰写

**工作流：**
```bash
# 直接执行，无需rsync
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex exec \"分析这段代码的性能问题...\"'"
```

**示例：**
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex exec \"评估这三个改进方向的必要性：1) 任务队列持久化 2) 自动重试+失败告警 3) 任务状态查询API\"'"
```

---

## 二、代码编写/修改任务

**适用场景：**
- 编写新功能
- 修改现有代码
- 添加测试
- 代码重构

### 标准工作流

**Step 1: 同步代码到韩国服务器**
```bash
rsync -az --delete -e "ssh -i ~/.ssh/id_ed25519" \
  ~/.openclaw/workspace/ai_coder/ \
  root@43.108.18.71:/home/ccuser/ai-coder/
```

**Step 2: 创建 session 并设置 full-access**
```bash
# 创建session
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex sessions new --name code-task'"

# 设置full-access（必须！否则无法写文件）
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex -s code-task set-mode full-access'"
```

**Step 3: 丢任务给 Codex**
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex -s code-task --no-wait \"实现以下功能：1) 创建 core/retry.py 2) 添加 RetryExecutor 类 3) 支持自动重试\"'"
```

**Step 4: 同步代码回本地**
```bash
rsync -az -e "ssh -i ~/.ssh/id_ed25519" \
  root@43.108.18.71:/home/ccuser/ai-coder/ \
  ~/.openclaw/workspace/ai_coder/
```

### 关键配置

**ccr_auto_permission_mode: true**
```bash
# 在 ~/.claude.json 中启用（已配置）
"ccr_auto_permission_mode": true,
```

**但要注意：**
- MCP 工具调用（omx_memory, omx_state）仍会被 ccr 拦截
- Codex 只能通过 bash 命令读写文件
- 任务描述要完整，让 Codex 用 bash heredoc 写文件

---

## 三、常用命令速查

### acpx 基本操作

```bash
# 创建 session
acpx codex sessions new --name <name>

# 设置 full-access 模式
acpx codex -s <name> set-mode full-access

# 状态查询
acpx codex -s <name> status

# 关闭 session
acpx codex sessions close <name>

# 列出所有 session
acpx codex sessions list
```

### SSH 完整命令模板

```bash
# 创建 session
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex sessions new --name <name>'"

# 执行任务（分析类）
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex exec \"任务描述\"'"

# 执行任务（代码类，需full-access）
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && cd /home/ccuser && /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex -s <name> --no-wait \"任务描述\"'"
```

---

## 四、Session 管理

### 查看活跃 session
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex sessions list'"
```

### 清理 closed session 文件
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex sessions list'" | grep "\[closed\]" | awk '{print $1}' | tr -d '[]' | while read sid; do
  ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "rm -f /home/ccuser/.acpx/sessions/${sid}*.json"
done
```

### ai_coder 自动清理
ai_coder 的 RemoteExecutor 每次执行前会自动清理 closed sessions。

---

## 五、常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `No acpx session found` | 不在 session 的 cwd 目录 | `cd /home/ccuser` 后执行 |
| MCP 工具调用被取消 | ccr 权限限制 | 用 bash 命令代替 MCP 调用 |
| 无法写入文件 | 不是 full-access 模式 | `set-mode full-access` |
| Session 一直 running | 任务还在执行中 | 等待或 `sessions close` |

---

## 六、日志查看

### acpx session 日志
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "tail -f /home/ccuser/.acpx/sessions/<session-id>.stream.ndjson"
```

### 查看 Codex 输出
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "cat /home/ccuser/.acpx/sessions/<session-id>.stream.ndjson" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        d = json.loads(line)
        if d.get('method') == 'ping': continue
        if 'result' in d and isinstance(d['result'], dict):
            content = d['result'].get('content', [])
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get('type') == 'text':
                        print(c['text'][:500])
    except: pass
"
```

---

## 七、最佳实践

### 1. 任务描述要完整
```
# ❌ 不好 - Codex 不知道要做什么
"实现重试功能"

# ✅ 好 - 完整的任务描述
"在 /home/ccuser/ai-coder/core/retry.py 中实现 RetryExecutor 类：
1. 接受 max_retries=3, retry_delay=5 参数
2. 失败后发送飞书告警到 webhook URL
3. 审计日志写入 /home/ccuser/ai-coder/data/tasks.jsonl
使用 Python 标准库，仅用 urllib 发 HTTP 请求。"
```

### 2. 分析类任务用 exec
```bash
# exec 是单次执行，会话自动关闭
ssh ... "acpx codex exec \"分析代码...\""
```

### 3. 代码类任务用 session + full-access
```bash
# 创建 → 设置full-access → 执行 → 关闭
ssh ... "acpx sessions new --name task"
ssh ... "acpx -s task set-mode full-access"
ssh ... "acpx -s task --no-wait \"写代码任务\""
```

### 4. 用完即删 session
```bash
ssh ... "acpx sessions close <name>"
```

---

## 八、相关文档

- ai_coder: ~/.openclaw/workspace/ai_coder/
- 飞书教程: docs/飞书机器人ClaudeCode连接教程.md
