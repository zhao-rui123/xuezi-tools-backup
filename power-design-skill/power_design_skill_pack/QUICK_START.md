
# 电力设计技能包 - 快速入门指南

## 安装

无需安装，直接将以下文件复制到您的项目目录：
- `power_design_skill.py` - 核心技能包
- `openclaw_integration.py` - OpenClaw集成模块

## 基本使用

### 方式1：直接导入使用

```python
from power_design_skill import (
    LoadCalculation,
    ShortCircuitCalculation,
    CableSelection,
    calculate_load
)

# 计算负荷
result = calculate_load(
    powers=[5.5, 7.5, 11, 15],
    equipment_type="风机、水泵"
)
print(f"视在功率: {result.apparent_power:.2f} kVA")
print(f"计算电流: {result.calculation_current:.2f} A")
```

### 方式2：使用OpenClaw集成

```python
from openclaw_integration import PowerDesignSkill

skill = PowerDesignSkill()

# 计算负荷
result = skill.execute("calculate_load", {
    "powers": [5.5, 7.5, 11, 15],
    "equipment_type": "风机、水泵"
})

print(result)
```

### 方式3：全套系统设计

```python
from power_design_skill import PowerDesignCalculator

calculator = PowerDesignCalculator()

# 定义设备
equipment = [
    {"power": 7.5, "type": "冷加工机床", "count": 8},
    {"power": 5.5, "type": "风机、水泵", "count": 6},
    {"power": 2.0, "type": "照明", "count": 30}
]

# 执行全套计算
results = calculator.calculate_distribution_system(
    equipment_data=equipment,
    transformer_capacity=500
)

# 生成报告
report = calculator.generate_calculation_report(results)
print(report)
```

## 常用计算场景

### 场景1：计算车间负荷

```python
from power_design_skill import LoadCalculation

# 车间设备
lathes = [7.5] * 10  # 10台7.5kW车床
fans = [5.5] * 5     # 5台5.5kW风机
lights = [2.0] * 20  # 20盏2kW照明

# 分别计算
lathe_load = LoadCalculation.demand_coefficient_method(lathes, "冷加工机床")
fan_load = LoadCalculation.demand_coefficient_method(fans, "风机、水泵")
light_load = LoadCalculation.demand_coefficient_method(lights, "照明")

# 计算总负荷
total = LoadCalculation.calculate_with_simultaneity(
    [lathe_load, fan_load, light_load],
    simultaneity_factor_p=0.9,
    simultaneity_factor_q=0.95
)

print(f"车间总负荷: {total.apparent_power:.2f} kVA")
```

### 场景2：选择变压器

```python
from power_design_skill import TransformerSelection

# 已知计算负荷
calculated_load = 650  # kVA

# 选择变压器
capacity = TransformerSelection.select_by_load(
    apparent_power=calculated_load,
    load_factor=0.7,      # 负载率70%
    growth_factor=1.2     # 发展系数1.2
)

load_rate = calculated_load / capacity * 100
print(f"推荐变压器容量: {capacity} kVA")
print(f"实际负载率: {load_rate:.1f}%")
```

### 场景3：计算短路电流

```python
from power_design_skill import ShortCircuitCalculation

# 低压系统短路电流
result = ShortCircuitCalculation.ohmic_method(
    system_voltage=0.4,        # 380V系统
    transformer_power=1000,    # 1000kVA变压器
    uk_percent=4.5,           # 阻抗电压4.5%
    line_length=100           # 线路长度100m
)

print(f"三相短路电流: {result.three_phase_current:.2f} kA")
print(f"短路容量: {result.short_circuit_capacity:.2f} MVA")
```

### 场景4：选择电缆

```python
from power_design_skill import CableSelection

# 选择电缆
result = CableSelection.select_cable(
    calculation_current=150,     # 计算电流150A
    length=200,                  # 线路长度200m
    voltage=380,
    max_voltage_drop=5.0,       # 最大允许电压降5%
    short_circuit_current=15,   # 短路电流15kA
    protection_time=0.5         # 保护动作时间0.5s
)

print(f"推荐电缆截面: {result.cross_section} mm²")
print(f"电压降: {result.voltage_drop:.2f}%")
print(f"热稳定校验: {'通过' if result.thermal_stability else '不通过'}")
```

### 场景5：无功补偿

```python
from power_design_skill import ReactivePowerCompensation

# 计算补偿容量
compensation = ReactivePowerCompensation.compensation_capacity(
    active_power=500,    # 有功功率500kW
    cos_phi1=0.7,       # 补偿前功率因数0.7
    cos_phi2=0.95       # 补偿后功率因数0.95
)

print(f"所需补偿容量: {compensation:.2f} kvar")

# 或者按变压器估算
estimated = ReactivePowerCompensation.transformer_compensation(
    transformer_capacity=1000,  # 1000kVA变压器
    load_factor=0.7,
    compensation_rate=0.3
)
print(f"估算补偿容量: {estimated:.2f} kvar")
```

### 场景6：接地设计

```python
from power_design_skill import GroundingDesign

# 接地网设计
resistance = GroundingDesign.grounding_grid_resistance(
    area=2000,           # 接地网面积2000m²
    soil_resistivity=40, # 粘土电阻率40Ω·m
    total_length=500     # 接地体总长度500m
)

print(f"接地电阻: {resistance:.2f} Ω")
print(f"是否满足要求: {'是' if resistance <= 4 else '否'}")
```

### 场景7：保护整定

```python
from power_design_skill import ProtectionSetting

# 电动机保护整定
motor_current = 50  # 电动机额定电流50A

result = ProtectionSetting.motor_protection(
    motor_rated_current=motor_current,
    starting_current_multiple=7,
    starting_time=5
)

print(f"速断保护定值: {result.instantaneous_current:.1f} A")
print(f"过流保护定值: {result.time_delay_current:.1f} A")

# 灵敏度校验
sensitivity = ProtectionSetting.sensitivity_check(
    min_short_circuit_current=800,
    protection_setting=result.instantaneous_current
)
print(f"灵敏度系数: {sensitivity:.2f}")
```

## 命令行使用

```bash
# 计算负荷
python openclaw_integration.py calculate_load '{"powers": [5.5, 7.5, 11], "equipment_type": "风机、水泵"}'

# 计算短路电流
python openclaw_integration.py calculate_short_circuit '{"transformer_power": 1000}'

# 选择电缆
python openclaw_integration.py select_cable '{"current": 150, "length": 200}'

# 无功补偿
python openclaw_integration.py compensate_reactive_power '{"active_power": 500, "cos_phi1": 0.7}'
```

## 常见问题

### Q1: 如何选择需要系数？

A: 技能包内置了常用设备的需要系数表，您可以直接使用设备类型：
- 冷加工机床: Kd=0.14, cosφ=0.5
- 热加工机床: Kd=0.24, cosφ=0.6
- 风机、水泵: Kd=0.75, cosφ=0.8
- 照明: Kd=0.9, cosφ=0.9

### Q2: 电压降限值是多少？

A: 根据规范要求：
- 照明回路: ≤3%
- 动力回路: ≤5%
- 特殊设备: 根据设备要求

### Q3: 变压器经济负载率是多少？

A: 一般取60%~70%，此时变压器效率最高。

### Q4: 接地电阻要求是多少？

A: 根据GB 50065-2011：
- 低压系统: R ≤ 4Ω
- 高压系统: R ≤ 10Ω（根据电压等级）

## 获取更多帮助

- 查看完整文档: README.md
- 查看使用示例: examples.py
- 运行测试: python test_power_design.py
