# 电力设计技能包 - 快速参考卡

## 核心类速查

```python
from power_design_skill import (
    LoadCalculation,
    ShortCircuitCalculation, 
    CableSelection,
    ProtectionSetting,
    ReactivePowerCompensation,
    GroundingDesign,
    TransformerSelection,
    CircuitBreakerSelection
)
```

## 最常用功能

### 1. 负荷计算（需要系数法）
```python
result = LoadCalculation.demand_coefficient_method(
    equipment_powers=[5.5, 7.5, 11, 15],  # 设备功率(kW)
    equipment_type="风机、水泵",           # 设备类型
    voltage=0.38                           # 电压(kV)
)
print(f"计算电流: {result.calculation_current:.2f} A")
```

### 2. 短路电流计算（低压）
```python
result = ShortCircuitCalculation.ohmic_method(
    system_voltage=0.4,        # 系统电压(kV)
    transformer_power=1000,    # 变压器容量(kVA)
    uk_percent=4.5,            # 阻抗电压%
    line_length=100,           # 线路长度(m)
    cable_resistance=0.193,    # 电阻(mΩ/m)
    cable_reactance=0.08       # 电抗(mΩ/m)
)
print(f"短路电流: {result.three_phase_current:.2f} kA")
```

### 3. 电缆选择
```python
result = CableSelection.select_cable(
    calculation_current=150,   # 计算电流(A)
    length=200,                # 线路长度(m)
    voltage=380,               # 电压(V)
    power_factor=0.85,
    max_voltage_drop=5.0,      # 最大压降%
    short_circuit_current=15,  # 短路电流(kA)
    short_circuit_time=0.5     # 短路时间(s)
)
print(f"推荐截面: {result.cross_section} mm²")
print(f"电压降: {result.voltage_drop:.2f}%")
```

## 设备类型需要系数表

| 设备类型 | Kd | cosφ |
|---------|-----|------|
| 冷加工机床 | 0.14 | 0.5 |
| 热加工机床 | 0.24 | 0.6 |
| 风机、水泵 | 0.75 | 0.8 |
| 通风机 | 0.75 | 0.8 |
| 压缩机 | 0.75 | 0.8 |
| 起重机 | 0.25 | 0.5 |
| 电焊机 | 0.35 | 0.6 |
| 电阻炉 | 0.8 | 0.95 |
| 照明 | 0.9 | 0.9 |
| 住宅 | 0.5 | 0.9 |
| 办公楼 | 0.7 | 0.9 |
| 商场 | 0.75 | 0.9 |
| 医院 | 0.6 | 0.8 |
| 学校 | 0.6 | 0.9 |

## 电缆载流量表

| 截面(mm²) | 载流量(A) |
|-----------|-----------|
| 1.5 | 19 |
| 2.5 | 26 |
| 4 | 34 |
| 6 | 44 |
| 10 | 60 |
| 16 | 80 |
| 25 | 105 |
| 35 | 130 |
| 50 | 160 |
| 70 | 200 |
| 95 | 240 |
| 120 | 275 |
| 150 | 310 |
| 185 | 355 |
| 240 | 420 |
| 300 | 480 |

## 土壤电阻率参考

| 土壤类型 | 电阻率(Ω·m) |
|---------|------------|
| 沼泽地 | 5 |
| 黑土 | 20 |
| 粘土 | 40 |
| 砂质粘土 | 80 |
| 黄土 | 150 |
| 砂土 | 300 |
| 多石土壤 | 500 |
| 岩石 | 1000 |

## 常用计算公式

**负荷计算：**
```
Pc = Kd × Pe
Qc = Pc × tanφ
Sc = √(Pc² + Qc²)
Ic = Sc / (√3 × Un)
```

**无功补偿：**
```
Qc = P × (tanφ1 - tanφ2)
```

**电压降：**
```
ΔU% = (√3 × I × L × (Rcosφ + Xsinφ)) / (10 × Un)
```

**热稳定校验：**
```
Smin = (Ik × √t) / C    (C=143铜电缆)
```

## 设计规范依据

1. 《工业与民用供配电设计手册》第四版
2. GB 50052-2009 供配电系统设计规范
3. GB 50054-2011 低压配电设计规范
4. GB 50065-2011 接地设计规范
5. IEC 60909 短路电流计算标准

## 技能包路径

```
~/.openclaw/workspace/power-design-skill/power_design_skill_pack/
```

## 测试命令

```bash
cd ~/.openclaw/workspace/power-design-skill/power_design_skill_pack
python3 power_design_skill.py
```

---
*快速参考卡 - 2026-03-13*
