# 自我进化系统 (Self-Evolution System) v2.0

> **真正的自我进化**：整合 unified-memory 和所有改进模块，实现感知-认知-执行-反馈的完整闭环。

## 🧬 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户交互层                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      感知层 (Perception)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ 交互记录器    │ │ 错误捕获器    │ │ 性能监控器    │            │
│  │ 对话数据     │ │ 异常事件     │ │ Token/时间   │            │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘            │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      统一记忆系统 (UMS)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ 增强检索     │ │ 知识图谱     │ │ 智能分析     │            │
│  │ (Recall)    │ │ (Graph)     │ │ (Analyzer)   │            │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘            │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      认知层 (Cognition)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ 模式识别     │ │ 关联分析     │ │ 预测引擎     │            │
│  │ 错误模式     │ │ 知识关联     │ │ 工作建议     │            │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘            │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      执行层 (Execution)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ 自我改进     │ │ 目标管理     │ │ 自动优化     │            │
│  │ (错误学习)   │ │ (长期规划)   │ │ (建议应用)   │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 模块组成

### 核心引擎

| 模块 | 文件 | 功能 |
|------|------|------|
| **进化引擎** | `core/evolution_engine.py` | 核心控制器，管理进化状态 |
| **整合适配器** | `core/evolution_adapter.py` | 统一接口，连接所有模块 |
| **触发器** | `triggers/evolution_triggers.py` | 自动化触发机制 |

### 现有模块（已整合）

| 模块 | 来源 | 功能 |
|------|------|------|
| **增强检索** | unified-memory | 智能记忆存储与检索 |
| **知识图谱** | unified-memory | 实体关系网络分析 |
| **记忆分析** | unified-memory | 模式识别与主题提取 |
| **长期规划** | self-improvement | 目标分解与进度跟踪 |
| **预测建议** | self-improvement | 基于历史的行为预测 |
| **错误学习** | self-improvement | 从错误中自动学习 |
| **性能监控** | self-improvement | 运行效率监控分析 |

## 🚀 快速开始

### 1. 初始化系统

```bash
cd ~/.openclaw/workspace/skills/self-improvement
python3 core/evolution_adapter.py init
```

### 2. 手动执行进化

```bash
# 查看状态
python3 core/evolution_engine.py status

# 执行一次完整进化
python3 core/evolution_engine.py evolve

# 生成报告
python3 core/evolution_engine.py report --period daily
```

### 3. 在代码中使用

```python
# 方式1: 使用整合适配器（推荐）
from core.evolution_adapter import EvolutionIntegrationAdapter

adapter = EvolutionIntegrationAdapter()

# 记录交互
adapter.record_interaction(
    query="用户查询",
    response_time_ms=2500,
    tokens_in=1500,
    tokens_out=800,
    tools_used=["read", "write"],
    success=True
)

# 获取相关上下文
context = adapter.get_relevant_context("股票分析")

# 执行自我进化
adapter.evolve()
```

```python
# 方式2: 使用触发器（自动化场景）
from triggers.evolution_triggers import on_conversation_end

# 对话结束时自动触发
on_conversation_end(
    query="用户查询",
    response_time_ms=2500,
    tokens_in=1500,
    tokens_out=800,
    tools_used=["read", "write"],
    success=True
)
```

## ⚙️ 自动化配置

### 添加定时任务

```bash
# 编辑 crontab
crontab -e

# 每日23:00执行自我进化
0 23 * * * /usr/bin/python3 ~/.openclaw/workspace/skills/self-improvement/triggers/evolution_triggers.py daily

# 每周日22:00生成周报
0 22 * * 0 /usr/bin/python3 ~/.openclaw/workspace/skills/self-improvement/triggers/evolution_triggers.py weekly

# 每月1日08:00深度分析
0 8 1 * * /usr/bin/python3 ~/.openclaw/workspace/skills/self-improvement/triggers/evolution_triggers.py monthly
```

### 心跳集成

在 `HEARTBEAT.md` 中添加：

```markdown
## 自我进化检查
- [ ] 执行日常进化（如超过24小时未执行）
- [ ] 检查是否有新的优化建议
- [ ] 查看进化等级和性能评分
```

## 📊 进化等级系统

系统会根据以下指标自动计算进化等级：

| 等级 | 名称 | 条件 |
|------|------|------|
| ⭐ | **Initial** (初始) | 默认状态 |
| ⭐⭐ | **Learning** (学习) | 交互>100 或 学习模式>5 |
| ⭐⭐⭐ | **Adapting** (适应) | 交互>1000 或 学习模式>20 |
| ⭐⭐⭐⭐ | **Optimizing** (优化) | 性能评分>90 或 改进>10 |
| ⭐⭐⭐⭐⭐ | **Self-Aware** (自觉) | 所有指标优秀 |

## 📈 数据流说明

### 1. 交互记录流

```
用户对话 → record_interaction() → 进化引擎记录
                           ↓
                    ┌──────┴──────┐
                    ↓             ↓
              unified-memory   知识图谱
              (存储记忆)       (更新关联)
                    ↓             ↓
              模式识别 ←────── 关联分析
                    ↓
              生成优化建议
```

### 2. 错误学习流

```
错误发生 → record_error() → 学习模式存储
                       ↓
                  unified-memory
                  (高重要度存储)
                       ↓
                  下次遇到类似查询
                       ↓
                  自动提示经验
```

### 3. 自我进化流

```
定时触发/手动触发 → evolve() → 生成报告
                          → 应用优化
                          → 更新等级
                          → 同步记忆
```

## 🎯 使用场景

### 场景1: 自动错误预防

```python
# 在回答用户前检查
from triggers.evolution_triggers import get_learning_advice

advice = get_learning_advice("用户查询")
if advice:
    print(f"💡 根据经验: {advice}")
    # 输出: 根据之前的经验(5次类似情况): 注意时区问题
```

### 场景2: 性能自动优化

当系统检测到响应时间>5秒时：
1. 自动创建优化建议
2. 记录到优化队列
3. 下次进化时自动应用（如果是低工作量优化）

### 场景3: 长期目标跟踪

```python
# 设置长期目标
python3 long_term_planner.py set-goal \
  --title "知识图谱系统开发" \
  --desc "构建增强型知识图谱" \
  --timeline "3个月"

# 自动分解为短期任务
python3 long_term_planner.py decompose --goal <goal_id>

# 日常工作自动关联
# 当对话提到"知识图谱"时，自动更新目标进度
```

## 📁 数据存储

| 文件 | 内容 |
|------|------|
| `memory/evolution/evolution_state.json` | 进化状态 |
| `memory/evolution/evolution_log.json` | 交互日志 |
| `memory/evolution/learning_patterns.json` | 学习模式 |
| `memory/evolution/optimization_queue.json` | 优化队列 |
| `memory/evolution/report_*.md` | 进化报告 |
| `memory/self-improvement.json` | 错误学习记录 |
| `memory/long_term_goals.json` | 长期目标 |
| `memory/performance.json` | 性能数据 |

## 🔧 高级用法

### 自定义学习模式

```python
from evolution_engine import SelfEvolutionEngine

engine = SelfEvolutionEngine()

# 创建自定义模式
pattern = LearningPattern(
    id="custom_001",
    pattern_type="preference",
    trigger="股票分析",
    condition="用户询问股票",
    action="自动获取自选股数据",
    confidence=0.9,
    occurrences=10
)

engine._save_learning_patterns({"custom_001": pattern})
```

### 扩展优化建议

```python
# 在 evolution_engine.py 中添加自定义检测逻辑
def _realtime_analysis(self, record):
    # 原有检测...
    
    # 添加自定义检测
    if "储能" in record.query and "股票" in record.query:
        self._create_optimization_suggestion(
            category="integration",
            title="创建储能股票分析技能包",
            description="检测到储能+股票联合查询，建议创建专项工具",
            impact=0.8,
            effort=0.6
        )
```

## 📝 命令参考

### evolution_engine.py

```bash
python3 evolution_engine.py evolve              # 执行完整进化
python3 evolution_engine.py report --period daily|weekly|monthly
python3 evolution_engine.py status              # 查看状态
python3 evolution_engine.py optimize            # 应用待处理优化
```

### evolution_adapter.py

```bash
python3 evolution_adapter.py init               # 初始化系统
python3 evolution_adapter.py status             # 查看完整状态
python3 evolution_adapter.py evolve             # 执行进化
python3 evolution_adapter.py report             # 生成完整报告
python3 evolution_adapter.py insights           # 获取洞察建议
```

### evolution_triggers.py

```bash
python3 evolution_triggers.py daily             # 每日进化（cron用）
python3 evolution_triggers.py weekly            # 每周回顾（cron用）
python3 evolution_triggers.py monthly           # 每月分析（cron用）
python3 evolution_triggers.py status            # 查看触发器状态
```

## 🔄 版本历史

- **v2.0** (2026-03-09): 完整版自我进化系统
  - 整合 unified-memory 所有模块
  - 新增进化引擎核心
  - 新增整合适配器
  - 新增自动化触发器
  - 实现感知-认知-执行-反馈闭环

- **v1.0** (2026-03-08): 基础版自我改进
  - 错误学习模块
  - 性能监控模块
  - 技能包管理模块
  - 长期规划模块

## 💡 设计原则

1. **自动优先** - 尽可能自动执行，减少人工干预
2. **渐进进化** - 从简单模式开始，逐步提升复杂度
3. **数据驱动** - 所有决策基于实际数据
4. **可解释性** - 每次进化都有清晰的记录和报告
5. **安全性** - 自动优化前先人工确认（高影响操作）

## 🔮 未来扩展

- [ ] 深度学习模型微调
- [ ] 多模态记忆自动处理
- [ ] 跨会话长期记忆
- [ ] 用户情感分析
- [ ] 主动建议系统

---

*让AI真正学会自我改进* 🤖✨
