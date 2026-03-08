#!/usr/bin/env python3
"""
项目投资税务计算器 - 适用于中国税收标准的项目投资分析
包括：投资增值税、土地增值税、契税、印花税、投资收益税收等
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import json

@dataclass
class InvestmentTaxResult:
    """项目投资税务结果"""
    # 投资阶段
    deed_tax: float                     # 契税
    stamp_tax_purchase: float           # 购置印花税
    land_value_added_tax: float         # 土地增值税（转让方）
    
    # 建设阶段
    construction_vat: float             # 建筑服务增值税
    equipment_vat: float                # 设备进项税
    
    # 运营阶段
    annual_vat: float                   # 年运营增值税
    annual_income_tax: float            # 年企业所得税
    annual_surcharge: float             # 年附加税费
    
    # 退出阶段
    exit_vat: float                     # 退出增值税
    exit_land_vat: float                # 退出土地增值税
    exit_income_tax: float              # 退出所得税
    
    # 合计
    total_investment_tax: float         # 投资阶段税费
    total_operation_tax: float          # 运营期税费合计
    total_exit_tax: float               # 退出阶段税费
    total_project_tax: float            # 项目全周期税费
    
    # 影响
    tax_impact_on_irr: float            # 税收对IRR影响
    effective_tax_rate: float           # 实际综合税率

class ProjectInvestmentTaxCalculator:
    """项目投资税务计算器"""
    
    # 税率配置
    DEED_TAX_RATE = 0.03                # 契税 3%
    STAMP_TAX_PURCHASE = 0.0005         # 产权转移书据 0.05%
    STAMP_TAX_CONTRACT = 0.0003         # 合同印花税 0.03%
    
    # 土地增值税预征率
    LAND_VAT_PRELEVY_RATES = {
        '住宅': 0.02,
        '商业': 0.03,
        '工业': 0.02,
    }
    
    # 土地增值税清算税率（四级超率累进）
    LAND_VAT_RATES = [
        (0.50, 0.30),      # 增值率≤50%，税率30%
        (1.00, 0.40),      # 50%<增值率≤100%，税率40%
        (2.00, 0.50),      # 100%<增值率≤200%，税率50%
        (float('inf'), 0.60),  # 增值率>200%，税率60%
    ]
    
    def __init__(self, 
                 project_type: str = '工业',
                 location: str = '市区',
                 enterprise_type: str = '一般企业'):
        """
        初始化
        
        Args:
            project_type: 项目类型（住宅/商业/工业）
            location: 所在地区（市区/县城/其他）
            enterprise_type: 企业类型（一般企业/小微企业/高新技术企业）
        """
        self.project_type = project_type
        self.location = location
        self.enterprise_type = enterprise_type
        
        # 城建税税率
        self.urban_tax_rate = 0.07 if location == '市区' else (0.05 if location == '县城' else 0.01)
        self.surcharge_rate = self.urban_tax_rate + 0.03 + 0.02  # 城建+教育+地方教育
    
    def calculate_acquisition_tax(self, 
                                  land_cost: float, 
                                  construction_cost: float = 0) -> Dict:
        """
        计算购置阶段税费
        
        Args:
            land_cost: 土地购置成本
            construction_cost: 建设成本（如有在建工程转让）
        """
        # 契税（买方）
        deed_tax = land_cost * self.DEED_TAX_RATE
        
        # 产权转移书据印花税
        stamp_tax = land_cost * self.STAMP_TAX_PURCHASE
        
        total = deed_tax + stamp_tax
        
        return {
            'deed_tax': deed_tax,
            'stamp_tax': stamp_tax,
            'total_acquisition_tax': total,
        }
    
    def calculate_construction_tax(self,
                                   construction_cost: float,
                                   equipment_cost: float,
                                   vat_rate_construction: float = 0.09,
                                   vat_rate_equipment: float = 0.13) -> Dict:
        """
        计算建设阶段税费
        
        Args:
            construction_cost: 建筑安装工程费（不含税）
            equipment_cost: 设备购置费（不含税）
            vat_rate_construction: 建筑服务税率（9%）
            vat_rate_equipment: 设备税率（13%）
        """
        # 建筑服务进项税
        construction_vat = construction_cost * vat_rate_construction
        
        # 设备进项税
        equipment_vat = equipment_cost * vat_rate_equipment
        
        # 合同印花税（建安合同）
        stamp_tax_construction = construction_cost * self.STAMP_TAX_CONTRACT
        stamp_tax_equipment = equipment_cost * self.STAMP_TAX_CONTRACT
        
        total_input_vat = construction_vat + equipment_vat
        total_stamp = stamp_tax_construction + stamp_tax_equipment
        
        return {
            'construction_vat': construction_vat,
            'equipment_vat': equipment_vat,
            'total_input_vat': total_input_vat,
            'stamp_tax_construction': stamp_tax_construction,
            'stamp_tax_equipment': stamp_tax_equipment,
            'total_stamp_tax': total_stamp,
        }
    
    def calculate_operation_tax(self,
                               annual_revenue: float,
                               annual_cost: float,
                               annual_expenses: float,
                               input_vat_credit: float = 0) -> Dict:
        """
        计算运营阶段年税费
        
        Args:
            annual_revenue: 年营业收入（不含税）
            annual_cost: 年营业成本（不含税）
            annual_expenses: 年期间费用
            input_vat_credit: 可抵扣进项税额余额
        """
        # 增值税（简化计算，假设13%销项，9%进项）
        output_vat = annual_revenue * 0.13
        input_vat = annual_cost * 0.09
        
        # 考虑留抵税额
        net_vat = max(0, output_vat - input_vat - input_vat_credit)
        vat_credit_remaining = max(0, input_vat_credit + input_vat - output_vat)
        
        # 附加税费
        surcharge = net_vat * self.surcharge_rate
        
        # 企业所得税
        taxable_income = annual_revenue - annual_cost - annual_expenses
        
        # 小微企业优惠
        if self.enterprise_type == '小微企业':
            if taxable_income <= 1000000:
                income_tax_rate = 0.05
                income_tax = taxable_income * 0.25 * 0.20
            elif taxable_income <= 3000000:
                income_tax = 1000000 * 0.25 * 0.20 + (taxable_income - 1000000) * 0.50 * 0.20
                income_tax_rate = income_tax / taxable_income if taxable_income > 0 else 0
            else:
                income_tax_rate = 0.25
                income_tax = taxable_income * income_tax_rate
        else:
            income_tax_rate = 0.25 if self.enterprise_type == '一般企业' else 0.15
            income_tax = max(0, taxable_income * income_tax_rate)
        
        # 印花税（销售合同）
        stamp_tax = annual_revenue * self.STAMP_TAX_CONTRACT
        
        return {
            'output_vat': output_vat,
            'input_vat': input_vat,
            'net_vat': net_vat,
            'vat_credit_remaining': vat_credit_remaining,
            'surcharge': surcharge,
            'taxable_income': taxable_income,
            'income_tax_rate': income_tax_rate,
            'income_tax': income_tax,
            'stamp_tax': stamp_tax,
            'total_operation_tax': net_vat + surcharge + income_tax + stamp_tax,
        }
    
    def calculate_exit_tax(self,
                          exit_revenue: float,          # 退出收入
                          total_investment: float,      # 总投资成本
                          accumulated_depreciation: float = 0,
                          land_appreciation: float = 0) -> Dict:
        """
        计算退出阶段税费
        
        Args:
            exit_revenue: 退出收入（转让价格）
            total_investment: 投资成本原值
            accumulated_depreciation: 累计折旧
            land_appreciation: 土地增值额
        """
        # 资产转让增值税（简化，假设按销售不动产9%）
        exit_vat = exit_revenue * 0.09 / 1.09
        
        # 土地增值税（如有土地增值）
        if land_appreciation > 0:
            appreciation_rate = land_appreciation / total_investment
            
            # 四级超率累进税率
            land_vat = 0
            remaining_appreciation = land_appreciation
            prev_rate = 0
            
            for threshold, rate in self.LAND_VAT_RATES:
                if appreciation_rate > prev_rate:
                    tier_amount = min(remaining_appreciation, 
                                    total_investment * (threshold - prev_rate))
                    land_vat += tier_amount * rate
                    remaining_appreciation -= tier_amount
                    prev_rate = threshold
                else:
                    break
        else:
            land_vat = 0
        
        # 企业所得税
        # 资产转让所得 = 转让收入 - 账面净值
        net_book_value = total_investment - accumulated_depreciation
        capital_gain = exit_revenue - net_book_value
        exit_income_tax = max(0, capital_gain * 0.25)
        
        # 印花税
        exit_stamp = exit_revenue * self.STAMP_TAX_PURCHASE
        
        return {
            'exit_vat': exit_vat,
            'land_value_added_tax': land_vat,
            'capital_gain': capital_gain,
            'exit_income_tax': exit_income_tax,
            'exit_stamp_tax': exit_stamp,
            'total_exit_tax': exit_vat + land_vat + exit_income_tax + exit_stamp,
        }
    
    def calculate_project_tax(self,
                             # 投资阶段
                             land_cost: float,
                             construction_cost: float,
                             equipment_cost: float,
                             # 运营阶段
                             annual_revenue: float,
                             annual_cost: float,
                             annual_expenses: float,
                             operation_years: int,
                             # 退出阶段
                             exit_revenue: float,
                             accumulated_depreciation: float = 0) -> InvestmentTaxResult:
        """
        计算项目全周期税费
        """
        # 投资阶段
        acquisition = self.calculate_acquisition_tax(land_cost)
        construction = self.calculate_construction_tax(construction_cost, equipment_cost)
        
        total_investment_tax = (acquisition['total_acquisition_tax'] + 
                               construction['total_stamp_tax'])
        
        # 运营阶段（多年）
        operation_year_1 = self.calculate_operation_tax(
            annual_revenue, annual_cost, annual_expenses,
            input_vat_credit=construction['total_input_vat']  # 第一年抵扣建设进项
        )
        
        # 简化：假设后续年份增值税无留抵
        operation_subsequent = self.calculate_operation_tax(
            annual_revenue, annual_cost, annual_expenses
        )
        
        total_operation_tax = (operation_year_1['total_operation_tax'] + 
                              operation_subsequent['total_operation_tax'] * (operation_years - 1))
        
        # 退出阶段
        total_investment_cost = land_cost + construction_cost + equipment_cost
        exit_phase = self.calculate_exit_tax(
            exit_revenue, total_investment_cost, accumulated_depreciation
        )
        
        # 合计
        total_project_tax = total_investment_tax + total_operation_tax + exit_phase['total_exit_tax']
        
        # 实际综合税率
        total_revenue = annual_revenue * operation_years + exit_revenue
        effective_tax_rate = total_project_tax / total_revenue if total_revenue > 0 else 0
        
        return InvestmentTaxResult(
            deed_tax=acquisition['deed_tax'],
            stamp_tax_purchase=acquisition['stamp_tax'],
            land_value_added_tax=0,  # 购置阶段不产生
            construction_vat=construction['construction_vat'],
            equipment_vat=construction['equipment_vat'],
            annual_vat=operation_subsequent['net_vat'],
            annual_income_tax=operation_subsequent['income_tax'],
            annual_surcharge=operation_subsequent['surcharge'],
            exit_vat=exit_phase['exit_vat'],
            exit_land_vat=exit_phase['land_value_added_tax'],
            exit_income_tax=exit_phase['exit_income_tax'],
            total_investment_tax=total_investment_tax,
            total_operation_tax=total_operation_tax,
            total_exit_tax=exit_phase['total_exit_tax'],
            total_project_tax=total_project_tax,
            tax_impact_on_irr=0,  # 需结合现金流计算
            effective_tax_rate=effective_tax_rate,
        )

def format_project_tax_report(result: InvestmentTaxResult, 
                              project_name: str = "项目",
                              operation_years: int = 10) -> str:
    """格式化项目投资税务报告"""
    lines = [
        f"\n{'='*70}",
        f"🏗️ 项目投资税务分析报告 - {project_name}",
        f"{'='*70}",
        f"",
        f"【一、投资阶段税费】",
        f"  契税: ¥{result.deed_tax:,.2f}",
        f"  购置印花税: ¥{result.stamp_tax_purchase:,.2f}",
        f"  小计: ¥{result.total_investment_tax:,.2f}",
        f"",
        f"【二、建设阶段进项税】",
        f"  建筑服务进项税: ¥{result.construction_vat:,.2f}",
        f"  设备进项税: ¥{result.equipment_vat:,.2f}",
        f"  （可用于抵扣运营期增值税）",
        f"",
        f"【三、运营阶段税费】（年均）",
        f"  年增值税: ¥{result.annual_vat:,.2f}",
        f"  年附加税费: ¥{result.annual_surcharge:,.2f}",
        f"  年企业所得税: ¥{result.annual_income_tax:,.2f}",
        f"  运营期合计({operation_years}年): ¥{result.total_operation_tax:,.2f}",
        f"",
        f"【四、退出阶段税费】",
        f"  资产转让增值税: ¥{result.exit_vat:,.2f}",
        f"  土地增值税: ¥{result.exit_land_vat:,.2f}",
        f"  退出所得税: ¥{result.exit_income_tax:,.2f}",
        f"  小计: ¥{result.total_exit_tax:,.2f}",
        f"",
        f"{'='*70}",
        f"【税费汇总】",
        f"  投资阶段: ¥{result.total_investment_tax:,.2f}",
        f"  运营阶段: ¥{result.total_operation_tax:,.2f}",
        f"  退出阶段: ¥{result.total_exit_tax:,.2f}",
        f"  全周期税费合计: ¥{result.total_project_tax:,.2f}",
        f"",
        f"  实际综合税率: {result.effective_tax_rate*100:.2f}%",
        f"{'='*70}",
    ]
    
    return "\n".join(lines)

# 储能项目示例
def storage_project_example():
    """储能电站项目示例"""
    calc = ProjectInvestmentTaxCalculator(
        project_type='工业',
        location='市区',
        enterprise_type='高新技术企业'  # 很多储能企业可申请高新
    )
    
    result = calc.calculate_project_tax(
        # 投资阶段
        land_cost=5000000,           # 土地500万
        construction_cost=15000000,  # 建设1500万
        equipment_cost=30000000,     # 设备3000万
        # 运营阶段
        annual_revenue=8000000,      # 年营收800万
        annual_cost=3000000,         # 年成本300万
        annual_expenses=1000000,     # 年费用100万
        operation_years=15,          # 运营15年
        # 退出阶段
        exit_revenue=20000000,       # 退出残值2000万
        accumulated_depreciation=40000000,  # 累计折旧
    )
    
    print(format_project_tax_report(result, "100MWh储能电站项目", 15))
    
    return result

if __name__ == "__main__":
    storage_project_example()
