# 零碳园区技能包 - 快速参考

## 部署位置
`~/.openclaw/workspace/skills/zero-carbon-park/`

## 核心功能

### 1. 基础能源计算
```python
from core.energy_base import EnergyBase

energy = EnergyBase()

# 无功补偿计算
result = energy.calculate_power_factor_correction(
    active_power=500,    # 有功功率(kW)
    current_pf=0.75,     # 当前功率因数
    target_pf=0.95       # 目标功率因数
)
print(f"需要补偿: {result['compensation_required_kvar']:.2f} kvar")

# 水泵功率计算
pump = energy.calculate_water_pump_power(
    flow_rate=100,   # 流量(m³/h)
    head=50          # 扬程(m)
)
print(f"轴功率: {pump['shaft_power_kw']:.2f} kW")
```

### 2. 光伏风电计算
```python
from calculations.pv_wind import PVWindCalculator

pv = PVWindCalculator()

# 最佳倾角计算
tilt = pv.calculate_optimal_tilt(latitude=39.9)
print(f"最佳倾角: {tilt['optimal_tilt_angle']:.1f}°")
```

### 3. 碳排放计算
```python
from core.carbon_calc import CarbonCalculator

carbon = CarbonCalculator()

# 计算碳排放量
emission = carbon.calculate_emission(
    energy_type='electricity',
    amount=10000,    # 电量(kWh)
    region='china'
)
print(f"碳排放: {emission:.2f} kg CO2")
```

### 4. 行业数据库
```python
from industries.industry_db import IndustryDatabase

db = IndustryDatabase()

# 查询行业信息
info = db.get_industry_info('chemical')
print(f"行业名称: {info['name']}")
print(f"单位能耗: {info['energy_consumption']}")
```

## 功能模块

| 模块 | 功能 |
|------|------|
| `core/energy_base` | 水电气暖基础计算 |
| `core/carbon_calc` | 碳排放核算 |
| `core/scheme_design` | 零碳园区方案设计 |
| `calculations/pv_wind` | 光伏风电设计 |
| `calculations/waste_heat` | 余热回收 |
| `calculations/building_energy` | 建筑节能 |
| `industries/industry_db` | 行业数据库 |
| `utils/equipment_db` | 设备数据库 |

## 测试通过
✅ 无功补偿计算 - 276.62 kvar
✅ 光伏最佳倾角 - 44.9° (北京)
✅ 水泵功率计算 - 18.17 kW

---
*快速参考 - 2026-03-13*
