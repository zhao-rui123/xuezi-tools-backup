# 微电网 / 离网 + 柴发场景输入模板

## 最小必填

- `project_info.project_name`
- `project_info.scenario_type = "microgrid"`
- `project_info.grid_connection_mode = "microgrid"`
- `project_info.latitude`
- `project_info.longitude`
- `load_data.peak_load_kw`
- `load_data.critical_load_kw`
- `load_data.backup_hours_required`
- `market_data.market_mode = "offgrid_internal"`
- `equipment.conventional_backup.enabled`
- `equipment.conventional_backup.fuel_cost_per_kwh`
- `resource_data.solar.installed_capacity_mwp` 或 `resource_data.wind.installed_capacity_mw`

## 推荐输入优先级

高精度优先：
- 原始 `15min` 负荷曲线
- 光伏 `8760` 小时出力，或 `8760` 小时辐照
- 风电 `8760` 风速序列 + `power_curve`，或 `8760` 小时出力

自动兜底：
- 只给站点坐标 + 装机量时，agent 会自动补齐可用资源数据，并沿用同一套风光模型计算
- 这条自动兜底链更适合中精度方案，不等同于你提供 `8760` 原始资源序列时的高精度结果

## 自动计算口径

- `project_info.latitude / longitude`
  作为资源自动补齐和光伏倾角推荐的基础坐标

- `resource_data.public_resource_year`
  可选；指定自动抓取公开小时级资源时使用的年份。未填写时默认取最近一个完整自然年。

- `resource_data.solar.tilt_deg = null`
  表示不手填倾角，agent 会按站点纬度自动给出推荐倾角，并直接参与计算

- `resource_data.solar.azimuth_deg`
  默认 `180`，即朝南；如有特殊朝向可显式覆盖

- `resource_data.solar.tracking_mode`
  可填 `fixed_tilt`、`single_axis`、`dual_axis`

## 当前场景口径

- 当前模板用于 `microgrid / offgrid_internal` 场景，不走源网荷储并网交易口径
- 储能和风光容量会进入离网优化链路，与柴发保供约束一起评估
- 柴发当前按 `fuel_cost_per_kwh` 近似进入内部供电成本，不展开更细柴油机启停与分段效率模型
- `backup_hours_required` 与 `critical_load_kw` 用于约束保供型容量下限
- `backup_soc_ratio` 用于给储能保留保供 `SOC`

## 关键字段说明

- `resource_data.solar.installed_capacity_mwp`
  计划光伏装机；若只给位置和装机量，agent 仍可自动走资源补齐与倾角推荐

- `resource_data.wind.installed_capacity_mw`
  计划风电装机；若同时提供 `wind_speed_series_mps_path + power_curve`，会优先走更高精度口径

- `equipment.conventional_backup.minimum_output_kw`
  柴发最小稳定出力口径，用于限制备用机组下限

- `equipment.conventional_backup.fuel_cost_per_kwh`
  柴发折算单位供电成本，当前离网成本测算直接使用

## 推荐流程

1. 先填 `examples/microgrid_offgrid_template.json`
2. 如果已有 `8760` 风光资源数据，优先补入路径字段
3. 如果暂时只有站点坐标和装机量，也可以先跑自动兜底版
4. 运行 `analyze`，查看推荐容量、推荐倾角、资源精度、剩余柴发成本与财务结果
