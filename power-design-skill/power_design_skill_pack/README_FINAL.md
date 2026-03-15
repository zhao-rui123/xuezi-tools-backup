
# 🏭 工业与民用配电设计手册（第四版）技能包

## 📦 项目简介

本技能包是基于《工业与民用配电设计手册》第四版开发的完整电力设计计算工具，
适用于OpenClaw平台，可用于工业与民用建筑的供配电系统设计计算。

---

## ✨ 主要特性

- ✅ **严格依据手册**：所有公式和方法均来自《工业与民用配电设计手册》第四版
- ✅ **完整功能覆盖**：涵盖负荷计算、短路电流、电缆选择、保护整定等9大模块
- ✅ **OpenClaw集成**：标准技能接口，支持JSON输入输出
- ✅ **无外部依赖**：纯Python标准库实现
- ✅ **完整测试覆盖**：32个单元测试，确保计算准确性
- ✅ **详细文档**：包含快速入门、完整文档、公式速查表

---

## 🚀 快速开始

### 安装

无需安装，直接使用：

```python
from power_design_skill import calculate_load

result = calculate_load(
    powers=[5.5, 7.5, 11],
    equipment_type="风机、水泵"
)
print(f"视在功率: {result.apparent_power:.2f} kVA")
```

### OpenClaw集成

```python
from openclaw_integration import PowerDesignSkill

skill = PowerDesignSkill()
result = skill.execute("calculate_load", {
    "powers": [5.5, 7.5, 11],
    "equipment_type": "风机、水泵"
})
print(result)
```

---

## 📊 功能模块

| 模块 | 功能 | 方法 |
|------|------|------|
| 负荷计算 | 需要系数法、利用系数法、单位指标法 | 3种 |
| 短路电流 | 标幺值法、有名值法 | 2种 |
| 电缆选择 | 载流量、电压降、热稳定 | 3种校验 |
| 保护整定 | 速断、过流、灵敏度 | 完整配置 |
| 无功补偿 | 容量计算、输出估算 | 精确计算 |
| 接地设计 | 水平、垂直、接地网 | 3种类型 |
| 变压器选择 | 容量、经济负载率 | 多维度 |
| 断路器选择 | 额定电流、分断能力 | 智能选择 |

---

## 📁 文件结构

```
power_design_skill_pack/
├── power_design_skill.py      # 核心技能包 (41KB)
├── openclaw_integration.py    # OpenClaw集成 (17KB)
├── examples.py                # 使用示例 (11KB)
├── test_power_design.py       # 测试文件 (13KB)
├── README.md                  # 完整文档 (9KB)
├── QUICK_START.md             # 快速入门 (7KB)
├── FORMULA_SHEET.md           # 公式速查表 (8KB)
├── SKILL_PACK_README.md       # 技能包说明 (5KB)
├── FINAL_SUMMARY.md           # 项目总结 (6KB)
├── MANIFEST.md                # 文件清单 (2KB)
├── config.json                # 配置文件 (2KB)
├── __init__.py                # 包初始化 (2KB)
├── requirements.txt           # 依赖说明 (1KB)
└── LICENSE                    # MIT许可证 (1KB)
```

---

## 📖 文档资源

| 文档 | 内容 | 适用对象 |
|------|------|---------|
| [QUICK_START.md](QUICK_START.md) | 快速入门指南 | ⭐ 初学者 |
| [README.md](README.md) | 完整使用文档 | 👨‍💻 开发人员 |
| [FORMULA_SHEET.md](FORMULA_SHEET.md) | 公式速查表 | 👷 设计人员 |
| [examples.py](examples.py) | 使用示例 | 📚 所有用户 |
| [FINAL_SUMMARY.md](FINAL_SUMMARY.md) | 项目总结 | 📋 项目概览 |

---

## 🧪 测试

```bash
python test_power_design.py
```

**测试结果：**
```
Ran 32 tests in 0.002s
OK
```

---

## 📐 计算公式

技能包包含100+计算公式，详细列表请参考 [FORMULA_SHEET.md](FORMULA_SHEET.md)

---

## 🎯 设计规范

本技能包严格依据以下规范：

- ✅ 《工业与民用配电设计手册》第四版
- ✅ GB 50052-2009 供配电系统设计规范
- ✅ GB 50054-2011 低压配电设计规范
- ✅ GB 50055-2011 通用用电设备配电设计规范
- ✅ GB 50057-2010 建筑物防雷设计规范
- ✅ GB 50065-2011 交流电气装置的接地设计规范
- ✅ IEC 60909 短路电流计算标准

---

## 💡 使用示例

### 示例1：负荷计算

```python
from power_design_skill import calculate_load

result = calculate_load(
    powers=[5.5, 7.5, 11, 15],
    equipment_type="风机、水泵"
)

print(f"有功功率: {result.active_power:.2f} kW")
print(f"视在功率: {result.apparent_power:.2f} kVA")
print(f"计算电流: {result.calculation_current:.2f} A")
```

### 示例2：短路电流计算

```python
from power_design_skill import calculate_short_circuit

result = calculate_short_circuit(
    system_voltage=0.4,
    transformer_power=1000
)

print(f"三相短路电流: {result.three_phase_current:.2f} kA")
print(f"短路容量: {result.short_circuit_capacity:.2f} MVA")
```

### 示例3：全套系统设计

```python
from power_design_skill import PowerDesignCalculator

calculator = PowerDesignCalculator()

equipment_data = [
    {"power": 7.5, "type": "冷加工机床", "count": 8},
    {"power": 5.5, "type": "风机、水泵", "count": 6},
    {"power": 2.0, "type": "照明", "count": 30},
]

results = calculator.calculate_distribution_system(
    equipment_data=equipment_data,
    transformer_capacity=500
)

report = calculator.generate_calculation_report(results)
print(report)
```

---

## ⚙️ 技术规格

- **Python版本**: >= 3.7
- **外部依赖**: 无（纯Python标准库）
- **代码行数**: 约4000行
- **测试用例**: 32个
- **计算公式**: 100+
- **支持设备**: 14种类型
- **电压等级**: 35kV及以下

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

## 📞 更多信息

- 快速入门: [QUICK_START.md](QUICK_START.md)
- 完整文档: [README.md](README.md)
- 公式速查: [FORMULA_SHEET.md](FORMULA_SHEET.md)
- 使用示例: [examples.py](examples.py)

---

**版本**: v1.0.0  
**发布日期**: 2026-03-13  
**依据手册**: 《工业与民用配电设计手册》第四版
