# 电力交易工商业储能场景输入模板

## 最小必填

- `project_info.project_name`
- `project_info.province`
- `project_info.city`
- `project_info.voltage_level_kv`
- `load_data.load_series_kw_path`
- `load_data.peak_load_kw`
- `market_data.market_price_series_path`
- `market_data.arbitrage_plan.mode`
- `market_data.arbitrage_plan.min_charge_hours`
- `market_data.arbitrage_plan.min_discharge_hours`
- `market_data.arbitrage_plan.min_spread_yuan_per_mwh`

## 常用项目参数

- `market_data.contract_capacity_kw`
  用于限制充电时的可购电空间；有明确合同容量时应填写。
- `market_data.transformer_capacity_kva`
  没有合同容量时可作为变压器边界参考。
- `market_data.demand_charge_rate_per_kw_month`
  如果项目还要叠加需量收益，应填写。
- `market_data.ancillary_service_*`
  辅助服务收益口径；没有就填 `0`。
- `market_data.demand_response_*`
  需求响应收益口径；没有就填 `0`。
- `market_data.arbitrage_plan.continuous_horizon`
  `false` 表示逐日独立优化，`true` 表示跨日连续 `SOC`。
- `market_data.arbitrage_plan.max_charge_hours`
  单次充电窗口上限，默认建议 `6`。
- `market_data.arbitrage_plan.max_discharge_hours`
  单次放电窗口上限，默认建议 `6`。
- `equipment.storage.sizing_target_day_coverage_ratio`
  推荐装机覆盖分位，默认 `0.9`。

## 默认口径

- `market_data.arbitrage_plan.continuous_horizon`
  默认 `false`，即不跨日。
- `market_data.arbitrage_plan.min_spread_yuan_per_mwh`
  默认 `250`。
- `equipment.storage.sizing_target_day_coverage_ratio`
  默认 `0.9`，即按 `90%` 分位覆盖推荐装机量。
- 放电边界
  默认按厂内消纳口径建模，不按反输电电网口径计算。

## 输入边界

- `load_series_kw_path` 应为原始 `15min` 负荷曲线，不要给测算模型文件。
- `market_price_series_path` 应为原始现货价格表，不要先做人工筛选。
- 若价格单位是 `元/MWh`，当前逻辑可自动识别；若是 `元/kWh` 也可自动识别。

## 推荐流程

1. 先用 `examples/power_trading_storage_template.json` 填项目参数。
2. 再对照 `examples/power_trading_storage_input.json` 检查字段是否齐全。
3. 用 `analyze` 跑出推荐 `MW / MWh`、套利窗口和收益。
