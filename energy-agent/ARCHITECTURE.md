# 储能电价循环优化Agent - 架构设计

*版本：v1.0 | 日期：2026-04-09 | 状态：Phase 1 交付物*

---

## 1. 设计目标

将 `cycle_optimizer.py` 从一次性脚本升级为**持久化Agent**：
- 支持多天跨天充放电循环（今天充电，明天放电）
- 不预设固定阈值，动态计算最优策略
- 支持国网电费清单Excel（96点/天和24点/天）
- 提供CLI交互 + JSON结果导出

---

## 2. 核心模块划分

```
energy-agent/
├── agent/
│   ├── __init__.py
│   ├── core.py              # [A] Agent主入口，状态管理，对话交互
│   ├── data_loader.py       # [B] Excel加载器，格式自动识别
│   ├── cycle_engine.py      # [C] 核心DP算法（继承现有逻辑）
│   ├── strategy_optimizer.py# [D] 多天跨天策略增强
│   └── report_generator.py  # [E] 控制台报告 + JSON导出
├── config/
│   └── default_config.json   # 默认参数配置
├── tests/
│   └── test_cycle_engine.py  # 单元测试
├── main.py                   # CLI入口
└── ARCHITECTURE.md           # 本文档
```

### 模块职责

| 模块 | 职责 | 关键类/函数 |
|------|------|------------|
| **core.py** | Agent生命周期管理、状态持久化、CLI交互 | `EnergyAgent` |
| **data_loader.py** | Excel解析、多格式兼容、数据清洗 | `PriceDataLoader` |
| **cycle_engine.py** | 候选循环枚举、DP加权区间调度 | `CycleEngine` |
| **strategy_optimizer.py** | 跨天循环增强、全局策略优化 | `StrategyOptimizer` |
| **report_generator.py** | 格式化输出、JSON序列化 | `ReportGenerator` |

---

## 3. 数据流设计

```
[Excel文件]
     │
     ▼
┌─────────────┐
│ DataLoader  │ ← 自动识别96点/24点格式
└──────┬──────┘
       │ List[Tuple[datetime, float]]
       ▼
┌─────────────┐
│ CycleEngine │ ← 枚举候选循环 + DP最优选择
└──────┬──────┘
       │ List[CycleResult]
       ▼
┌──────────────────────┐
│ StrategyOptimizer    │ ← 跨天增强（可选）
└──────┬───────────────┘
       │ List[CycleResult]
       ▼
┌──────────────────────┐
│ ReportGenerator      │ ← 控制台 + JSON
└──────────────────────┘
```

### 数据结构

```python
@dataclass
class PricePoint:
    dt: datetime       # 时间点
    price: float       # 电价（元/MWh）

@dataclass
class CycleResult:
    charge_start: datetime
    charge_end: datetime
    charge_len: int         # 小时数
    charge_price: float     # 充电均价
    discharge_start: datetime
    discharge_end: datetime
    discharge_len: int
    discharge_price: float  # 放电均价
    spread: float           # 价差
    profit_per_mwh: float   # 每MWh利润
```

---

## 4. Agent与用户交互方式

### 4.1 CLI交互（主要方式）

```bash
# 基本用法
python main.py run <excel文件> [--output <输出路径>]

# 高级选项
python main.py run <excel文件> \
  --min-charge-len 2 --max-charge-len 6 \
  --min-discharge-len 2 --max-discharge-len 6 \
  --positive-only \
  --output ./output/result.json

# 仅查看Top-N候选循环（不跑DP）
python main.py top <excel文件> --n 10

# 帮助
python main.py --help
```

### 4.2 交互式模式

```bash
$ python main.py interactive
energy-agent> load data/电费清单_2026_03.xlsx
energy-agent> show summary
energy-agent> optimize
energy-agent> export result.json
energy-agent> quit
```

### 4.3 程序化调用（Python API）

```python
from agent.core import EnergyAgent

agent = EnergyAgent()
agent.load_excel("电费清单.xlsx")
agent.configure(min_charge_len=3, max_charge_len=5)
result = agent.optimize()
agent.export_json("output.json")
print(agent.report())
```

---

## 5. 核心算法说明（CycleEngine）

### 5.1 两阶段算法

**阶段1：候选循环枚举**
- 充电时长范围：`[min_charge_len, max_charge_len]`（默认2-6小时）
- 放电时长范围：`[min_discharge_len, max_discharge_len]`（默认2-6小时）
- 只保留 `spread > 0` 的正收益循环
- 时间复杂度：O(n × charge_range × discharge_range)

**阶段2：加权区间调度DP**
- 按 `discharge_end` 排序
- 二分查找找每个循环右侧最近不重叠的前置循环
- DP状态：`dp[i] = max(dp[i-1], profit[i] + dp[p(i)])`
- 回溯重建最优解

### 5.2 跨天策略增强（StrategyOptimizer）

默认算法只处理"今天充明天放"紧邻的两段式循环。
`StrategyOptimizer` 额外探索：
- **跨天循环**：充电和放电之间允许隔1-3天
- **充电延迟**：找到低价区间后，等待确认再充电
- **放电延迟**：找到高价区间后，等待确认再放电

### 5.3 不预设阈值的动态计算

- 不写死"低于xxx元充电"
- 所有阈值由枚举阶段自动发现
- 用户可设置 `min_spread > 0` 过滤微利循环

---

## 6. 配置参数（default_config.json）

```json
{
  "cycle": {
    "min_charge_len": 2,
    "max_charge_len": 6,
    "min_discharge_len": 2,
    "max_discharge_len": 6,
    "positive_only": true,
    "min_spread": 0
  },
  "strategy": {
    "enable_cross_day": false,
    "max_gap_days": 3,
    "enable_delayed_charge": false,
    "enable_delayed_discharge": false
  },
  "output": {
    "default_output_dir": "./output",
    "json_indent": 2,
    "console_format": "pretty"
  }
}
```

---

## 7. 输出格式

### 7.1 控制台报告示例

```
============================================================
⚡ 储能电价循环优化报告
============================================================

📊 数据概览
   文件：电费清单_2026_03.xlsx
   时间范围：2026-03-01 00:00 ~ 2026-03-07 23:00
   数据点数：168 个（小时间隔）

💰 最优充放电循环（共 3 个）
──────────────────────────────────────────────────────────────
循环 #1  ★ 推荐
  充电：2026-03-02 23:00 ~ 2026-03-03 04:00（6小时）
  充电均价：380.50 元/MWh
  放电：2026-03-03 07:00 ~ 2026-03-03 12:00（6小时）
  放电均价：612.30 元/MWh
  价差：231.80 元/MWh
  利润：231.80 元/MWh

循环 #2
  充电：2026-03-05 00:00 ~ 2026-03-05 05:00（5小时）
  充电均价：395.20 元/MWh
  放电：2026-03-05 08:00 ~ 2026-03-05 13:00（5小时）
  放电均价：585.60 元/MWh
  价差：190.40 元/MWh
  利润：190.40 元/MWh

──────────────────────────────────────────────────────────────
📈 汇总统计
   总循环数：3 个
   总利润：623.50 元/MWh
   平均价差：207.83 元/MWh
============================================================
```

### 7.2 JSON导出格式

```json
{
  "version": "2.0",
  "generated_at": "2026-04-09T12:38:00",
  "data_summary": {
    "source_file": "电费清单_2026_03.xlsx",
    "time_range": {
      "start": "2026-03-01T00:00:00",
      "end": "2026-03-07T23:00:00"
    },
    "data_points": 168
  },
  "optimization_params": {
    "min_charge_len": 2,
    "max_charge_len": 6,
    "min_discharge_len": 2,
    "max_discharge_len": 6,
    "positive_only": true
  },
  "total_cycles": 3,
  "total_profit": 623.50,
  "avg_spread": 207.83,
  "cycles": [
    {
      "id": 1,
      "recommend": true,
      "charge_start": "2026-03-02T23:00:00",
      "charge_end": "2026-03-03T04:00:00",
      "charge_len": 6,
      "charge_price": 380.50,
      "discharge_start": "2026-03-03T07:00:00",
      "discharge_end": "2026-03-03T12:00:00",
      "discharge_len": 6,
      "discharge_price": 612.30,
      "spread": 231.80,
      "profit_per_mwh": 231.80
    }
  ]
}
```

---

## 8. 依赖关系

```
核心依赖（Python >= 3.9）：
- pandas          # Excel读取
- numpy           # 数值计算
- openpyxl        # Excel文件解析

可选依赖：
- click           # CLI框架（如果需要更漂亮的CLI）
- rich            # 控制台彩色输出
```

---

## 9. 后续Phase规划

| Phase | 内容 | 优先级 |
|-------|------|--------|
| P2 | DataLoader多格式兼容（96点/24点自动识别） | P0 |
| P2 | 核心cycle_engine模块化重构 | P0 |
| P3 | CLI交互界面（main.py + click） | P1 |
| P3 | ReportGenerator美化输出 | P1 |
| P4 | StrategyOptimizer跨天策略 | P2 |
| P5 | 单元测试覆盖 | P2 |

---

## 10. 已知约束与待确认

1. **Excel格式**：现有代码只处理"实时"列（col_idx=2），是否需要支持"日前"列？
2. **96点/天数据**：15分钟间隔，每天96个数据点，需要确认格式是否与24点共存
3. **储能容量**：目前输出单位是"元/MWh"，是否需要根据具体储能容量换算？
4. **多文件输入**：是否需要支持一次输入多个Excel文件？
