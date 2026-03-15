# OpenClaw 零碳园区建设技能包

一个专业的零碳园区规划与节能诊断Python工具包，为能源工程师、节能服务公司和园区管理者提供全面的技术计算和方案设计支持。

## 功能概览

### 核心模块

| 模块 | 功能描述 |
|------|----------|
| `core/energy_base` | 水电气暖基础能源计算 |
| `core/carbon_calc` | 碳排放核算与减排规划 |
| `core/scheme_design` | 零碳园区综合方案设计 |
| `industries/industry_db` | 12大高耗能行业工艺参数库 |
| `calculations/pv_wind` | 光伏风电系统设计与倾角计算 |
| `calculations/waste_heat` | 余热余冷回收与产品选型 |
| `calculations/building_energy` | 工业建筑节能计算 |
| `calculations/harmonic` | 谐波分析与治理 |
| `utils/geo_tools` | 地理工具与气候数据 |
| `utils/equipment_db` | 节能设备产品数据库 |

## 快速开始

### 安装

```bash
# 将技能包复制到项目目录
cp -r openclaw_skill /your/project/path/

# 在Python中使用
import sys
sys.path.insert(0, '/your/project/path')

from openclaw_skill import EnergyBase, CarbonCalculator, SchemeDesigner
```

### 基础使用示例

```python
from openclaw_skill import EnergyBase, PVWindCalculator, IndustryDatabase

# 1. 基础能源计算
energy = EnergyBase()
result = energy.calculate_power_factor_correction(
    active_power=500,
    current_pf=0.75,
    target_pf=0.95
)
print(f"需要补偿: {result['compensation_required_kvar']:.2f} kvar")

# 2. 光伏最佳倾角计算
pv = PVWindCalculator()
tilt = pv.calculate_optimal_tilt(latitude=39.9)
print(f"最佳倾角: {tilt['optimal_tilt_angle']:.1f}°")

# 3. 行业信息查询
db = IndustryDatabase()
info = db.get_industry_info('chemical')
print(f"行业名称: {info['name']}")
```

## 详细功能说明

### 1. 水电气暖基础计算

#### 水系统计算
- 水管网压力损失计算
- 水泵功率计算与选型
- 水泵节能改造效益

```python
from openclaw_skill import EnergyBase

energy = EnergyBase()

# 压力损失计算
loss = energy.calculate_water_pressure_loss(
    flow_rate=100,  # m³/h
    pipe_diameter=150,  # mm
    pipe_length=500  # m
)

# 水泵功率计算
pump = energy.calculate_water_pump_power(
    flow_rate=100,
    head=50
)
```

#### 电气系统计算
- 无功补偿计算
- 变压器损耗分析
- 电缆选型计算

```python
# 无功补偿
pf = energy.calculate_power_factor_correction(
    active_power=500,  # kW
    current_pf=0.75,
    target_pf=0.95
)

# 变压器损耗
tx = energy.calculate_transformer_loss(
    capacity=1000,  # kVA
    load_rate=0.75
)

# 电缆选型
cable = energy.calculate_cable_sizing(
    power=100,  # kW
    voltage=380,  # V
    length=200  # m
)
```

#### 暖通系统计算
- 采暖热负荷计算
- 空调冷负荷计算
- 暖通节能改造

```python
# 采暖热负荷
heating = energy.calculate_heating_load(
    area=10000,  # m²
    building_type='industrial'
)

# 空调冷负荷
cooling = energy.calculate_cooling_load(
    area=10000,
    building_type='industrial'
)
```

### 2. 碳排放核算

#### 排放计算
- 范围1: 固定燃烧、移动源、工业过程排放
- 范围2: 外购电力、热力排放
- 范围3: 上游排放

```python
from openclaw_skill import CarbonCalculator

carbon = CarbonCalculator(region='east')

# 固定燃烧排放
fuel = {'natural_gas': 100000, 'diesel': 50}
result = carbon.calculate_stationary_combustion(fuel)

# 外购电力排放
elec = carbon.calculate_purchased_electricity(
    electricity_mwh=1000,
    green_electricity_mwh=200
)

# 总排放
total = carbon.calculate_total_emissions()
```

#### 减排规划
- 减排措施评估
- 碳中和路径规划
- 产品碳足迹

```python
# 减排措施
measures = [
    {
        'name': '光伏系统',
        'type': 'renewable',
        'reduction_tco2': 500,
        'investment': 2000000,
        'annual_benefit': 400000
    }
]
reduction = carbon.calculate_reduction_measures(measures)

# 碳中和路径
pathway = carbon.calculate_carbon_neutral_pathway(
    base_year_emission=10000,
    target_year=2060
)
```

### 3. 行业数据库

支持12大高耗能行业:
- 化工行业
- 钢铁行业
- 纺织行业
- 数据中心
- 有色金属
- 金属冶炼
- 汽车制造
- 新能源设备制造
- 石油石化
- 食品加工
- 医药制造
- 造纸行业
- 水泥行业

```python
from openclaw_skill import IndustryDatabase

db = IndustryDatabase()

# 获取行业信息
info = db.get_industry_info('chemical')

# 踏勘指导
survey = db.get_site_survey_guide('chemical')

# 节能措施
measures = db.get_energy_saving_measures('chemical', 'high')

# 谐波信息
harmonic = db.get_harmonic_info('steel')

# 光伏储能建议
renewable = db.get_renewable_recommendations('data_center')
```

### 4. 光伏风电设计

#### 最佳倾角计算
根据经纬度自动计算光伏最佳倾角:

```python
from openclaw_skill import PVWindCalculator

pv = PVWindCalculator()

# 简单计算
tilt = pv.calculate_optimal_tilt(
    latitude=39.9,  # 北京
    optimization='annual'
)

# 详细分析
detailed = pv.calculate_detailed_tilt_analysis(
    latitude=39.9,
    longitude=116.4
)
```

#### 光伏系统设计
```python
# 设计光伏阵列
array = pv.design_pv_array(
    capacity_kw=500,
    latitude=39.9,
    install_type='rooftop'
)

# 风光互补系统
hybrid = pv.design_hybrid_system(
    latitude=39.9,
    longitude=116.4,
    avg_wind_speed=5.5,
    electricity_demand_kwh=1000000,
    renewable_target=0.5
)
```

### 5. 余热余冷回收

```python
from openclaw_skill import WasteHeatCalculator, HeatSource

wh = WasteHeatCalculator()

# 定义热源
source = HeatSource(
    name='窑炉烟气',
    temp_in=350,
    temp_out=150,
    flow_rate=5000,
    medium='flue_gas'
)

# 计算余热潜力
potential = wh.calculate_waste_heat_potential(source)

# 设计回收系统
system = wh.design_recovery_system(
    source_temp=350,
    source_power=500,
    application='power_generation'
)

# 设备选型
equipment = wh.select_equipment(source, {})
```

### 6. 建筑节能计算

```python
from openclaw_skill import BuildingEnergyCalculator, BuildingEnvelope

building = BuildingEnergyCalculator()

# 定义围护结构
envelope = BuildingEnvelope(
    wall_area=3000,
    roof_area=2000,
    window_area=800,
    floor_area=5000,
    wall_u=0.6,
    roof_u=0.5
)

# 热损失计算
heat_loss = building.calculate_envelope_heat_loss(envelope)

# 年采暖负荷
heating = building.calculate_annual_heating_load(envelope, 'cold')

# 围护结构优化
optimization = building.optimize_envelope(envelope)

# 照明对比
lighting = building.compare_lighting_options(area=5000)
```

### 7. 谐波分析

```python
from openclaw_skill import HarmonicAnalyzer

analyzer = HarmonicAnalyzer()

# THD计算
harmonics = {5: 25, 7: 15, 11: 8}
thd = analyzer.calculate_thd(harmonics)

# 合规性检查
compliance = analyzer.check_compliance(harmonics, 'voltage_380v')

# 影响分析
impact = analyzer.analyze_harmonic_impact(
    thd_voltage=8.5,
    thd_current=20,
    transformer_capacity=1000,
    load_power=600
)

# 治理方案
mitigation = analyzer.design_mitigation_system(
    harmonics=harmonics,
    load_power=100
)
```

### 8. 零碳园区方案设计

```python
from openclaw_skill import SchemeDesigner, SchemeConfig

# 配置方案
config = SchemeConfig(
    name='某工业园区',
    location=(39.9, 116.4),
    area=50000,
    building_area=30000,
    annual_electricity=2000000,
    annual_heat=5000,
    industry_type='chemical'
)

# 创建设计师
designer = SchemeDesigner(config)

# 生成综合方案
scheme = designer.generate_comprehensive_scheme(
    target_renewable_ratio=0.5
)

# 导出报告
report = designer.export_scheme_report()
```

### 9. 地理工具

```python
from openclaw_skill import GeoTools

geo = GeoTools()

# 获取城市坐标
coords = geo.get_coordinates('北京')

# 获取气候分区
climate = geo.get_climate_zone(latitude=39.9)

# 获取太阳辐射
radiation = geo.get_solar_radiation(city_name='北京')

# 位置综合信息
info = geo.get_location_info(39.9, 116.4)
```

### 10. 设备数据库

```python
from openclaw_skill import EquipmentDatabase

db = EquipmentDatabase()

# 查询设备
module = db.get_pv_module('mono_550w')
inverter = db.get_inverter('string_100k')
motor = db.get_efficient_motor('ie3_15kw')

# 按功率搜索
motors = db.search_by_power('motor', 10, 30)

# 设备推荐
recommendations = db.get_recommendation(
    'inverter',
    {'target_power': 100}
)
```

## 目录结构

```
openclaw_skill/
├── __init__.py              # 包初始化
├── README.md                # 说明文档
├── example_usage.py         # 使用示例
├── core/                    # 核心模块
│   ├── energy_base.py       # 基础能源计算
│   ├── carbon_calc.py       # 碳排放核算
│   └── scheme_design.py     # 方案设计
├── industries/              # 行业数据库
│   └── industry_db.py       # 12大行业参数
├── calculations/            # 计算模块
│   ├── pv_wind.py           # 光伏风电
│   ├── waste_heat.py        # 余热余冷
│   ├── building_energy.py   # 建筑节能
│   └── harmonic.py          # 谐波分析
└── utils/                   # 工具模块
    ├── geo_tools.py         # 地理工具
    └── equipment_db.py      # 设备数据库
```

## 技术规格

### 支持的计算类型

| 类别 | 计算内容 |
|------|----------|
| 水系统 | 压力损失、水泵功率、节能改造 |
| 电气系统 | 无功补偿、变压器损耗、电缆选型 |
| 燃气系统 | 管道选型、锅炉效率 |
| 暖通系统 | 热负荷、冷负荷、节能改造 |
| 光伏系统 | 最佳倾角、阵列设计、发电量估算 |
| 风电系统 | 功率计算、系统设计、资源分析 |
| 储能系统 | 容量设计、收益估算 |
| 余热回收 | 资源评估、系统设计、设备选型 |
| 建筑节能 | 围护结构、照明、通风 |
| 谐波治理 | THD计算、影响分析、治理方案 |
| 碳排放 | 核算、减排规划、碳足迹 |

### 行业覆盖

- 化工行业
- 钢铁行业
- 纺织行业
- 数据中心
- 有色金属
- 金属冶炼
- 汽车制造
- 新能源设备制造
- 石油石化
- 食品加工
- 医药制造
- 造纸行业
- 水泥行业
- 电子制造

## 版本信息

- 版本: 1.0.0
- 作者: OpenClaw Team
- 更新日期: 2024

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎反馈。
