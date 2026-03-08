#!/usr/bin/env python3
"""
中国企业税务计算器 - 企业所得税、增值税、附加税费等计算
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

@dataclass
class EnterpriseTaxResult:
    """企业税费计算结果"""
    # 收入
    revenue: float                    # 营业收入
    
    # 增值税
    vat_output: float                 # 销项税额
    vat_input: float                  # 进项税额
    vat_payable: float                # 应交增值税
    
    # 附加税费
    urban_tax: float                  # 城建税
    education_surcharge: float        # 教育费附加
    local_education: float            # 地方教育附加
    total_surcharge: float            # 附加税费合计
    
    # 企业所得税
    taxable_income: float             # 应纳税所得额
    income_tax_rate: float            # 所得税税率
    income_tax: float                 # 企业所得税
    
    # 其他税费
    stamp_tax: float                  # 印花税
    
    # 合计
    total_tax: float                  # 税费合计
    tax_burden_rate: float            # 税负率

class ChinaEnterpriseTaxCalculator:
    """中国企业税务计算器"""
    
    # 城建税税率（根据地区）
    URBAN_TAX_RATES = {
        '市区': 0.07,
        '县城': 0.05,
        '其他': 0.01,
    }
    
    # 企业所得税税率
    INCOME_TAX_RATES = {
        '一般企业': 0.25,
        '小微企业': 0.05,  # 实际税负5%
        '高新技术企业': 0.15,
        '西部大开发': 0.15,
    }
    
    # 附加税费率
    EDUCATION_SURCHARGE_RATE = 0.03      # 教育费附加
    LOCAL_EDUCATION_RATE = 0.02          # 地方教育附加
    
    def __init__(self, location: str = '市区', enterprise_type: str = '一般企业'):
        """
        初始化计算器
        
        Args:
            location: 企业所在地（市区/县城/其他）
            enterprise_type: 企业类型（一般企业/小微企业/高新技术企业）
        """
        self.location = location
        self.enterprise_type = enterprise_type
    
    def calculate_vat(self, revenue: float, cost: float, 
                     output_rate: float = 0.13, 
                     input_rate: float = 0.13) -> Dict:
        """
        计算增值税
        
        Args:
            revenue: 营业收入（不含税）
            cost: 营业成本（不含税）
            output_rate: 销项税率（默认13%）
            input_rate: 进项税率（默认13%）
        """
        vat_output = revenue * output_rate        # 销项税额
        vat_input = cost * input_rate             # 进项税额
        vat_payable = max(0, vat_output - vat_input)  # 应交增值税
        
        return {
            'vat_output': vat_output,
            'vat_input': vat_input,
            'vat_payable': vat_payable,
        }
    
    def calculate_surcharge(self, vat_payable: float) -> Dict:
        """计算附加税费"""
        urban_rate = self.URBAN_TAX_RATES.get(self.location, 0.07)
        
        urban_tax = vat_payable * urban_rate
        education_surcharge = vat_payable * self.EDUCATION_SURCHARGE_RATE
        local_education = vat_payable * self.LOCAL_EDUCATION_RATE
        
        total = urban_tax + education_surcharge + local_education
        
        return {
            'urban_tax': urban_tax,
            'education_surcharge': education_surcharge,
            'local_education': local_education,
            'total_surcharge': total,
        }
    
    def calculate_income_tax(self, revenue: float, cost: float, 
                            operating_expenses: float = 0,
                            other_income: float = 0,
                            tax_adjustments: float = 0) -> Dict:
        """
        计算企业所得税
        
        Args:
            revenue: 营业收入
            cost: 营业成本
            operating_expenses: 期间费用（销售+管理+财务费用）
            other_income: 其他收益/营业外收入
            tax_adjustments: 纳税调整增加额
        """
        # 利润总额
        total_profit = revenue - cost - operating_expenses + other_income
        
        # 应纳税所得额
        taxable_income = total_profit + tax_adjustments
        
        # 小微企业优惠（简化计算）
        if self.enterprise_type == '小微企业':
            if taxable_income <= 1000000:
                # 应纳税所得额减按25%，税率20%，实际税负5%
                actual_tax = taxable_income * 0.25 * 0.20
                effective_rate = 0.05
            elif taxable_income <= 3000000:
                # 超过100万部分减按50%，税率20%
                actual_tax = 1000000 * 0.25 * 0.20 + (taxable_income - 1000000) * 0.50 * 0.20
                effective_rate = actual_tax / taxable_income
            else:
                actual_tax = taxable_income * 0.25
                effective_rate = 0.25
        else:
            tax_rate = self.INCOME_TAX_RATES.get(self.enterprise_type, 0.25)
            actual_tax = taxable_income * tax_rate
            effective_rate = tax_rate
        
        return {
            'total_profit': total_profit,
            'taxable_income': taxable_income,
            'income_tax_rate': effective_rate,
            'income_tax': max(0, actual_tax),
        }
    
    def calculate_stamp_tax(self, revenue: float, contracts: int = 1) -> float:
        """
        计算印花税（简化版）
        
        Args:
            revenue: 营业收入
            contracts: 合同数量（用于定额计算）
        """
        # 销售合同印花税：万分之三
        sales_stamp = revenue * 0.0003
        
        # 资金账簿印花税：万分之二点五（简化，按收入估算）
        capital_stamp = revenue * 0.00025
        
        return sales_stamp + capital_stamp
    
    def calculate_all(self, 
                     revenue: float,                    # 营业收入（不含税）
                     cost: float,                       # 营业成本（不含税）
                     operating_expenses: float = 0,     # 期间费用
                     vat_output_rate: float = 0.13,     # 销项税率
                     vat_input_rate: float = 0.13,      # 进项税率
                     other_income: float = 0,           # 其他收益
                     tax_adjustments: float = 0,        # 纳税调整
                     contracts: int = 1) -> EnterpriseTaxResult:
        """计算全部税费"""
        
        # 增值税
        vat = self.calculate_vat(revenue, cost, vat_output_rate, vat_input_rate)
        
        # 附加税费
        surcharge = self.calculate_surcharge(vat['vat_payable'])
        
        # 企业所得税（用含税收入计算）
        revenue_with_tax = revenue + vat['vat_output']
        cost_with_tax = cost + vat['vat_input']
        income_tax = self.calculate_income_tax(
            revenue_with_tax, 
            cost_with_tax, 
            operating_expenses,
            other_income,
            tax_adjustments
        )
        
        # 印花税
        stamp_tax = self.calculate_stamp_tax(revenue_with_tax, contracts)
        
        # 税费合计
        total_tax = (vat['vat_payable'] + 
                    surcharge['total_surcharge'] + 
                    income_tax['income_tax'] + 
                    stamp_tax)
        
        # 税负率
        tax_burden_rate = total_tax / revenue_with_tax if revenue_with_tax > 0 else 0
        
        return EnterpriseTaxResult(
            revenue=revenue_with_tax,
            vat_output=vat['vat_output'],
            vat_input=vat['vat_input'],
            vat_payable=vat['vat_payable'],
            urban_tax=surcharge['urban_tax'],
            education_surcharge=surcharge['education_surcharge'],
            local_education=surcharge['local_education'],
            total_surcharge=surcharge['total_surcharge'],
            taxable_income=income_tax['taxable_income'],
            income_tax_rate=income_tax['income_tax_rate'],
            income_tax=income_tax['income_tax'],
            stamp_tax=stamp_tax,
            total_tax=total_tax,
            tax_burden_rate=tax_burden_rate,
        )

def format_tax_report(result: EnterpriseTaxResult, location: str, enterprise_type: str) -> str:
    """格式化税务报告"""
    lines = [
        f"\n{'='*70}",
        f"📊 中国企业税务计算报告",
        f"{'='*70}",
        f"",
        f"企业类型: {enterprise_type}",
        f"所在地区: {location}",
        f"",
        f"【营业收入】",
        f"  含税收入: ¥{result.revenue:,.2f}",
        f"",
        f"【增值税】",
        f"  销项税额: ¥{result.vat_output:,.2f}",
        f"  进项税额: ¥{result.vat_input:,.2f}",
        f"  应交增值税: ¥{result.vat_payable:,.2f}",
        f"",
        f"【附加税费】",
        f"  城建税: ¥{result.urban_tax:,.2f}",
        f"  教育费附加: ¥{result.education_surcharge:,.2f}",
        f"  地方教育附加: ¥{result.local_education:,.2f}",
        f"  附加税费合计: ¥{result.total_surcharge:,.2f}",
        f"",
        f"【企业所得税】",
        f"  应纳税所得额: ¥{result.taxable_income:,.2f}",
        f"  适用税率: {result.income_tax_rate*100:.1f}%",
        f"  应交所得税: ¥{result.income_tax:,.2f}",
        f"",
        f"【其他税费】",
        f"  印花税: ¥{result.stamp_tax:,.2f}",
        f"",
        f"{'='*70}",
        f"【税费合计】",
        f"  总税费: ¥{result.total_tax:,.2f}",
        f"  税负率: {result.tax_burden_rate*100:.2f}%",
        f"{'='*70}",
    ]
    
    return "\n".join(lines)

# 税务筹划建议
def get_tax_planning_suggestions(result: EnterpriseTaxResult, 
                                 enterprise_type: str) -> list:
    """获取税务筹划建议"""
    suggestions = []
    
    # 小微企业优惠建议
    if result.taxable_income > 3000000 and enterprise_type == '一般企业':
        suggestions.append("💡 考虑拆分业务，成立小微企业享受所得税优惠（实际税负5%）")
    
    # 增值税进项建议
    if result.vat_payable > result.vat_output * 0.5:
        suggestions.append("💡 进项税额较少，建议加强供应商管理，尽可能取得增值税专用发票")
    
    # 税负率分析
    if result.tax_burden_rate > 0.10:
        suggestions.append("⚠️ 税负率较高（>10%），建议进行税务筹划优化")
    elif result.tax_burden_rate < 0.03:
        suggestions.append("⚠️ 税负率较低（<3%），注意税务合规风险")
    
    # 高新技术企业建议
    if result.income_tax_rate == 0.25:
        suggestions.append("💡 如符合条件，建议申请高新技术企业，所得税降至15%")
    
    return suggestions

if __name__ == "__main__":
    # 测试示例
    calc = ChinaEnterpriseTaxCalculator(location='市区', enterprise_type='小微企业')
    
    result = calc.calculate_all(
        revenue=1000000,          # 年收入100万
        cost=600000,              # 成本60万
        operating_expenses=150000, # 费用15万
        vat_output_rate=0.13,
        vat_input_rate=0.13,
    )
    
    print(format_tax_report(result, '市区', '小微企业'))
    
    print("\n【税务筹划建议】")
    for s in get_tax_planning_suggestions(result, '小微企业'):
        print(s)
