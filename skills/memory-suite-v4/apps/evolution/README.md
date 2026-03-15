# Memory Suite v4.0 - 自我进化模块

## 概述

自我进化模块（Evolution Module）是 Memory Suite v4.0 的核心应用层模块，负责：
- 📊 生成自我进化报告
- 🎯 技能成长追踪
- 📈 使用频率统计
- 💡 改进建议生成

## 目录结构

```
apps/evolution/
├── __init__.py              # 模块初始化
├── evolution_reporter.py    # 进化报告生成器
├── skill_evaluator.py       # 技能评估器
└── test_evolution.py        # 集成测试
```

## 快速开始

### 1. 生成进化报告

```bash
# 生成上个月的进化报告（默认）
python3 apps/evolution/evolution_reporter.py

# 生成指定月份的报告
python3 apps/evolution/evolution_reporter.py --month 2026-02

# 或使用 Python API
from apps.evolution import EvolutionReporter

reporter = EvolutionReporter()
report_file = reporter.generate_monthly_report("2026-02")
```

### 2. 评估技能包

```bash
# 评估最近 7 天的技能使用
python3 apps/evolution/skill_evaluator.py --action evaluate --period 7

# 生成周度技能报告
python3 apps/evolution/skill_evaluator.py --action report

# 查看技能统计
python3 apps/evolution/skill_evaluator.py --action stats

# 或使用 Python API
from apps.evolution import SkillEvaluator

evaluator = SkillEvaluator()

# 记录技能使用
evaluator.record_usage(
    skill_name="memory-suite",
    action="save",
    success=True,
    duration_ms=1500,
    tokens_used=2000
)

# 评估技能
evaluations = evaluator.evaluate_skills(period_days=7)

# 生成周报告
report_file = evaluator.generate_weekly_report()
```

## API 参考

### EvolutionReporter

#### `generate_monthly_report(month_str: Optional[str] = None) -> Optional[str]`

生成月度进化报告。

**参数:**
- `month_str`: 月份字符串 (YYYY-MM 格式)，默认为上个月

**返回:**
- 报告文件路径（Markdown 格式）

**示例:**
```python
reporter = EvolutionReporter()
report = reporter.generate_monthly_report("2026-02")
```

### SkillEvaluator

#### `record_usage(skill_name: str, action: str, success: bool, ...) -> str`

记录技能使用。

**参数:**
- `skill_name`: 技能包名称
- `action`: 执行的动作
- `success`: 是否成功
- `duration_ms`: 耗时（毫秒）
- `tokens_used`: 使用的 Token 数
- `error_message`: 错误信息（可选）

**返回:**
- 记录 ID

#### `evaluate_skills(period_days: int = 7) -> List[SkillEvaluation]`

评估技能包。

**参数:**
- `period_days`: 评估周期（天数）

**返回:**
- 评估结果列表

#### `generate_weekly_report(week_start: Optional[str] = None) -> Optional[str]`

生成周度技能使用报告。

**参数:**
- `week_start`: 周开始日期，默认为上周一

**返回:**
- 报告文件路径

## 与 Scheduler 集成

在 `scheduler.py` 中添加以下任务：

```python
# 自我进化任务
from apps.evolution import EvolutionReporter, SkillEvaluator

# 月度进化报告（每月 2 号 09:00）
def task_evolution_report():
    reporter = EvolutionReporter()
    return reporter.generate_monthly_report()

# 技能评估（每周日 22:00）
def task_skill_eval():
    evaluator = SkillEvaluator()
    return evaluator.evaluate_skills(period_days=7)
```

### Cron 配置

```cron
# 自我进化任务
0 9 2 * * python3 scheduler.py run evolution-report  # 每月 2 号
0 22 * * 0 python3 scheduler.py run skill-eval       # 每周日
```

## 输出文件

### 进化报告

位置：`memory/evolution/reports/evolution_report_YYYY-MM.md`

包含：
- 📊 系统状态
- 📈 成长指标
- 🎯 技能成长
- 📚 学习进度
- 💡 改进建议
- 📅 下月计划

### 技能评估报告

位置：`memory/evolution/evaluations/skill_report_YYYY-MM-DD.md`

包含：
- 📈 总体概况
- 🏆 技能排行 TOP10
- 📋 详细评估（每个技能的优缺点和建议）

## 数据文件

- `memory/evolution/skill_usage.json` - 技能使用记录
- `memory/evolution/evaluations/skill_evaluation.json` - 技能评估结果
- `memory/evolution/reports/*.json` - 进化报告原始数据

## 测试

运行集成测试：

```bash
python3 apps/evolution/test_evolution.py
```

## 依赖

- Python 3.8+
- 标准库（无外部依赖）

## 版本

v4.0.0 - Memory Suite v4.0 融合版

## 作者

Memory Suite Team
