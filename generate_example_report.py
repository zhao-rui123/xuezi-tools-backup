#!/usr/bin/env python3
"""
生成示例Excel报告 - 100MWh储能电站
"""

import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/project-finance-model')

from project_finance_model import ProjectFinancialModel, ProjectInputs
from excel_report_generator import ExcelReportGenerator

# 100MWh储能电站真实案例
inputs = ProjectInputs(
    project_name="100MWh储能电站项目",
    project_type="电化学储能",
    operation_years=15,
    
    # CAPEX投资
    land_cost=8000000,          # 土地800万（20亩×40万/亩）
    construction_cost=25000000, # 建设2500万（厂房、基础）
    equipment_cost=45000000,    # 设备4500万（电池系统+BMS+PCS）
    installation_cost=8000000,  # 安装800万
    other_cost=4000000,         # 其他400万（设计、监理、验收）
    working_capital=3000000,    # 流动资金300万
    
    # OPEX运营（年）
    annual_revenue=15800000,    # 年收入1580万
    #   - 峰谷套利：100MWh×2次/天×300天×0.5元/kWh = 3000万度×0.5元 = 1500万
    #   - 容量租赁：100MWh×8万/MWh/年 = 80万
    annual_cost=2800000,        # 年运营成本280万
    maintenance_cost=1200000,   # 维护费120万（设备2.5%）
    labor_cost=800000,          # 人工费80万（4人×20万/年）
    
    # 融资
    equity_ratio=0.30,          # 资本金30%
    loan_ratio=0.70,            # 贷款70%
    loan_rate=0.0425,           # 利率4.25%（LPR优惠）
    loan_term=10,               # 贷款10年
    
    # 税务
    enterprise_type="高新技术企业",  # 储能企业可申请高新
    location="市区",
    
    # 折现
    discount_rate=0.08,         # 折现率8%
)

# 创建模型
model = ProjectFinancialModel(inputs)
metrics = model.calculate_financial_metrics()

# 生成Excel报告
generator = ExcelReportGenerator(model)
output_path = '/Users/zhaoruicn/.openclaw/workspace/示例_100MWh储能电站财务分析报告.xlsx'
output_path = generator.generate_report(output_path)

print(f"✅ 示例报告已生成: {output_path}")
print(f"\n📊 关键财务指标:")
print(f"  总投资: ¥{metrics.total_investment/10000:,.0f}万元")
print(f"  NPV: ¥{metrics.npv/10000:,.0f}万元")
print(f"  IRR: {metrics.irr*100:.2f}%")
print(f"  静态回收期: {metrics.payback_period:.1f}年")
print(f"  动态回收期: {metrics.dynamic_payback:.1f}年")
