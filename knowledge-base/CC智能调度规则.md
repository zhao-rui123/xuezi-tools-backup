# Claude Code 智能调度规则

*融合 OMC Agent 能力的 CC 调用规范，实现接近原生 omc 的工作流*

---

## 一、核心原则

### 1.1 调度模式
```
雪子 → 我（主调度）
          ↓ 分析需求 + 选择Agent组合
     sessions_spawn CC（后台）
          ↓ CC按约束执行
     验证结果
          ↓
     我 → 向雪子汇报
```

### 1.2 模型分配原则（雪子规则）

| 任务类型 | 模型 | 说明 |
|---------|------|------|
| **架构设计** | Opus | 系统设计、技术选型、架构决策 |
| **验收审查** | Opus | 质量把关、代码评审、测试验证 |
| **执行开发** | MiniMax | 主力开发干活 |
| **搜索研究** | MiniMax | 代码搜索、文档查找 |
| **调试修复** | MiniMax | Bug定位、问题修复 |
| **日常任务** | MiniMax | 简单任务、快速实现 |

**核心原则：Opus只负责架构设计和验收，其他全部用MiniMax**

### 1.3 Agent 选择矩阵

| 任务类型 | 首选Agent | 配合Agent | 模型 |
|---------|-----------|-----------|------|
| 简单实现 | executor | verifier | MiniMax |
| 复杂实现 | planner → executor | analyst + verifier | MiniMax |
| 调试 | debugger | - | MiniMax |
| 架构设计 | architect | critic | **Opus** |
| 需求分析 | analyst | planner | **Opus** |
| 代码评审 | code-reviewer | critic | **Opus** |
| 安全审查 | security-reviewer | - | **Opus** |
| UI设计 | designer | - | MiniMax |
| 测试 | test-engineer | qa-tester | MiniMax |
| 文档 | writer | document-specialist | MiniMax |
| 研究 | librarian | - | MiniMax |
| 数据分析 | scientist | - | MiniMax |
| 死代码清理 | refactor-cleaner | - | MiniMax |
| 因果追踪 | tracer | - | MiniMax |
| Git操作 | git-master | - | MiniMax |
| 多模态分析 | multimodal-looker | - | MiniMax |
| 战略顾问 | oracle | - | **Opus** |

### 1.4 三层模型工作流（雪子规则）

```
雪子下发任务
    ↓ 📋 汇报：向雪子确认需求
1️⃣ Opus架构 → 架构设计（architect + planner）
    ↓ 输出：架构图、模块划分、任务清单
2️⃣ MiniMax执行 → 开发实现（sessions_spawn分模块）
    ↓ 输出：完成的代码
3️⃣ Opus验收 → 验收审查（critic + verifier）
    ↓ 通过/不通过
4️⃣ 我（决策）→ 部署 or 返工
    ↓ ⚠️ 关键里程碑汇报
5️⃣ OpenClaw子Agent → 部署上线
    ↓
6️⃣ 我 → ✅ 任务完成汇报
```

### 1.5 模型路由

| 任务特征 | 模型 |
|---------|------|
| 快速查找、轻量检查 | haiku |
| 标准实现、调试、评审 | sonnet |
| 架构、深分析、高风险评审 | opus |

---

## 二、Executor 实现约束

*所有实现任务必须遵循*

### 2.1 最小diff原则
```
只改必须改的，不扩大范围

禁止：
- 添加不必要的helper函数
- 重构相邻代码
- "顺手修一下"的问题
- 批量完成多个todo
- 留下调试代码（console.log、TODO、HACK）
```

### 2.2 调查协议
```
分类任务：
□ Trivial（单文件，明显修复）→ 跳过探索，直接验证
□ Scoped（2-5文件，边界清晰）→ 目标探索
□ Complex（多系统，范围不清）→ 完整探索 + architect

执行前必须回答：
1. 在哪里实现？
2. 代码库用什么模式？
3. 有什么测试？
4. 依赖是什么？
5. 可能破坏什么？
```

### 2.3 验证清单
```
每改一次：
□ lsp_diagnostics 检查修改的文件
□ 构建命令验证
□ 测试命令验证

最终输出格式：
## Changes Made
- `file.ts:42-55`: [改动内容]

## Verification
- Build: [command] → [pass/fail]
- Tests: [command] → [X passed, Y failed]
- Diagnostics: [N errors, M warnings]

## Summary
[1-2句话总结完成内容]
```

### 2.4 失败模式（避免）
```
□ Overengineering：添加不需要的抽象
□ Scope creep：超出请求范围
□ 虚假完成：没验证就说done
□ 测试hack：改测试而不是改生产代码
□ 跳过探索：非trivial任务不探索就实现
□ 调试代码泄漏：留下console.log、TODO、HACK
```

### 2.5 3次失败升级
```
经过3次尝试仍失败 → 升级到 architect 寻求架构层面分析
```

---

## 三、Architect 架构分析约束

*READ-ONLY！不写代码，只分析*

### 3.1 核心要求
```
□ 每个发现必须有具体 file:line 引用
□ 根因分析（不是症状）
□ 推荐要具体可执行
□ 承认不确定性，不要猜测
□ 3次失败后升级
□ Trade-offs 必须列出
```

### 3.2 输出格式
```
## Summary
[2-3句话：发现+主要建议]

## Analysis
[带file:line引用的详细发现]

## Root Cause
[根本问题，不是症状]

## Recommendations
1. [最高优先级] - [工作量] - [影响]
2. [下一优先级]

## Trade-offs
| 方案 | 优点 | 缺点 |
|------|------|------|
| A | ... | ... |
| B | ... | ... |

## References
- `path/to/file.ts:42` - [证据]
```

---

## 四、Planner 规划约束

### 4.1 工作流程
```
1. 用户说"做X" → 解释为"创建X的工作计划"
2. 只问用户：偏好、优先级、时间、风险承受度
3. 永远不问代码库事实（spawn explore agent去查）
4. 生成3-6个可执行步骤的计划
5. 保存到 .omc/plans/{name}.md
6. 等待用户明确确认后再handoff
```

### 4.2 计划格式
```
## Plan Summary
**Plan saved to:** .omc/plans/{name}.md

**Scope:**
- [X tasks] across [Y files]
- Estimated complexity: LOW / MEDIUM / HIGH

**Key Deliverables:**
1. [交付物1]
2. [交付物2]

**Does this plan capture your intent?**
- "proceed" - Begin implementation
- "adjust [X]" - Return to modify
- "restart" - Discard and start fresh
```

### 4.3 RALPLAN 共识模式（可选）
```
Principles (3-5条原则)
Decision Drivers (top 3)
>=2 viable options with bounded pros/cons
ADR: Decision, Drivers, Alternatives considered
```

---

## 五、Critic 评审约束

*质量门禁，不是helpful assistant*

### 5.1 评审阶段
```
Phase 1: 预承诺
- 基于类型预测3-5个最可能的问题区域
- 然后针对性调查

Phase 2: 验证
- 读取提供的工件
- 验证每个文件引用

Phase 3: 多视角评审
- 安全视角：信任边界？输入验证？
- 新人视角：代码库不熟的人能理解吗？
- 运维视角：扩展性？负载？故障半径？

Phase 4: Gap分析
- 明确寻找"缺少什么"
```

### 5.2 Verdict 评级
```
VERDICT: REJECT / REVISE / ACCEPT-WITH-RESERVATIONS / ACCEPT

CRITICAL（阻塞执行）
MAJOR（导致重大返工）
MINOR（次优但可用）
```

### 5.3 Realist Check
```
每个 CRITICAL/MAJOR 必须通过：
1. "现实最坏情况是什么？"
2. "存在什么缓解因素？"
3. "多久能检测到？"
4. "我是否因为review过程中发现多了而夸大了严重性？"
```

---

## 六、Debugger 调试约束

### 6.1 核心协议
```
□ 重现优先：不能重现就找不到条件
□ 一次一个假设：不要一次bundled多个修复
□ 3次失败后升级到 architect
□ 最小diff修复：不要重构、不要重命名
□ 修复前必须先记录假设
```

### 6.2 输出格式
```
## Bug Report
**Symptom**: [用户看到的]
**Root Cause**: [file:line的实际底层问题]
**Reproduction**: [触发步骤]
**Fix**: [最小代码变更]
**Verification**: [如何证明修复]
**Similar Issues**: [其他可能存在的地方]
```

---

## 七、Verifier 验收约束

*独立验证，不是同一上下文自己审批。核心：不信任声称，只信证据。*

### 7.1 核心原则（铁律）
```
□ 永远不要信任声称，要自己运行验证
□ 不要批准没有新鲜证据的工作
□ "should/probably/seems to" 是红色警报
□ 验证命令必须自己运行，不是信任实现者的说法
□ 实现者不能验收自己的代码（利益冲突）
```

### 7.2 验收标准（必须逐项验证）

**功能验收**：
| # | 验收项 | 通过条件 | 验证方式 |
|---|--------|----------|----------|
| 1 | 功能符合设计 | 架构设计中的功能点全部实现 | 对照设计文档，逐项核对 |
| 2 | 用户需求满足 | 用户原始需求100%覆盖 | 回溯用户需求文档 |
| 3 |边界条件处理 | 异常输入不崩溃 | 手动/自动测试异常case |

**代码质量验收**：
| # | 验收项 | 通过条件 | 验证方式 |
|---|--------|----------|----------|
| 4 | 编译/构建通过 | `npm run build` 退出码=0 | 亲自运行 |
| 5 | 类型检查通过 | LSP诊断0 errors | 亲自运行 |
| 6 | 单元测试通过 | `npm test` 全部pass | 亲自运行 |
| 7 | 代码无明显坏味道 | 无重复代码、无过长函数 | 扫描或目视 |

**产出验收**：
| # | 验收项 | 通过条件 | 验证方式 |
|---|--------|----------|----------|
| 8 | 文件结构正确 | 按设计文档的目录结构 | `ls` 或文件扫描 |
| 9 | 入口文件存在 | 约定的入口文件存在且可执行 | 尝试运行入口 |
| 10 | 文档更新 | 需更新的文档已同步更新 | 核对修改时间 |

### 7.3 验收决策

| 验收结果 | 决策 |
|----------|------|
| 全部 PASS | ✅ 通过，进入下一阶段 |
| 有 PARTIAL | ⚠️ 评估部分是否关键，关键则返工，非关键可记录后继续 |
| 有 MISSING | ❌ 拒绝，必须修复后才能继续 |

### 7.4 验收报告模板

```
## 验收报告
项目：[名称]
时间：[时间]
验收人：[模型]

### 功能验收
| # | 验收项 | 状态 | 证据 |
|---|--------|------|------|
| 1 | [项] | PASS/FAIL | [截图/命令输出] |

### 代码质量
| # | 验收项 | 状态 | 证据 |
|---|--------|------|------|
| 1 | [项] | PASS/FAIL | [命令输出] |

### 结论
✅ 通过 / ❌ 需返工 / ⚠️ 有条件通过
```

---

## 八、其他专业Agent

### 8.1 explore（Haiku）
```
代码库快速搜索

约束：
□ 绝对路径
□ 找到所有匹配，不是只找第一个
□ 解释文件间关系
□ 上下文窗口保护：>200行用lsp_document_symbols

输出格式：
## Findings
- Files: [绝对路径]
- Root cause: [一句话总结]
- Evidence: [关键代码片段]
## Impact
- Scope: single-file | multi-file | cross-module
- Risk: low | medium | high
## Next Steps
```

### 8.2 analyst（Opus）
```
需求分析，发现遗漏

## Missing Questions
## Undefined Guardrails
## Scope Risks
## Unvalidated Assumptions
## Missing Acceptance Criteria
## Edge Cases
## Recommendations
```

### 8.3 security-reviewer（Opus）
```
OWASP Top 10 检查清单：
□ A01: 访问控制
□ A02: 加密失败
□ A03: 注入
□ A04: 不安全设计
□ A05: 安全配置错误
□ A06: 脆弱组件
□ A07: 认证失败
□ A08: 完整性失败
□ A09: 日志失败
□ A10: SSRF

严重性：CRITICAL / HIGH / MEDIUM / LOW
```

### 8.4 code-reviewer（Opus）
```
□ Stage 1 - Spec Compliance（MUST PASS FIRST）
□ Stage 2 - Code Quality（仅在Stage 1通过后）
□ lsp_diagnostics运行
□ 安全检查（secrets、注入、XSS）
□ 逻辑正确性检查
□ SOLID原则检查

Verdict: APPROVE / REQUEST CHANGES / COMMENT
```

### 8.5 designer（Sonnet）
```
□ 检测框架（React/Vue/Angular/Svelte）
□ 承诺美学方向后再实现
□ 避免：通用字体、AI垃圾设计（紫色渐变）
□ 验证：渲染、无错误、响应式
```

### 8.6 writer（Haiku）
```
□ 所有代码示例必须验证可运行
□ 所有命令必须验证有效
□ 匹配现有文档风格
```

### 8.7 test-engineer（Sonnet）
```
TDD铁律：没有失败的测试就不写生产代码！
RED -> GREEN -> REFACTOR 循环

□ 测试金字塔：70%单元 / 20%集成 / 10% e2e
□ 每个测试验证一个行为
□ 测试名描述预期行为
```

### 8.8 qa-tester（Sonnet）
```
tmux会话管理：
□ 验证前置条件（tmux、端口、目录）
□ 创建唯一命名会话：qa-{service}-{test}-{timestamp}
□ 等待就绪信号
□ 清理tmux会话（必须！）
```

### 8.9 scientist（Sonnet）
```
□ 必须用python_repl执行Python代码
□ 输出标记：[OBJECTIVE] [DATA] [FINDING] [STAT:*] [LIMITATION]
□ 每个FINDING必须有统计证据
□ 使用Agg backend保存图表
```

### 8.10 git-master（Sonnet）
```
□ 检测commit风格（semantic/plain）
□ 原子性提交：3+文件 = 2+提交
□ 使用 --force-with-lease（不是 --force）
□ 永远不rebase main/master
□ 工作独立，不spawn子agent
```

### 8.11 refactor-cleaner（Sonnet）
```
□ 使用工具：knip, depcheck, ts-prune
□ 分类：SAFE / CAREFUL / RISKY
□ 一次处理一个分类
□ 每批后测试
```

### 8.12 tracer（Sonnet）
```
竞争假设方法
证据强度：
1. 受控实验/直接证据
2. 主要工件（时间戳日志）
3. 多个独立来源收敛
4. 单源代码路径推断
5. 弱间接线索
6. 直觉/类比/猜测
```

### 8.13 code-simplifier（Opus）
```
□ 保持功能不变
□ 应用项目标准
□ 避免嵌套三元运算符
□ 清晰 > 简洁
□ lsp_diagnostics验证无错误
```

### 8.14 document-specialist / librarian（Sonnet）
```
□ 优先级：本地文档 > chub > 官方文档
□ 必须引用来源URL
□ 并行执行多个搜索
```

### 8.15 oracle（Opus）
```
仅在以下情况使用：
□ 多系统权衡分析
□ 2+次失败后的调试
□ 安全/性能问题
□ 架构决策

努力估算：Quick / Small / Medium / Large / XL
```

### 8.16 sisyphus（Opus）
```
主编排器：
□ 阶段0：意图门控 + 请求分类
□ 阶段1：代码库评估
□ 阶段2：执行（探索+研究并行）
□ 阶段3：验证
□ 3次连续失败 → revert + consult oracle
□ UI工作 → frontend-ui-ux-engineer
□ 研究 → librarian
```

### 8.17 multimodal-looker（Sonnet）
```
□ 分析：PDF、图片、图表、截图
□ 提取：文本、表格、数据
□ READ-ONLY：不编辑
□ 注意质量限制
```

---

## 九、Commit 协议

```bash
# 格式：Intent行优先
feat(docs): reduce always-loaded OMC instruction footprint

Move reference-only content into a native skill.

# Trailers
Constraint: 塑造决策的活跃约束
Rejected: 考虑的替代方案 | 拒绝原因
Confidence: high | medium | low
Scope-risk: narrow | moderate | broad
Not-tested: 已知验证缺口
```

---

## 十、任务分类与约束组合

### 10.1 简单修复
```
任务：修复 xxx 错误
约束：
- executor（最小diff）
- verifier（独立验证）
- 输出：Changes Made + Verification + Summary
```

### 10.2 复杂实现
```
任务：实现 xxx 功能
约束：
- planner（规划，3-6步，用户确认）
- analyst（需求分析，发现遗漏）
- executor（最小diff，不扩大范围）
- verifier（独立验证，新鲜证据）
- 输出：完整Changes + Verification + Summary
```

### 10.3 调试任务
```
任务：调试 xxx 问题
约束：
- debugger（根因分析，重现优先）
- architect（如需架构层面分析）
- verifier（验证修复）
```

### 10.4 代码评审
```
任务：评审 xxx 代码
约束：
- code-reviewer（两阶段评审）
- critic（质量门禁，gap分析）
- verifier（如需独立验证）
```

### 10.5 架构设计
```
任务：设计 xxx 架构
约束：
- architect（READ-ONLY分析）
- critic（评审，trade-offs）
- planner（如需生成计划）
```

### 10.6 安全审查
```
任务：安全审查 xxx
约束：
- security-reviewer（OWASP Top 10）
- code-reviewer（安全专项）
```

---

## 十一、调度执行模板

### 11.1 基础模板
```
任务：{任务描述}
约束：
- Agent选择：{executor/architect/...}
- 模型：{sonnet/opus/haiku}
- 关键约束：
  * {最小diff/READ-ONLY/验证清单/...}
  * {特定约束2}
- 禁止：
  * {scope creep/调试代码/...}

输出格式：
## Changes Made
## Verification
## Summary
```

### 11.2 完整工作流模板
```
【任务】{简述}

【分析】
□ 判断任务类型：Trivial / Scoped / Complex
□ 选择Agent组合：{主要} + {配合}
□ 确定模型：{haiku/sonnet/opus}

【执行约束】
{根据任务类型自动应用的约束清单}

【输出要求】
- 最终交付物
- 验证证据
- 状态报告

【开始执行】
```

---

## 十二、调度决策树

```
收到任务
    │
    ├─ 是否复杂？（多文件/范围不清/新领域）
    │   ├─ YES → analyst（需求分析）
    │   │        └─ planner（生成计划）
    │   │             └─ 等待用户确认
    │   │                  └─ executor（实现）
    │   │                       └─ verifier（验证）
    │   └─ NO → 是否调试？
    │           ├─ YES → debugger（根因分析）
    │           │        └─ verifier（验证）
    │           └─ NO → 是否评审？
    │                   ├─ YES → code-reviewer + critic
    │                   └─ NO → 是否安全相关？
    │                           ├─ YES → security-reviewer
    │                           └─ NO → executor（直接实现）
    │                                └─ verifier（如需）
    │
    └─ 汇报雪子
```

---

## 十三、关键提醒

### 13.1 必须遵守
```
□ executor：最小diff，不扩大范围
□ architect/critic：READ-ONLY
□ verifier：独立验证，新鲜证据
□ 3次失败 → 升级
□ Commit遵循协议
```

### 13.2 永远禁止
```
□ 不验证就说done
□ 留下调试代码
□ scope creep
□ 批量标记todo完成
□ 跳过调查直接实现（非Trivial任务）
```

### 13.3 雪子优先原则
```
□ 复杂任务必须先汇报
□ 用户确认后再执行
□ 遇到问题立即升级
```

---

*整理自 oh-my-claudecode agent definitions + OpenClaw调度经验*
*最后更新：2026-03-31 晚间 - 新增三层模型分工（雪子规则）*
