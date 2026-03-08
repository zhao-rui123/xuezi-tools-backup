#!/usr/bin/env python3
"""
项目投资财务测算系统 - 完整版
整合CAPEX、OPEX、税务、财务指标分析
适用于储能、新能源、制造业等投资项目
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

# 引入税务计算器
import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/china-enterprise-tax')
from project_investment_tax import ProjectInvestmentTaxCalculator

@dataclass
class ProjectInputs:
    """项目输入参数"""
    # 基本信息
    project_name: str = "项目"
    project_type: str = "储能电站"  # 储能/光伏/风电/制造业
    operation_years: int = 15
    construction_period: int = 1  # 建设期（年）
    
    # CAPEX投资
    land_cost: float = 0              # 土地购置
    construction_cost: float = 0      # 建设工程
    equipment_cost: float = 0         # 设备购置
    installation_cost: float = 0      # 安装工程
    other_cost: float = 0             # 其他费用
    working_capital: float = 0        # 流动资金
    
    # OPEX运营
    annual_revenue: float = 0         # 年收入
    annual_cost: float = 0            # 年运营成本
    annual_expenses: float = 0        # 年期间费用
    maintenance_cost: float = 0       # 年维护费
    labor_cost: float = 0             # 年人工费
    
    # 融资
    equity_ratio: float = 0.30        # 资本金比例
    loan_ratio: float = 0.70          # 贷款比例
    loan_rate: float = 0.045          # 贷款利率（4.5%）
    loan_term: int = 10               # 贷款期限
    
    # 折旧
    depreciation_years: int = 15      # 折旧年限
    residual_rate: float = 0.05       # 残值率
    
    # 税务
    location: str = "市区"
    enterprise_type: str = "高新技术企业"
    
    # 其他
    discount_rate: float = 0.08       # 折现率（8%）
    inflation_rate: float = 0.02      # 通胀率（2%）
    revenue_growth: float = 0.00      # 收入增长率
    cost_growth: float = 0.02         # 成本增长率

@dataclass
class FinancialMetrics:
    """财务指标结果"""
    # 投资指标
    total_investment: float           # 总投资
    equity_investment: float          # 资本金
    loan_amount: float                # 贷款额
    
    # 收益指标
    total_revenue: float              # 总收入
    total_cost: float                 # 总成本
    total_tax: float                  # 总税费
    total_profit: float               # 总利润
    
    # 现金流指标
    npv: float                        # 净现值
    irr: float                        # 内部收益率
    payback_period: float             # 静态回收期
    dynamic_payback: float            # 动态回收期
    
    # 财务比率
    roi: float                        # 投资利润率
    roe: float                        # 资本金利润率
    debt_service_coverage: float      # 偿债备付率
    
    # 年均指标
    annual_avg_revenue: float         # 年均收入
    annual_avg_profit: float          # 年均利润
    annual_avg_cash_flow: float       # 年均现金流

@dataclass  
class YearlyCashFlow:
    """年度现金流"""
    year: int
    revenue: float
    cost: float
    depreciation: float
    interest: float
    tax: float
    net_profit: float
    cash_flow: float
    cumulative_cf: float
    discounted_cf: float

class ProjectFinancialModel:
    """项目投资财务模型"""
    
    def __init__(self, inputs: ProjectInputs):
        self.inputs = inputs
        self.tax_calc = ProjectInvestmentTaxCalculator(
            project_type='工业',
            location=inputs.location,
            enterprise_type=inputs.enterprise_type
        )
        self.yearly_data: List[YearlyCashFlow] = []
        self.metrics: Optional[FinancialMetrics] = None
    
    def calculate_total_investment(self) -> Dict:
        """计算总投资"""
        capex = (self.inputs.land_cost + 
                self.inputs.construction_cost + 
                self.inputs.equipment_cost + 
                self.inputs.installation_cost + 
                self.inputs.other_cost)
        
        total = capex + self.inputs.working_capital
        
        equity = total * self.inputs.equity_ratio
        loan = total * self.inputs.loan_ratio
        
        return {
            'capex': capex,
            'working_capital': self.inputs.working_capital,
            'total_investment': total,
            'equity': equity,
            'loan': loan,
        }
    
    def calculate_depreciation(self, investment: float) -> float:
        """计算年折旧（直线法）"""
        depreciable_amount = investment * (1 - self.inputs.residual_rate)
        return depreciable_amount / self.inputs.depreciation_years
    
    def calculate_loan_schedule(self, loan: float) -> List[Dict]:
        """计算贷款还款计划（等额本息）"""
        n = self.inputs.loan_term
        r = self.inputs.loan_rate
        
        # 等额本息月供公式
        if r == 0:
            payment = loan / n
        else:
            payment = loan * r * (1 + r)**n / ((1 + r)**n - 1)
        
        schedule = []
        balance = loan
        
        for year in range(1, n + 1):
            interest = balance * r
            principal = payment - interest
            balance -= principal
            
            schedule.append({
                'year': year,
                'payment': payment,
                'principal': principal,
                'interest': interest,
                'balance': max(0, balance),
            })
        
        return schedule
    
    def calculate_yearly_cash_flow(self) -> List[YearlyCashFlow]:
        """计算年度现金流"""
        inv = self.calculate_total_investment()
        loan_schedule = self.calculate_loan_schedule(inv['loan'])
        annual_depreciation = self.calculate_depreciation(inv['capex'])
        
        yearly_data = []
        cumulative_cf = -inv['total_investment']  # 初始投资
        
        for year in range(1, self.inputs.operation_years + 1):
            # 收入成本（考虑增长）
            revenue = self.inputs.annual_revenue * ((1 + self.inputs.revenue_growth) ** (year - 1))
            cost = (self.inputs.annual_cost + self.inputs.maintenance_cost + self.inputs.labor_cost) * \
                   ((1 + self.inputs.cost_growth) ** (year - 1))
            
            # 利息
            interest = 0
            if year <= len(loan_schedule):
                interest = loan_schedule[year - 1]['interest']
            
            # 折旧
            depreciation = annual_depreciation if year <= self.inputs.depreciation_years else 0
            
            # 税前利润
            profit_before_tax = revenue - cost - depreciation - interest
            
            # 所得税
            if self.inputs.enterprise_type == '小微企业':
                if profit_before_tax <= 1000000:
                    tax = profit_before_tax * 0.05
                elif profit_before_tax <= 3000000:
                    tax = 1000000 * 0.05 + (profit_before_tax - 1000000) * 0.10
                else:
                    tax = profit_before_tax * 0.25
            elif self.inputs.enterprise_type == '高新技术企业':
                tax = profit_before_tax * 0.15
            else:
                tax = profit_before_tax * 0.25
            
            tax = max(0, tax)
            
            # 净利润
            net_profit = profit_before_tax - tax
            
            # 现金流 = 净利润 + 折旧 - 本金偿还
            principal_payment = 0
            if year <= len(loan_schedule):
                principal_payment = loan_schedule[year - 1]['principal']
            
            cash_flow = net_profit + depreciation - principal_payment
            
            # 最后一年加回流动资金和残值
            if year == self.inputs.operation_years:
                residual_value = inv['capex'] * self.inputs.residual_rate
                cash_flow += self.inputs.working_capital + residual_value
            
            cumulative_cf += cash_flow
            
            # 折现
            discount_factor = (1 + self.inputs.discount_rate) ** year
            discounted_cf = cash_flow / discount_factor
            
            yearly_data.append(YearlyCashFlow(
                year=year,
                revenue=revenue,
                cost=cost,
                depreciation=depreciation,
                interest=interest,
                tax=tax,
                net_profit=net_profit,
                cash_flow=cash_flow,
                cumulative_cf=cumulative_cf,
                discounted_cf=discounted_cf,
            ))
        
        return yearly_data
    
    def calculate_financial_metrics(self) -> FinancialMetrics:
        """计算财务指标"""
        inv = self.calculate_total_investment()
        self.yearly_data = self.calculate_yearly_cash_flow()
        
        # 总投资
        total_investment = inv['total_investment']
        equity = inv['equity']
        loan = inv['loan']
        
        # 总收入成本利润
        total_revenue = sum(y.revenue for y in self.yearly_data)
        total_cost = sum(y.cost for y in self.yearly_data)
        total_tax = sum(y.tax for y in self.yearly_data)
        total_profit = sum(y.net_profit for y in self.yearly_data)
        
        # NPV（净现值）
        npv = -total_investment + sum(y.discounted_cf for y in self.yearly_data)
        
        # IRR（内部收益率）- 使用手动计算（numpy 2.0+已移除np.irr）
        cash_flows = [-total_investment] + [y.cash_flow for y in self.yearly_data]
        irr = self._calculate_irr_manual(cash_flows)
        
        # 回收期
        payback_period = self._calculate_payback_period()
        dynamic_payback = self._calculate_dynamic_payback()
        
        # 财务比率
        roi = total_profit / total_investment if total_investment > 0 else 0
        roe = total_profit / equity if equity > 0 else 0
        
        # 年均指标
        n = self.inputs.operation_years
        annual_avg_revenue = total_revenue / n
        annual_avg_profit = total_profit / n
        annual_avg_cash_flow = sum(y.cash_flow for y in self.yearly_data) / n
        
        self.metrics = FinancialMetrics(
            total_investment=total_investment,
            equity_investment=equity,
            loan_amount=loan,
            total_revenue=total_revenue,
            total_cost=total_cost,
            total_tax=total_tax,
            total_profit=total_profit,
            npv=npv,
            irr=irr,
            payback_period=payback_period,
            dynamic_payback=dynamic_payback,
            roi=roi,
            roe=roe,
            debt_service_coverage=0,  # 简化
            annual_avg_revenue=annual_avg_revenue,
            annual_avg_profit=annual_avg_profit,
            annual_avg_cash_flow=annual_avg_cash_flow,
        )
        
        return self.metrics
    
    def _calculate_irr_manual(self, cash_flows: List[float]) -> float:
        """手动计算IRR（二分查找+牛顿迭代混合）"""
        def npv(rate):
            return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
        
        # 检查现金流符号变化
        signs = [1 if cf > 0 else -1 if cf < 0 else 0 for cf in cash_flows]
        if not any(s > 0 for s in signs) or not any(s < 0 for s in signs):
            return 0.0  # 没有符号变化，无解
        
        # 二分查找确定大致范围
        low, high = -0.99, 10.0  # -99% 到 1000%
        
        # 确保high足够大
        while npv(high) > 0 and high < 100:
            high *= 2
        
        # 二分查找
        for _ in range(50):
            mid = (low + high) / 2
            npv_mid = npv(mid)
            
            if abs(npv_mid) < 0.0001:
                return mid
            
            if npv_mid > 0:
                low = mid
            else:
                high = mid
        
        # 牛顿迭代精化
        rate = (low + high) / 2
        for _ in range(20):
            npv_val = npv(rate)
            if abs(npv_val) < 0.00001:
                break
            
            # 数值微分
            h = 0.0001
            derivative = (npv(rate + h) - npv(rate - h)) / (2 * h)
            
            if abs(derivative) < 1e-10:
                break
            
            rate = rate - npv_val / derivative
        
        return rate
    
    def _calculate_payback_period(self) -> float:
        """计算静态回收期"""
        inv = self.calculate_total_investment()
        cumulative = -inv['total_investment']
        
        for i, year_data in enumerate(self.yearly_data, 1):
            cumulative += year_data.cash_flow
            if cumulative >= 0:
                # 插值计算
                prev_cumulative = cumulative - year_data.cash_flow
                fraction = abs(prev_cumulative) / year_data.cash_flow
                return i - 1 + fraction
        
        return float('inf')
    
    def _calculate_dynamic_payback(self) -> float:
        """计算动态回收期"""
        inv = self.calculate_total_investment()
        cumulative = -inv['total_investment']
        
        for i, year_data in enumerate(self.yearly_data, 1):
            cumulative += year_data.discounted_cf
            if cumulative >= 0:
                prev_cumulative = cumulative - year_data.discounted_cf
                fraction = abs(prev_cumulative) / year_data.discounted_cf
                return i - 1 + fraction
        
        return float('inf')
    
    def sensitivity_analysis(self, variables: List[str] = None) -> Dict:
        """敏感性分析"""
        if variables is None:
            variables = ['annual_revenue', 'annual_cost', 'total_investment']
        
        base_npv = self.metrics.npv if self.metrics else self.calculate_financial_metrics().npv
        
        results = {}
        for var in variables:
            # 变化 ±10%, ±20%
            changes = [-0.20, -0.10, 0, 0.10, 0.20]
            npv_changes = []
            
            for change in changes:
                # 修改输入
                original_value = getattr(self.inputs, var)
                new_value = original_value * (1 + change)
                setattr(self.inputs, var, new_value)
                
                # 重新计算
                new_model = ProjectFinancialModel(self.inputs)
                new_metrics = new_model.calculate_financial_metrics()
                npv_changes.append(new_metrics.npv)
                
                # 恢复
                setattr(self.inputs, var, original_value)
            
            results[var] = {
                'changes': changes,
                'npv_values': npv_changes,
                'sensitivity': (npv_changes[-1] - npv_changes[0]) / base_npv if base_npv != 0 else 0,
            }
        
        return results

def format_financial_report(model: ProjectFinancialModel) -> str:
    """格式化财务报告"""
    inputs = model.inputs
    metrics = model.metrics if model.metrics else model.calculate_financial_metrics()
    yearly = model.yearly_data
    
    inv = model.calculate_total_investment()
    
    lines = [
        f"\n{'='*80}",
        f"📊 项目投资财务测算报告",
        f"{'='*80}",
        f"",
        f"【项目基本信息】",
        f"  项目名称: {inputs.project_name}",
        f"  项目类型: {inputs.project_type}",
        f"  运营期: {inputs.operation_years}年",
        f"  企业类型: {inputs.enterprise_type}",
        f"",
        f"【投资概况】",
        f"  土地购置: ¥{inputs.land_cost:,.2f}",
        f"  建设工程: ¥{inputs.construction_cost:,.2f}",
        f"  设备购置: ¥{inputs.equipment_cost:,.2f}",
        f"  安装工程: ¥{inputs.installation_cost:,.2f}",
        f"  其他费用: ¥{inputs.other_cost:,.2f}",
        f"  流动资金: ¥{inputs.working_capital:,.2f}",
        f"  ─────────────────────────────",
        f"  总投资: ¥{metrics.total_investment:,.2f}",
        f"    其中: 资本金(30%): ¥{metrics.equity_investment:,.2f}",
        f"          贷款(70%): ¥{metrics.loan_amount:,.2f}",
        f"",
        f"【运营概况】",
        f"  年收入: ¥{inputs.annual_revenue:,.2f}",
        f"  年运营成本: ¥{inputs.annual_cost:,.2f}",
        f"  年维护费: ¥{inputs.maintenance_cost:,.2f}",
        f"  年人工费: ¥{inputs.labor_cost:,.2f}",
        f"  年均税费: ¥{metrics.total_tax/inputs.operation_years:,.2f}",
        f"",
        f"【财务指标】（核心）",
        f"  ┌─────────────────────────────────────┐",
        f"  │  NPV(净现值):     ¥{metrics.npv:,.2f}          │",
        f"  │  IRR(内部收益率):  {metrics.irr*100:.2f}%             │",
        f"  │  静态回收期:      {metrics.payback_period:.2f}年           │",
        f"  │  动态回收期:      {metrics.dynamic_payback:.2f}年           │",
        f"  │  投资利润率(ROI): {metrics.roi*100:.2f}%             │",
        f"  │  资本金利润率(ROE):{metrics.roe*100:.2f}%             │",
        f"  └─────────────────────────────────────┘",
        f"",
        f"【全周期汇总】",
        f"  总收入: ¥{metrics.total_revenue:,.2f}",
        f"  总成本: ¥{metrics.total_cost:,.2f}",
        f"  总税费: ¥{metrics.total_tax:,.2f}",
        f"  总利润: ¥{metrics.total_profit:,.2f}",
        f"",
        f"【年均指标】",
        f"  年均收入: ¥{metrics.annual_avg_revenue:,.2f}",
        f"  年均利润: ¥{metrics.annual_avg_profit:,.2f}",
        f"  年均现金流: ¥{metrics.annual_avg_cash_flow:,.2f}",
        f"{'='*80}",
    ]
    
    # 添加前5年现金流表
    lines.extend([
        f"",
        f"【现金流明细】（前5年）",
        f"{'年份':<6}{'收入':<12}{'成本':<12}{'税费':<12}{'现金流':<12}{'累计':<12}",
        f"{'-'*66}",
    ])
    
    for y in yearly[:5]:
        lines.append(f"{y.year:<6}¥{y.revenue:<11,.0f}¥{y.cost:<11,.0f}¥{y.tax:<11,.0f}¥{y.cash_flow:<11,.0f}¥{y.cumulative_cf:<11,.0f}")
    
    lines.append(f"{'='*80}")
    
    return "\n".join(lines)

# 示例：储能项目
def storage_project_example():
    """储能项目示例"""
    inputs = ProjectInputs(
        project_name="100MWh储能电站",
        project_type="储能电站",
        operation_years=15,
        
        # CAPEX
        land_cost=5000000,
        construction_cost=15000000,
        equipment_cost=30000000,
        installation_cost=5000000,
        other_cost=3000000,
        working_capital=2000000,
        
        # OPEX
        annual_revenue=8000000,    # 峰谷套利收入
        annual_cost=1500000,       # 运维
        maintenance_cost=800000,   # 维护
        labor_cost=600000,         # 人工
        
        # 融资
        equity_ratio=0.30,
        loan_ratio=0.70,
        loan_rate=0.045,
        loan_term=10,
        
        # 税务
        enterprise_type="高新技术企业",
        location="市区",
        
        # 折现
        discount_rate=0.08,
    )
    
    model = ProjectFinancialModel(inputs)
    metrics = model.calculate_financial_metrics()
    
    print(format_financial_report(model))
    
    return model, metrics

if __name__ == "__main__":
    storage_project_example()
