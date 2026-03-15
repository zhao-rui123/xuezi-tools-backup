
# 电力设计技能包 v2.0.0 更新说明

## 📦 版本信息

- **版本**: 2.0.0
- **发布日期**: 2026-03-13
- **更新内容**: 整合三本设计手册，添加Excel导出功能

---

## 🆕 新增功能

### 1. 钢铁企业电力设计模块 (SteelPlantPowerDesign)

依据《钢铁企业电力设计手册》上、下册

#### 功能列表：
- **按单位产品耗电量计算负荷**
  - 支持14种钢铁产品类型
  - 自动计算年电能消耗量

- **电弧炉负荷计算**
  - 熔化期/精炼期功率因数
  - 冲击负荷系数

- **谐波计算**
  - 2/3/4/5/7次谐波
  - 总谐波畸变率THD

- **轧钢机冲击负荷计算**
  - 平均负荷
  - 冲击负荷
  - 无功冲击

- **无功补偿容量计算**
  - 针对钢铁企业特殊负荷优化
  - 电弧炉/轧钢机补偿

#### 支持的钢铁产品类型：
- 生铁、转炉钢、电炉钢
- 连铸坯、热轧板、冷轧板
- 线材、棒材、钢管

### 2. 高压送电线路设计模块 (TransmissionLineDesign)

依据《电力工程高压送电线路设计手册》第二版

#### 功能列表：
- **电气参数计算**
  - 电阻、电抗、电纳
  - 波阻抗、自然功率

- **导线弧垂计算**
  - 悬链线方程
  - 气象条件修正

- **导线截面选择**
  - 按经济电流密度
  - 电压降校验

- **杆塔荷载计算**
  - 垂直荷载
  - 风荷载
  - 综合荷载

- **绝缘配合设计**
  - 绝缘子片数
  - 海拔修正
  - 污秽等级

- **杆塔接地设计**
  - 接地电阻计算
  - 水平/垂直接地体

#### 支持的导线型号：
- LGJ-70 ~ LGJ-800
- 共11种常用钢芯铝绞线

#### 支持的气象条件：
- I类(轻冰区)
- II类(中冰区)
- III类(重冰区)
- IV类(特重冰区)

#### 支持的电压等级：
- 35kV、66kV、110kV
- 220kV、330kV、500kV

### 3. Excel导出模块 (ExcelExporter)

#### 功能列表：
- **负荷计算结果导出**
  - 格式化表格
  - 自动求和

- **短路电流结果导出**
  - 清晰的数据展示

- **电缆选择结果导出**
  - 包含校验结果

- **保护整定结果导出**
  - 完整的整定参数

- **完整报告导出**
  - 多工作表
  - 包含所有计算结果

#### 导出格式：
- Excel (.xlsx) - 需要openpyxl
- CSV (.csv) - 备选格式

---

## 📊 功能统计

| 类别 | 数量 |
|------|------|
| 总模块数 | 11个 |
| 总函数数 | 50+ |
| 计算公式 | 150+ |
| 支持设备类型 | 25+ |
| 电压等级 | 11种 |
| 导出格式 | 2种 |

---

## 📖 使用示例

### 钢铁企业负荷计算

```python
from power_design_skill import SteelPlantPowerDesign

steel_design = SteelPlantPowerDesign()

# 计算年产100万吨转炉钢的负荷
result = steel_design.calculate_by_unit_production(
    production_capacity=1000000,
    product_type="转炉钢",
    operating_hours=7000
)

print(f"有功功率: {result.active_power:.2f} kW")
print(f"视在功率: {result.apparent_power:.2f} kVA")
```

### 电弧炉负荷计算

```python
result = steel_design.arc_furnace_load(
    furnace_capacity=100,  # 100吨
    transformer_power=80,  # 80MVA
    operating_mode='normal'
)

print(f"有功功率: {result['active_power_mw']:.2f} MW")
print(f"功率因数: {result['power_factor']:.2f}")
```

### 谐波计算

```python
harmonics = steel_design.harmonic_calculation(
    fundamental_current=1000
)

print(f"THD: {harmonics['THD']:.2f}%")
```

### 送电线路电气参数计算

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
```

### 导线弧垂计算

```python
result = line_design.sag_calculation(
    span_length=300,
    conductor_type="LGJ-240"
)

print(f"弧垂: {result['sag_m']:.2f} m")
```

### 导线截面选择

```python
result = line_design.conductor_selection(
    transmission_power=100,
    voltage=220,
    line_length=50
)

print(f"推荐导线: {result['selected_conductor']}")
print(f"电压降: {result['voltage_drop_percent']:.2f}%")
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

## 🔧 安装依赖

```bash
pip install openpyxl>=3.0.0
```

---

## 📁 文件结构

```
power_design_skill_pack/
├── power_design_skill.py          # 核心技能包 (41KB)
├── steel_transmission_modules.py  # 钢铁企业和送电线路模块 (15KB)
├── excel_exporter.py              # Excel导出模块 (12KB)
├── openclaw_integration.py        # OpenClaw集成 (25KB)
├── examples.py                    # 原有示例 (11KB)
├── examples_complete.py           # 完整示例 (15KB)
├── test_power_design.py           # 测试文件 (13KB)
├── README.md                      # 完整文档 (9KB)
├── QUICK_START.md                 # 快速入门 (7KB)
├── FORMULA_SHEET.md               # 公式速查表 (8KB)
├── UPDATE_v2.0.md                 # 本文件
├── config.json                    # 配置文件 (2KB)
├── __init__.py                    # 包初始化 (3KB)
├── requirements.txt               # 依赖说明 (1KB)
└── LICENSE                        # MIT许可证 (1KB)
```

---

## 📚 依据的设计手册

1. **《工业与民用配电设计手册》第四版**
   - 负荷计算
   - 短路电流计算
   - 电缆选择
   - 保护整定

2. **《钢铁企业电力设计手册》上、下册**
   - 钢铁企业负荷计算
   - 电弧炉供电
   - 谐波及其滤波
   - 冲击负荷计算

3. **《电力工程高压送电线路设计手册》第二版**
   - 电气参数计算
   - 电线力学
   - 杆塔设计
   - 基础设计
   - 绝缘配合

---

## ⚠️ 注意事项

1. Excel导出功能需要安装openpyxl库
2. 如果没有openpyxl，会自动降级为CSV格式
3. 所有计算结果仅供参考，实际工程应遵循现行规范
4. 高压线路设计应由具有相应资质的设计人员完成

---

## 📞 技术支持

如有问题或建议，请参考相应文档文件。

---

**版本**: v2.0.0  
**更新日期**: 2026-03-13
