#!/usr/bin/env python3
"""
生成示例Excel报告 - 50MWh工商业储能（更健康的案例）
"""

import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/project-finance-model')

from project_finance_model import ProjectFinancialModel, ProjectInputs
from excel_report_generator import ExcelReportGenerator

# 50MWh工商业储能项目（更合理的规模）
inputs = ProjectInputs(
    project_name="50MWh工商业储能项目",
    project_type="工商业储能",
    operation_years=12,
    
    # CAPEX投资（更紧凑）
    land_cost=2000000,          # 土地200万（5亩）
    construction_cost=8000000,  # 建设800万
    equipment_cost=18000000,    # 设备1800万（集装箱式，3600元/kWh）
    installation_cost=3000000,  # 安装300万
    other_cost=1500000,         # 其他150万
    working_capital=1000000,    # 流动资金100万
    
    # OPEX运营（年）
    annual_revenue=9800000,     # 年收入980万
    #   - 峰谷套利：50MWh×2次/天×300天×0.7元/kWh价差 = 2100万度×0.7元 = 1470万
    #   - 需求侧响应：假设每年200万
    #   - 实际保守估计：980万（考虑80%容量利用率）
    annual_cost=1200000,        # 年运营成本120万
    maintenance_cost=600000,    # 维护费60万
    labor_cost=400000,          # 人工费40万（2人）
    
    # 融资
    equity_ratio=0.30,
    loan_ratio=0.70,
    loan_rate=0.0425,
    loan_term=8,
    
    # 税务
    enterprise_type="高新技术企业",
    location="市区",
    
    # 折现
    discount_rate=0.08,
)

# 创建模型
model = ProjectFinancialModel(inputs)
metrics = model.calculate_financial_metrics()

# 生成Excel报告
generator = ExcelReportGenerator(model)
output_path = '/Users/zhaoruicn/.openclaw/workspace/示例_50MWh工商业储能财务分析报告.xlsx'
output_path = generator.generate_report(output_path)

print(f"✅ 示例报告已生成: {output_path}")
print(f"\n📊 关键财务指标:")
print(f"  总投资: ¥{metrics.total_investment/10000:,.0f}万元")
print(f"  资本金: ¥{metrics.equity_investment/10000:,.0f}万元")
print(f"  NPV: ¥{metrics.npv/10000:,.0f}万元")
print(f"  IRR: {metrics.irr*100:.2f}%")
print(f"  静态回收期: {metrics.payback_period:.1f}年")
print(f"  动态回收期: {metrics.dynamic_payback:.1f}年")
print(f"  ROI: {metrics.roi*100:.1f}%")
print(f"  ROE: {metrics.roe*100:.1f}%")

if metrics.npv > 0 and metrics.irr > 0.08:
    print(f"\n✅ 项目财务可行！")
elif metrics.npv > 0:
    print(f"\n⚠️ 项目基本可行，但收益偏低")
else:
    print(f"\n❌ 项目财务不可行")
