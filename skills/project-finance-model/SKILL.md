---
name: project-finance-model
description: 项目投资财务测算系统 - 完整版CAPEX/OPEX/税务/IRR/NPV分析
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# Project Finance Model - 项目投资财务测算系统

## 功能概述

**输入CAPEX/OPEX，输出完整财务分析！**

专为储能、新能源、制造业投资项目设计的财务模型：

- ✅ **投资分析** - CAPEX分解、资金来源、建设期利息
- ✅ **运营分析** - OPEX、收入成本预测、现金流
- ✅ **税务分析** - 增值税、所得税、附加税费（精确计算）
- ✅ **财务指标** - IRR、NPV、静态/动态回收期、ROI、ROE
- ✅ **敏感性分析** - 收入/成本/投资变化对收益的影响
- ✅ **融资分析** - 贷款还款计划、资本金比例

## 核心财务指标

| 指标 | 说明 | 判断标准 |
|------|------|----------|
| **NPV** | 净现值 | >0 项目可行 |
| **IRR** | 内部收益率 | >折现率 项目可行 |
| **静态回收期** | 不考虑资金时间价值 | 越短越好 |
| **动态回收期** | 考虑资金时间价值 | 越短越好 |
| **ROI** | 投资利润率 | 越高越好 |
| **ROE** | 资本金利润率 | 越高越好 |

## 使用方法

### Python调用

```python
from project_finance_model import ProjectFinancialModel, ProjectInputs, format_financial_report

# 定义项目参数
inputs = ProjectInputs(
    project_name="100MWh储能电站",
    project_type="储能电站",
    operation_years=15,
    
    # CAPEX投资（万元）
    land_cost=500,           # 土地500万
    construction_cost=1500,  # 建设1500万
    equipment_cost=3000,     # 设备3000万
    installation_cost=500,   # 安装500万
    other_cost=300,          # 其他300万
    working_capital=200,     # 流动资金200万
    
    # OPEX运营（万元/年）
    annual_revenue=2000,     # 年收入2000万
    annual_cost=300,         # 运营成本300万
    maintenance_cost=150,    # 维护费150万
    labor_cost=100,          # 人工100万
    
    # 融资
    equity_ratio=0.30,       # 资本金30%
    loan_ratio=0.70,         # 贷款70%
    loan_rate=0.045,         # 利率4.5%
    loan_term=10,            # 贷款10年
    
    # 税务
    enterprise_type="高新技术企业",
    location="市区",
    
    # 折现率
    discount_rate=0.08,      # 8%
)

# 创建模型并计算
model = ProjectFinancialModel(inputs)
metrics = model.calculate_financial_metrics()

# 输出报告
print(format_financial_report(model))
```

### 输出示例

```
================================================================================
📊 项目投资财务测算报告
================================================================================

【项目基本信息】
  项目名称: 100MWh储能电站
  项目类型: 储能电站
  运营期: 15年
  企业类型: 高新技术企业

【投资概况】
  总投资: ¥60,000,000.00
    其中: 资本金(30%): ¥18,000,000.00
          贷款(70%): ¥42,000,000.00

【财务指标】（核心）
  ┌─────────────────────────────────────┐
  │  NPV(净现值):     ¥8,500,000.00      │
  │  IRR(内部收益率):  12.5%             │
  │  静态回收期:      7.5年              │
  │  动态回收期:      9.2年              │
  │  投资利润率(ROI): 15.2%              │
  │  资本金利润率(ROE): 25.6%            │
  └─────────────────────────────────────┘

【全周期汇总】
  总收入: ¥300,000,000.00
  总成本: ¥100,000,000.00
  总税费: ¥45,000,000.00
  总利润: ¥155,000,000.00
================================================================================
```

## 项目参数说明

### CAPEX（资本性支出）
| 参数 | 说明 | 示例 |
|------|------|------|
| land_cost | 土地购置 | 500万 |
| construction_cost | 建设工程 | 1500万 |
| equipment_cost | 设备购置 | 3000万 |
| installation_cost | 安装工程 | 500万 |
| other_cost | 其他费用 | 300万 |
| working_capital | 流动资金 | 200万 |

### OPEX（运营支出）
| 参数 | 说明 | 示例 |
|------|------|------|
| annual_revenue | 年营业收入 | 2000万 |
| annual_cost | 年运营成本 | 300万 |
| maintenance_cost | 年维护费 | 150万 |
| labor_cost | 年人工费 | 100万 |

### 融资参数
| 参数 | 说明 | 常用值 |
|------|------|--------|
| equity_ratio | 资本金比例 | 30% |
| loan_ratio | 贷款比例 | 70% |
| loan_rate | 贷款利率 | 4.5% |
| loan_term | 贷款期限 | 10年 |

### 税务参数
| 参数 | 选项 |
|------|------|
| enterprise_type | 一般企业/小微企业/高新技术企业 |
| location | 市区/县城/其他 |

## 敏感性分析

```python
# 分析收入、成本、投资对NPV的影响
sensitivity = model.sensitivity_analysis(
    variables=['annual_revenue', 'annual_cost', 'total_investment']
)

# 输出：不同变化幅度下的NPV
# -20%: NPV = xxx
# -10%: NPV = xxx
#   0%: NPV = xxx（基准）
# +10%: NPV = xxx
# +20%: NPV = xxx
```

## 适用项目类型

- ⚡ **储能电站** - 电化学储能、抽水蓄能
- 🌞 **光伏电站** - 集中式/分布式光伏
- 💨 **风电项目** - 陆上/海上风电
- 🏭 **制造业** - 工厂建设、产线投资
- 🔋 **新能源汽车** - 充电桩、换电站

## 税务集成

本模型已集成 `china-enterprise-tax` 技能包的税务计算：
- 增值税（销项-进项）
- 企业所得税（高新企业15%、小微5%）
- 附加税费（城建+教育+地方教育）
- 印花税

## 判断标准

| 指标 | 优秀 | 良好 | 一般 | 差 |
|------|------|------|------|-----|
| IRR | >15% | 10-15% | 8-10% | <8% |
| NPV | >0 | - | - | <0 |
| 回收期 | <8年 | 8-10年 | 10-12年 | >12年 |

## 注意事项

1. **收入预测**：需基于 realistic 的电价、利用率预测
2. **成本增长**：考虑了2%的年成本增长（通胀）
3. **税务简化**：部分小税种简化处理
4. **折旧方法**：直线法折旧，残值率5%

## 相关技能包

- `china-enterprise-tax` - 企业税务计算
- `storage-calc` - 储能专项测算
- `stock-analysis-pro` - 投资收益分析

---

*适用于中国税收法规和会计准则，2024年版*
