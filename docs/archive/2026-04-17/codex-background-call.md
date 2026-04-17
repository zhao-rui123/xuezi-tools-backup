# Codex 后台调用完全指南

> 适用环境：韩国阿里云服务器 + OpenAI Codex
> 更新时间：2026-04-13

---

## 一、核心问题

**普通调用会超时：**
```bash
codex exec "任务描述"
# ❌ 会话超时，任务被杀死
```

**后台调用不超时：**
```bash
acpx codex --no-wait "任务描述"
# ✅ 任务在独立后台进程跑，完全不超时
```

---

## 二、工具链

| 工具 | 用途 |
|------|------|
| `acpx` | ACP协议客户端，后台任务调度 |
| `codex` | OpenAI Codex CLI |
| `omx` | oh-my-codex 编排层（20个专业Agent） |

---

## 三、正确流程

### 第一步：创建持久session
```bash
acpx codex sessions new
```
> 每个session可以复用，多次任务丢进同一个session

### 第二步：后台丢任务
```bash
acpx codex --no-wait "任务描述" --cwd /项目路径
```
> 立即返回，不阻塞，可以继续做其他事

### 第三步：查看状态
```bash
acpx codex status
```

### 其他命令
```bash
acpx codex sessions          # 查看session列表
acpx codex cancel           # 取消当前任务
acpx codex sessions delete   # 删除session
```

---

## 四、session管理策略

### 方式A：一个session跑一个任务
```bash
acpx codex sessions new
acpx codex --no-wait "任务A"
# 等待完成...
acpx codex sessions new    # 新session
acpx codex --no-wait "任务B"
```

### 方式B：一个session跑多个相关任务（推荐）
```bash
acpx codex sessions new
acpx codex --no-wait "任务1"
acpx codex --no-wait "任务2"
acpx codex --no-wait "任务3"
```

### 方式C：命名session
```bash
acpx codex sessions new --name my-project
acpx codex --no-wait "任务" --session my-project
```

---

## 五、完整示例

### 示例1：写一个Python脚本
```bash
# 1. 创建session
acpx codex sessions new

# 2. 后台丢任务
acpx codex --no-wait "用Python写一个快速排序算法，保存到 ~/codex-workspace/quick_sort.py"

# 3. 去做其他事...

# 4. 回来查看结果
acpx codex status
# 或者直接读文件
cat ~/codex-workspace/quick_sort.py
```

### 示例2：重构整个项目
```bash
# 1. 创建session
acpx codex sessions new

# 2. 后台丢任务（项目路径用--cwd指定）
acpx codex --no-wait "重构 ~/codex-workspace/my-project 的认证模块" --cwd ~/codex-workspace/my-project

# 3. 任务完成后查看diff
cd ~/codex-workspace/my-project && git diff
```

### 示例3：多任务并行
```bash
acpx codex sessions new

# 同时丢3个任务
acpx codex --no-wait "写README.md" &
acpx codex --no-wait "写测试用例" &
acpx codex --no-wait "优化性能" &

wait  # 等待所有任务完成
```

---

## 六、oh-my-codex（omx）专业Agent

`omx`是Codex的编排层，内置20个专业Agent：

| Agent | 职责 |
|-------|------|
| `architect` | 系统设计、架构边界 |
| `planner` | 任务拆解、执行计划 |
| `executor` | 代码实现、重构 |
| `analyst` | 需求澄清、验收标准 |
| `critic` | 计划/设计审查 |
| `code-reviewer` | 全方位代码审查 |
| `security-reviewer` | 安全漏洞检查 |
| `debugger` | 根因分析、回归隔离 |
| `test-engineer` | 测试策略、覆盖率 |
| `researcher` | 外部文档调研 |
| `designer` | UX/UI设计 |
| `git-master` | Git提交策略 |
| `verifier` | 完成验证 |
| `team-executor` | 团队协作执行 |

### 调用omx Agent
```bash
omx exec --agent architect "设计一个REST API系统"
```

---

## 七、常见问题

### Q: session超时了怎么办？
```bash
# 查看现有session
acpx codex sessions

# 恢复或新建
acpx codex sessions new
```

### Q: 任务卡住了怎么办？
```bash
acpx codex cancel
# 然后重新丢任务
```

### Q: 怎么知道任务完成了？
```bash
acpx codex status
# running = 进行中
# done = 已完成
```

### Q: 输出结果在哪？
- 文件类结果：指定路径（如`--cwd`参数指定的目录）
- 日志：`~/.acpx/logs/`
- 交互记录：`~/.acpx/sessions/`

---

## 八、工作目录建议

```bash
# 推荐工作目录结构
~/codex-workspace/
├── projects/          # 项目代码
├── temp/             # 临时文件
└── output/           # 输出结果
```

---

## 九、进阶技巧

### 1. 自动重试
```bash
until acpx codex --no-wait "任务"; do
  echo "失败，重试..."
  sleep 5
done
```

### 2. 后台运行+日志
```bash
acpx codex --no-wait "任务" 2>&1 | tee ~/codex.log &
```

### 3. 多session并行
```bash
# 同时跑3个项目
acpx codex sessions new --name project-a
acpx codex sessions new --name project-b
acpx codex sessions new --name project-c

acpx codex --no-wait "A任务" --session project-a &
acpx codex --no-wait "B任务" --session project-b &
acpx codex --no-wait "C任务" --session project-c &
```

---

## 十、总结

| 场景 | 命令 |
|------|------|
| 快速单次任务 | `acpx codex --no-wait "任务"` |
| 复杂多步骤任务 | `acpx codex sessions new` + `acpx codex --no-wait` |
| 需要专业Agent | `omx exec --agent <agent名> "任务"` |
| 查看状态 | `acpx codex status` |
| 取消任务 | `acpx codex cancel` |

---

**核心理念**：用 `--no-wait` 解放你的时间，任务在后台跑，你去做更有价值的事。
