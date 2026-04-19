# AI Coder

安全的 Python CLI 工具，统一调用本地 Claude Code 和韩国 Codex。

## 功能

- **双平台支持**：本地 Claude (MiniMax/Opus) + 韩国 Codex (GPT-5.4)
- **安全设计**：防命令注入、严格 SSH 验证、输入净化
- **Session 管理**：创建、关闭、状态查询
- **后台模式**：`--no-wait` 不阻塞执行
- **Skills 支持**：OMC/OMX 技能调用
- **自动重试**：失败自动重试 + 飞书告警 + 审计日志

## 安装

```bash
pip3 install click paramiko
cd ai_coder
python3 -m pip install -e .
```

## 配置

### 环境变量

```bash
# 本地（可选）
export AI_CODER_LOCAL_ACPX="acpx"
export AI_CODER_WORKSPACE="~/.openclaw/workspace"

# 韩国服务器（使用 kr 时必须）
export AI_CODER_KR_HOST="43.108.18.71"
export AI_CODER_KR_USER="ccuser"
export AI_CODER_SSH_KEY="~/.ssh/id_ed25519"
```

### 配置文件

```yaml
# ~/.ai_coder/config.yaml
local:
  acpx_path: acpx
  workspace: ~/.openclaw/workspace

remote:
  host: 43.108.18.71
  user: ccuser
  ssh_key: ~/.ssh/id_ed25519
```

## 韩国 Codex 工作流

### 核心原则：任务分类决定工作流

| 任务类型 | 工作流 | 说明 |
|---------|--------|------|
| **分析/思考类** | 直接调用 | 代码无需修改，直接分析 |
| **代码编写/修改** | rsync → Codex → rsync | 需要修改服务器上的代码 |

### 分析/思考类任务

适用：代码审查、架构建议、需求分析、文档撰写

```bash
# 直接执行，无需 rsync
python3 -m ai_coder exec "分析这段代码的性能问题..." -p kr
```

### 代码编写/修改任务

适用：新功能编写、代码修改、重构

**Step 1: 同步代码到韩国服务器**
```bash
rsync -az --delete -e "ssh -i ~/.ssh/id_ed25519" \
  ~/.openclaw/workspace/ai_coder/ \
  root@43.108.18.71:/home/ccuser/ai-coder/
```

**Step 2: 创建 session 并设置 full-access**
```bash
# 创建 session
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 \
  "su - ccuser -c 'source ~/.nvm/nvm.sh && \
  /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex sessions new --name code-task'"

# 设置 full-access（必须！否则无法写文件）
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 \
  "su - ccuser -c 'source ~/.nvm/nvm.sh && \
  /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex -s code-task set-mode full-access'"
```

**Step 3: 丢任务给 Codex**
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 \
  "su - ccuser -c 'source ~/.nvm/nvm.sh && cd /home/ccuser && \
  /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex -s code-task --no-wait \
  \"实现重试功能：创建 core/retry.py，添加 RetryExecutor 类\"'"
```

**Step 4: 同步代码回本地**
```bash
rsync -az -e "ssh -i ~/.ssh/id_ed25519" \
  root@43.108.18.71:/home/ccuser/ai-coder/ \
  ~/.openclaw/workspace/ai_coder/
```

### 任务描述最佳实践

```
# ❌ 不好 - Codex 不知道要做什么
"实现重试功能"

# ✅ 好 - 完整的任务描述
"在 /home/ccuser/ai-coder/core/retry.py 中实现 RetryExecutor 类：
1. 接受 max_retries=3, retry_delay=5 参数
2. 失败后发送飞书告警
3. 审计日志写入 data/tasks.jsonl
使用 Python 标准库，仅用 urllib 发 HTTP 请求。"
```

## 使用

### 本地执行

```bash
# 执行单次任务
python3 -m ai_coder exec "任务描述" -p local

# 创建 session
python3 -m ai_coder session-new my-session -p local

# 后台执行
python3 -m ai_coder exec "任务" -p local -s my-session --no-wait

# 查询状态
python3 -m ai_coder status -p local -s my-session
```

### 韩国执行

```bash
# 执行单次任务
python3 -m ai_coder exec "任务描述" -p kr

# 创建 session
python3 -m ai_coder session-new kr-session -p kr

# 后台执行
python3 -m ai_coder exec "任务" -p kr -s kr-session --no-wait
```

### 重试配置

RemoteExecutor 支持自动重试：

```python
from ai_coder.executors.remote import RemoteExecutor

executor = RemoteExecutor(
    host="43.108.18.71",
    user="ccuser",
    ssh_key="~/.ssh/id_ed25519",
    acpx_path="/home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx",
    max_retries=3,      # 默认 3 次
    retry_delay=5,      # 默认 5 秒间隔
)
```

失败后会自动：
1. 重试指定次数
2. 全部失败后发送飞书告警
3. 记录审计日志到 `data/tasks.jsonl`

### Skills

```bash
# 列出 skills
python3 -m ai_coder skills

# 执行 skill
python3 -m ai_coder skill omc "任务描述"
```

## 子 Agent 执行（推荐）

为避免阻塞主对话，建议通过子 Agent 调用：

```python
# 主 Agent 启动子 Agent
sessions_spawn({
    "task": "cd ~/.openclaw/workspace && python3 -m ai_coder exec '任务' -p local --wait",
    "runtime": "subagent",
    "runTimeoutSeconds": 300
})
```

### 优势

- ✅ 不阻塞主对话
- ✅ 支持并行执行
- ✅ 超时控制
- ✅ 独立日志

## Session 管理

### 查看活跃 session
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 \
  "su - ccuser -c 'source ~/.nvm/nvm.sh && \
  /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex sessions list'"
```

### 清理 closed session
ai_coder 的 RemoteExecutor 每次执行前会自动清理 closed sessions。

手动清理：
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 \
  "su - ccuser -c 'source ~/.nvm/nvm.sh && \
  /home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex sessions list'" \
  | grep "\[closed\]" | awk '{print $1}' | tr -d '[]' | while read sid; do
  ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 \
    "rm -f /home/ccuser/.acpx/sessions/${sid}*.json"
done
```

## 安全特性

| 特性 | 实现 |
|------|------|
| 输入净化 | 危险字符/模式检测，拒绝而非改写 |
| Session 名验证 | 只允许字母数字和连字符 |
| SSH 安全 | `RejectPolicy()` 严格 host key 验证 |
| 无 shell 拼接 | 参数列表传递，`shlex.join()` |
| 配置懒加载 | 本地运行时不需要韩国配置 |

## 测试

```bash
cd ai_coder
python3 -m pytest tests/ -v
```

## 目录结构

```
ai_coder/
├── cli.py              # CLI 入口
├── core/               # 核心模型
│   ├── retry.py        # 重试 + 告警 + 审计
│   └── ...
├── executors/          # 本地/远程执行器
├── config/             # 配置管理
├── security/           # 安全模块
├── background/         # 后台任务管理
├── skills/             # Skills 系统
├── data/               # 审计日志目录
└── tests/              # 测试套件
```

## 开发

### 添加新执行器

1. 继承 `executors/base.py` 的 `BaseExecutor`
2. 实现 `execute()` 和 `is_available()`
3. 在 `executors/factory.py` 注册

### 添加新 Skill

1. 在 `skills/builtin/` 创建 skill 文件
2. 实现 `build_skill()` 函数
3. 在 `cli.py` 注册到 `SkillRegistry`

## 许可证

MIT
