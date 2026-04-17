# 韩国CC Codex后台调用完全指南

> 本文档是雪子助手调用韩国服务器Codex的完整索引
> 更新：2026-04-17（验证acpx --no-wait模式可用）

---

## 韩国服务器信息

| 项目 | 值 |
|------|-----|
| **IP** | 43.108.18.71 |
| **用户** | ccuser |
| **SSH密钥** | ~/.ssh/id_ed25519 |
| **acpx路径** | /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx |
| **omx路径** | /home/ccuser/.nvm/versions/node/v20.20.2/bin/omx |
| **codex路径** | /usr/local/bin/codex |

---

## 一、acpx codex 后台调用（核心方式）

### 原理
- `codex exec` 会话超时被杀
- `acpx codex --no-wait` 任务在独立后台进程跑，不超时

### 标准流程

```bash
# 第一步：创建持久session（一次性）
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx codex sessions new --name my-session'"

# 第二步：后台丢任务（必须在session的cwd目录下执行）
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && cd /home/ccuser && /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx codex -s my-session --no-wait \"任务描述\"'"

# 查看状态
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c '/home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex status'"

# 查看session列表
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c '/home/ccuser/.nvm/versions/node/v18.20.8/bin/acpx codex sessions'"
```

### 快速命令模板

```bash
# 创建session
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx codex sessions new --name <name>'"

# 后台调用（注意：必须在session的cwd目录下执行）
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && cd /home/ccuser && /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx codex -s <session-name> --no-wait \"<task>\"'"

# 查看日志
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "tail -f /home/ccuser/.acpx/sessions/<session-id>.stream.ndjson"
```

### 常见问题

| 问题 | 解决 |
|------|------|
| `agent needs reconnect` | 重新sessions new |
| `No acpx session found` | 在session的cwd目录(/home/ccuser)下执行 |
| `⚠ No acpx session found` | 使用完整路径调用acpx，并cd到/home/ccuser |

### 关键要点（2026-04-17验证）

1. **必须使用完整路径**：`/home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx`
2. **必须在session目录执行**：`cd /home/ccuser`（session默认cwd）
3. **必须source nvm.sh**：加载Node环境
4. **--no-wait模式**：任务在独立后台进程跑，完全不超时 ✅

---

## 二、omx exec 调用（omx工作流）

### omx简介
- oh-my-codex是Codex的编排层
- 内置20个专业Agent
- 支持skill/keyword路由

### 常用命令

```bash
# 非交互式执行
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v20.20.2/bin/omx exec \"任务\" --skip-git-repo-check'"

# 指定Agent执行
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v20.20.2/bin/omx exec --agent architect \"系统设计任务\"'"
```

### 20个专业Agent

| Agent | 职责 |
|-------|------|
| architect | 系统设计、架构边界 |
| planner | 任务拆解、执行计划 |
| executor | 代码实现、重构 |
| analyst | 需求澄清、验收标准 |
| critic | 计划/设计审查 |
| code-reviewer | 全方位代码审查 |
| security-reviewer | 安全漏洞检查 |
| debugger | 根因分析、回归隔离 |
| test-engineer | 测试策略、覆盖率 |
| researcher | 外部文档调研 |
| designer | UX/UI设计 |
| writer | 文档编写 |
| explore | 快速代码库搜索 |
| vision | 图片/截图分析 |
| git-master | Git提交策略 |
| verifier | 完成验证 |
| team-executor | 团队协作执行 |

### omx Skills（工作流）

| Skill | 触发词 | 功能 |
|-------|--------|------|
| $autopilot | autopilot: | 全自主执行 |
| $deep-interview | deep-interview: | 苏格拉底式深度访谈 |
| $plan | plan: / ralplan: | 战略规划、任务拆解 |
| $team | team N: | N个Agent并行协作 |
| $code-review | code-review: | 一键代码审查 |

---

## 三、Codex登录状态

```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'codex login status'"
```

当前状态：`Logged in using ChatGPT`

### 重新登录（如果token过期）
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'codex auth login --device-auth'"
```

---

## 四、日志查看

### acpx session日志
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "tail -f /home/ccuser/.acpx/sessions/<session-id>.stream.ndjson"
```

### 查看任务输出
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "cat /home/ccuser/.acpx/sessions/<session-id>.stream.ndjson | grep 'stdout' | tail -5"
```

---

## 五、我调用韩国CC的完整流程

```bash
# 1. 创建session
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx codex sessions new --name bg-call'"

# 2. 丢任务（必须在/home/ccuser目录下执行）
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && cd /home/ccuser && /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx codex -s bg-call --no-wait \"任务描述\"'"

# 3. 等待几秒后查看结果
sleep 20 && ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "cat /home/ccuser/.acpx/sessions/*.stream.ndjson 2>/dev/null | grep 'stdout' | tail -3"
```

---

## 六、完整示例

### 示例1：让Codex写Python脚本（验证可用）
```bash
# 创建session
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx codex sessions new --name py-task'"

# 丢任务（必须在/home/ccuser目录下执行）
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && cd /home/ccuser && /home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx codex -s py-task --no-wait \"用Python写一个快速排序算法，保存到 /home/ccuser/codex-workspace/quick_sort.py\"'"

# 查看结果
sleep 30
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "cat /home/ccuser/codex-workspace/quick_sort.py 2>/dev/null"
```

### 示例2：用omx autopilot模式
```bash
ssh -i ~/.ssh/id_ed25519 root@43.108.18.71 "su - ccuser -c 'source ~/.nvm/nvm.sh && /home/ccuser/.nvm/versions/node/v20.20.2/bin/omx exec \"autopilot: 开发一个REST API\" --skip-git-repo-check'"
```

---

## 七、注意事项

1. **session管理**：session会保持活跃，但建议用完就删
2. **token状态**：Codex用ChatGPT登录，需确保token有效
3. **omx调用**：omx exec会启动持久会话，适合长时间任务
4. **acpx调用**：acpx --no-wait是纯后台方式，推荐使用

---

## 八、相关文档

- 原始指南：韩国用户发的 `codex-background-call.md`
- acpx配置：/home/ccuser/.claude/memory/acpx-and-oh-my-codex.md
- 飞书教程：~/.openclaw/workspace/docs/飞书机器人ClaudeCode连接教程.md
