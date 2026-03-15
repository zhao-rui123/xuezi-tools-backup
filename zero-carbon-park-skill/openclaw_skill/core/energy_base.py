"""
基础能源计算模块
==============
涵盖水、电、气、暖的基础计算
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EnergyData:
    """能源数据类"""
    water: float = 0  # 水用量 (m³)
    electricity: float = 0  # 用电量 (kWh)
    gas: float = 0  # 用气量 (m³)
    heat: float = 0  # 用热量 (GJ)
    cooling: float = 0  # 用冷量 (GJ)


class EnergyBase:
    """基础能源计算类"""
    
    # 标准煤折算系数 (kgce/单位)
    COAL_EQUIVALENT = {
        'electricity': 0.1229,  # kgce/kWh
        'water': 0.0857,  # kgce/m³ (含供水能耗)
        'natural_gas': 1.2143,  # kgce/m³
        'liquefied_gas': 1.7143,  # kgce/kg
        'steam': 0.1286,  # kgce/kg (0.4MPa)
        'hot_water': 0.0857,  # kgce/GJ
        'cooling': 0.036,  # kgce/GJ
        'diesel': 1.4571,  # kgce/kg
        'gasoline': 1.4714,  # kgce/kg
    }
    
    # 碳排放因子 (tCO2/单位)
    CARBON_FACTOR = {
        'electricity': 0.5703,  # tCO2/MWh (电网平均)
        'electricity_green': 0.0,  # 绿电
        'natural_gas': 2.162,  # tCO2/1000m³
        'liquefied_gas': 3.101,  # tCO2/t
        'steam': 0.11,  # tCO2/t (燃煤锅炉)
        'steam_gas': 0.06,  # tCO2/t (燃气锅炉)
        'diesel': 3.16,  # tCO2/t
        'gasoline': 3.15,  # tCO2/t
        'water': 0.168,  # tCO2/1000m³
    }
    
    def __init__(self):
        self.energy_data = EnergyData()
    
    # ==================== 水系统计算 ====================
    
    def calculate_water_pressure_loss(
        self, 
        flow_rate: float,  # m³/h
        pipe_diameter: float,  # mm
        pipe_length: float,  # m
        roughness: float = 0.1,  # mm (钢管)
        fittings_k: List[float] = None  # 局部阻力系数
    ) -> Dict[str, float]:
        """
        计算水管网压力损失
        
        Args:
            flow_rate: 流量 (m³/h)
            pipe_diameter: 管径 (mm)
            pipe_length: 管长 (m)
            roughness: 绝对粗糙度 (mm)
            fittings_k: 局部阻力系数列表
        
        Returns:
            压力损失计算结果
        """
        # 流速计算 (m/s)
        velocity = (flow_rate / 3600) / (math.pi * (pipe_diameter/2000)**2)
        
        # 雷诺数
        reynolds = velocity * (pipe_diameter/1000) / 1e-6  # 水运动粘度约1e-6
        
        # 摩擦系数 (Colebrook-White近似)
        if reynolds < 2300:
            friction = 64 / reynolds
        else:
            # Haaland近似
            friction = 0.25 / (math.log10(roughness/(3.7*pipe_diameter) + 5.74/reynolds**0.9))**2
        
        # 沿程阻力损失 (m)
        hf = friction * (pipe_length / (pipe_diameter/1000)) * (velocity**2 / (2*9.81))
        
        # 局部阻力损失 (m)
        hj = 0
        if fittings_k:
            hj = sum(k * velocity**2 / (2*9.81) for k in fittings_k)
        
        # 总压力损失 (m, kPa)
        total_head = hf + hj
        total_pressure = total_head * 9.81  # kPa
        
        return {
            'velocity': round(velocity, 2),
            'reynolds': round(reynolds, 0),
            'friction_factor': round(friction, 4),
            'friction_loss_m': round(hf, 2),
            'local_loss_m': round(hj, 2),
            'total_head_loss_m': round(total_head, 2),
            'total_pressure_loss_kpa': round(total_pressure, 2),
        }
    
    def calculate_water_pump_power(
        self,
        flow_rate: float,  # m³/h
        head: float,  # m
        efficiency: float = 0.75,  # 水泵效率
        motor_efficiency: float = 0.92  # 电机效率
    ) -> Dict[str, float]:
        """
        计算水泵功率
        
        Args:
            flow_rate: 流量 (m³/h)
            head: 扬程 (m)
            efficiency: 水泵效率
            motor_efficiency: 电机效率
        
        Returns:
            功率计算结果
        """
        # 轴功率 (kW)
        shaft_power = (flow_rate * head * 9.81 * 1000) / (3600 * 1000 * efficiency)
        
        # 电机输入功率 (kW)
        motor_power = shaft_power / motor_efficiency
        
        # 推荐电机功率 (kW) - 取标准规格并留裕量
        std_motors = [0.75, 1.1, 1.5, 2.2, 3, 4, 5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75]
        recommended = next((m for m in std_motors if m >= motor_power * 1.15), 75)
        
        return {
            'shaft_power_kw': round(shaft_power, 2),
            'motor_input_power_kw': round(motor_power, 2),
            'recommended_motor_kw': recommended,
            'total_efficiency': round(efficiency * motor_efficiency, 3),
        }
    
    def calculate_water_energy_saving(
        self,
        original_flow: float,
        original_head: float,
        original_efficiency: float,
        new_flow: float = None,
        new_head: float = None,
        new_efficiency: float = None,
        operating_hours: float = 8760
    ) -> Dict[str, float]:
        """
        计算水泵节能改造效益
        """
        new_flow = new_flow or original_flow
        new_head = new_head or original_head
        new_efficiency = new_efficiency or original_efficiency * 1.15  # 假设效率提升15%
        
        original_power = (original_flow * original_head * 9.81) / (3600 * original_efficiency)
        new_power = (new_flow * new_head * 9.81) / (3600 * new_efficiency)
        
        saving_power = original_power - new_power
        saving_energy = saving_power * operating_hours
        saving_cost = saving_energy * 0.8  # 假设电价0.8元/kWh
        
        return {
            'original_power_kw': round(original_power, 2),
            'new_power_kw': round(new_power, 2),
            'saving_power_kw': round(saving_power, 2),
            'annual_saving_kwh': round(saving_energy, 0),
            'annual_saving_cost_yuan': round(saving_cost, 0),
        }
    
    # ==================== 电气系统计算 ====================
    
    def calculate_power_factor_correction(
        self,
        active_power: float,  # kW
        current_pf: float,  # 当前功率因数
        target_pf: float  # 目标功率因数
    ) -> Dict[str, float]:
        """
        计算无功补偿容量
        
        Args:
            active_power: 有功功率 (kW)
            current_pf: 当前功率因数
            target_pf: 目标功率因数
        
        Returns:
            补偿计算结果
        """
        # 当前无功功率
        current_tan_phi = math.tan(math.acos(current_pf))
        current_q = active_power * current_tan_phi
        
        # 目标无功功率
        target_tan_phi = math.tan(math.acos(target_pf))
        target_q = active_power * target_tan_phi
        
        # 所需补偿容量
        compensation = current_q - target_q
        
        # 视在功率变化
        current_s = active_power / current_pf
        target_s = active_power / target_pf
        s_reduction = current_s - target_s
        
        # 电流减少百分比
        current_reduction = (1 - target_pf/current_pf) * 100
        
        # 线损减少百分比
        loss_reduction = (1 - (target_pf/current_pf)**2) * 100
        
        return {
            'current_reactive_power_kvar': round(current_q, 2),
            'target_reactive_power_kvar': round(target_q, 2),
            'compensation_required_kvar': round(compensation, 2),
            'apparent_power_reduction_kva': round(s_reduction, 2),
            'current_reduction_percent': round(current_reduction, 2),
            'line_loss_reduction_percent': round(loss_reduction, 2),
        }
    
    def calculate_transformer_loss(
        self,
        capacity: float,  # kVA
        load_rate: float,  # 负载率 (0-1)
        no_load_loss: float = None,  # 空载损耗 (kW)
        load_loss: float = None  # 负载损耗 (kW)
    ) -> Dict[str, float]:
        """
        计算变压器损耗
        
        Args:
            capacity: 变压器容量 (kVA)
            load_rate: 负载率
            no_load_loss: 空载损耗，None则按经验公式估算
            load_loss: 负载损耗，None则按经验公式估算
        
        Returns:
            损耗计算结果
        """
        # 经验估算值 (干式变压器)
        if no_load_loss is None:
            no_load_loss = 0.005 * capacity  # 约0.5%
        if load_loss is None:
            load_loss = 0.015 * capacity  # 约1.5%
        
        # 总损耗
        total_loss = no_load_loss + load_rate**2 * load_loss
        
        # 效率
        output_power = capacity * load_rate * 0.9  # 假设功率因数0.9
        efficiency = output_power / (output_power + total_loss)
        
        # 年损耗电量 (按8760小时)
        annual_loss = total_loss * 8760
        
        # 经济负载率
        economic_load = math.sqrt(no_load_loss / load_loss)
        
        return {
            'no_load_loss_kw': round(no_load_loss, 2),
            'load_loss_kw': round(load_loss * load_rate**2, 2),
            'total_loss_kw': round(total_loss, 2),
            'efficiency_percent': round(efficiency * 100, 2),
            'annual_loss_kwh': round(annual_loss, 0),
            'economic_load_rate': round(economic_load, 2),
        }
    
    def calculate_cable_sizing(
        self,
        power: float,  # kW
        voltage: float,  # V
        length: float,  # m
        max_voltage_drop: float = 0.05,  # 最大压降5%
        power_factor: float = 0.9,
        cable_type: str = 'copper',  # copper/aluminum
        installation: str = 'air'  # air/ground/conduit
    ) -> Dict[str, any]:
        """
        电缆选型计算
        """
        # 电流计算
        current = power * 1000 / (math.sqrt(3) * voltage * power_factor)
        
        # 电阻率 (Ω·mm²/m)
        resistivity = 0.0172 if cable_type == 'copper' else 0.0282
        
        # 敷设系数
        install_factor = {
            'air': 1.0,
            'ground': 0.85,
            'conduit': 0.7
        }.get(installation, 1.0)
        
        # 标准电缆截面 (mm²)
        std_sections = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
        
        # 载流量表 (A, 铜芯空气中敷设, 环境温度30°C)
        ampacity_table = {
            1.5: 20, 2.5: 28, 4: 37, 6: 48, 10: 65, 16: 88, 
            25: 113, 35: 142, 50: 171, 70: 218, 95: 264, 
            120: 308, 150: 356, 185: 408, 240: 486, 300: 559
        }
        
        # 选择最小截面 (满足载流量)
        min_section_ampacity = None
        for section in std_sections:
            ampacity = ampacity_table.get(section, 0) * install_factor
            if ampacity >= current * 1.25:  # 留25%裕量
                min_section_ampacity = section
                break
        
        # 选择最小截面 (满足压降)
        min_section_voltage = None
        for section in std_sections:
            resistance = resistivity * length * 2 / section  # 往返
            voltage_drop = current * resistance / voltage
            if voltage_drop <= max_voltage_drop:
                min_section_voltage = section
                break
        
        # 最终选择
        recommended_section = max(min_section_ampacity or 300, min_section_voltage or 300)
        
        # 实际压降
        actual_resistance = resistivity * length * 2 / recommended_section
        actual_voltage_drop = current * actual_resistance
        actual_voltage_drop_percent = actual_voltage_drop / voltage * 100
        
        return {
            'calculated_current_a': round(current, 1),
            'min_section_by_ampacity_mm2': min_section_ampacity,
            'min_section_by_voltage_mm2': min_section_voltage,
            'recommended_section_mm2': recommended_section,
            'actual_voltage_drop_v': round(actual_voltage_drop, 2),
            'actual_voltage_drop_percent': round(actual_voltage_drop_percent, 2),
            'cable_resistance_ohm': round(actual_resistance, 4),
        }
    
    # ==================== 燃气系统计算 ====================
    
    def calculate_gas_pipe_sizing(
        self,
        flow_rate: float,  # m³/h
        pressure_in: float,  # kPa (入口压力)
        pressure_out: float,  # kPa (出口压力)
        pipe_length: float,  # m
        gas_type: str = 'natural_gas'
    ) -> Dict[str, float]:
        """
        燃气管道选型计算 (低压燃气)
        """
        # 燃气特性
        gas_props = {
            'natural_gas': {'density': 0.75, 'viscosity': 1.5e-5},  # kg/m³, Pa·s
            'liquefied_gas': {'density': 2.0, 'viscosity': 1.0e-5},
        }
        props = gas_props.get(gas_type, gas_props['natural_gas'])
        
        # 允许压降
        delta_p = pressure_in - pressure_out
        
        # 简化计算 - 使用经验公式
        # 管径估算 (mm)
        # Q = 0.5 * d^2.5 * sqrt(deltaP/L) (简化公式)
        import math
        d_estimated = (flow_rate / (0.5 * math.sqrt(delta_p / pipe_length))) ** (1/2.5)
        
        # 标准管径
        std_diameters = [20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200]
        recommended_d = next((d for d in std_diameters if d >= d_estimated * 10), 200)
        
        # 实际流速
        area = math.pi * (recommended_d/2000)**2
        velocity = (flow_rate / 3600) / area
        
        return {
            'estimated_diameter_mm': round(d_estimated * 10, 1),
            'recommended_diameter_mm': recommended_d,
            'actual_velocity_ms': round(velocity, 2),
            'pressure_drop_pa': round(delta_p * 1000, 0),
        }
    
    def calculate_gas_boiler_efficiency(
        self,
        fuel_consumption: float,  # m³/h
        boiler_output: float,  # kW
        fuel_calorific: float = 35.8  # MJ/m³ (天然气低位发热量)
    ) -> Dict[str, float]:
        """
        燃气锅炉效率计算
        """
        # 输入热量 (kW)
        input_heat = fuel_consumption * fuel_calorific * 1000 / 3600
        
        # 效率
        efficiency = boiler_output / input_heat
        
        # 排烟损失估算 (简化)
        exhaust_loss = 0.06 if efficiency > 0.9 else 0.1
        
        # 年运行费用估算 (8000小时)
        gas_price = 3.5  # 元/m³
        annual_cost = fuel_consumption * 8000 * gas_price
        
        return {
            'input_heat_kw': round(input_heat, 2),
            'output_heat_kw': round(boiler_output, 2),
            'efficiency_percent': round(efficiency * 100, 2),
            'annual_fuel_cost_yuan': round(annual_cost, 0),
        }
    
    # ==================== 暖通系统计算 ====================
    
    def calculate_heating_load(
        self,
        area: float,  # m²
        heat_index: float = None,  # W/m², 热指标
        building_type: str = 'industrial'
    ) -> Dict[str, float]:
        """
        采暖热负荷计算
        """
        # 热指标参考值 (W/m²)
        heat_indices = {
            'industrial': 80,
            'office': 70,
            'residential': 60,
            'warehouse': 50,
            'workshop_high': 100,
        }
        
        index = heat_index or heat_indices.get(building_type, 80)
        
        # 热负荷
        heat_load = area * index  # W
        heat_load_kw = heat_load / 1000
        
        # 年采暖耗热量 (采暖季120天, 每天10小时)
        annual_heat = heat_load_kw * 120 * 10  # kWh
        annual_gj = annual_heat * 0.0036  # GJ
        
        return {
            'heat_load_w': round(heat_load, 0),
            'heat_load_kw': round(heat_load_kw, 2),
            'heat_index_wm2': index,
            'annual_heat_kwh': round(annual_heat, 0),
            'annual_heat_gj': round(annual_gj, 2),
        }
    
    def calculate_cooling_load(
        self,
        area: float,
        cool_index: float = None,
        building_type: str = 'industrial'
    ) -> Dict[str, float]:
        """
        空调冷负荷计算
        """
        # 冷指标参考值 (W/m²)
        cool_indices = {
            'industrial': 120,
            'office': 100,
            'data_center': 800,
            'warehouse': 40,
            'clean_room': 300,
        }
        
        index = cool_index or cool_indices.get(building_type, 120)
        
        # 冷负荷
        cool_load = area * index
        cool_load_kw = cool_load / 1000
        
        # 制冷机功率 (COP=4)
        chiller_power = cool_load_kw / 4
        
        # 年制冷耗电量 (制冷季150天, 每天10小时)
        annual_power = chiller_power * 150 * 10
        
        return {
            'cool_load_w': round(cool_load, 0),
            'cool_load_kw': round(cool_load_kw, 2),
            'cool_index_wm2': index,
            'chiller_power_kw': round(chiller_power, 2),
            'annual_power_kwh': round(annual_power, 0),
        }
    
    def calculate_hvac_energy_saving(
        self,
        area: float,
        current_index: float,
        improved_index: float,
        building_type: str = 'industrial',
        system_type: str = 'heating'  # heating/cooling
    ) -> Dict[str, float]:
        """
        暖通节能改造效益计算
        """
        if system_type == 'heating':
            current_load = area * current_index / 1000
            improved_load = area * improved_index / 1000
            saving_kw = current_load - improved_load
            annual_hours = 120 * 10  # 采暖季
            energy_price = 0.35  # 元/kWh (按燃气折算)
        else:
            current_load = area * current_index / 1000
            improved_load = area * improved_index / 1000
            saving_kw = current_load - improved_load
            annual_hours = 150 * 10  # 制冷季
            energy_price = 0.8  # 元/kWh
        
        annual_saving_kwh = saving_kw * annual_hours
        annual_saving_cost = annual_saving_kwh * energy_price
        
        return {
            'current_load_kw': round(current_load, 2),
            'improved_load_kw': round(improved_load, 2),
            'saving_power_kw': round(saving_kw, 2),
            'annual_saving_kwh': round(annual_saving_kwh, 0),
            'annual_saving_cost_yuan': round(annual_saving_cost, 0),
        }
    
    # ==================== 综合能源计算 ====================
    
    def calculate_comprehensive_energy(
        self,
        water_m3: float = 0,
        electricity_kwh: float = 0,
        gas_m3: float = 0,
        heat_gj: float = 0,
        cooling_gj: float = 0
    ) -> Dict[str, float]:
        """
        综合能耗计算
        """
        # 折标准煤
        coal_water = water_m3 * self.COAL_EQUIVALENT['water'] / 1000  # tce
        coal_elec = electricity_kwh * self.COAL_EQUIVALENT['electricity'] / 1000
        coal_gas = gas_m3 * self.COAL_EQUIVALENT['natural_gas'] / 1000
        coal_heat = heat_gj * 34.12 * self.COAL_EQUIVALENT['steam'] / 1000
        coal_cooling = cooling_gj * 34.12 * self.COAL_EQUIVALENT['cooling'] / 1000
        
        total_coal = coal_water + coal_elec + coal_gas + coal_heat + coal_cooling
        
        # 碳排放
        co2_elec = electricity_kwh / 1000 * self.CARBON_FACTOR['electricity']
        co2_gas = gas_m3 / 1000 * self.CARBON_FACTOR['natural_gas']
        co2_heat = heat_gj * 0.11  # 简化计算
        
        total_co2 = co2_elec + co2_gas + co2_heat
        
        return {
            'coal_water_tce': round(coal_water, 2),
            'coal_electricity_tce': round(coal_elec, 2),
            'coal_gas_tce': round(coal_gas, 2),
            'coal_heat_tce': round(coal_heat, 2),
            'coal_cooling_tce': round(coal_cooling, 2),
            'total_coal_tce': round(total_coal, 2),
            'co2_electricity_t': round(co2_elec, 2),
            'co2_gas_t': round(co2_gas, 2),
            'co2_heat_t': round(co2_heat, 2),
            'total_co2_t': round(total_co2, 2),
        }
