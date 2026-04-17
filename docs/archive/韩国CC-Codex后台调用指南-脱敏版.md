# 韩国服务器 Codex 后台调用指南（脱敏版）

> 适用环境：韩国阿里云服务器 + OpenAI Codex
> 更新时间：2026-04-14

---

## 一、服务器信息

| 项目 | 示例值 |
|------|--------|
| 服务器IP | 你的服务器IP |
| 用户名 | 用户名（如ccuser） |
| SSH密钥 | ~/.ssh/id_ed25519 |

---

## 二、核心工具

| 工具 | 用途 |
|------|------|
| `acpx` | ACP协议客户端，后台任务调度 |
| `codex` | OpenAI Codex CLI |
| `omx` | oh-my-codex 编排层（20个专业Agent） |

---

## 三、acpx codex 后台调用

### 为什么需要acpx？
- `codex exec` 会话超时被杀
- `acpx codex --no-wait` 任务在独立后台进程跑，不超时

### 标准流程

```bash
# 第一步：创建持久session（一次性）
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c '/path/to/acpx codex sessions new --name my-task'"

# 第二步：后台丢任务
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c '/path/to/acpx codex -s my-task --no-wait \"任务描述\"'"

# 查看状态
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c '/path/to/acpx codex status'"

# 查看session列表
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c '/path/to/acpx codex sessions'"
```

### 快速模板

```bash
# 创建session
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c '/path/to/acpx codex sessions new --name <名称>'"

# 后台调用
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c '/path/to/acpx codex -s <名称> --no-wait \"<任务>\"'"
```

---

## 四、omx exec 调用（omx工作流）

### omx简介
- oh-my-codex是Codex的编排层
- 内置20个专业Agent
- 支持skill/keyword路由

### 常用命令

```bash
# 非交互式执行
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c 'source ~/.nvm/nvm.sh && /path/to/omx exec \"任务\" --skip-git-repo-check'"

# 指定Agent执行
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c 'source ~/.nvm/nvm.sh && /path/to/omx exec --agent architect \"系统设计任务\"'"
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

## 五、Codex登录状态

```bash
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c 'codex login status'"
```

### 重新登录（如果token过期）
```bash
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c 'codex auth login --device-auth'"
```

---

## 六、日志查看

### acpx session日志
```bash
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "tail -f ~/.acpx/sessions/<session-id>.stream.ndjson"
```

### 查看任务输出
```bash
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "cat ~/.acpx/sessions/*.stream.ndjson | grep 'stdout' | tail -5"
```

---

## 七、完整示例

### 示例1：让Codex写Python脚本
```bash
# 创建session
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c '/path/to/acpx codex sessions new --name py-task'"

# 丢任务
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c '/path/to/acpx codex -s py-task --no-wait \"用Python写一个快速排序算法，保存到 /home/用户名/workspace/quick_sort.py\"'"

# 查看结果
sleep 30
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "cat /home/用户名/workspace/quick_sort.py 2>/dev/null"
```

### 示例2：用omx autopilot模式
```bash
ssh -i ~/.ssh/id_ed25519 用户名@服务器IP "su - 用户名 -c 'source ~/.nvm/nvm.sh && /path/to/omx exec \"autopilot: 开发一个REST API\" --skip-git-repo-check'"
```

---

## 八、常见问题

| 问题 | 解决 |
|------|------|
| `agent needs reconnect` | 重新sessions new |
| `No acpx session found` | 用完整路径调用acpx |
| session状态`dead` | 重新sessions new |

---

## 九、注意事项

1. acpx必须用完整路径
2. --no-wait依赖已创建的session，先sessions new
3. Codex用ChatGPT登录，需确保token有效
4. omx exec会启动持久session，适合长时间任务

---

**核心理念**：用 `--no-wait` 解放你的时间，任务在后台跑，你去做更有价值的事。
