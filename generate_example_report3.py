#!/usr/bin/env python3
"""
生成示例Excel报告 - 20MWh工商业储能（精品案例）
"""

import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/project-finance-model')

from project_finance_model import ProjectFinancialModel, ProjectInputs
from excel_report_generator import ExcelReportGenerator

# 20MWh工商业储能（浙江某工厂项目，高电价差）
inputs = ProjectInputs(
    project_name="20MWh工商业储能项目（浙江）",
    project_type="工商业储能",
    operation_years=10,
    
    # CAPEX投资
    land_cost=500000,           # 土地50万（租赁或自有）
    construction_cost=2000000,  # 建设200万（基础、电缆）
    equipment_cost=7200000,     # 设备720万（3600元/kWh）
    installation_cost=800000,   # 安装80万
    other_cost=500000,          # 其他50万
    working_capital=300000,     # 流动资金30万
    
    # OPEX运营（年）
    annual_revenue=4320000,     # 年收入432万
    #   浙江峰谷价差大（峰1.2元，谷0.3元，差0.9元）
    #   20MWh × 2次/天 × 300天 × 0.9元 × 80%效率 = 864万度 × 0.5元平均价差 = 432万
    annual_cost=350000,         # 年运营成本35万
    maintenance_cost=180000,    # 维护费18万（设备2.5%）
    labor_cost=120000,          # 人工费12万（1人兼职）
    
    # 融资
    equity_ratio=0.30,
    loan_ratio=0.70,
    loan_rate=0.0425,
    loan_term=7,
    
    # 税务
    enterprise_type="高新技术企业",
    location="市区",
    
    # 折现
    discount_rate=0.08,
)

# 创建模型
model = ProjectFinancialModel(inputs)
metrics = model.calculate_financial_metrics()

print(f"📊 项目基础数据:")
print(f"  总投资: ¥{metrics.total_investment/10000:.0f}万元")
print(f"  年收入: ¥{inputs.annual_revenue/10000:.0f}万元")
print(f"  年成本: ¥{(inputs.annual_cost+inputs.maintenance_cost+inputs.labor_cost)/10000:.0f}万元")
print(f"\n📊 财务指标计算:")
print(f"  NPV: ¥{metrics.npv/10000:.0f}万元")
print(f"  IRR: {metrics.irr*100:.2f}%")
print(f"  静态回收期: {metrics.payback_period:.1f}年")
print(f"  动态回收期: {metrics.dynamic_payback:.1f}年")

# 生成Excel报告
generator = ExcelReportGenerator(model)
output_path = '/Users/zhaoruicn/.openclaw/workspace/示例_20MWh工商业储能财务分析.xlsx'
output_path = generator.generate_report(output_path)

print(f"\n✅ 报告已生成: {output_path}")
