# AI Coder

安全的 Python CLI 工具，统一调用本地 Claude Code 和韩国 Codex。

## 功能

- **双平台支持**：本地 Claude (MiniMax/Opus) + 韩国 Codex (GPT-5.4)
- **安全设计**：防命令注入、严格 SSH 验证、输入净化
- **Session 管理**：创建、关闭、状态查询
- **后台模式**：`--no-wait` 不阻塞执行
- **Skills 支持**：OMC/OMX 技能调用

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
├── executors/          # 本地/远程执行器
├── config/             # 配置管理
├── security/           # 安全模块
├── background/         # 后台任务管理
├── skills/             # Skills 系统
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
