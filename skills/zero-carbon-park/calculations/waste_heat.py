"""
余热余冷计算模块
==============
包含余热资源评估、回收系统设计、产品选型
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class HeatSource:
    """热源数据类"""
    name: str
    temp_in: float  # 入口温度 °C
    temp_out: float  # 出口温度 °C
    flow_rate: float  # 流量 (kg/h 或 m³/h)
    medium: str  # 介质类型
    operating_hours: float = 8000  # 年运行小时


class WasteHeatCalculator:
    """余热余冷计算器"""
    
    # 介质比热容 (kJ/kg·K)
    SPECIFIC_HEAT = {
        'water': 4.18,
        'steam': 2.1,
        'air': 1.005,
        'flue_gas': 1.1,
        'oil': 2.0,
        'organic_heat_transfer': 2.5,
    }
    
    # 介质密度 (kg/m³)
    DENSITY = {
        'water': 1000,
        'air': 1.2,
        'flue_gas': 1.0,
        'steam': 0.6,
    }
    
    # 余热回收设备参数
    RECOVERY_EQUIPMENT = {
        'waste_heat_boiler': {
            'name': '余热锅炉',
            'temp_range': '300-1000°C',
            'efficiency': 0.60,
            'application': '高温烟气',
            'cost_per_kw': 800,
        },
        'thermal_oil_heater': {
            'name': '导热油余热锅炉',
            'temp_range': '200-500°C',
            'efficiency': 0.55,
            'application': '中温烟气',
            'cost_per_kw': 1000,
        },
        'air_preheater': {
            'name': '空气预热器',
            'temp_range': '150-400°C',
            'efficiency': 0.50,
            'application': '预热燃烧空气',
            'cost_per_kw': 400,
        },
        'economizer': {
            'name': '省煤器',
            'temp_range': '100-300°C',
            'efficiency': 0.55,
            'application': '预热锅炉给水',
            'cost_per_kw': 500,
        },
        'orc_unit': {
            'name': 'ORC发电机组',
            'temp_range': '80-300°C',
            'efficiency': 0.12,
            'application': '中低温余热发电',
            'cost_per_kw': 3000,
        },
        'heat_pump': {
            'name': '余热驱动热泵',
            'temp_range': '30-100°C',
            'cop': 3.5,
            'application': '低温余热提升',
            'cost_per_kw': 1500,
        },
        'run_around_coil': {
            'name': '中间媒质式换热器',
            'temp_range': '40-150°C',
            'efficiency': 0.45,
            'application': '腐蚀性烟气',
            'cost_per_kw': 600,
        },
    }
    
    def __init__(self):
        pass
    
    # ==================== 余热资源计算 ====================
    
    def calculate_waste_heat_potential(
        self,
        source: HeatSource
    ) -> Dict[str, float]:
        """
        计算余热资源量
        
        Args:
            source: 热源数据
        
        Returns:
            余热潜力计算结果
        """
        # 温度降
        delta_t = source.temp_in - source.temp_out
        
        # 比热容
        cp = self.SPECIFIC_HEAT.get(source.medium, 1.0)
        
        # 密度
        density = self.DENSITY.get(source.medium, 1.0)
        
        # 质量流量 (kg/h)
        if source.medium in ['water', 'oil', 'organic_heat_transfer']:
            mass_flow = source.flow_rate * density
        else:
            mass_flow = source.flow_rate * density
        
        # 余热功率 (kW)
        heat_power = mass_flow * cp * delta_t / 3600
        
        # 年余热量 (GJ)
        annual_heat = heat_power * source.operating_hours * 0.0036
        
        # 可回收热量 (假设回收效率60%)
        recoverable_efficiency = 0.60
        recoverable_power = heat_power * recoverable_efficiency
        recoverable_annual = annual_heat * recoverable_efficiency
        
        return {
            'source_name': source.name,
            'temp_in_c': source.temp_in,
            'temp_out_c': source.temp_out,
            'delta_t_c': delta_t,
            'flow_rate': source.flow_rate,
            'mass_flow_kg_h': round(mass_flow, 0),
            'heat_power_kw': round(heat_power, 2),
            'annual_heat_gj': round(annual_heat, 2),
            'recoverable_power_kw': round(recoverable_power, 2),
            'recoverable_annual_gj': round(recoverable_annual, 2),
            'operating_hours': source.operating_hours,
        }
    
    def analyze_multiple_sources(
        self,
        sources: List[HeatSource]
    ) -> Dict[str, any]:
        """
        分析多个余热源
        
        Args:
            sources: 热源列表
        
        Returns:
            综合分析结果
        """
        results = []
        total_power = 0
        total_annual = 0
        
        for source in sources:
            result = self.calculate_waste_heat_potential(source)
            results.append(result)
            total_power += result['recoverable_power_kw']
            total_annual += result['recoverable_annual_gj']
        
        # 按温度分级
        high_temp = [r for r in results if r['temp_in_c'] >= 300]
        medium_temp = [r for r in results if 150 <= r['temp_in_c'] < 300]
        low_temp = [r for r in results if r['temp_in_c'] < 150]
        
        return {
            'sources': results,
            'total_recoverable_power_kw': round(total_power, 2),
            'total_recoverable_annual_gj': round(total_annual, 2),
            'by_temperature': {
                'high_temp_300c_plus': {
                    'count': len(high_temp),
                    'total_power_kw': round(sum(r['recoverable_power_kw'] for r in high_temp), 2),
                },
                'medium_temp_150_300c': {
                    'count': len(medium_temp),
                    'total_power_kw': round(sum(r['recoverable_power_kw'] for r in medium_temp), 2),
                },
                'low_temp_below_150c': {
                    'count': len(low_temp),
                    'total_power_kw': round(sum(r['recoverable_power_kw'] for r in low_temp), 2),
                },
            },
        }
    
    # ==================== 余热回收系统设计 ====================
    
    def design_recovery_system(
        self,
        source_temp: float,
        source_power: float,
        application: str = 'power_generation',  # power_generation/steam/heating/cooling
        sink_temp: float = 25
    ) -> Dict[str, any]:
        """
        设计余热回收系统
        
        Args:
            source_temp: 热源温度 (°C)
            source_power: 热源功率 (kW)
            application: 应用场景
            sink_temp: 环境温度 (°C)
        
        Returns:
            回收系统设计方案
        """
        # 选择合适的回收技术
        if source_temp >= 300:
            if application == 'power_generation':
                technology = 'waste_heat_boiler'
                additional_equipment = 'steam_turbine'
            else:
                technology = 'waste_heat_boiler'
                additional_equipment = None
        elif source_temp >= 150:
            if application == 'power_generation':
                technology = 'orc_unit'
                additional_equipment = None
            else:
                technology = 'thermal_oil_heater'
                additional_equipment = None
        elif source_temp >= 80:
            technology = 'heat_pump'
            additional_equipment = None
        else:
            technology = 'run_around_coil'
            additional_equipment = None
        
        equip_info = self.RECOVERY_EQUIPMENT[technology]
        
        # 计算回收效率
        efficiency = equip_info.get('efficiency', 0.5)
        if application == 'power_generation' and technology == 'orc_unit':
            # ORC发电效率
            power_output = source_power * efficiency
            thermal_output = 0
        elif application == 'power_generation' and technology == 'waste_heat_boiler':
            # 余热锅炉+汽轮机
            steam_efficiency = 0.25  # 汽轮机效率
            power_output = source_power * efficiency * steam_efficiency
            thermal_output = source_power * efficiency * (1 - steam_efficiency)
        else:
            power_output = 0
            thermal_output = source_power * efficiency
        
        # 投资估算
        investment = source_power * equip_info['cost_per_kw']
        
        # 年收益
        operating_hours = 8000
        if power_output > 0:
            annual_benefit = power_output * operating_hours * 0.8  # 电价0.8元
        else:
            annual_benefit = thermal_output * operating_hours * 0.1  # 热能0.1元/kWh
        
        # 投资回收期
        payback = investment / annual_benefit if annual_benefit > 0 else float('inf')
        
        return {
            'source_temp_c': source_temp,
            'source_power_kw': source_power,
            'application': application,
            'recommended_technology': technology,
            'technology_name': equip_info['name'],
            'efficiency': round(efficiency * 100, 1),
            'power_output_kw': round(power_output, 2),
            'thermal_output_kw': round(thermal_output, 2),
            'investment_yuan': round(investment, 0),
            'annual_benefit_yuan': round(annual_benefit, 0),
            'payback_period_years': round(payback, 1),
            'additional_equipment': additional_equipment,
        }
    
    def select_equipment(
        self,
        heat_source: HeatSource,
        requirements: Dict[str, any]
    ) -> List[Dict[str, any]]:
        """
        余热回收设备选型
        
        Args:
            heat_source: 热源信息
            requirements: 需求参数
        
        Returns:
            设备选型建议列表
        """
        temp = heat_source.temp_in
        power = self.calculate_waste_heat_potential(heat_source)['recoverable_power_kw']
        
        recommendations = []
        
        # 根据温度筛选适用技术
        for tech_code, tech_info in self.RECOVERY_EQUIPMENT.items():
            temp_range = tech_info['temp_range']
            min_temp = float(temp_range.split('-')[0].replace('°C', '').replace('<', ''))
            max_temp = float(temp_range.split('-')[1].replace('°C', '').replace('>', ''))
            
            if min_temp <= temp <= max_temp or (temp >= min_temp and '>' in temp_range):
                # 计算适用性评分
                score = 100
                
                # 温度匹配度
                temp_match = 1 - abs(temp - (min_temp + max_temp) / 2) / (max_temp - min_temp)
                score *= temp_match
                
                # 功率适用性
                if power < 100:
                    score *= 0.8
                elif power > 1000:
                    score *= 0.9
                
                # 投资估算
                investment = power * tech_info['cost_per_kw']
                
                recommendations.append({
                    'technology_code': tech_code,
                    'technology_name': tech_info['name'],
                    'applicable_temp_range': temp_range,
                    'efficiency': tech_info.get('efficiency', tech_info.get('cop', 0)),
                    'application': tech_info['application'],
                    'investment_yuan': round(investment, 0),
                    'suitability_score': round(score, 1),
                })
        
        # 按适用性评分排序
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return recommendations
    
    # ==================== 换热器设计 ====================
    
    def design_heat_exchanger(
        self,
        hot_stream: Dict[str, float],
        cold_stream: Dict[str, float],
        exchanger_type: str = 'shell_and_tube'
    ) -> Dict[str, any]:
        """
        设计换热器
        
        Args:
            hot_stream: 热流体参数 {temp_in, temp_out, flow_rate, cp, medium}
            cold_stream: 冷流体参数 {temp_in, temp_out, flow_rate, cp, medium}
            exchanger_type: 换热器类型
        
        Returns:
            换热器设计参数
        """
        # 热负荷
        q_hot = hot_stream['flow_rate'] * hot_stream['cp'] * \
                (hot_stream['temp_in'] - hot_stream['temp_out'])
        q_cold = cold_stream['flow_rate'] * cold_stream['cp'] * \
                 (cold_stream['temp_out'] - cold_stream['temp_in'])
        
        # 取较小值作为设计负荷
        q_design = min(q_hot, q_cold)  # kW
        
        # 对数平均温差
        dt1 = hot_stream['temp_in'] - cold_stream['temp_out']
        dt2 = hot_stream['temp_out'] - cold_stream['temp_in']
        
        if dt1 == dt2:
            lmtd = dt1
        else:
            lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
        
        # 总传热系数 (W/m²·K)
        u_values = {
            'shell_and_tube': 300,
            'plate': 400,
            'finned_tube': 50,
        }
        u = u_values.get(exchanger_type, 300)
        
        # 换热面积
        area = q_design * 1000 / (u * lmtd)  # m²
        
        # 投资估算 (元/m²)
        cost_per_m2 = {
            'shell_and_tube': 800,
            'plate': 600,
            'finned_tube': 1000,
        }.get(exchanger_type, 800)
        
        investment = area * cost_per_m2
        
        return {
            'heat_duty_kw': round(q_design, 2),
            'lmtd_k': round(lmtd, 2),
            'overall_u_w_m2_k': u,
            'heat_transfer_area_m2': round(area, 2),
            'exchanger_type': exchanger_type,
            'investment_yuan': round(investment, 0),
            'hot_stream': hot_stream,
            'cold_stream': cold_stream,
        }
    
    # ==================== 余冷计算 ====================
    
    def calculate_waste_cold_potential(
        self,
        cold_source_temp: float,  # 冷源温度 (°C)
        ambient_temp: float,  # 环境温度 (°C)
        cooling_capacity: float,  # 制冷量 (kW)
        cop: float = 3.0  # 制冷系数
    ) -> Dict[str, float]:
        """
        计算余冷资源潜力
        
        Args:
            cold_source_temp: 冷源温度
            ambient_temp: 环境温度
            cooling_capacity: 制冷量
            cop: 制冷系数
        
        Returns:
            余冷潜力分析
        """
        # 余冷功率 (可提供的冷量)
        waste_cold_power = cooling_capacity
        
        # 对应的热量排放
        heat_rejection = cooling_capacity * (1 + 1/cop)
        
        # 年余冷量
        operating_hours = 4000  # 制冷季
        annual_cold = waste_cold_power * operating_hours * 0.0036  # GJ
        
        # 可利用场景
        applications = []
        if cold_source_temp < 10:
            applications.append('空调预冷')
            applications.append('工艺冷却')
        if cold_source_temp < 5:
            applications.append('冷藏冷冻')
        if cold_source_temp < 0:
            applications.append('制冰')
        
        # 节能潜力
        electricity_saving = waste_cold_power / cop * operating_hours
        cost_saving = electricity_saving * 0.8
        
        return {
            'cold_source_temp_c': cold_source_temp,
            'ambient_temp_c': ambient_temp,
            'waste_cold_power_kw': waste_cold_power,
            'heat_rejection_kw': round(heat_rejection, 2),
            'annual_cold_gj': round(annual_cold, 2),
            'applications': applications,
            'electricity_saving_kwh': round(electricity_saving, 0),
            'cost_saving_yuan': round(cost_saving, 0),
        }
    
    def design_cold_recovery_system(
        self,
        cold_source_temp: float,
        cold_power: float,
        target_application: str = 'space_cooling'
    ) -> Dict[str, any]:
        """
        设计余冷回收系统
        """
        # 余冷利用技术
        if target_application == 'space_cooling':
            technology = '吸收式制冷'
            efficiency = 0.7
        elif target_application == 'process_cooling':
            technology = '换热器直接换热'
            efficiency = 0.8
        else:
            technology = '热泵提升'
            efficiency = 0.6
        
        # 可回收冷量
        recovered_cold = cold_power * efficiency
        
        # 投资估算
        investment = cold_power * 1000  # 元/kW
        
        # 年收益
        operating_hours = 4000
        electricity_saved = recovered_cold / 3 * operating_hours  # 假设替代电制冷COP=3
        annual_benefit = electricity_saved * 0.8
        
        return {
            'cold_source_temp_c': cold_source_temp,
            'cold_power_kw': cold_power,
            'target_application': target_application,
            'technology': technology,
            'efficiency': efficiency,
            'recovered_cold_kw': round(recovered_cold, 2),
            'investment_yuan': round(investment, 0),
            'annual_electricity_saved_kwh': round(electricity_saved, 0),
            'annual_benefit_yuan': round(annual_benefit, 0),
        }
    
    # ==================== 综合优化 ====================
    
    def optimize_heat_recovery_network(
        self,
        heat_sources: List[HeatSource],
        heat_demands: List[Dict[str, float]]
    ) -> Dict[str, any]:
        """
        优化余热回收网络 (夹点分析简化版)
        
        Args:
            heat_sources: 热源列表
            heat_demands: 热需求列表 [{temp_required, heat_demand}, ...]
        
        Returns:
            优化方案
        """
        # 计算总余热资源
        total_source_power = 0
        for source in heat_sources:
            result = self.calculate_waste_heat_potential(source)
            total_source_power += result['recoverable_power_kw']
        
        # 计算总热需求
        total_demand = sum(d['heat_demand'] for d in heat_demands)
        
        # 匹配分析
        matches = []
        remaining_sources = heat_sources.copy()
        
        for demand in heat_demands:
            for source in remaining_sources[:]:
                if source.temp_in >= demand['temp_required'] + 20:  # 最小温差20°C
                    result = self.calculate_waste_heat_potential(source)
                    matches.append({
                        'source': source.name,
                        'demand_temp': demand['temp_required'],
                        'matched_power': result['recoverable_power_kw'],
                    })
                    remaining_sources.remove(source)
                    break
        
        # 外部加热需求
        external_heat = max(0, total_demand - total_source_power)
        
        return {
            'total_source_power_kw': round(total_source_power, 2),
            'total_demand_kw': round(total_demand, 2),
            'matched_pairs': matches,
            'external_heat_required_kw': round(external_heat, 2),
            'self_sufficiency_rate': round(total_source_power / total_demand * 100, 1) if total_demand > 0 else 0,
        }
