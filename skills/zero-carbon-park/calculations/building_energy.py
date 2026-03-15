"""
建筑节能计算模块
==============
包含工业建筑节能、围护结构热工、空调系统优化
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class BuildingEnvelope:
    """建筑围护结构参数"""
    wall_area: float  # m²
    roof_area: float  # m²
    window_area: float  # m²
    floor_area: float  # m²
    wall_u: float = 0.5  # W/m²·K
    roof_u: float = 0.4  # W/m²·K
    window_u: float = 2.5  # W/m²·K
    floor_u: float = 0.6  # W/m²·K


class BuildingEnergyCalculator:
    """建筑节能计算器"""
    
    # 气候分区参数
    CLIMATE_ZONES = {
        'severe_cold': {
            'name': '严寒地区',
            'heating_degree_days': 4000,
            'cooling_degree_days': 100,
            'design_temp_heating': -20,
            'design_temp_cooling': 30,
        },
        'cold': {
            'name': '寒冷地区',
            'heating_degree_days': 2500,
            'cooling_degree_days': 200,
            'design_temp_heating': -10,
            'design_temp_cooling': 32,
        },
        'hot_summer_cold_winter': {
            'name': '夏热冬冷地区',
            'heating_degree_days': 1500,
            'cooling_degree_days': 1200,
            'design_temp_heating': -2,
            'design_temp_cooling': 35,
        },
        'hot_summer_warm_winter': {
            'name': '夏热冬暖地区',
            'heating_degree_days': 300,
            'cooling_degree_days': 2000,
            'design_temp_heating': 8,
            'design_temp_cooling': 34,
        },
        'mild': {
            'name': '温和地区',
            'heating_degree_days': 800,
            'cooling_degree_days': 300,
            'design_temp_heating': 2,
            'design_temp_cooling': 28,
        },
    }
    
    # 节能标准
    ENERGY_STANDARDS = {
        'industrial_2015': {
            'wall_u_max': 0.60,
            'roof_u_max': 0.50,
            'window_u_max': 3.0,
        },
        'industrial_2020': {
            'wall_u_max': 0.50,
            'roof_u_max': 0.40,
            'window_u_max': 2.5,
        },
        'public_2015': {
            'wall_u_max': 0.50,
            'roof_u_max': 0.45,
            'window_u_max': 2.5,
        },
    }
    
    def __init__(self):
        pass
    
    # ==================== 围护结构热工计算 ====================
    
    def calculate_envelope_heat_loss(
        self,
        envelope: BuildingEnvelope,
        indoor_temp: float = 18,
        outdoor_temp: float = -5,
        infiltration_rate: float = 0.5  # 次/h
    ) -> Dict[str, float]:
        """
        计算围护结构热损失
        
        Args:
            envelope: 围护结构参数
            indoor_temp: 室内温度
            outdoor_temp: 室外温度
            infiltration_rate: 换气次数
        
        Returns:
            热损失计算结果
        """
        delta_t = indoor_temp - outdoor_temp
        
        # 各部分传热损失
        wall_loss = envelope.wall_area * envelope.wall_u * delta_t
        roof_loss = envelope.roof_area * envelope.roof_u * delta_t
        window_loss = envelope.window_area * envelope.window_u * delta_t
        floor_loss = envelope.floor_area * envelope.floor_u * delta_t
        
        # 冷风渗透
        building_volume = envelope.floor_area * 4  # 假设层高4m
        air_density = 1.2
        air_cp = 1.005
        infiltration_loss = (building_volume * infiltration_rate / 3600 * 
                           air_density * air_cp * delta_t * 1000)  # W
        
        total_loss = wall_loss + roof_loss + window_loss + floor_loss + infiltration_loss
        
        # 热负荷指标
        heat_index = total_loss / envelope.floor_area
        
        return {
            'wall_loss_w': round(wall_loss, 0),
            'roof_loss_w': round(roof_loss, 0),
            'window_loss_w': round(window_loss, 0),
            'floor_loss_w': round(floor_loss, 0),
            'infiltration_loss_w': round(infiltration_loss, 0),
            'total_heat_loss_w': round(total_loss, 0),
            'heat_loss_index_w_m2': round(heat_index, 1),
            'envelope_loss_percent': round((total_loss - infiltration_loss) / total_loss * 100, 1),
        }
    
    def calculate_annual_heating_load(
        self,
        envelope: BuildingEnvelope,
        climate_zone: str = 'cold',
        indoor_temp: float = 18
    ) -> Dict[str, float]:
        """
        计算年采暖热负荷
        """
        zone = self.CLIMATE_ZONES.get(climate_zone, self.CLIMATE_ZONES['cold'])
        hdd = zone['heating_degree_days']
        
        # 传热系数总和
        total_u_area = (envelope.wall_area * envelope.wall_u +
                       envelope.roof_area * envelope.roof_u +
                       envelope.window_area * envelope.window_u +
                       envelope.floor_area * envelope.floor_u)
        
        # 年热负荷 (简化计算)
        # Q = U·A·HDD·24 / 1000 (kWh)
        annual_load = total_u_area * hdd * 24 / 1000
        
        # 单位面积负荷
        load_per_area = annual_load / envelope.floor_area
        
        # 与标准对比
        standard = self.ENERGY_STANDARDS['industrial_2020']
        standard_load = (envelope.wall_area * standard['wall_u_max'] +
                        envelope.roof_area * standard['roof_u_max'] +
                        envelope.window_area * standard['window_u_max']) * hdd * 24 / 1000
        
        return {
            'climate_zone': climate_zone,
            'heating_degree_days': hdd,
            'annual_heating_load_kwh': round(annual_load, 0),
            'load_per_m2_kwh': round(load_per_area, 1),
            'standard_limit_kwh': round(standard_load, 0),
            'compliance': annual_load <= standard_load,
            'improvement_potential_percent': round((annual_load - standard_load) / annual_load * 100, 1) if annual_load > standard_load else 0,
        }
    
    def calculate_cooling_load(
        self,
        envelope: BuildingEnvelope,
        climate_zone: str = 'hot_summer_cold_winter',
        indoor_temp: float = 26,
        internal_gain: float = 20  # W/m² 内部得热
    ) -> Dict[str, float]:
        """
        计算空调冷负荷
        """
        zone = self.CLIMATE_ZONES.get(climate_zone, self.CLIMATE_ZONES['hot_summer_cold_winter'])
        cdd = zone['cooling_degree_days']
        outdoor_temp = zone['design_temp_cooling']
        
        delta_t = outdoor_temp - indoor_temp
        
        # 围护结构得热
        solar_gain_factor = 0.6  # 窗户太阳得热系数
        envelope_gain = (envelope.wall_area * envelope.wall_u +
                        envelope.roof_area * envelope.roof_u +
                        envelope.window_area * envelope.window_u * solar_gain_factor) * delta_t
        
        # 内部得热
        internal_heat = envelope.floor_area * internal_gain
        
        # 总冷负荷
        total_cooling = envelope_gain + internal_heat
        
        # 年冷负荷估算
        annual_cooling = total_cooling * cdd * 24 / (delta_t * 1000)  # kWh
        
        return {
            'climate_zone': climate_zone,
            'cooling_degree_days': cdd,
            'design_cooling_load_w': round(total_cooling, 0),
            'cooling_load_index_w_m2': round(total_cooling / envelope.floor_area, 1),
            'annual_cooling_load_kwh': round(annual_cooling, 0),
            'annual_cooling_per_m2_kwh': round(annual_cooling / envelope.floor_area, 1),
        }
    
    def optimize_envelope(
        self,
        envelope: BuildingEnvelope,
        target_standard: str = 'industrial_2020',
        climate_zone: str = 'cold'
    ) -> Dict[str, any]:
        """
        围护结构节能优化建议
        """
        standard = self.ENERGY_STANDARDS.get(target_standard, self.ENERGY_STANDARDS['industrial_2020'])
        
        recommendations = []
        
        # 墙体优化
        if envelope.wall_u > standard['wall_u_max']:
            current_u = envelope.wall_u
            target_u = standard['wall_u_max']
            
            # 估算保温层厚度
            # 假设增加保温，导热系数0.04 W/m·K
            insulation_k = 0.04
            required_thickness = insulation_k * (1/target_u - 1/current_u) * 1000  # mm
            
            recommendations.append({
                'component': '外墙',
                'current_u': current_u,
                'target_u': target_u,
                'action': f'增加保温层厚度约{round(required_thickness, 0)}mm',
                'priority': '高' if current_u > target_u * 1.3 else '中',
            })
        
        # 屋顶优化
        if envelope.roof_u > standard['roof_u_max']:
            current_u = envelope.roof_u
            target_u = standard['roof_u_max']
            insulation_k = 0.04
            required_thickness = insulation_k * (1/target_u - 1/current_u) * 1000
            
            recommendations.append({
                'component': '屋顶',
                'current_u': current_u,
                'target_u': target_u,
                'action': f'增加保温层厚度约{round(required_thickness, 0)}mm',
                'priority': '高',
            })
        
        # 窗户优化
        if envelope.window_u > standard['window_u_max']:
            recommendations.append({
                'component': '外窗',
                'current_u': envelope.window_u,
                'target_u': standard['window_u_max'],
                'action': '更换为Low-E中空玻璃窗或增加遮阳',
                'priority': '中',
            })
        
        # 计算优化后节能潜力
        original_load = self.calculate_annual_heating_load(envelope, climate_zone)
        
        optimized_envelope = BuildingEnvelope(
            wall_area=envelope.wall_area,
            roof_area=envelope.roof_area,
            window_area=envelope.window_area,
            floor_area=envelope.floor_area,
            wall_u=min(envelope.wall_u, standard['wall_u_max']),
            roof_u=min(envelope.roof_u, standard['roof_u_max']),
            window_u=min(envelope.window_u, standard['window_u_max']),
            floor_u=envelope.floor_u
        )
        
        optimized_load = self.calculate_annual_heating_load(optimized_envelope, climate_zone)
        
        saving_potential = original_load['annual_heating_load_kwh'] - optimized_load['annual_heating_load_kwh']
        
        return {
            'recommendations': recommendations,
            'original_annual_load_kwh': original_load['annual_heating_load_kwh'],
            'optimized_annual_load_kwh': optimized_load['annual_heating_load_kwh'],
            'saving_potential_kwh': round(saving_potential, 0),
            'saving_rate_percent': round(saving_potential / original_load['annual_heating_load_kwh'] * 100, 1),
        }
    
    # ==================== 工业建筑节能 ====================
    
    def calculate_industrial_building_energy(
        self,
        floor_area: float,
        building_type: str = 'workshop',  # workshop/warehouse/office
        climate_zone: str = 'cold',
        operation_hours: float = 4800  # 年运行小时
    ) -> Dict[str, any]:
        """
        计算工业建筑能耗
        
        Args:
            floor_area: 建筑面积 (m²)
            building_type: 建筑类型
            climate_zone: 气候分区
            operation_hours: 年运行小时
        """
        # 能耗指标 (kWh/m²·年)
        energy_indices = {
            'workshop': {'heating': 80, 'cooling': 40, 'lighting': 15, 'equipment': 30},
            'warehouse': {'heating': 50, 'cooling': 20, 'lighting': 8, 'equipment': 5},
            'office': {'heating': 60, 'cooling': 50, 'lighting': 20, 'equipment': 25},
        }
        
        indices = energy_indices.get(building_type, energy_indices['workshop'])
        
        # 根据气候分区调整
        zone = self.CLIMATE_ZONES.get(climate_zone, self.CLIMATE_ZONES['cold'])
        heating_factor = zone['heating_degree_days'] / 2500
        cooling_factor = zone['cooling_degree_days'] / 1200
        
        # 计算各项能耗
        heating = floor_area * indices['heating'] * heating_factor
        cooling = floor_area * indices['cooling'] * cooling_factor
        lighting = floor_area * indices['lighting'] * (operation_hours / 4800)
        equipment = floor_area * indices['equipment'] * (operation_hours / 4800)
        
        total = heating + cooling + lighting + equipment
        
        return {
            'building_type': building_type,
            'floor_area_m2': floor_area,
            'climate_zone': climate_zone,
            'heating_kwh': round(heating, 0),
            'cooling_kwh': round(cooling, 0),
            'lighting_kwh': round(lighting, 0),
            'equipment_kwh': round(equipment, 0),
            'total_kwh': round(total, 0),
            'energy_index_kwh_m2': round(total / floor_area, 1),
            'by_end_use': {
                'heating_percent': round(heating / total * 100, 1),
                'cooling_percent': round(cooling / total * 100, 1),
                'lighting_percent': round(lighting / total * 100, 1),
                'equipment_percent': round(equipment / total * 100, 1),
            }
        }
    
    def design_industrial_ventilation(
        self,
        building_volume: float,  # m³
        pollution_level: str = 'low',  # low/medium/high
        indoor_temp: float = 20,
        outdoor_temp: float = -5,
        heat_recovery: bool = True
    ) -> Dict[str, any]:
        """
        设计工业建筑通风系统
        
        Args:
            building_volume: 建筑体积
            pollution_level: 污染等级
            indoor_temp: 室内温度
            outdoor_temp: 室外温度
            heat_recovery: 是否热回收
        """
        # 换气次数
        air_changes = {
            'low': 2,
            'medium': 4,
            'high': 6,
        }.get(pollution_level, 3)
        
        # 通风量
        airflow = building_volume * air_changes  # m³/h
        
        # 热负荷
        air_density = 1.2
        air_cp = 1.005
        delta_t = indoor_temp - outdoor_temp
        
        heat_load = airflow * air_density * air_cp * delta_t / 3600  # kW
        
        # 热回收
        if heat_recovery:
            hr_efficiency = 0.65
            saved_heat = heat_load * hr_efficiency
            hr_investment = airflow * 2  # 元/(m³/h)
        else:
            saved_heat = 0
            hr_investment = 0
        
        # 风机功率
        fan_pressure = 500  # Pa
        fan_efficiency = 0.65
        fan_power = airflow * fan_pressure / (3600 * fan_efficiency * 1000)  # kW
        
        return {
            'airflow_m3_h': round(airflow, 0),
            'air_changes_per_hour': air_changes,
            'heat_load_kw': round(heat_load, 2),
            'fan_power_kw': round(fan_power, 2),
            'heat_recovery': heat_recovery,
            'hr_efficiency': hr_efficiency if heat_recovery else 0,
            'saved_heat_kw': round(saved_heat, 2),
            'hr_investment_yuan': round(hr_investment, 0),
            'annual_heating_saving_kwh': round(saved_heat * 2400, 0) if heat_recovery else 0,  # 采暖季2400小时
        }
    
    # ==================== 照明系统计算 ====================
    
    def calculate_lighting_system(
        self,
        area: float,
        required_illuminance: float = 300,  # lx
        lamp_type: str = 'led',
        room_height: float = 3
    ) -> Dict[str, any]:
        """
        计算照明系统
        
        Args:
            area: 面积 (m²)
            required_illuminance: 要求照度 (lx)
            lamp_type: 灯具类型
            room_height: 房间高度 (m)
        """
        # 灯具参数
        lamp_specs = {
            'led': {'efficacy': 120, 'lifespan': 50000, 'cost_per_w': 15},
            'fluorescent': {'efficacy': 80, 'lifespan': 15000, 'cost_per_w': 8},
            'metal_halide': {'efficacy': 90, 'lifespan': 10000, 'cost_per_w': 12},
            'high_pressure_sodium': {'efficacy': 100, 'lifespan': 20000, 'cost_per_w': 10},
        }
        
        spec = lamp_specs.get(lamp_type, lamp_specs['led'])
        
        # 利用系数 (简化)
        utilization_factor = 0.6
        
        # 维护系数
        maintenance_factor = 0.8
        
        # 所需光通量
        required_lumens = required_illuminance * area / (utilization_factor * maintenance_factor)
        
        # 灯具功率
        lamp_power = required_lumens / spec['efficacy']  # W
        
        # 功率密度
        power_density = lamp_power / area
        
        # 与标准对比
        standard_limit = 9  # W/m² (工业建筑照明标准)
        
        # 年耗电量
        operating_hours = 2400  # 年运行小时
        annual_consumption = lamp_power * operating_hours / 1000  # kWh
        
        # 投资
        investment = lamp_power * spec['cost_per_w']
        
        return {
            'area_m2': area,
            'required_illuminance_lx': required_illuminance,
            'lamp_type': lamp_type,
            'lamp_efficacy_lm_w': spec['efficacy'],
            'total_lamp_power_w': round(lamp_power, 0),
            'power_density_w_m2': round(power_density, 1),
            'standard_limit_w_m2': standard_limit,
            'compliance': power_density <= standard_limit,
            'annual_consumption_kwh': round(annual_consumption, 0),
            'investment_yuan': round(investment, 0),
            'lifespan_hours': spec['lifespan'],
        }
    
    def compare_lighting_options(
        self,
        area: float,
        required_illuminance: float = 300
    ) -> Dict[str, any]:
        """
        对比不同照明方案
        """
        options = []
        
        for lamp_type in ['led', 'fluorescent', 'metal_halide', 'high_pressure_sodium']:
            result = self.calculate_lighting_system(area, required_illuminance, lamp_type)
            
            # 计算10年总成本
            annual_cost = result['annual_consumption_kwh'] * 0.8  # 电费
            lifespan_years = result['lifespan_hours'] / 2400
            replacement_cost = result['investment_yuan'] / lifespan_years * 10 if lifespan_years < 10 else 0
            total_10y_cost = result['investment_yuan'] + annual_cost * 10 + replacement_cost
            
            options.append({
                'lamp_type': lamp_type,
                'power_density_w_m2': result['power_density_w_m2'],
                'annual_consumption_kwh': result['annual_consumption_kwh'],
                'initial_investment': result['investment_yuan'],
                'total_10y_cost': round(total_10y_cost, 0),
            })
        
        # 按10年总成本排序
        options.sort(key=lambda x: x['total_10y_cost'])
        
        return {
            'area_m2': area,
            'required_illuminance_lx': required_illuminance,
            'options': options,
            'recommendation': options[0]['lamp_type'],
        }
    
    # ==================== 自然采光计算 ====================
    
    def calculate_daylighting(
        self,
        room_area: float,
        window_area: float,
        window_orientation: str = 'south',
        room_depth: float = 6
    ) -> Dict[str, any]:
        """
        计算自然采光
        
        Args:
            room_area: 房间面积
            window_area: 窗面积
            window_orientation: 朝向
            room_depth: 房间进深
        """
        # 窗地比
        window_to_floor_ratio = window_area / room_area
        
        # 采光系数 (简化)
        orientation_factor = {
            'south': 1.0,
            'east': 0.8,
            'west': 0.8,
            'north': 0.6,
        }.get(window_orientation, 0.8)
        
        daylight_factor = window_to_floor_ratio * orientation_factor * 5  # 简化公式
        
        # 采光达标面积比例
        # 假设进深6m以内可达标
        effective_depth = min(room_depth, 6)
        compliance_ratio = effective_depth / room_depth
        
        # 年采光时数 (简化)
        annual_daylight_hours = 2400 * compliance_ratio
        
        # 照明节能潜力
        lighting_power = room_area * 9  # W
        saving_potential = lighting_power * annual_daylight_hours / 1000 * 0.5  # 50%时间可利用自然光
        
        return {
            'window_to_floor_ratio': round(window_to_floor_ratio, 3),
            'daylight_factor_percent': round(daylight_factor * 100, 1),
            'effective_daylight_depth_m': effective_depth,
            'compliance_area_ratio': round(compliance_ratio * 100, 1),
            'annual_daylight_hours': round(annual_daylight_hours, 0),
            'lighting_saving_potential_kwh': round(saving_potential, 0),
            'recommendations': [
                '增加南向窗户面积' if window_to_floor_ratio < 0.15 else '窗地比合适',
                '采用高透光率玻璃' if daylight_factor < 2 else '采光良好',
                '设置反光板或导光管' if room_depth > 6 else None,
            ],
        }
    
    # ==================== 综合节能评估 ====================
    
    def comprehensive_building_assessment(
        self,
        envelope: BuildingEnvelope,
        building_type: str = 'workshop',
        climate_zone: str = 'cold',
        operation_hours: float = 4800
    ) -> Dict[str, any]:
        """
        建筑综合节能评估
        """
        # 围护结构评估
        heat_loss = self.calculate_envelope_heat_loss(envelope)
        heating_load = self.calculate_annual_heating_load(envelope, climate_zone)
        cooling_load = self.calculate_cooling_load(envelope, climate_zone)
        
        # 整体能耗
        total_energy = self.calculate_industrial_building_energy(
            envelope.floor_area, building_type, climate_zone, operation_hours
        )
        
        # 围护结构优化
        optimization = self.optimize_envelope(envelope, 'industrial_2020', climate_zone)
        
        # 照明对比
        lighting_comparison = self.compare_lighting_options(envelope.floor_area)
        
        # 综合建议
        total_saving_potential = (
            optimization['saving_potential_kwh'] +
            lighting_comparison['options'][0]['annual_consumption_kwh'] * 0.3  # LED节能30%
        )
        
        return {
            'building_info': {
                'type': building_type,
                'floor_area_m2': envelope.floor_area,
                'climate_zone': climate_zone,
            },
            'current_performance': {
                'heat_loss_index_w_m2': heat_loss['heat_loss_index_w_m2'],
                'annual_heating_kwh': heating_load['annual_heating_load_kwh'],
                'annual_cooling_kwh': cooling_load['annual_cooling_load_kwh'],
                'total_energy_kwh': total_energy['total_kwh'],
                'energy_index_kwh_m2': total_energy['energy_index_kwh_m2'],
            },
            'envelope_optimization': optimization,
            'lighting_recommendation': lighting_comparison,
            'total_saving_potential_kwh': round(total_saving_potential, 0),
            'saving_rate_percent': round(total_saving_potential / total_energy['total_kwh'] * 100, 1),
            'priority_measures': [
                '围护结构保温改造' if heating_load['compliance'] == False else None,
                'LED照明改造',
                '自然采光优化',
                '通风热回收',
            ],
        }
