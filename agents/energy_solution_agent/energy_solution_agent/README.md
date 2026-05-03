# Energy Solution Agent

本项目是一个本地可运行的 Python CLI，用于对新能源电力、综合能源、光储充、冷热负荷、零碳工厂和中国电力市场场景做规则驱动分析。

它的定位不是正式可研设计软件，而是一个专家级方案分析底座，便于 `openclaw` 或其他上层 agent 在本地 baseline、联网规则刷新、年度时序、调度和结算框架上稳定输出复杂方案。

## 当前能力

- 光伏资源建模
- 风电资源建模
- 储能年度调度、寿命、衰减和收益近似
- 光储充与充电场站负荷分析
- 冷热负荷 sizing 与电负荷耦合
- 零碳工厂路径、碳核算和行业模板
- 中国电力市场分时/需量/市场响应近似
- 省级规则 baseline + override + 在线刷新
- benchmark 批跑、聚合摘要和质量门槛

## 运行方式

### 1. 单案例分析

```bash
python -m energy_solution_agent analyze --input path/to/input.json --output path/to/output.json --report path/to/report.md
```

### 2. 开启联网规则刷新

```bash
python -m energy_solution_agent analyze --input path/to/input.json --output path/to/output.json --report path/to/report.md --live-rules
```

`--live-rules` 会：
- 根据省级 profile 的官方来源链接抓取网页
- 提取规则关键词和部分结构化字段
- 尝试生成在线规则 patch
- 将 patch 覆盖到 `market_data`
- 在输出中保留抓取状态、时间、来源和生效字段

### 3. benchmark 批跑

```bash
python -m energy_solution_agent benchmark --examples examples --output out/benchmark_summary.json
```

## 示例

### 已内置样例

- `examples/zero_carbon_factory_input.json`
- `examples/charging_station_input.json`
- `examples/market_storage_input.json`
- `examples/series_ingest_input.json`
- `examples/data_center_input.json`
- `examples/steel_factory_input.json`
- `examples/jingye_storage_input.json`
- `examples/mauritania_mine_input.json`
- `examples/railway_storage_input.json`

### 真数据文件样例

- `examples/load_24h.csv`
- `examples/pv_24h.csv`
- `examples/wind_speed_24h.csv`

程序支持从 `json / csv / txt` 读取本地序列文件。

## 输出

单案例分析会生成：
- 结构化 JSON
- 中文 Markdown 报告

benchmark 会生成：
- `summary`
- `benchmarks`

其中 `summary` 会聚合：
- 总案例数
- 场景分布
- 省份分布
- 置信度分布
- 平均收益
- 平均 IRR
- 最大缺口/风险
- 质量门槛通过率

## 已知边界

- 该程序更适合高质量方案级/投决前测算，不替代正式可研、电气设计审查或施工图设计。
- 联网规则刷新当前已接入，但在线页面结构化抽取仍属于增强层，不应替代人工最终复核。
- 冷热部分当前重点是 sizing 和年量，不是完整暖通设备设计软件。
- 充电场站部分当前是运营近似，不是严格排队论仿真器。

## 扩展建议

后续如果继续迭代，优先方向建议是：
- 增加更多省级规则样本
- 增加更多 benchmark 样例
- 深化储能与市场联动
- 深化行业模板
- 增强 `8760` 真数据清洗与接管

## 目录重点

- `src/energy_solution_agent/engine.py`：主引擎
- `src/energy_solution_agent/solvers.py`：调度和求解
- `src/energy_solution_agent/resource_models.py`：光伏/风电资源模型
- `src/energy_solution_agent/settlement.py`：结算逻辑
- `src/energy_solution_agent/live_rules.py`：联网规则刷新与解析
- `src/energy_solution_agent/benchmark.py`：benchmark 批跑与汇总
- `tests/test_engine.py`：回归测试
