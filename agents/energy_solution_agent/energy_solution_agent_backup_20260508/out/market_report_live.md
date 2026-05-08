# 新能源电力解决方案分析报告

## 项目概况
- 项目名称：示例市场响应型储能项目
- 场景类型：user_side_storage
- 省份：山东
- 数据完整度：A
- 数据质量等级：high / 100
- 省级规则状态：verified
- 电网区域：华北

## 推荐方案
- 光伏：1.85 MWp
- 风电：0 MW
- 储能：2.5 MW / 5.0 MWh
- 充电容量：0 MW
- 供冷容量：0 RT
- 供热容量：0 MWth

## 核心测算
- 年光伏发电量：352.29
- 年风电发电量：None
- 年储能放电量：4.13
- 年充电量：0.0
- 年供冷量：None
- 年供热量：None
- 年购电量：44.87

## 市场规则要点
- 山东现货市场和新版省级市场规则较成熟，用户侧和新型主体参与度高。
- 官方政策解读明确：山东电力现货市场于 2024-06-17 转入正式运行；新版市场规则自 2026-01-01 起执行。
- 工商业分时仍需结合现货和代理购电等口径综合分析，不能单独看固定分时。
- 储能应按现货、日内和用户侧报价参与逻辑设计调度情景，不应只按静态峰谷套利。

## 资源评估
- 光伏资源口径：monthly_irradiation_kwh_per_m2 / medium
- 光伏 P50/P90：352.29 / 331.15
- 光伏倾角/方位角/温度修正：0.9862 / 1.0 / 1.0
- 光伏有效 PR：0.83
- 风电资源口径：no_wind_resource / low
- 风电 P50/P90：None / None
- 风电功率曲线：False

## 调度结果
- 基线峰值购电功率：2813.29
- 储能后峰值购电功率：2814.44
- 估算削峰量：-1.16
- 日储能循环次数：0.002
- 储能策略模式：market_responding
- 年储能吞吐量：6.65
- 年等效满循环：0.826
- 估算寿命年限：8471.53
- 绿电/新能源充电占比：0.0
- 有效往返效率：0.9081
- 预留SOC/保供SOC：0.08 / 0.05
- 年衰减率/寿命末容量比：0.022 / 0.56
- 充电排队指数：None
- 充电多车型多样性系数：None
- 年锅炉燃料等价值：0.0
- 冷/热峰值需求：None / None

## 财务结果
- 年收益/节费：271370.0
- 年电量电费：31283.17
- 年需量电费：210000.0
- 年辅助服务收益：72000.0
- 年需求响应收益：-4.16
- 储能更换年份/成本：None / None
- 运维递增率：0.02
- 项目 IRR：None
- 回收期：None
- NPV：-9726340.79
- 单位减碳成本：32689.34

## 碳结果
- 基线排放：24.68
- 项目后排放：0.0
- 年减排量：24.68
- 声明边界：需按范围一/二边界、环境属性归属和外部核证要求进一步确认零碳声明边界

## 减排路径拆分
- 工艺/热源替代与能效提升：减排 0.0 tCO2e，占比 0.0
- 绿电/光伏/储能替代购电排放：减排 194.1 tCO2e，占比 1.0

## 储能月度视图
- 1月：充电 2.52 MWh，放电 4.131 MWh，毛收益 3.72
- 2月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0
- 3月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0
- 4月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0
- 5月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0
- 6月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0
- 7月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0
- 8月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0
- 9月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0
- 10月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0
- 11月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0
- 12月：充电 0.0 MWh，放电 0.0 MWh，毛收益 0.0

## 风险与缺口
- 风险：光伏发电量当前基于 monthly_irradiation_kwh_per_m2 估算，资源精度仍可提升。

## 数据质量检查
- load_data.load_series_kw：missing - load_data.load_series_kw 缺失或为空。
- load_data.cooling_load_series_kw：missing - load_data.cooling_load_series_kw 缺失或为空。
- load_data.heating_load_series_kw：missing - load_data.heating_load_series_kw 缺失或为空。
- resource_data.solar.hourly_generation_profile_kw：missing - resource_data.solar.hourly_generation_profile_kw 缺失或为空。
- resource_data.wind.hourly_generation_profile_kw：missing - resource_data.wind.hourly_generation_profile_kw 缺失或为空。
- resource_data.wind.wind_speed_series_mps：missing - resource_data.wind.wind_speed_series_mps 缺失或为空。
- charging_data.arrival_profile：missing - charging_data.arrival_profile 缺失或为空。

## 敏感性分析
- 峰谷价差下降10%：年度收益影响 -21709.6，IRR 敏感度 medium
- 设备投资上升10%：年度收益影响 0.0，IRR 敏感度 high
- 年可调用天数下降10%：年度收益影响 -16282.2，IRR 敏感度 medium
- 绿电覆盖率下降10%：年度收益影响 -123.4，IRR 敏感度 medium
