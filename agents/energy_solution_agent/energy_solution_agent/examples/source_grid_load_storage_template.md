# 源网荷储工商业场景输入模板

## 最小必填

- `project_info.project_name`
- `project_info.province`
- `project_info.city`
- `project_info.voltage_level_kv`
- `load_data.load_series_kw_path`
- `load_data.peak_load_kw`
- `resource_data.solar` 或 `resource_data.wind`
- `market_data.market_mode`

## 推荐原始输入

- 用户原始 `15min` 负荷曲线
- 光伏小时出力序列，或可推导光伏发电的原始资源参数
- 风电小时风速/出力序列，或可推导风电发电的原始资源参数
- 项目当地分时电价、需量电费、合同容量/变压器容量

## 当前场景口径

- 先按光伏/风电发电序列压低用户净负荷
- 再基于净负荷调用现有储能容量测算逻辑
- 第一版默认按厂内消纳口径建模
- 第一版不展开复杂反送电收益结算
- 储能策略优先推荐 `renewable_priority`

## 玩法路由

- `renewable_self_consumption`
  默认自发自用优先
- `renewable_peak_shaving`
  目标优先压需量/压峰值
- `renewable_tou_arbitrage`
  有分时电价时自动命中
- `renewable_market_cooptimization`
  有现货/交易价格序列时自动命中
- `renewable_export_oriented`
  `allow_export_to_grid = true` 时优先命中
- 也可以显式填写 `project_info.operation_mode` 强制覆盖自动路由

## 分析模式

- 当前这条市场协同优化线默认只做 `historical_backtest`
- 即：基于历史价格回测和反推装机，不做未来价格预测

## 市场协同优化附加参数

- `market_data.renewable_charge_threshold_price_per_kwh`
  当电价低于这个阈值时，可触发“绿电优先转储、低价市电供负荷”的玩法
- `market_data.cooptimization_min_sell_spread_per_kwh`
  当前低价与未来高价之间至少要满足的价差门槛
- `market_data.export_price_per_kwh`
  允许外送时的结算电价；不填时会退回到保守估算

## 关键输出

- `annual_renewable_direct_use_mwh`
  新能源直接供负荷的电量
- `annual_renewable_surplus_mwh`
  新能源超过负荷的富余电量
- `storage_sizing_basis`
  当前储能容量测算口径，源网荷储场景应为 `net_load_after_pv_wind`
- `sizing_net_load_peak_kw`
  光伏/风电压降后的净负荷峰值

## 推荐流程

1. 先填 `examples/source_grid_load_storage_template.json`
2. 再参考 `examples/source_grid_load_storage_input.json` 检查字段完整性
3. 用 `analyze` 生成净负荷、储能推荐容量、调度与财务结果
