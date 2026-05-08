# Energy Solution Agent

本项目是一个本地可运行的 Python CLI，用于对新能源电力、综合能源、工商业储能、光储充、冷热负荷、零碳工厂以及中国电力市场场景做规则驱动分析。

它的定位不是正式可研或电气设计软件，而是一个方案分析底座，供上层 agent 在本地基线规则、年度时序、调度、结算和省级差异规则之上稳定输出结构化结论。

## 当前能力

- 光伏资源建模
- 风电资源建模
- 储能年度调度、寿命、衰减和收益近似
- 光储充与充电站负荷协同分析
- 冷热负荷 sizing 与电负荷耦合
- 零碳工厂路径、碳核算和行业模板
- 中国电力市场分时、需量、交易结算近似
- 省级规则 baseline、override 与在线刷新
- benchmark 批跑、聚合摘要和质量门槛
- 电力交易工商业储能场景
  支持 `spot_intraday` 日内套利窗口识别、叠加原始 `15min` 负荷反推装机量，以及交易型收益输出
- 源网荷储工商业场景
  支持光伏/风电先压低用户净负荷，再基于净负荷判断储能装机容量与运行策略

## 运行方式

### 单案例分析

```bash
python -m energy_solution_agent analyze --input path/to/input.json --output path/to/output.json --report path/to/report.md
```

### 开启在线规则刷新

```bash
python -m energy_solution_agent analyze --input path/to/input.json --output path/to/output.json --report path/to/report.md --live-rules
```

`--live-rules` 会：

- 根据省级 profile 的官方链接抓取网页
- 提取规则关键词和部分结构化字段
- 尝试生成在线规则 patch
- 将 patch 覆盖到 `market_data`
- 在输出中保留抓取状态、时间、来源和生效字段

### Benchmark 批跑

```bash
python -m energy_solution_agent benchmark --examples examples --output out/benchmark_summary.json
```

## 校验

项目当前没有额外引入 lint/typecheck 依赖，默认校验入口统一为：

```bash
python scripts/verify.py
```

该脚本会执行：

- `src/` 与 `tests/` 下 Python 文件的 `ast` 语法校验
- `tests.test_data_ingest`
- `tests.test_solvers`
- `tests.test_engine`

## 示例

### 内置输入样例

- `examples/zero_carbon_factory_input.json`
- `examples/charging_station_input.json`
- `examples/market_storage_input.json`
- `examples/power_trading_storage_input.json`
- `examples/source_grid_load_storage_input.json`
- `examples/power_trading_storage_template.json`
- `examples/source_grid_load_storage_template.json`
- `examples/series_ingest_input.json`
- `examples/data_center_input.json`
- `examples/steel_factory_input.json`
- `examples/jingye_storage_input.json`
- `examples/mauritania_mine_input.json`
- `examples/railway_storage_input.json`

### 原始序列样例

- `examples/load_24h.csv`
- `examples/pv_24h.csv`
- `examples/wind_speed_24h.csv`

### Power Trading 模板

- 可运行示例：`examples/power_trading_storage_input.json`
- 项目模板：`examples/power_trading_storage_template.json`
- 字段说明：`examples/power_trading_storage_template.md`

### Source Grid Load Storage 模板

- 可运行示例：`examples/source_grid_load_storage_input.json`
- 项目模板：`examples/source_grid_load_storage_template.json`
- 字段说明：`examples/source_grid_load_storage_template.md`

推荐每个电力交易工商业储能项目至少提供：

- `market_data.market_price_series_path`
- `load_data.load_series_kw_path`
- `load_data.peak_load_kw`
- `market_data.contract_capacity_kw` 或 `market_data.transformer_capacity_kva`
- `market_data.arbitrage_plan.min_charge_hours`
- `market_data.arbitrage_plan.min_discharge_hours`
- `market_data.arbitrage_plan.max_charge_hours`
- `market_data.arbitrage_plan.max_discharge_hours`
- `market_data.arbitrage_plan.min_spread_yuan_per_mwh`
- `equipment.storage.sizing_target_day_coverage_ratio`

电力交易场景当前默认口径：

- 不跨日，`continuous_horizon = false`
- 最小价差阈值 `250 元/MWh`
- 装机量按 `90%` 分位覆盖推荐
- 默认按厂内消纳建模，不按反输电口径计算

源网荷储场景当前默认口径：

- 先用光伏/风电压低用户净负荷，再进入储能 sizing
- 第一版默认按厂内消纳口径处理，不先展开复杂反送电结算
- 储能调度优先沿用现有 `renewable_priority` / `peak_shaving` / `market_responding` 策略框架
- 支持 `operation_mode` 自动路由：
  `renewable_self_consumption`、`renewable_peak_shaving`、`renewable_tou_arbitrage`、`renewable_market_cooptimization`、`renewable_export_oriented`

## 输出

单案例分析会生成：

- 结构化 JSON
- 中文 Markdown 报告

benchmark 会生成：

- `summary`
- `benchmarks`

其中 `summary` 聚合：

- 总案例数
- 场景分布
- 省份分布
- 置信度分布
- 平均收益
- 平均 IRR
- 最大数据缺口
- 质量门槛通过率

## 已知边界

- 更适合高质量方案级、投决前测算，不替代正式可研、电气设计审查或施工图设计
- 在线规则刷新已接入，但网页结构化提取仍属于增强层，不替代人工最终复核
- 冷热部分当前重点是 sizing 和年量，不是完整暖通设计软件
- 充电站部分当前是运营近似，不是严格排队仿真器

## 目录重点

- `src/energy_solution_agent/engine.py`：主引擎
- `src/energy_solution_agent/solvers.py`：调度和求解
- `src/energy_solution_agent/resource_models.py`：光伏、风电资源模型
- `src/energy_solution_agent/settlement.py`：结算逻辑
- `src/energy_solution_agent/live_rules.py`：在线规则刷新与解析
- `src/energy_solution_agent/benchmark.py`：benchmark 批跑与汇总
- `tests/test_engine.py`：回归测试
