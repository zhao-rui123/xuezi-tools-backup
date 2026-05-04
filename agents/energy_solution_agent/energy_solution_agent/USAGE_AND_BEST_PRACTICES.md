# Energy Solution Agent 使用说明 + 最佳实践手册

> 目标：让这套新能源方案 / 前置可研 agent 在日常项目里稳定、快速、专业地跑出可信结果。

---

## 1. 这套 agent 适合做什么

### 最适合
- 海外矿区 / 园区 / 工厂的风光储前置方案分析
- 工商业储能 / 光储充 / 零碳工厂的投决前测算
- 多方案经济对比（IRR / NPV / coverage / cycle）
- 快速生成中文 Word 报告 + 图表

### 不适合直接替代
- 正式可研院的最终版可研报告
- 电气施工图设计 / 一次二次校核
- 真实 EMS 控制策略上线参数
- 银行最终授信模型（可做前置，不建议直接当最终底稿）

---

## 2. 最推荐的工作流

### 工作流 A：最快速（已有项目坐标）
适合：海外项目、资源还没整理、想先快速看方向

1. 填 `project_info.lat/lon`
2. 设 `resource_mode = "auto_fetch"`
3. 选一个合理的 `scenario_type`
4. 填年负荷、峰值负荷、外购电/柴油替代电价
5. 跑 `analyze`

优点：快，能自动抓资源。  
缺点：资源精度取决于 NASA POWER / Open-Meteo。

---

### 工作流 B：标准专业版（推荐）
适合：你已经拿到了逐时资源或项目负荷资料

1. 用 `master_input_template.json` 起项目
2. 填 8760 光伏 / 风速 / 负荷数据
3. 设设备模型（组件 / 风机 / 储能）
4. 明确税法适用性和融资结构
5. 先跑 `analyze`
6. 再跑 `econ_scan.py` 找最优组合
7. 最后导出 Word 报告

这是最稳的一套。

---

### 工作流 C：汇报版（给老板/客户）
适合：已经有一个候选方案，要出正式汇报稿

1. 用标准输入跑出结果
2. 检查以下 4 项：
   - IRR / NPV
   - 基线年成本 vs 项目后成本
   - 收益拆解
   - 风险与敏感性
3. 导出 Word 报告
4. 必要时补项目背景文字

---

## 3. 输入文件最重要的 10 个字段

### 1) `project_info.scenario_type`
常用：
- `zero_carbon_factory`
- `microgrid`
- `charging_station`
- `market_storage`

### 2) `project_info.resource_mode`
- `auto_fetch`：自动抓资源
- 空：手工输入资源数据

### 3) `project_info.lat / lon`
自动抓资源时必须有。

### 4) `load_data.annual_consumption_mwh`
最关键字段之一，影响所有 sizing 和经济性。

### 5) `load_data.peak_load_kw`
决定储能 / 并网 / 削峰基础规模。

### 6) `market_data.market_mode`
常用：
- `offgrid_internal`
- `ppa`
- `tou_tariff`
- `spot`

### 7) `market_data.fuel_cost_per_kwh`
离网/柴油替代项目最关键。别填错单位。  
这里默认按 **RMB/kWh** 理解。

### 8) `financial.optimization_target`
可选：
- `irr`
- `npv`

如果你是老板或投委会导向，优先 `irr`。  
如果你更看绝对价值，优先 `npv`。

### 9) `financial.is_overseas_project`
海外项目强烈建议显式写：
```json
"is_overseas_project": true
```
避免税法判断歧义。

### 10) `equipment.storage.power_candidate_kw / energy_candidate_kwh`
如果要让 agent 自动择优储能，必须给候选集合，而不是只给一个值。

---

## 4. 自动资源抓取怎么用

### 最简写法
```json
{
  "project_info": {
    "resource_mode": "auto_fetch",
    "lat": 23.196941,
    "lon": -11.959593
  }
}
```

### 目前第一版接入
- NASA POWER：光照
- Open-Meteo：风速、温度

### 自动结果会写入
- 光伏：年辐照、月度辐照、8760小时辐照
- 风电：8760风速、年平均风速
- 资源来源元数据

### 注意
第一版是“前置可研级自动资源”，不是最终商业数据库替代品。  
正式高价值项目，建议后续用 8760 专业数据覆盖。

---

## 5. 8760 真数据的最佳实践

### 最推荐输入
- `resource_data.solar.hourly_generation_profile_kw`（8760）
- `resource_data.wind.wind_speed_series_mps`（8760）+ turbine model
- `load_data.load_series_kw`（8760）

### 如果没有 8760
可以退而求其次：
- 168 小时周型
- 24 小时工作日 / 周末双日型
- 季节性日型

### 原则
**8760 > 168 > 24+weekend > 24单日型**

---

## 6. 储能怎么让它“选得靠谱”

### 现在的推荐方法
给一组候选：
```json
"power_candidate_kw": [10000, 20000, 30000],
"energy_candidate_kwh": [20000, 35000, 50000]
```

agent 会：
- 跑真实 dispatch
- 跑真实 finance
- 按 `optimization_target` 选最优

### 经验建议
- 如果电价低（如 0.15 美元/kWh 级别），储能通常要小甚至不要
- 如果替代电价高（如 0.30 美元/kWh），小储能往往最优
- 大储能不一定更赚，很多时候只会把 IRR 拉低

### 看哪几个指标判断储能是否合理
- `storage_equivalent_full_cycles_per_year`
- `storage_lcos`
- `annual_storage_discharge_mwh`
- `annual_ancillary_service_revenue`

### 红线
如果储能年循环太低（<200），通常说明：
- 储能偏大
- 或时序不匹配
- 或电价机制不支持

---

## 7. 海外项目最佳实践

### 必做
```json
"financial": {
  "is_overseas_project": true,
  "tax": {"applicable": false}
}
```

### 原因
- 避免误套中国增值税 / 所得税逻辑
- 保持财务口径清晰

### 还建议你明确
- 外购电价 / 柴油替代成本
- 汇率口径（如果后续要扩展）
- 资源来源说明

---

## 8. 什么时候该用 `econ_scan.py`

### 建议用在这 3 种场景
1. 你不知道 PV / 储能该配多大
2. 你想比较 IRR 最优 vs NPV 最优
3. 你怀疑当前推荐方案不是最优

### 典型命令
```bash
PYTHONPATH=src python3 scripts/econ_scan.py examples/mauritania_mine_input.json --fuel 0.30 --target irr
```

### 它适合回答的问题
- 光伏要不要再小一点？
- 储能是 10/20 还是 20/35 更好？
- 电价从 0.15 提到 0.30 以后最优方案怎么变？

---

## 9. 看报告时优先看哪几页

### 对老板 / 业主
优先看：
1. 推荐方案
2. 财务分析
3. 收益拆解
4. 风险与敏感性

### 对技术团队
优先看：
1. 资源评估
2. 调度结果
3. 储能月度充放电图
4. 时序和输入假设

### 对投委会 / 金融方
优先看：
1. 基线年能源成本
2. NPV / IRR / DSCR
3. 分项 LCOE / LCOS
4. Tornado 敏感性图

---

## 10. 最常见的 8 个坑

### 坑1：把美元/kWh直接当人民币/kWh
现在模型默认财务口径按 **RMB/kWh**。  
如果你说“0.30 美元/kWh”，要么先换算，要么统一明确口径。

### 坑2：海外项目忘了关税法
这会直接把结果带歪。

### 坑3：只给年电量，不给峰值负荷
会影响储能 sizing。

### 坑4：用 24 小时单日型直接当全年
能跑，但精度有限。

### 坑5：给了风速但没给 turbine model
现在有默认模型，但最好显式指定。

### 坑6：储能候选只给一个点
那就不是优化，而是指定。

### 坑7：只看覆盖率，不看 IRR
高覆盖率不等于经济最优。

### 坑8：只看 IRR，不看收益结构
有时项目 IRR 好，是某一项收益过于敏感，不一定稳。

---

## 11. 一套推荐的“标准输入策略”

### 海外风光储项目
- `resource_mode = auto_fetch`
- `scenario_type = zero_carbon_factory`
- `is_overseas_project = true`
- 给一组储能候选
- 先按 `irr` 优化
- 再跑 `npv` 对照

### 国内工商业储能
- `scenario_type = market_storage`
- 明确 `tou_tariff`
- 储能候选多给几组
- 看 `storage_lcos` 和 `annual_demand_charge_cost`

### 零碳工厂汇报版
- 建议补：
  - `seasonal_daily_profiles_kw`
  - 冷热负荷序列
  - `carbon_claim_target`
- 报告效果最好

---

## 12. 如果你只记住一句话

> **先把输入边界弄清楚，再让 agent 跑最优；不要拿模糊输入去追求“精确结果”。**

这套 agent 已经很强，但它最擅长的是：
**在清晰边界下，快速找出可信、专业、可交付的最优前置方案。**

---

## 13. 推荐配套文件

- `templates/master_input_template.json`
- `templates/master_delivery_checklist.md`
- `templates/device_model_catalog.md`

这三份一起用，最稳。
