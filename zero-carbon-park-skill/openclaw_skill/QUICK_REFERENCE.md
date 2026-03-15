# OpenClaw 技能包速查表

## 快速入口

```python
from openclaw_skill import (
    EnergyBase,           # 基础能源计算
    CarbonCalculator,     # 碳排放核算
    SchemeDesigner,       # 方案设计
    IndustryDatabase,     # 行业数据库
    PVWindCalculator,     # 光伏风电
    WasteHeatCalculator,  # 余热余冷
    BuildingEnergyCalculator,  # 建筑节能
    HarmonicAnalyzer,     # 谐波分析
    GeoTools,             # 地理工具
    EquipmentDatabase,    # 设备数据库
)
```

---

## 1. 基础能源计算 (EnergyBase)

### 水系统
```python
energy = EnergyBase()

# 压力损失
energy.calculate_water_pressure_loss(
    flow_rate=100,      # m³/h
    pipe_diameter=150,  # mm
    pipe_length=500     # m
)

# 水泵功率
energy.calculate_water_pump_power(
    flow_rate=100,      # m³/h
    head=50             # m
)
```

### 电气系统
```python
# 无功补偿
energy.calculate_power_factor_correction(
    active_power=500,   # kW
    current_pf=0.75,
    target_pf=0.95
)

# 变压器损耗
energy.calculate_transformer_loss(
    capacity=1000,      # kVA
    load_rate=0.75
)

# 电缆选型
energy.calculate_cable_sizing(
    power=100,          # kW
    voltage=380,        # V
    length=200          # m
)
```

### 暖通系统
```python
# 采暖热负荷
energy.calculate_heating_load(
    area=10000,         # m²
    building_type='industrial'
)

# 空调冷负荷
energy.calculate_cooling_load(
    area=10000,
    building_type='industrial'
)
```

### 综合能耗
```python
energy.calculate_comprehensive_energy(
    water_m3=10000,
    electricity_kwh=500000,
    gas_m3=50000,
    heat_gj=200
)
```

---

## 2. 碳排放核算 (CarbonCalculator)

```python
carbon = CarbonCalculator(region='east')

# 固定燃烧排放
carbon.calculate_stationary_combustion({
    'natural_gas': 100000,
    'diesel': 50
})

# 外购电力排放
carbon.calculate_purchased_electricity(
    electricity_mwh=1000,
    green_electricity_mwh=200
)

# 总排放
carbon.calculate_total_emissions()

# 减排措施评估
carbon.calculate_reduction_measures([
    {
        'name': '光伏系统',
        'type': 'renewable',
        'reduction_tco2': 500,
        'investment': 2000000,
        'annual_benefit': 400000
    }
])

# 碳中和路径
carbon.calculate_carbon_neutral_pathway(
    base_year_emission=10000,
    target_year=2060
)
```

---

## 3. 行业数据库 (IndustryDatabase)

```python
db = IndustryDatabase()

# 获取行业列表
db.get_industry_list()

# 获取行业信息
db.get_industry_info('chemical')

# 踏勘指导
db.get_site_survey_guide('chemical')

# 节能措施
db.get_energy_saving_measures('chemical', 'high')

# 谐波信息
db.get_harmonic_info('steel')

# 光伏储能建议
db.get_renewable_recommendations('data_center')

# 碳排放特征
db.get_carbon_profile('chemical')
```

### 支持的行业代码
| 代码 | 行业名称 |
|------|----------|
| chemical | 化工行业 |
| steel | 钢铁行业 |
| textile | 纺织行业 |
| data_center | 数据中心 |
| nonferrous_metal | 有色金属 |
| metal_smelting | 金属冶炼 |
| automotive | 汽车制造 |
| new_energy_equipment | 新能源设备制造 |
| petroleum | 石油石化 |
| food_processing | 食品加工 |
| pharmaceutical | 医药制造 |
| electronics | 电子制造 |
| paper | 造纸行业 |
| cement | 水泥行业 |

---

## 4. 光伏风电计算 (PVWindCalculator)

### 最佳倾角计算
```python
pv = PVWindCalculator()

# 简单计算
pv.calculate_optimal_tilt(
    latitude=39.9,
    optimization='annual'  # annual/winter/summer
)

# 详细分析
pv.calculate_detailed_tilt_analysis(
    latitude=39.9,
    longitude=116.4
)
```

### 光伏系统设计
```python
pv.design_pv_array(
    capacity_kw=500,
    latitude=39.9,
    install_type='rooftop'  # rooftop/ground/bipv
)
```

### 风电系统设计
```python
pv.design_wind_turbine(
    avg_wind_speed=5.5,
    target_capacity=100,
    turbine_type='small'  # small/medium/large
)
```

### 风光互补系统
```python
pv.design_hybrid_system(
    latitude=39.9,
    longitude=116.4,
    avg_wind_speed=5.5,
    electricity_demand_kwh=1000000,
    renewable_target=0.5
)
```

---

## 5. 余热余冷计算 (WasteHeatCalculator)

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
wh.calculate_waste_heat_potential(source)

# 设计回收系统
wh.design_recovery_system(
    source_temp=350,
    source_power=500,
    application='power_generation'  # power_generation/steam/heating/cooling
)

# 设备选型
wh.select_equipment(source, {})

# 换热器设计
wh.design_heat_exchanger(
    hot_stream={'temp_in': 350, 'temp_out': 150, 'flow_rate': 5000, 'cp': 1.1, 'medium': 'flue_gas'},
    cold_stream={'temp_in': 20, 'temp_out': 80, 'flow_rate': 10000, 'cp': 4.18, 'medium': 'water'}
)

# 余冷计算
wh.calculate_waste_cold_potential(
    cold_source_temp=5,
    ambient_temp=25,
    cooling_capacity=100
)
```

---

## 6. 建筑节能计算 (BuildingEnergyCalculator)

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
    roof_u=0.5,
    window_u=2.8
)

# 热损失计算
building.calculate_envelope_heat_loss(envelope)

# 年采暖负荷
building.calculate_annual_heating_load(
    envelope,
    climate_zone='cold'  # severe_cold/cold/hot_summer_cold_winter/hot_summer_warm_winter/mild
)

# 空调冷负荷
building.calculate_cooling_load(envelope, climate_zone='cold')

# 围护结构优化
building.optimize_envelope(
    envelope,
    target_standard='industrial_2020',
    climate_zone='cold'
)

# 照明对比
building.compare_lighting_options(
    area=5000,
    required_illuminance=300
)

# 自然采光
building.calculate_daylighting(
    room_area=100,
    window_area=20,
    window_orientation='south'
)

# 工业建筑能耗
building.calculate_industrial_building_energy(
    floor_area=5000,
    building_type='workshop',  # workshop/warehouse/office
    climate_zone='cold'
)

# 通风系统设计
building.design_industrial_ventilation(
    building_volume=20000,
    pollution_level='medium',  # low/medium/high
    heat_recovery=True
)
```

---

## 7. 谐波分析 (HarmonicAnalyzer)

```python
analyzer = HarmonicAnalyzer()

# THD计算
harmonics = {5: 25, 7: 15, 11: 8, 13: 5}
analyzer.calculate_thd(harmonics)

# 电流THD计算
analyzer.calculate_current_thd(
    fundamental_current=100,
    harmonics=harmonics
)

# 合规性检查
analyzer.check_compliance(
    harmonics,
    voltage_level='voltage_380v'  # voltage_380v/voltage_6kv/voltage_10kv/voltage_35kv
)

# 影响分析
analyzer.analyze_harmonic_impact(
    thd_voltage=8.5,
    thd_current=20,
    transformer_capacity=1000,
    load_power=600
)

# 治理方案设计
analyzer.design_mitigation_system(
    harmonics=harmonics,
    load_power=100,
    target_thd=5.0
)

# 获取行业谐波特征
analyzer.get_industry_harmonic_profile('steel')

# 获取谐波源治理选项
analyzer.get_source_mitigation_options('vfd_6pulse')
```

---

## 8. 零碳园区方案设计 (SchemeDesigner)

```python
from openclaw_skill import SchemeDesigner
from openclaw_skill.core.scheme_design import SchemeConfig

# 配置方案
config = SchemeConfig(
    name='某工业园区',
    location=(39.9, 116.4),  # (纬度, 经度)
    area=50000,              # m²
    building_area=30000,     # m²
    annual_electricity=2000000,  # kWh
    annual_heat=5000,        # GJ
    annual_cooling=3000,     # GJ
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

---

## 9. 地理工具 (GeoTools)

```python
geo = GeoTools()

# 获取城市坐标
geo.get_coordinates('北京')

# 根据经纬度查找城市
geo.get_city_by_coordinates(39.9, 116.4)

# 获取气候分区
geo.get_climate_zone(city_name='北京')
geo.get_climate_zone(latitude=39.9)

# 获取太阳辐射
geo.get_solar_radiation(city_name='北京')
geo.get_solar_radiation(latitude=39.9)

# 最佳光伏倾角
geo.get_optimal_pv_tilt(39.9, optimization='annual')

# 最佳光伏方位角
geo.get_optimal_pv_azimuth(39.9)

# 估算风资源
geo.estimate_wind_resource(39.9, 116.4, altitude=50)

# 获取附近城市
geo.get_nearby_cities(39.9, 116.4, radius_km=100)

# 位置综合信息
geo.get_location_info(39.9, 116.4)
```

---

## 10. 设备数据库 (EquipmentDatabase)

```python
db = EquipmentDatabase()

# 查询设备
db.get_pv_module('mono_550w')
db.get_inverter('string_100k')
db.get_battery_system('lithium_215kwh')
db.get_wind_turbine('small_50kw')
db.get_efficient_motor('ie3_15kw')
db.get_vfd('vfd_15kw')
db.get_air_compressor('screw_37kw')
db.get_heat_pump('ashp_100kw')
db.get_waste_heat_equipment('whb_500kw')
db.get_led_light('led_highbay_100w')
db.get_active_filter('apf_100a')

# 按功率搜索
db.search_by_power('motor', min_power=10, max_power=30)

# 设备推荐
db.get_recommendation('inverter', {'target_power': 100})

# 设备对比
db.compare_equipment('motor', ['ie3_15kw', 'ie4_15kw'])
```

---

## 常用常数

### 标准煤折算系数 (kgce/单位)
| 能源类型 | 系数 |
|----------|------|
| 电力 | 0.1229 kgce/kWh |
| 天然气 | 1.2143 kgce/m³ |
| 蒸汽 | 0.1286 kgce/kg |
| 水 | 0.0857 kgce/m³ |

### 碳排放因子 (tCO2/单位)
| 能源类型 | 因子 |
|----------|------|
| 电网电力 | 0.5703 tCO2/MWh |
| 天然气 | 2.162 tCO2/1000m³ |
| 蒸汽(燃煤) | 0.11 tCO2/GJ |

---

## 常见问题

### Q: 如何根据经纬度计算光伏最佳倾角?
```python
from openclaw_skill import PVWindCalculator

pv = PVWindCalculator()
result = pv.calculate_optimal_tilt(latitude=39.9)
print(f"最佳倾角: {result['optimal_tilt_angle']:.1f}°")
```

### Q: 如何查询某行业的踏勘要点?
```python
from openclaw_skill import IndustryDatabase

db = IndustryDatabase()
guide = db.get_site_survey_guide('chemical')
print(guide['key_info'])
```

### Q: 如何设计一个余热回收系统?
```python
from openclaw_skill import WasteHeatCalculator, HeatSource

wh = WasteHeatCalculator()
source = HeatSource(name='烟气', temp_in=300, temp_out=150, flow_rate=5000, medium='flue_gas')
potential = wh.calculate_waste_heat_potential(source)
system = wh.design_recovery_system(300, potential['recoverable_power_kw'], 'power_generation')
```

### Q: 如何检查谐波是否达标?
```python
from openclaw_skill import HarmonicAnalyzer

analyzer = HarmonicAnalyzer()
result = analyzer.check_compliance({5: 25, 7: 15}, 'voltage_380v')
print(f"是否达标: {result['overall_compliance']}")
```

---

## 更新日志

### v1.0.0 (2024)
- 初始版本发布
- 包含10个核心模块
- 支持14个高耗能行业
- 涵盖水电气暖、光伏风电、余热回收、建筑节能、谐波治理、碳排放核算
