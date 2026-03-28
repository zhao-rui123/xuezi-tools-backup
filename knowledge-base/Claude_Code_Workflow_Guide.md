# Claude Code 工作流完整指南

## 概述

这套系统由三层 Skills 构成：
- **方法论层**（superpowers）- 管"怎么开发"
- **领域层**（MiniMax）- 管"用什么技术"
- **编排层**（dev-workflow）- 管"什么时候用什么"

---

## 一、安装清单

### 1. Superpowers（方法论 Skills）

GitHub: `github.com/obra/superpowers`（34k stars）

下载后复制 `skills/` 目录到 `~/.claude/skills/`：

```
skills/
├── brainstorming/              # 头脑风暴
├── writing-plans/             # 制定计划
├── systematic-debugging/       # 系统调试
├── test-driven-development/    # TDD 测试驱动
├── receiving-code-review/       # 代码审查
├── subagent-driven-development/ # 子代理并行开发
├── finishing-a-development-branch/ # 收尾交付
├── using-git-worktrees/        # Git Worktree
├── verification-before-completion/ # 完成前验证
├── executing-plans/            # 执行计划
├── dispatching-parallel-agents/ # 并行代理调度
├── requesting-code-review/      # 请求审查
└── writing-skills/            # 编写 Skills
```

### 2. 领域 Skills（MiniMax）

已装在 `~/.claude/skills/`：
- `frontend-dev` — React/Next.js/Tailwind/GSAP
- `fullstack-dev` — REST API/JWT/WebSocket
- `android-native-dev` — Kotlin/Jetpack Compose
- `ios-application-dev` — SwiftUI/UIKit
- `minimax-xlsx` — Excel
- `minimax-pdf` — PDF
- `minimax-docx` — Word
- `pandas-skill` — 数据分析

### 3. 编排 Workflow

创建 `~/.claude/skills/dev-workflow/SKILL.md`：

```markdown
# Dev Workflow

完整项目开发时的工作流：

1. 需求 → brainstorming
2. 需求明确 → writing-plans
3. 技术选型 → 对应领域技能
4. 开发 → test-driven-development
5. 审查 → receiving-code-review
6. 交付 → finishing-a-development-branch
```

### 4. Hooks 和 Commands（可选）

- `~/.claude/hooks.json` — 生命周期钩子
- `~/.claude/commands/brainstorm.md` — /brainstorm
- `~/.claude/commands/write-plan.md` — /write-plan
- `~/.claude/commands/execute-plan.md` — /execute-plan

---

## 二、工作流详解

### 简单项目（1-2小时能完成）

```
明确需求 → 直接写代码 → 基本验证
```

跳过 brainstorming 和 writing-plans，直接用对应领域技能实现。

### 常规项目（半天-几天）

```
brainstorming → writing-plans → TDD开发 → 审查 → 收尾
```

### 复杂项目（需要并行）

```
brainstorming → writing-plans
       ↓
subagent-driven-development（拆成多个子任务并行）
       ↓
验证 → 审查 → 收尾
```

---

## 三、Skills 调度规则

### 什么时候用 brainstorming
- 用户说"帮我做一个 XXX"但需求不明确
- 有多个方案可选，不知道哪个好
- 不确定技术可行性

### 什么时候用 writing-plans
- brainstorming 完成后
- 需要拆成小任务
- 需要用户确认开发范围

### 什么时候用 TDD
- 开始写代码时
- 需要保证代码质量
- 有明确的验收标准

### 什么时候用代码审查
- 功能开发完成
- 准备合并/交付前
- 需要检查问题

### 什么时候用子代理并行
- 项目可以分成独立模块
- 多个模块技术不相关
- 想加速开发

---

## 四、技术栈对应

| 需求 | 调用技能 |
|------|---------|
| React/前端界面 | `frontend-dev` + `frontend-design` |
| 完整前后端应用 | `fullstack-dev` |
| Android App | `android-native-dev` |
| iOS App | `ios-application-dev` |
| Excel 数据处理 | `minimax-xlsx` + `pandas-skill` |
| Word 文档 | `minimax-docx` |
| PDF 处理 | `minimax-pdf` |
| 股票数据分析 | 用云服务器脚本（见 stock_data_tutorial.md）|

---

## 五、原则

1. **YAGNI** — 不提前实现不需要的功能
2. **DRY** — 重复代码提取成公共模块
3. **小步提交** — 每完成一个功能就 commit
4. **不跳步** — 简单项目可省略阶段，但顺序不能乱
5. **superpowers 是骨架，领域技能是血肉** — 两者配合

---

## 六、云服务器联动

云服务器 IP：106.54.25.161

连接：`ssh -i ~/.ssh/id_ed25519 root@106.54.25.161`

云服务器用途：
- GitHub 下载（速度快）
- 股票数据获取
- Agent Reach 联网搜索
- 其他本地网络不通的任务

股票脚本位置：`/tmp/stock_technical_analysis.py`
使用：`python3 /tmp/stock_technical_analysis.py [股票代码]`

---

## 七、给 AI Agent 的指令模板

开发新项目时，可以这样触发工作流：

```
帮我做一个 [项目描述]
要求：
1. 先 brainstorming 聊清楚需求
2. 制定开发计划
3. 用 TDD 方式开发
4. 开发完成后做代码审查
```

或者直接说需求，让 AI 自己判断走哪个流程。
