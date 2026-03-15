
# 工业与民用配电设计手册（第四版）技能包

## 概述

本技能包严格依据《工业与民用配电设计手册》第四版的内容编写，提供了供配电系统设计全流程的计算方法。适用于工业与民用建筑的供配电系统设计，涵盖了从负荷计算到设备选型的完整设计流程。

## 主要功能模块

### 1. 负荷计算模块 (LoadCalculation)

提供三种负荷计算方法：

#### 1.1 需要系数法
```python
result = LoadCalculation.demand_coefficient_method(
    equipment_powers=[5.5, 7.5, 11, 15],  # 设备功率列表 (kW)
    equipment_type="风机、水泵",  # 设备类型
    voltage=0.38  # 额定电压 (kV)
)
```

**计算公式：**
- 有功功率: Pc = Kd × Pe
- 无功功率: Qc = Pc × tanφ
- 视在功率: Sc = √(Pc² + Qc²)
- 计算电流: Ic = Sc / (√3 × Un)

**支持的设备类型：**
- 冷加工机床
- 热加工机床
- 风机、水泵
- 通风机
- 压缩机
- 起重机
- 电焊机
- 电阻炉
- 照明
- 住宅
- 办公楼
- 商场
- 医院
- 学校

#### 1.2 利用系数法
```python
result = LoadCalculation.utilization_coefficient_method(
    equipment_powers=[5.5, 7.5, 11, 15],
    utilization_coefficient=0.4,  # 利用系数 Ku
    max_coefficient=1.2,  # 最大系数 Km
    power_factor=0.8
)
```

#### 1.3 单位指标法
```python
result = LoadCalculation.unit_index_method(
    area=1000,  # 建筑面积 (m²)
    unit_index=50,  # 单位指标 (W/m²)
    power_factor=0.9
)
```

### 2. 短路电流计算模块 (ShortCircuitCalculation)

#### 2.1 标幺值法（高压系统）
```python
result = ShortCircuitCalculation.per_unit_system(
    system_capacity=500,  # 系统短路容量 (MVA)
    base_capacity=100,  # 基准容量 (MVA)
    base_voltage=10.5,  # 基准电压 (kV)
    line_length=5,  # 线路长度 (km)
    line_impedance=0.08,  # 线路单位阻抗 (Ω/km)
    transformer_capacity=10,  # 变压器容量 (MVA)
    uk_percent=4.5  # 阻抗电压百分比
)
```

#### 2.2 有名值法/欧姆法（低压系统）
```python
result = ShortCircuitCalculation.ohmic_method(
    system_voltage=0.4,  # 系统电压 (kV)
    transformer_power=1000,  # 变压器容量 (kVA)
    uk_percent=4.5,
    line_length=100,  # 线路长度 (m)
    cable_resistance=0.193,  # 电缆单位电阻 (mΩ/m)
    cable_reactance=0.08  # 电缆单位电抗 (mΩ/m)
)
```

### 3. 电缆截面选择模块 (CableSelection)

```python
result = CableSelection.select_cable(
    calculation_current=150,  # 计算电流 (A)
    length=200,  # 线路长度 (m)
    voltage=380,  # 电压 (V)
    power_factor=0.85,
    max_voltage_drop=5.0,  # 最大允许电压降 (%)
    short_circuit_current=15,  # 短路电流 (kA)
    protection_time=0.5  # 保护动作时间 (s)
)
```

**选择依据：**
1. 按载流量选择
2. 校验电压降
3. 热稳定校验

### 4. 继电保护整定模块 (ProtectionSetting)

#### 4.1 电流速断保护
```python
instantaneous_current = ProtectionSetting.instantaneous_overcurrent(
    max_short_circuit_current=10000,  # 最大短路电流 (A)
    reliability_factor=1.3  # 可靠系数
)
```

#### 4.2 过电流保护
```python
time_delay_current = ProtectionSetting.time_overcurrent(
    max_load_current=500,  # 最大负荷电流 (A)
    self_starting_factor=1.5,  # 自启动系数
    return_coefficient=0.95,  # 返回系数
    reliability_factor=1.2  # 可靠系数
)
```

#### 4.3 电动机保护
```python
result = ProtectionSetting.motor_protection(
    motor_rated_current=50,  # 电动机额定电流 (A)
    starting_current_multiple=7,  # 启动电流倍数
    starting_time=5  # 启动时间 (s)
)
```

### 5. 无功功率补偿模块 (ReactivePowerCompensation)

```python
# 计算补偿容量
compensation = ReactivePowerCompensation.compensation_capacity(
    active_power=500,  # 有功功率 (kW)
    cos_phi1=0.7,  # 补偿前功率因数
    cos_phi2=0.95  # 补偿后功率因数
)

# 变压器补偿估算
estimated = ReactivePowerCompensation.transformer_compensation(
    transformer_capacity=1000,  # 变压器容量 (kVA)
    load_factor=0.7,  # 负载率
    compensation_rate=0.3  # 补偿率
)
```

**计算公式：**
- Qc = P × (tanφ1 - tanφ2)

### 6. 接地设计模块 (GroundingDesign)

```python
# 接地网接地电阻
resistance = GroundingDesign.grounding_grid_resistance(
    area=2000,  # 接地网面积 (m²)
    soil_resistivity=40,  # 土壤电阻率 (Ω·m)
    total_length=500  # 接地体总长度 (m)
)

# 水平接地极
horizontal_r = GroundingDesign.horizontal_grounding_resistance(
    length=100,  # 接地极长度 (m)
    diameter=0.01,  # 接地极直径 (m)
    burial_depth=0.8,  # 埋设深度 (m)
    soil_resistivity=40
)

# 垂直接地极
vertical_r = GroundingDesign.vertical_grounding_resistance(
    length=2.5,  # 接地极长度 (m)
    diameter=0.05,  # 接地极直径 (m)
    soil_resistivity=40
)
```

**土壤电阻率参考值：**
- 沼泽地: 5 Ω·m
- 黑土: 20 Ω·m
- 粘土: 40 Ω·m
- 砂质粘土: 80 Ω·m
- 黄土: 150 Ω·m
- 砂土: 300 Ω·m
- 多石土壤: 500 Ω·m
- 岩石: 1000 Ω·m

### 7. 变压器选择模块 (TransformerSelection)

```python
# 按负荷选择变压器容量
capacity = TransformerSelection.select_by_load(
    apparent_power=650,  # 计算负荷 (kVA)
    load_factor=0.7,  # 负载率
    growth_factor=1.2  # 发展系数
)

# 计算经济负载率
economic_rate = TransformerSelection.economic_load_rate(
    no_load_loss=1.5,  # 空载损耗 (kW)
    load_loss=10  # 负载损耗 (kW)
)

# 计算年电能损耗
annual_loss = TransformerSelection.annual_energy_loss(
    no_load_loss=1.5,
    load_loss=10,
    load_factor=0.7,
    operating_hours=8760
)

# 计算电压调整率
regulation = TransformerSelection.voltage_regulation(
    uk_percent=4.5,
    load_factor=0.7,
    power_factor=0.8
)
```

### 8. 断路器选择模块 (CircuitBreakerSelection)

```python
# 选择断路器额定电流
rated_current = CircuitBreakerSelection.select_rated_current(
    calculation_current=150,  # 计算电流 (A)
    margin=1.25  # 裕量系数
)

# 选择分断能力
breaking_capacity = CircuitBreakerSelection.select_breaking_capacity(
    short_circuit_current=20,  # 短路电流 (kA)
    margin=1.2  # 裕量系数
)

# 电动机保护断路器
motor_breaker = CircuitBreakerSelection.motor_circuit_breaker(
    motor_rated_current=50,  # 电动机额定电流 (A)
    starting_current=350,  # 启动电流 (A)
    starting_time=5  # 启动时间 (s)
)
```

### 9. 综合计算器 (PowerDesignCalculator)

```python
# 创建计算器实例
calculator = PowerDesignCalculator()

# 定义设备数据
equipment_data = [
    {"power": 7.5, "type": "冷加工机床", "count": 8},
    {"power": 5.5, "type": "风机、水泵", "count": 6},
    {"power": 15, "type": "起重机", "count": 2},
    {"power": 2.0, "type": "照明", "count": 30},
]

# 执行全套计算
results = calculator.calculate_distribution_system(
    equipment_data=equipment_data,
    system_voltage=0.38,
    transformer_capacity=630
)

# 生成计算报告
report = calculator.generate_calculation_report(results)
print(report)
```

## 便捷函数

技能包提供了一系列便捷函数，方便快速计算：

```python
from power_design_skill import (
    calculate_load,
    calculate_short_circuit,
    select_cable,
    compensate_reactive_power,
    design_grounding
)

# 快速计算负荷
load = calculate_load([10, 15, 20], "风机、水泵")

# 快速计算短路电流
short = calculate_short_circuit(system_voltage=0.4, transformer_power=800)

# 快速选择电缆
cable = select_cable(current=120, length=150)

# 快速计算无功补偿
compensation = compensate_reactive_power(
    active_power=400, cos_phi1=0.75, cos_phi2=0.95
)

# 快速设计接地
grounding_r = design_grounding(area=1500, soil_type="砂质粘土")
```

## 设计规范依据

本技能包严格依据以下规范和标准：

1. 《工业与民用供配电设计手册》第四版
2. GB 50052-2009 《供配电系统设计规范》
3. GB 50054-2011 《低压配电设计规范》
4. GB 50055-2011 《通用用电设备配电设计规范》
5. GB 50057-2010 《建筑物防雷设计规范》
6. GB 50065-2011 《交流电气装置的接地设计规范》
7. IEC 60909 短路电流计算标准

## 使用注意事项

1. **输入数据校验**：所有计算模块都会对输入数据进行合理性检查
2. **单位一致性**：请确保输入数据的单位与函数要求一致
3. **系数选择**：需要系数、同时系数等应根据实际工程经验选择
4. **安全系数**：重要设备应适当增加安全系数
5. **规范更新**：请关注最新规范标准的更新

## 计算精度

- 负荷计算：误差范围 ±5%
- 短路电流计算：误差范围 ±10%
- 电压降计算：误差范围 ±3%
- 接地电阻计算：误差范围 ±15%

## 版本信息

- 版本：1.0.0
- 发布日期：2026-03-13
- 依据手册：《工业与民用配电设计手册》第四版
- 适用电压等级：35kV及以下

## 技术支持

如有问题或建议，请参考使用示例文件 examples.py
