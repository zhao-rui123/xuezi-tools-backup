
# 🏭 电力设计技能包 v2.0.0

## 📦 项目简介

本技能包整合了**三本权威电力设计手册**的内容：

1. **《工业与民用配电设计手册》第四版** - 通用配电设计
2. **《钢铁企业电力设计手册》上、下册** - 钢铁企业专用设计
3. **《电力工程高压送电线路设计手册》第二版** - 高压送电线路设计

提供完整的电力设计计算功能，支持结果导出到Excel。

---

## ✨ 主要特性

- ✅ **三本手册整合** - 涵盖工业/民用/钢铁企业/高压送电线路
- ✅ **完整功能覆盖** - 11个功能模块，22个API函数
- ✅ **Excel导出** - 支持多工作表格式化导出
- ✅ **OpenClaw集成** - 标准技能接口
- ✅ **无外部依赖** - 基础功能纯Python实现
- ✅ **详细文档** - 包含公式速查表和使用示例

---

## 🚀 快速开始

### 安装依赖

```bash
pip install openpyxl>=3.0.0
```

### 基础使用

```python
from power_design_skill import (
    PowerDesignCalculator,
    SteelPlantPowerDesign,
    TransmissionLineDesign,
    ExcelExporter
)

# 1. 基础配电设计
calculator = PowerDesignCalculator()
results = calculator.calculate_distribution_system(
    equipment_data=[
        {"power": 7.5, "type": "冷加工机床", "count": 8},
        {"power": 5.5, "type": "风机、水泵", "count": 6},
    ],
    transformer_capacity=500
)

# 2. 钢铁企业设计
steel_design = SteelPlantPowerDesign()
result = steel_design.calculate_by_unit_production(
    production_capacity=1000000,  # 1百万吨
    product_type="转炉钢"
)

# 3. 送电线路设计
line_design = TransmissionLineDesign()
result = line_design.electrical_parameters(
    conductor_type="LGJ-240",
    line_length=50,
    voltage=220
)

# 4. 导出到Excel
exporter = ExcelExporter()
filepath = exporter.export_full_report(results)
```

---

## 📊 功能模块

### 基础模块 (9个)

| 模块 | 功能 | 适用场景 |
|------|------|---------|
| 负荷计算 | 需要系数法/利用系数法/单位指标法 | 通用配电 |
| 短路电流 | 标幺值法/有名值法 | 高低压系统 |
| 电缆选择 | 载流量/电压降/热稳定校验 | 电缆设计 |
| 保护整定 | 速断/过流/灵敏度校验 | 继电保护 |
| 无功补偿 | 补偿容量计算 | 功率因数改善 |
| 接地设计 | 接地电阻计算 | 接地系统 |
| 变压器选择 | 容量/经济负载率 | 变压器选型 |
| 断路器选择 | 额定电流/分断能力 | 开关设备 |
| 综合计算器 | 全套系统设计 | 整体设计 |

### 钢铁企业模块 (5个)

| 模块 | 功能 | 适用场景 |
|------|------|---------|
| 单位产品耗电 | 按产量计算负荷 | 钢铁企业规划 |
| 电弧炉负荷 | 电弧炉功率计算 | 电炉供电设计 |
| 谐波计算 | 2/3/4/5/7次谐波 | 电能质量分析 |
| 轧钢机冲击 | 冲击负荷计算 | 轧机供电设计 |
| 无功补偿 | 补偿容量计算 | SVC/TSC设计 |

### 送电线路模块 (6个)

| 模块 | 功能 | 适用场景 |
|------|------|---------|
| 电气参数 | R/X/B/Zc/Pn计算 | 线路设计 |
| 弧垂计算 | 悬链线方程 | 架线施工 |
| 导线选择 | 经济电流密度 | 导线选型 |
| 杆塔荷载 | 垂直/风/综合荷载 | 杆塔设计 |
| 绝缘配合 | 绝缘子片数 | 绝缘设计 |
| 杆塔接地 | 接地电阻计算 | 防雷接地 |

---

## 📁 文件结构

```
power_design_skill_pack/
├── 📄 power_design_skill.py          # 核心技能包 (41KB)
├── 📄 steel_transmission_modules.py  # 钢铁企业和送电线路 (19KB)
├── 📄 excel_exporter.py              # Excel导出模块 (26KB)
├── 📄 openclaw_integration.py        # OpenClaw集成 (25KB)
├── 📄 examples.py                    # 基础示例 (11KB)
├── 📄 examples_complete.py           # 完整示例 (13KB)
├── 📄 test_power_design.py           # 测试文件 (13KB)
├── 📖 README.md                      # 完整文档 (9KB)
├── 📖 QUICK_START.md                 # 快速入门 (7KB)
├── 📖 FORMULA_SHEET.md               # 公式速查表 (8KB)
├── 📖 UPDATE_v2.0.md                 # 更新说明 (7KB)
├── ⚙️  config.json                    # 配置文件 (2KB)
├── ⚙️  __init__.py                    # 包初始化 (3KB)
├── ⚙️  requirements.txt               # 依赖说明 (1KB)
└── ⚙️  LICENSE                        # MIT许可证 (1KB)
```

---

## 📖 文档资源

| 文档 | 内容 | 适用对象 |
|------|------|---------|
| [QUICK_START.md](QUICK_START.md) | 快速入门指南 | ⭐ 初学者 |
| [README.md](README.md) | 完整使用文档 | 👨‍💻 开发人员 |
| [FORMULA_SHEET.md](FORMULA_SHEET.md) | 公式速查表 | 👷 设计人员 |
| [UPDATE_v2.0.md](UPDATE_v2.0.md) | 更新说明 | 📋 版本信息 |
| [examples_complete.py](examples_complete.py) | 完整示例 | 📚 所有用户 |

---

## 💡 使用示例

### 钢铁企业负荷计算

```python
from power_design_skill import SteelPlantPowerDesign

steel_design = SteelPlantPowerDesign()

# 计算年产100万吨转炉钢的负荷
result = steel_design.calculate_by_unit_production(
    production_capacity=1000000,
    product_type="转炉钢"
)

print(f"有功功率: {result.active_power/1000:.2f} MW")
print(f"视在功率: {result.apparent_power/1000:.2f} MVA")
```

### 电弧炉负荷计算

```python
result = steel_design.arc_furnace_load(
    furnace_capacity=100,  # 100吨
    transformer_power=80   # 80MVA
)

print(f"有功功率: {result['active_power_mw']:.2f} MW")
print(f"功率因数: {result['power_factor']:.2f}")
```

### 谐波计算

```python
harmonics = steel_design.harmonic_calculation(fundamental_current=1000)

print(f"2次谐波: {harmonics[2]:.1f} A")
print(f"3次谐波: {harmonics[3]:.1f} A")
print(f"THD: {harmonics['THD']:.2f}%")
```

### 送电线路电气参数

```python
from power_design_skill import TransmissionLineDesign

line_design = TransmissionLineDesign()

result = line_design.electrical_parameters(
    conductor_type="LGJ-240",
    line_length=50,
    voltage=220
)

print(f"电阻: {result['resistance_ohm']:.2f} Ω")
print(f"波阻抗: {result['wave_impedance_ohm']:.2f} Ω")
print(f"自然功率: {result['natural_power_mw']:.2f} MW")
```

### 导线弧垂计算

```python
sag = line_design.sag_calculation(
    span_length=300,
    conductor_type="LGJ-240"
)

print(f"弧垂: {sag['sag_m']:.2f} m")
print(f"最大应力: {sag['max_stress_mpa']:.2f} MPa")
```

### 导线截面选择

```python
conductor = line_design.conductor_selection(
    transmission_power=100,  # 100MW
    voltage=220,             # 220kV
    line_length=50           # 50km
)

print(f"推荐导线: {conductor['selected_conductor']}")
print(f"电压降: {conductor['voltage_drop_percent']:.2f}%")
```

### 导出到Excel

```python
from power_design_skill import (
    PowerDesignCalculator,
    ExcelExporter
)

calculator = PowerDesignCalculator()
results = calculator.calculate_distribution_system(
    equipment_data=[...],
    transformer_capacity=500
)

exporter = ExcelExporter()
filepath = exporter.export_full_report(results)

print(f"已导出到: {filepath}")
```

---

## 📋 设计规范依据

- ✅ 《工业与民用配电设计手册》第四版
- ✅ 《钢铁企业电力设计手册》上、下册
- ✅ 《电力工程高压送电线路设计手册》第二版
- ✅ GB 50052-2009 供配电系统设计规范
- ✅ GB 50054-2011 低压配电设计规范
- ✅ GB 50055-2011 通用用电设备配电设计规范
- ✅ GB 50057-2010 建筑物防雷设计规范
- ✅ GB 50065-2011 交流电气装置的接地设计规范
- ✅ IEC 60909 短路电流计算标准

---

## ⚙️ 技术规格

- **Python版本**: >= 3.7
- **外部依赖**: openpyxl (Excel导出)
- **代码行数**: 约5000行
- **计算公式**: 150+
- **支持设备**: 25+ 种
- **电压等级**: 11种 (0.38kV ~ 500kV)

---

## ⚠️ 使用声明

1. 本技能包仅供学习和参考使用
2. 实际工程设计应遵循现行国家标准和规范
3. 重要工程应由具有相应资质的设计人员完成
4. 计算结果应结合工程经验进行判断

---

## 📄 许可证

MIT License

Copyright (c) 2026 Power Design Skill Pack

---

**版本**: v2.0.0  
**发布日期**: 2026-03-13  
**状态**: ✅ 已完成
