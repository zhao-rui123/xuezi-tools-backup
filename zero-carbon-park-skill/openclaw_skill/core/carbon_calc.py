"""
碳排放核算模块
============
涵盖企业碳排放核算、产品碳足迹、碳减排量计算
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class EmissionData:
    """排放数据类"""
    scope1: float = 0  # 范围1直接排放 (tCO2e)
    scope2: float = 0  # 范围2间接排放 (tCO2e)
    scope3: float = 0  # 范围3其他间接排放 (tCO2e)


class CarbonCalculator:
    """碳排放计算器"""
    
    # 排放因子库 (tCO2/单位)
    EMISSION_FACTORS = {
        # 化石燃料
        'raw_coal': 1.9003,  # tCO2/t
        'washed_coal': 2.4368,
        'coke': 2.8604,
        'crude_oil': 3.0202,
        'gasoline': 3.1505,
        'diesel': 3.1605,
        'kerosene': 3.1605,
        'fuel_oil': 3.2366,
        'lpg': 3.1663,
        'natural_gas': 2.1622,  # tCO2/1000m³
        'lng': 2.1622,
        'cng': 2.1622,
        
        # 电力
        'grid_electricity': 0.5703,  # tCO2/MWh (全国电网平均)
        'grid_electricity_north': 0.5871,  # 华北
        'grid_electricity_northeast': 0.5987,  # 东北
        'grid_electricity_east': 0.5257,  # 华东
        'grid_electricity_central': 0.5253,  # 华中
        'grid_electricity_northwest': 0.4925,  # 西北
        'grid_electricity_south': 0.4097,  # 南方
        'self_generation_coal': 0.8536,
        'self_generation_gas': 0.3798,
        
        # 热力
        'steam_coal': 0.11,  # tCO2/GJ
        'steam_gas': 0.06,
        'steam_biomass': 0.02,
        'hot_water': 0.08,
        
        # 工业过程
        'cement_clinker': 0.538,  # tCO2/t熟料
        'lime': 0.683,  # tCO2/t石灰
        'steel': 1.72,  # tCO2/t粗钢
        'ammonia': 2.1,  # tCO2/t合成氨
        'ethylene': 1.8,  # tCO2/t乙烯
        'aluminum': 12.8,  # tCO2/t原铝
        'soda_ash': 0.415,  # tCO2/t纯碱
    }
    
    # 行业碳排放强度基准 (tCO2/万元产值)
    INDUSTRY_BENCHMARKS = {
        'chemical': 8.5,
        'steel': 12.3,
        'cement': 15.2,
        'nonferrous_metal': 6.8,
        'paper': 4.5,
        'textile': 2.8,
        'food_processing': 1.5,
        'pharmaceutical': 3.2,
        'electronics': 0.8,
        'automotive': 1.2,
        'data_center': 25.0,
        'petroleum': 18.5,
    }
    
    def __init__(self, region: str = 'national'):
        """
        初始化
        
        Args:
            region: 电网区域 (national/north/northeast/east/central/northwest/south)
        """
        self.region = region
        self.emission_data = EmissionData()
    
    def get_electricity_factor(self) -> float:
        """获取电网排放因子"""
        factor_map = {
            'national': 'grid_electricity',
            'north': 'grid_electricity_north',
            'northeast': 'grid_electricity_northeast',
            'east': 'grid_electricity_east',
            'central': 'grid_electricity_central',
            'northwest': 'grid_electricity_northwest',
            'south': 'grid_electricity_south',
        }
        key = factor_map.get(self.region, 'grid_electricity')
        return self.EMISSION_FACTORS[key]
    
    # ==================== 范围1: 直接排放 ====================
    
    def calculate_stationary_combustion(
        self,
        fuel_consumption: Dict[str, float]
    ) -> Dict[str, float]:
        """
        固定燃烧排放计算
        
        Args:
            fuel_consumption: 燃料消耗量字典 {燃料类型: 数量, ...}
                单位: 固体液体燃料-t, 气体燃料-1000m³
        
        Returns:
            排放计算结果
        """
        total_emission = 0
        details = {}
        
        for fuel_type, amount in fuel_consumption.items():
            factor = self.EMISSION_FACTORS.get(fuel_type, 0)
            emission = amount * factor
            total_emission += emission
            details[fuel_type] = {
                'consumption': amount,
                'factor': factor,
                'emission_tco2': round(emission, 2)
            }
        
        self.emission_data.scope1 += total_emission
        
        return {
            'total_emission_tco2': round(total_emission, 2),
            'details': details
        }
    
    def calculate_mobile_combustion(
        self,
        vehicle_fuel: Dict[str, float]
    ) -> Dict[str, float]:
        """
        移动源排放计算 (厂内车辆)
        """
        total_emission = 0
        details = {}
        
        for fuel_type, amount in vehicle_fuel.items():
            factor = self.EMISSION_FACTORS.get(fuel_type, 0)
            emission = amount * factor
            total_emission += emission
            details[fuel_type] = round(emission, 2)
        
        self.emission_data.scope1 += total_emission
        
        return {
            'total_emission_tco2': round(total_emission, 2),
            'details': details
        }
    
    def calculate_process_emissions(
        self,
        process_data: Dict[str, Tuple[float, float]]
    ) -> Dict[str, float]:
        """
        工业过程排放计算
        
        Args:
            process_data: {过程类型: (产量, 排放因子), ...}
        
        Returns:
            排放计算结果
        """
        total_emission = 0
        details = {}
        
        for process, (output, factor) in process_data.items():
            emission = output * factor
            total_emission += emission
            details[process] = {
                'output': output,
                'factor': factor,
                'emission_tco2': round(emission, 2)
            }
        
        self.emission_data.scope1 += total_emission
        
        return {
            'total_emission_tco2': round(total_emission, 2),
            'details': details
        }
    
    # ==================== 范围2: 间接排放 ====================
    
    def calculate_purchased_electricity(
        self,
        electricity_mwh: float,
        green_electricity_mwh: float = 0
    ) -> Dict[str, float]:
        """
        外购电力排放计算
        
        Args:
            electricity_mwh: 外购电量 (MWh)
            green_electricity_mwh: 绿电量 (MWh)
        """
        factor = self.get_electricity_factor()
        
        # 扣除绿电后的电网电量
        grid_electricity = electricity_mwh - green_electricity_mwh
        
        emission = grid_electricity * factor
        
        self.emission_data.scope2 += emission
        
        return {
            'total_electricity_mwh': electricity_mwh,
            'green_electricity_mwh': green_electricity_mwh,
            'grid_electricity_mwh': grid_electricity,
            'emission_factor': factor,
            'emission_tco2': round(emission, 2),
            'green_reduction_tco2': round(green_electricity_mwh * factor, 2)
        }
    
    def calculate_purchased_heat(
        self,
        heat_gj: float,
        heat_source: str = 'steam_coal'
    ) -> Dict[str, float]:
        """
        外购热力排放计算
        """
        factor = self.EMISSION_FACTORS.get(heat_source, 0.11)
        emission = heat_gj * factor
        
        self.emission_data.scope2 += emission
        
        return {
            'heat_gj': heat_gj,
            'emission_factor': factor,
            'emission_tco2': round(emission, 2)
        }
    
    # ==================== 范围3: 其他间接排放 ====================
    
    def calculate_upstream_emissions(
        self,
        purchased_goods: Dict[str, float],
        transport_data: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        上游排放计算 (简化版)
        
        Args:
            purchased_goods: {物料类型: 采购量, ...}
            transport_data: 运输相关数据
        """
        # 简化计算 - 使用平均排放因子
        avg_factors = {
            'raw_materials': 0.5,  # tCO2/t
            'packaging': 1.2,
            'auxiliary': 0.3,
        }
        
        total_emission = 0
        details = {}
        
        for material, amount in purchased_goods.items():
            factor = avg_factors.get(material, 0.5)
            emission = amount * factor
            total_emission += emission
            details[material] = round(emission, 2)
        
        self.emission_data.scope3 += total_emission
        
        return {
            'total_emission_tco2': round(total_emission, 2),
            'details': details
        }
    
    # ==================== 综合核算 ====================
    
    def calculate_total_emissions(self) -> Dict[str, float]:
        """
        计算总排放量
        """
        total = (self.emission_data.scope1 + 
                self.emission_data.scope2 + 
                self.emission_data.scope3)
        
        return {
            'scope1_direct_tco2': round(self.emission_data.scope1, 2),
            'scope2_indirect_tco2': round(self.emission_data.scope2, 2),
            'scope3_other_tco2': round(self.emission_data.scope3, 2),
            'total_emissions_tco2': round(total, 2),
            'scope1_percent': round(self.emission_data.scope1 / total * 100, 1) if total > 0 else 0,
            'scope2_percent': round(self.emission_data.scope2 / total * 100, 1) if total > 0 else 0,
            'scope3_percent': round(self.emission_data.scope3 / total * 100, 1) if total > 0 else 0,
        }
    
    def calculate_intensity_indicators(
        self,
        output_value: float = None,  # 万元
        production: float = None,  # 吨产品
        area: float = None,  # m²
        employee: int = None
    ) -> Dict[str, float]:
        """
        计算碳排放强度指标
        """
        total = self.calculate_total_emissions()['total_emissions_tco2']
        
        indicators = {}
        
        if output_value:
            indicators['carbon_per_output'] = round(total / output_value, 2)  # tCO2/万元
        if production:
            indicators['carbon_per_product'] = round(total / production, 2)  # tCO2/t
        if area:
            indicators['carbon_per_area'] = round(total / area * 10000, 2)  # tCO2/万m²
        if employee:
            indicators['carbon_per_employee'] = round(total / employee, 2)  # tCO2/人
        
        return indicators
    
    # ==================== 碳减排计算 ====================
    
    def calculate_reduction_measures(
        self,
        measures: List[Dict]
    ) -> Dict[str, any]:
        """
        计算减排措施效果
        
        Args:
            measures: 减排措施列表
                [
                    {
                        'name': '措施名称',
                        'type': 'energy_efficiency/renewable/ccus/fuel_switch',
                        'reduction_tco2': 100,
                        'investment': 500000,  # 元
                        'annual_benefit': 80000,  # 元/年
                    },
                    ...
                ]
        
        Returns:
            减排效果汇总
        """
        total_reduction = sum(m['reduction_tco2'] for m in measures)
        total_investment = sum(m['investment'] for m in measures)
        total_benefit = sum(m['annual_benefit'] for m in measures)
        
        # 按类型分类
        by_type = {}
        for m in measures:
            t = m['type']
            if t not in by_type:
                by_type[t] = {'count': 0, 'reduction': 0, 'investment': 0}
            by_type[t]['count'] += 1
            by_type[t]['reduction'] += m['reduction_tco2']
            by_type[t]['investment'] += m['investment']
        
        # 计算投资回收期
        payback = total_investment / total_benefit if total_benefit > 0 else float('inf')
        
        # 单位减排成本
        abatement_cost = total_investment / total_reduction if total_reduction > 0 else 0
        
        return {
            'total_reduction_tco2': round(total_reduction, 2),
            'total_investment_yuan': round(total_investment, 0),
            'total_annual_benefit_yuan': round(total_benefit, 0),
            'payback_period_years': round(payback, 1),
            'abatement_cost_yuan_per_tco2': round(abatement_cost, 0),
            'by_type': by_type,
            'measures': measures
        }
    
    def calculate_carbon_neutral_pathway(
        self,
        base_year_emission: float,
        target_year: int,
        base_year: int = 2024,
        reduction_targets: Dict[int, float] = None
    ) -> Dict[str, any]:
        """
        碳中和路径规划
        
        Args:
            base_year_emission: 基准年排放量 (tCO2)
            target_year: 目标年份
            base_year: 基准年份
            reduction_targets: 阶段性减排目标 {年份: 减排比例}
        """
        if reduction_targets is None:
            # 默认路径: 2030年减25%, 2040年减60%, 2060年碳中和
            reduction_targets = {
                2030: 0.25,
                2035: 0.40,
                2040: 0.60,
                2050: 0.85,
                target_year: 1.0
            }
        
        pathway = []
        for year, ratio in sorted(reduction_targets.items()):
            if year <= target_year:
                pathway.append({
                    'year': year,
                    'target_reduction_percent': ratio * 100,
                    'target_emission_tco2': round(base_year_emission * (1 - ratio), 2),
                    'cumulative_reduction_tco2': round(base_year_emission * ratio, 2)
                })
        
        # 年均减排率
        years = target_year - base_year
        annual_rate = (1 - 1.0) ** (1/years) - 1  # 到0的等比递减
        
        return {
            'base_year': base_year,
            'base_emission_tco2': base_year_emission,
            'target_year': target_year,
            'pathway': pathway,
            'required_annual_reduction_rate': round(abs(annual_rate) * 100, 2),
        }
    
    # ==================== 碳足迹计算 ====================
    
    def calculate_product_carbon_footprint(
        self,
        product_name: str,
        annual_production: float,  # 年产量
        total_emission: float,  # 总排放
        allocation_method: str = 'mass'  # mass/economic/energy
    ) -> Dict[str, float]:
        """
        产品碳足迹计算
        """
        # 简化计算 - 假设全部排放分配给该产品
        pcf = total_emission / annual_production
        
        return {
            'product_name': product_name,
            'annual_production_t': annual_production,
            'total_emission_tco2': total_emission,
            'pcf_kgco2_per_kg': round(pcf, 2),
            'pcf_tco2_per_t': round(pcf, 2),
        }
    
    def compare_with_benchmark(
        self,
        industry: str,
        actual_emission: float,
        output_value: float = None
    ) -> Dict[str, any]:
        """
        与行业基准对比
        """
        benchmark = self.INDUSTRY_BENCHMARKS.get(industry, 5.0)
        
        if output_value:
            actual_intensity = actual_emission / output_value
            comparison = actual_intensity / benchmark
            
            return {
                'industry': industry,
                'benchmark_tco2_per_10kyuan': benchmark,
                'actual_intensity_tco2_per_10kyuan': round(actual_intensity, 2),
                'comparison_ratio': round(comparison, 2),
                'status': '领先' if comparison < 0.8 else ('达标' if comparison <= 1.2 else '落后'),
                'improvement_potential_percent': round(max(0, (comparison - 0.8) / comparison * 100), 1) if comparison > 0.8 else 0
            }
        
        return {'benchmark': benchmark}
