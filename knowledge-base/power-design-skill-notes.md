# 电力设计技能包学习笔记

## 技能包概述
**来源**: 《工业与民用配电设计手册》第四版
**功能**: 供配电系统设计全流程计算
**适用**: 35kV及以下工业与民用建筑供配电设计

## 核心功能模块

### 1. 负荷计算 (LoadCalculation)
```python
from power_design_skill import LoadCalculation

# 需要系数法
result = LoadCalculation.demand_coefficient_method(
    equipment_powers=[5.5, 7.5, 11, 15],  # 设备功率列表(kW)
    equipment_type="风机、水泵",           # 设备类型
    voltage=0.38                           # 额定电压(kV)
)
# 返回: 有功功率P(kW)、无功功率Q(kvar)、视在功率S(kVA)、计算电流I(A)

# 支持的设备类型
DEMAND_FACTORS = {
    '冷加工机床': {'Kd': 0.14, 'cosφ': 0.5},
    '热加工机床': {'Kd': 0.24, 'cosφ': 0.6},
    '风机、水泵': {'Kd': 0.75, 'cosφ': 0.8},
    '通风机': {'Kd': 0.75, 'cosφ': 0.8},
    '压缩机': {'Kd': 0.75, 'cosφ': 0.8},
    '起重机': {'Kd': 0.25, 'cosφ': 0.5},
    '电焊机': {'Kd': 0.35, 'cosφ': 0.6},
    '电阻炉': {'Kd': 0.8, 'cosφ': 0.95},
    '照明': {'Kd': 0.9, 'cosφ': 0.9},
    '住宅': {'Kd': 0.5, 'cosφ': 0.9},
    '办公楼': {'Kd': 0.7, 'cosφ': 0.9},
    '商场': {'Kd': 0.75, 'cosφ': 0.9},
    '医院': {'Kd': 0.6, 'cosφ': 0.8},
    '学校': {'Kd': 0.6, 'cosφ': 0.9},
}
```

**核心公式**:
- Pc = Kd × Pe (有功功率)
- Qc = Pc × tanφ (无功功率)
- Sc = √(Pc² + Qc²) (视在功率)
- Ic = Sc / (√3 × Un) (计算电流)

### 2. 短路电流计算 (ShortCircuitCalculation)
```python
from power_design_skill import ShortCircuitCalculation

# 低压系统 - 有名值法（欧姆法）
result = ShortCircuitCalculation.ohmic_method(
    system_voltage=0.4,        # 系统电压(kV)
    transformer_power=1000,    # 变压器容量(kVA)
    uk_percent=4.5,            # 阻抗电压百分比
    line_length=100,           # 线路长度(m)
    cable_resistance=0.193,    # 电缆单位电阻(mΩ/m)
    cable_reactance=0.08       # 电缆单位电抗(mΩ/m)
)
# 返回: 三相短路电流(kA)、短路阻抗(mΩ)

# 高压系统 - 标幺值法
result = ShortCircuitCalculation.per_unit_system(
    system_capacity=500,       # 系统短路容量(MVA)
    base_capacity=100,         # 基准容量(MVA)
    base_voltage=10.5,         # 基准电压(kV)
    transformer_capacity=10,   # 变压器容量(MVA)
    uk_percent=4.5             # 阻抗电压百分比
)
```

### 3. 电缆截面选择 (CableSelection)
```python
from power_design_skill import CableSelection

result = CableSelection.select_cable(
    calculation_current=150,      # 计算电流(A)
    length=200,                   # 线路长度(m)
    voltage=380,                  # 电压(V)
    power_factor=0.85,
    max_voltage_drop=5.0,         # 最大允许电压降(%)
    short_circuit_current=15,     # 短路电流(kA)
    short_circuit_time=0.5        # 短路时间(s)
)
# 返回: 推荐截面(mm²)、载流量(A)、电压降(%)、热稳定校验

# 常用电缆载流量表
CURRENT_CARRYING_CAPACITY = {
    1.5: 19, 2.5: 26, 4: 34, 6: 44,
    10: 60, 16: 80, 25: 105, 35: 130,
    50: 160, 70: 200, 95: 240, 120: 275,
    150: 310, 185: 355, 240: 420, 300: 480
}
```

**选择依据**:
1. 按载流量选择
2. 校验电压降 (ΔU% ≤ 5%)
3. 热稳定校验 (Smin = Ik×√t / C, C=143)

### 4. 继电保护整定 (ProtectionSetting)
- 电流速断保护
- 过电流保护
- 电动机保护

### 5. 无功补偿 (ReactivePowerCompensation)
```python
# 补偿容量计算
Qc = P × (tanφ1 - tanφ2)
```

### 6. 接地设计 (GroundingDesign)
**土壤电阻率参考值**:
- 沼泽地: 5 Ω·m
- 黑土: 20 Ω·m
- 粘土: 40 Ω·m
- 砂质粘土: 80 Ω·m
- 黄土: 150 Ω·m
- 砂土: 300 Ω·m
- 多石土壤: 500 Ω·m
- 岩石: 1000 Ω·m

### 7. 变压器选择 (TransformerSelection)
- 按负荷选择容量
- 计算经济负载率
- 计算年电能损耗
- 计算电压调整率

### 8. 断路器选择 (CircuitBreakerSelection)
- 选择额定电流
- 选择分断能力
- 电动机保护断路器

## 使用场景

### 场景1: 工厂配电设计
1. 统计所有设备功率
2. 用需要系数法计算总负荷
3. 选择变压器容量
4. 计算短路电流
5. 选择电缆和保护设备
6. 设计接地系统

### 场景2: 建筑电气设计
1. 按单位指标法估算负荷
2. 选择变压器和配电柜
3. 计算电压降
4. 设计无功补偿
5. 配置继电保护

### 场景3: 设备改造升级
1. 重新核算负荷
2. 校验现有开关容量
3. 重新选择电缆
4. 调整保护定值

## 设计规范依据
1. 《工业与民用供配电设计手册》第四版
2. GB 50052-2009 《供配电系统设计规范》
3. GB 50054-2011 《低压配电设计规范》
4. GB 50055-2011 《通用用电设备配电设计规范》
5. GB 50057-2010 《建筑物防雷设计规范》
6. GB 50065-2011 《交流电气装置的接地设计规范》
7. IEC 60909 短路电流计算标准

## 计算精度
- 负荷计算: ±5%
- 短路电流计算: ±10%
- 电压降计算: ±3%
- 接地电阻计算: ±15%

## 注意事项
1. 输入数据校验: 所有模块都有合理性检查
2. 单位一致性: 确保单位与函数要求一致
3. 系数选择: 需要根据工程经验选择
4. 安全系数: 重要设备应适当增加

---
*学习完成: 2026-03-13*
