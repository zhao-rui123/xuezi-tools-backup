
# 工业与民用配电设计手册（第四版）技能包
## Power Distribution Design Skill Pack v1.0.0

---

## 📦 技能包内容

本技能包基于《工业与民用配电设计手册》第四版，提供了完整的供配电系统设计计算功能。

### 文件清单

| 序号 | 文件名 | 说明 | 大小 |
|------|--------|------|------|
| 1 | power_design_skill.py | 核心技能包 | 41KB |
| 2 | openclaw_integration.py | OpenClaw集成 | 17KB |
| 3 | examples.py | 使用示例 | 11KB |
| 4 | test_power_design.py | 测试文件 | 13KB |
| 5 | README.md | 完整文档 | 9KB |
| 6 | QUICK_START.md | 快速入门 | 7KB |
| 7 | FORMULA_SHEET.md | 公式速查表 | 8KB |
| 8 | MANIFEST.md | 文件清单 | 2KB |
| 9 | config.json | 配置文件 | 2KB |
| 10 | __init__.py | 包初始化 | 2KB |
| 11 | requirements.txt | 依赖说明 | 1KB |
| 12 | LICENSE | 许可证 | 1KB |

---

## 🚀 快速开始

### 方式1：直接导入

```python
from power_design_skill import calculate_load

result = calculate_load(
    powers=[5.5, 7.5, 11],
    equipment_type="风机、水泵"
)
print(f"视在功率: {result.apparent_power:.2f} kVA")
```

### 方式2：OpenClaw集成

```python
from openclaw_integration import PowerDesignSkill

skill = PowerDesignSkill()
result = skill.execute("calculate_load", {
    "powers": [5.5, 7.5, 11],
    "equipment_type": "风机、水泵"
})
```

### 方式3：全套设计

```python
from power_design_skill import PowerDesignCalculator

calculator = PowerDesignCalculator()
results = calculator.calculate_distribution_system(
    equipment_data=[
        {"power": 7.5, "type": "冷加工机床", "count": 8},
        {"power": 5.5, "type": "风机、水泵", "count": 6},
    ],
    transformer_capacity=500
)
report = calculator.generate_calculation_report(results)
print(report)
```

---

## 📊 功能模块

### 1. 负荷计算模块
- ✅ 需要系数法
- ✅ 利用系数法
- ✅ 单位指标法
- ✅ 同时系数计算

### 2. 短路电流计算模块
- ✅ 标幺值法（高压系统）
- ✅ 有名值法/欧姆法（低压系统）
- ✅ 三相/两相/单相短路电流

### 3. 电缆截面选择模块
- ✅ 按载流量选择
- ✅ 电压降校验
- ✅ 热稳定校验

### 4. 继电保护整定模块
- ✅ 电流速断保护
- ✅ 过电流保护
- ✅ 时间级差配合
- ✅ 灵敏度校验

### 5. 无功功率补偿模块
- ✅ 补偿容量计算
- ✅ 电容器输出计算
- ✅ 变压器补偿估算

### 6. 接地设计模块
- ✅ 水平接地极
- ✅ 垂直接地极
- ✅ 接地网设计
- ✅ 季节系数修正

### 7. 变压器选择模块
- ✅ 按负荷选择容量
- ✅ 经济负载率计算
- ✅ 年电能损耗计算
- ✅ 电压调整率计算

### 8. 断路器选择模块
- ✅ 额定电流选择
- ✅ 分断能力选择
- ✅ 电动机保护配置

---

## 📐 计算公式

技能包包含100+计算公式，涵盖：
- 负荷计算公式
- 短路电流计算公式
- 电缆选择公式
- 保护整定公式
- 无功补偿公式
- 接地电阻公式
- 变压器选择公式

详细公式请参考 FORMULA_SHEET.md

---

## 📋 设计规范

本技能包严格依据以下规范：
- ✅ 《工业与民用配电设计手册》第四版
- ✅ GB 50052-2009 供配电系统设计规范
- ✅ GB 50054-2011 低压配电设计规范
- ✅ GB 50055-2011 通用用电设备配电设计规范
- ✅ GB 50057-2010 建筑物防雷设计规范
- ✅ GB 50065-2011 交流电气装置的接地设计规范
- ✅ IEC 60909 短路电流计算标准

---

## 🧪 测试验证

```bash
# 运行所有测试
python test_power_design.py

# 测试结果
Ran 32 tests in 0.002s
OK
```

---

## 📖 文档资源

| 文档 | 内容 | 适用对象 |
|------|------|---------|
| QUICK_START.md | 快速入门指南 | 初学者 |
| README.md | 完整使用文档 | 开发人员 |
| FORMULA_SHEET.md | 公式速查表 | 设计人员 |
| examples.py | 使用示例 | 所有用户 |

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

## 🎯 适用场景

- 工业厂房配电设计
- 民用建筑配电设计
- 变电站设计
- 配电系统改造
- 电气设计教学
- 工程计算验证

---

## ⚠️ 使用声明

1. 本技能包仅供学习和参考使用
2. 实际工程设计应遵循现行国家标准和规范
3. 重要工程应由具有相应资质的设计人员完成
4. 计算结果应结合工程经验进行判断

---

## 📞 技术支持

如有问题或建议，请参考文档文件或联系技术支持。

---

## 📄 许可证

MIT License

Copyright (c) 2026 Power Design Skill Pack

---

**版本**: v1.0.0  
**发布日期**: 2026-03-13  
**依据手册**: 《工业与民用配电设计手册》第四版
