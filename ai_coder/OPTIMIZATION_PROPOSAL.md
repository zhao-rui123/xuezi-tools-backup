# AI Coder 优化建议

基于 Golutra 分析（2026-04-20）

---

## Golutra 核心特性分析

### 1. 产品定位

Golutra 定位为**多 Agent 编排工作区**，核心理念是 "One Person. One AI Squad."：
- 将现有 CLI 工具（Claude Code、Gemini CLI、Codex、OpenCode、Qwen、OpenClaw 等）统一编排
- 不替代现有 CLI，而是作为编排层叠加其上
- 支持 Windows/macOS/Linux，Vue 3 + Rust (Tauri) 桌面应用

### 2. 核心功能特性

| 特性 | 说明 |
|------|------|
| **多 CLI 统一编排** | 一个界面同时管理多个 AI CLI，统一调度 |
| **无限多 Agent 并行执行** | 支持真正的并行执行，不仅仅是串行流水线 |
| **自动化编排** | 从分析到部署的完整自动化流程 |
| **自定义工作流 + 一键导入/导出** | 模板可分享、可复用 |
| **上下文感知终端** | 智能自动补全、项目上下文理解 |
| **直接注入（Direct Injection）** | 实时向终端流注入 Prompt，无需中断 Agent |
| **可视化界面 + 命令行** | GUI 方便监控，CLI 保留灵活性 |
| **长期运行 Agent** | 设计支持数周甚至更长的无监督运行 |
| **CEO Agent（规划中）** | 顶层自主协调器，可运行一个月无需人工干预 |
| **无限 Agent 网络（规划中）** | AI 自动创建 Agent 并扩展为协作网络 |
| **跨设备迁移（规划中）** | Agent 系统可在不同设备间迁移存活 |
| **移动端远程控制（规划中）** | 手机监控、干预、重新定向任务 |

### 3. 工作流编排机制

- **声明式工作流定义**：YAML 格式，步骤清晰
- **Agent 类型标签**：`analyst`、`architect`、`executor`、`verifier` 等
- **并行标记**：`parallel: true/false` 控制并行或串行
- **参数模板**：`{{var}}` 或 `{{var|默认值}}` 语法
- **一键导入/导出**：工作流模板可分享

### 4. 多 Agent 协作模式

- **Agent 角色专业化**：不同 Agent 有不同专长（代码审查、安全审查、性能分析等）
- **结果自动传递**：步骤间结果自动作为下一步输入
- **并行执行**：多个 Agent 同时工作，提高效率
- **上下文保持**：session 级别上下文复用

### 5. 可视化/交互设计

- **桌面应用 GUI**：直观的 Agent 头像、状态监控
- **点击头像查看日志**：实时inspect执行状态
- **终端注入**：直接向运行中的终端流注入 Prompt
- **后台静默运行**：Agent 在后台静默执行，用户无需持续关注

---

## 当前 AI Coder 现状

### 目录结构

```
ai_coder/
├── ai_coder/
│   ├── __main__.py          # 包入口
│   ├── cli.py                # CLI 定义（主要命令入口）
│   ├── background/           # 后台任务管理
│   │   ├── manager.py
│   │   ├── store.py
│   │   └── watcher.py
│   ├── config/               # 配置加载
│   │   ├── defaults.py
│   │   ├── loader.py
│   │   └── schema.py
│   ├── core/                 # 核心调度
│   │   ├── dispatcher.py
│   │   ├── lifecycle.py
│   │   ├── models.py
│   │   └── retry.py
│   ├── executors/            # 执行器
│   │   ├── factory.py
│   │   ├── local.py
│   │   └── remote.py
│   ├── security/             # 安全模块
│   │   ├── audit.py
│   │   ├── credentials.py
│   │   └── sanitizer.py
│   ├── skills/               # 技能系统
│   ├── workflows/            # 工作流模板
│   │   ├── autopilot.flow    # 自动驾驶开发（7步）
│   │   └── review.flow       # 代码审查（5步）
│   └── tests/
├── README.md
└── QUICKSTART.md
```

### CLI 命令

| 命令 | 功能 |
|------|------|
| `exec "task"` | 执行单次任务 |
| `session-new NAME` | 创建新 session |
| `session-close NAME` | 关闭 session |
| `status -s NAME` | 查询状态 |
| `skill <name> <task>` | 运行指定 skill |
| `skills` | 列出所有 skills |
| `workflow list` | 列出工作流模板 |
| `workflow run <name> --params '{}'` | 运行工作流 |
| `doctor` | 健康检查 |

### 现有工作流模板

- **autopilot.flow**：需求分析→架构设计→执行开发→单元测试→代码审查→修复优化（6步，串行）
- **review.flow**：初步扫描→质量审查→安全审查→性能审查→汇总报告（5步，串行）

### 当前不足

1. **工作流完全串行**：无并行执行能力
2. **无多 Agent 并行**：同一时间只有一个 Agent 在执行
3. **无结果自动传递机制**：步骤间需要手动指定 context
4. **无 GUI 界面**：纯命令行，状态不直观
5. **无 Direct Injection**：无法实时干预运行中的任务
6. **无长期自主运行能力**：每次需要人工启动
7. **工作流不支持并行分支**：只有 `parallel: false`
8. **无模板导入/导出分享机制**

---

## 建议新增功能

| 功能 | 描述 | 优先级 | 复杂度 |
|------|------|--------|--------|
| **并行工作流步骤** | 支持 `parallel: true` 让多个 Agent 同时执行不同步骤，结果自动聚合 | 高 | 中 |
| **工作流导入/导出** | 支持 `workflow export <name> --file xxx.flow` 导出模板，支持从文件导入 | 高 | 低 |
| **Direct Prompt Injection** | 工作流执行中支持 `inject <step> "新指令"` 实时干预，无需中断重启 | 中 | 高 |
| **多 Agent 并行执行** | 在同一工作流步骤内启动多个不同角色的 Agent 并行工作 | 中 | 高 |
| **任务状态可视化面板** | 新增 `ai_coder status --watch` 实时可视化面板，监控所有运行中任务 | 中 | 高 |
| **工作流模板市场** | 支持从 URL/文件导入他人分享的模板，一键安装 | 低 | 中 |
| **CEO 顶层协调器** | 基于 OMC 的高层 Agent，自动规划子任务、协调执行、长期无监督运行 | 低 | 极高 |
| **Session 上下文持久化** | 将 session 状态持久化到文件，支持中断恢复和跨设备迁移 | 低 | 中 |
| **Agent 资源限制配置** | 支持为不同 Agent 设置 timeout、max_tokens、cost_limit 等限制 | 低 | 低 |
| **后台任务 Web UI** | 提供轻量 Web 界面查看任务状态、日志注入 | 低 | 高 |

---

## 交互优化建议

### 1. 增强 `workflow run` 的步骤进度展示

**当前问题**：只有文字输出，没有视觉进度条

**优化方案**：
```bash
# 添加进度条和步骤可视化
$ ai_coder workflow run autopilot --params '{"task":"构建API"}'

🚀 开始执行：Autopilot 自动驾驶开发
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[██░░░░░░░░] 步骤 1/6：理解需求        → analyst      运行中...
[          ] 步骤 2/6：架构设计        → architect    等待
[          ] 步骤 3/6：执行开发        → executor     等待
[          ] 步骤 4/6：单元测试        → test-engineer 等待
[          ] 步骤 5/6：代码审查        → code-reviewer 等待
[          ] 步骤 6/6：修复优化        → executor     等待
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2. 新增 `workflow log` 命令

```bash
# 实时查看工作流执行日志
ai_coder workflow log <run-id> --follow
ai_coder workflow log <run-id> --step 3  # 只看第3步
ai_coder workflow log <run-id> --inject "重新执行这个测试"  # 注入指令
```

### 3. 优化 `doctor` 输出

当前 `doctor` 检查已经很不错，可以增加：
- 彩色进度条
- 修复建议更具体（直接给出命令）

### 4. 添加 `--verbose` / `--quiet` 选项

```bash
ai_coder exec "任务" --verbose   # 显示完整执行过程
ai_coder exec "任务" --quiet      # 只在完成时报错
```

---

## 工作流增强建议

### 1. 并行步骤支持（最高优先级）

修改 `.flow` 格式，增加并行语法：

```yaml
# review.flow 增强版：扫描和质量+安全可并行
name: Code Review 代码审查（增强版）
description: 多维度代码审查，支持并行执行
steps:
  - name: 初步扫描
    prompt: |
      快速了解代码整体结构...
    agent: explore
    parallel: false

  # 并行组：质量审查、安全审查、性能审查同时执行
  - name: 并行审查
    parallel: true
    agents:
      - name: 质量审查
        prompt: |
          深入审查代码质量...
        agent: code-reviewer
      - name: 安全审查
        prompt: |
          进行安全漏洞扫描...
        agent: security-reviewer
      - name: 性能审查
        prompt: |
          分析代码性能瓶颈...
        agent: analyst

  - name: 汇总报告
    prompt: |
      综合所有审查结果，生成最终报告...
    agent: architect
    parallel: false

agent: code-reviewer
parallel: false
```

### 2. 步骤结果传递机制

```yaml
steps:
  - name: 架构设计
    id: design
    agent: architect
    # 输出保存到上下文，ID 为 design

  - name: 执行开发
    prompt: |
      基于架构设计执行开发：
      {{design.output}}
    agent: executor
```

### 3. 条件分支

```yaml
steps:
  - name: 分析
    id: analysis
    agent: analyst

  - name: 简单任务
    condition: "{{analysis.complexity}} == 'low'"
    prompt: |
      执行简单任务...
    agent: executor

  - name: 复杂任务
    condition: "{{analysis.complexity}} == 'high'"
    prompt: |
      执行复杂任务，需要更多步骤...
    agent: architect
```

### 4. 新增推荐工作流模板

| 模板名 | 描述 | 步骤数 |
|--------|------|--------|
| `research` | 调研任务（信息收集→分析→总结→报告） | 5 |
| `refactor` | 重构任务（分析现状→设计→重构→测试→审查） | 5 |
| `bugfix` | Bug修复（复现→定位→修复→验证→审查） | 5 |
| `test-driven` | TDD开发（写测试→红→绿→重构） | 4 |

---

## 可复制的 Golutra 特性

### 高优先级可借鉴

#### 1. 工作流一键导入/导出（易实现，高价值）

```python
# 新增命令
@workflow_group.command("export")
@click.argument("workflow_name")
@click.option("--file", "-f", type=click.Path(), help="导出到文件")

@workflow_group.command("import")
@click.argument("file", type=click.Path(exists=True))
```

**实现思路**：
- 读取 `workflows/` 下的 `.flow` 文件
- 序列化为标准 YAML
- 支持从 URL 下载导入

#### 2. 并行工作流步骤（中等难度，高价值）

**实现思路**：
- 在 `WorkflowLoader.render()` 时解析 `parallel: true` 标记
- 新增 `ParallelStep` 类型，包含多个子步骤
- `workflow_run` 命令执行时，对于并行步骤：
  - 使用 `sessions_spawn` 同时启动多个子任务
  - 收集所有结果后汇总
  - 传递给下一步

#### 3. 步骤结果上下文传递（中等难度，高价值）

**实现思路**：
- 每个步骤执行后，将 output 存入 `workflow_context` 字典
- 渲染下一步 prompt 时，替换 `{{step_id.output}}` 占位符
- 持久化 context 到 `~/.ai_coder/workflow_runs/<run_id>/context.json`

#### 4. Direct Injection 概念（高难度，长期目标）

**实现思路**：
- 维护一个"注入队列"，每个 session 有一个
- 新增 `workflow inject <run-id> <step> "指令"` 命令
- 在 `Dispatcher` 中，Agent 每次循环开始前检查注入队列
- 有注入指令则优先执行

### 中等优先级

#### 5. Agent 角色标签扩展

当前 ai_coder 的 OMC skill 已支持 19 个 Agent，可以：
- 在工作流中直接引用：`agent: code-reviewer`、`agent: security-reviewer`
- 新增更多专业化 Agent（如 `devops-engineer`、`data-engineer`）

#### 6. 长期运行支持

- 工作流支持 checkpoint（检查点保存）
- 中断后 `workflow resume <run-id>` 恢复执行
- 状态持久化到 SQLite/JSON 文件

### 低优先级（长期愿景）

#### 7. CEO Agent 协调层

- 基于现有 OMC 的 `planner`/`architect` 构建
- 输入高层次目标，自主拆解子任务
- 协调多个专业 Agent 协作
- 支持长时间无监督运行

#### 8. 跨设备/跨环境迁移

- 工作流状态导出为可迁移文件
- 在另一台机器上导入继续执行

---

## 实施路线建议

### Phase 1（1-2周）：快速增强
1. ✅ 实现 `workflow export/import`
2. ✅ 新增 `research`、`refactor`、`bugfix` 工作流模板
3. ✅ 优化 `workflow run` 进度条展示

### Phase 2（2-4周）：核心改进
4. ✅ 实现并行步骤支持（`parallel: true`）
5. ✅ 实现步骤结果上下文传递（`{{step_id.output}}`）
6. ✅ 新增 `workflow log --follow` 实时日志

### Phase 3（长期）：高级特性
7. ⬜ Direct Injection 机制
8. ⬜ CEO Agent 协调层
9. ⬜ 可视化状态面板
10. ⬜ 跨设备迁移

---

## 总结

Golutra 的核心启示是：**"保留 CLI，增加编排层"**。ai_coder 已经有了良好的 CLI 基础和工作流框架，主要差距在于：

1. **并行能力**：工作流步骤串行执行，无法利用多核/多机并行
2. **结果传递**：步骤间没有自动化的上下文传递机制
3. **模板生态**：工作流无法导入导出分享
4. **可视化**：纯文本输出，状态不直观

建议优先实现**并行步骤**和**工作流导入导出**，这两项投入产出比最高。
