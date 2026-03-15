"""
钢铁企业电力设计和高压送电线路设计模块
"""

import math
from typing import List, Dict, Any

# 导入数据类
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# 尝试导入，如果失败则定义本地版本
try:
    from power_design_skill import LoadCalculationResult
except ImportError:
    from dataclasses import dataclass

    @dataclass
    class LoadCalculationResult:
        """负荷计算结果"""
        active_power: float
        reactive_power: float
        apparent_power: float
        calculation_current: float
        power_factor: float


# ==================== 钢铁企业电力设计模块 ====================
# 依据《钢铁企业电力设计手册》

class SteelPlantPowerDesign:
    """
    钢铁企业电力设计模块
    依据《钢铁企业电力设计手册》上、下册
    """

    # 钢铁企业典型设备需要系数表
    STEEL_PLANT_DEMAND_FACTORS = {
        '高炉鼓风机': {'Kd': 0.8, 'cosφ': 0.85, 'tanφ': 0.62},
        '制氧机': {'Kd': 0.85, 'cosφ': 0.88, 'tanφ': 0.54},
        '电弧炉': {'Kd': 0.9, 'cosφ': 0.75, 'tanφ': 0.88},
        '精炼炉': {'Kd': 0.85, 'cosφ': 0.8, 'tanφ': 0.75},
        '连铸机': {'Kd': 0.75, 'cosφ': 0.8, 'tanφ': 0.75},
        '轧钢机': {'Kd': 0.6, 'cosφ': 0.7, 'tanφ': 1.02},
        '加热炉': {'Kd': 0.9, 'cosφ': 0.95, 'tanφ': 0.33},
        '烧结机': {'Kd': 0.8, 'cosφ': 0.82, 'tanφ': 0.70},
        '焦化设备': {'Kd': 0.75, 'cosφ': 0.8, 'tanφ': 0.75},
        '除尘风机': {'Kd': 0.8, 'cosφ': 0.85, 'tanφ': 0.62},
        '水泵站': {'Kd': 0.85, 'cosφ': 0.85, 'tanφ': 0.62},
        '起重机': {'Kd': 0.35, 'cosφ': 0.5, 'tanφ': 1.73},
    }

    # 钢铁企业单位产品耗电指标 (kWh/t)
    POWER_CONSUMPTION_PER_UNIT = {
        '生铁': 450,
        '转炉钢': 650,
        '电炉钢': 550,
        '连铸坯': 80,
        '热轧板': 120,
        '冷轧板': 180,
        '线材': 100,
        '棒材': 90,
        '钢管': 150,
    }

    @staticmethod
    def calculate_by_unit_production(
        production_capacity: float,
        product_type: str,
        operating_hours: float = 7000
    ) -> LoadCalculationResult:
        """
        按单位产品耗电量计算负荷

        公式: Pc = (Pe' × N) / Tmax

        Args:
            production_capacity: 年产量 (t)
            product_type: 产品类型
            operating_hours: 年最大负荷利用小时数 (h)

        Returns:
            负荷计算结果
        """
        power_consumption = SteelPlantPowerDesign.POWER_CONSUMPTION_PER_UNIT.get(
            product_type, 500
        )

        # 年电能消耗量
        annual_energy = production_capacity * power_consumption

        # 计算有功功率
        Pc = annual_energy / operating_hours

        # 钢铁企业功率因数
        cosφ = 0.8
        tanφ = 0.75

        Qc = Pc * tanφ
        Sc = math.sqrt(Pc**2 + Qc**2)
        Ic = Sc / (math.sqrt(3) * 0.38)

        return LoadCalculationResult(
            active_power=Pc,
            reactive_power=Qc,
            apparent_power=Sc,
            calculation_current=Ic,
            power_factor=cosφ
        )

    @staticmethod
    def arc_furnace_load(
        furnace_capacity: float,  # 炉子容量 (t)
        transformer_power: float,  # 变压器容量 (MVA)
        operating_mode: str = 'normal'
    ) -> Dict[str, float]:
        """
        电弧炉负荷计算

        Args:
            furnace_capacity: 炉子容量 (t)
            transformer_power: 变压器容量 (MVA)
            operating_mode: 运行模式

        Returns:
            负荷参数
        """
        # 熔化期功率因数
        melt_pf = 0.75
        # 精炼期功率因数
        refine_pf = 0.85

        # 平均功率因数
        avg_pf = (melt_pf + refine_pf) / 2

        # 电弧炉冲击负荷系数
        impact_factor = 1.3 if operating_mode == 'melting' else 1.0

        # 计算负荷
        apparent_power = transformer_power * impact_factor
        active_power = apparent_power * avg_pf
        reactive_power = apparent_power * math.sqrt(1 - avg_pf**2)

        return {
            'active_power_mw': active_power,
            'reactive_power_mvar': reactive_power,
            'apparent_power_mva': apparent_power,
            'power_factor': avg_pf,
            'impact_factor': impact_factor,
            'furnace_capacity_t': furnace_capacity
        }

    @staticmethod
    def harmonic_calculation(
        fundamental_current: float,
        harmonic_orders: List[int] = None
    ) -> Dict[int, float]:
        """
        谐波电流计算（电弧炉典型谐波）

        Args:
            fundamental_current: 基波电流 (A)
            harmonic_orders: 谐波次数列表

        Returns:
            各次谐波电流
        """
        if harmonic_orders is None:
            harmonic_orders = [2, 3, 4, 5, 7]

        # 电弧炉典型谐波含量 (%)
        harmonic_content = {
            2: 0.15,  # 15%
            3: 0.20,  # 20%
            4: 0.08,  # 8%
            5: 0.12,  # 12%
            7: 0.06,  # 6%
        }

        harmonics = {}
        for order in harmonic_orders:
            content = harmonic_content.get(order, 0.05)
            harmonics[order] = fundamental_current * content

        # 总谐波畸变率
        thd = math.sqrt(sum([h**2 for h in harmonics.values()])) / fundamental_current * 100
        harmonics['THD'] = thd

        return harmonics

    @staticmethod
    def rolling_mill_impact_load(
        motor_power: float,
        load_factor: float = 0.6,
        impact_factor: float = 2.5
    ) -> Dict[str, float]:
        """
        轧钢机冲击负荷计算

        Args:
            motor_power: 电动机总功率 (kW)
            load_factor: 负载率
            impact_factor: 冲击系数

        Returns:
            冲击负荷参数
        """
        # 平均负荷
        avg_power = motor_power * load_factor

        # 冲击负荷
        impact_power = avg_power * impact_factor

        # 无功冲击
        impact_reactive = impact_power * 0.75  # tanφ ≈ 0.75

        return {
            'average_power_kw': avg_power,
            'impact_power_kw': impact_power,
            'impact_reactive_kvar': impact_reactive,
            'impact_factor': impact_factor
        }

    @staticmethod
    def reactive_power_compensation_sizing(
        load_power: float,
        current_pf: float,
        target_pf: float,
        load_type: str = 'arc_furnace'
    ) -> Dict[str, float]:
        """
        钢铁企业无功补偿容量计算

        Args:
            load_power: 负荷功率 (kW)
            current_pf: 当前功率因数
            target_pf: 目标功率因数
            load_type: 负荷类型

        Returns:
            补偿参数
        """
        tan_phi1 = math.sqrt(1 - current_pf**2) / current_pf
        tan_phi2 = math.sqrt(1 - target_pf**2) / target_pf

        # 基本补偿容量
        basic_compensation = load_power * (tan_phi1 - tan_phi2)

        # 根据负荷类型调整
        if load_type == 'arc_furnace':
            # 电弧炉需要额外考虑冲击负荷
            compensation = basic_compensation * 1.3
        elif load_type == 'rolling_mill':
            # 轧钢机需要动态补偿
            compensation = basic_compensation * 1.2
        else:
            compensation = basic_compensation

        return {
            'compensation_capacity_kvar': compensation,
            'basic_compensation_kvar': basic_compensation,
            'current_pf': current_pf,
            'target_pf': target_pf,
            'load_type': load_type
        }


# ==================== 高压送电线路设计模块 ====================
# 依据《电力工程高压送电线路设计手册》第二版

class TransmissionLineDesign:
    """
    高压送电线路设计模块
    依据《电力工程高压送电线路设计手册》第二版
    适用于35kV~500kV送电线路设计
    """

    # 常用导线参数
    CONDUCTOR_DATA = {
        'LGJ-70': {'section': 68.05, 'diameter': 10.80, 'weight': 275.2, 'breaking_load': 23390},
        'LGJ-95': {'section': 95.14, 'diameter': 12.78, 'weight': 380.8, 'breaking_load': 33190},
        'LGJ-120': {'section': 121.21, 'diameter': 14.25, 'weight': 471.6, 'breaking_load': 41000},
        'LGJ-150': {'section': 148.07, 'diameter': 15.75, 'weight': 575.6, 'breaking_load': 50000},
        'LGJ-185': {'section': 182.80, 'diameter': 17.50, 'weight': 706.6, 'breaking_load': 61150},
        'LGJ-240': {'section': 236.38, 'diameter': 19.90, 'weight': 908.5, 'breaking_load': 78110},
        'LGJ-300': {'section': 297.57, 'diameter': 22.40, 'weight': 1139.6, 'breaking_load': 97620},
        'LGJ-400': {'section': 397.83, 'diameter': 25.90, 'weight': 1510.5, 'breaking_load': 128700},
        'LGJ-500': {'section': 502.90, 'diameter': 29.12, 'weight': 1897.6, 'breaking_load': 161100},
        'LGJ-630': {'section': 635.50, 'diameter': 32.73, 'weight': 2394.0, 'breaking_load': 203100},
        'LGJ-800': {'section': 805.40, 'diameter': 36.85, 'weight': 3029.0, 'breaking_load': 257500},
    }

    # 气象条件分类
    WEATHER_CONDITIONS = {
        'I类(轻冰区)': {'wind': 25, 'ice': 0, 'temp_min': -20, 'temp_max': 40},
        'II类(中冰区)': {'wind': 30, 'ice': 5, 'temp_min': -25, 'temp_max': 40},
        'III类(重冰区)': {'wind': 35, 'ice': 10, 'temp_min': -30, 'temp_max': 40},
        'IV类(特重冰区)': {'wind': 35, 'ice': 15, 'temp_min': -35, 'temp_max': 40},
    }

    @staticmethod
    def electrical_parameters(
        conductor_type: str,
        line_length: float,
        voltage: float,
        num_circuits: int = 1
    ) -> Dict[str, float]:
        """
        计算线路电气参数

        Args:
            conductor_type: 导线型号
            line_length: 线路长度 (km)
            voltage: 额定电压 (kV)
            num_circuits: 回路数

        Returns:
            电气参数
        """
        conductor = TransmissionLineDesign.CONDUCTOR_DATA.get(conductor_type)
        if not conductor:
            raise ValueError(f"未知导线型号: {conductor_type}")

        section = conductor['section']  # mm²

        # 电阻 (Ω/km)
        r = 0.0315 / (section / 100)  # 铝的电阻率

        # 电抗 (Ω/km) - 近似值
        x = 0.4

        # 电纳 (S/km)
        b = 2.8e-6

        # 总参数
        R = r * line_length / num_circuits
        X = x * line_length / num_circuits
        B = b * line_length * num_circuits

        # 波阻抗
        Zc = math.sqrt(X / B) if B > 0 else 0

        # 自然功率
        Pn = voltage**2 / Zc if Zc > 0 else 0

        return {
            'resistance_ohm': R,
            'reactance_ohm': X,
            'susceptance_s': B,
            'wave_impedance_ohm': Zc,
            'natural_power_mw': Pn,
            'conductor_section_mm2': section
        }

    @staticmethod
    def sag_calculation(
        span_length: float,
        conductor_type: str,
        weather_condition: str = 'I类(轻冰区)',
        safety_factor: float = 2.5
    ) -> Dict[str, float]:
        """
        导线弧垂计算

        公式: f = (g × L²) / (8 × σ)

        Args:
            span_length: 档距 (m)
            conductor_type: 导线型号
            weather_condition: 气象条件
            safety_factor: 安全系数

        Returns:
            弧垂参数
        """
        conductor = TransmissionLineDesign.CONDUCTOR_DATA.get(conductor_type)
        if not conductor:
            raise ValueError(f"未知导线型号: {conductor_type}")

        section = conductor['section']  # mm²
        breaking_load = conductor['breaking_load']  # N
        weight = conductor['weight']  # kg/km

        # 最大使用应力 (MPa)
        max_stress = (breaking_load / section) / safety_factor

        # 比载 (N/m·mm²)
        weather = TransmissionLineDesign.WEATHER_CONDITIONS.get(weather_condition)
        ice_thickness = weather['ice'] if weather else 0

        # 自重比载
        g1 = weight * 9.8 / section / 1000

        # 冰重比载
        diameter = conductor['diameter']
        g2 = 0.9 * math.pi * ice_thickness * (diameter + ice_thickness) * 9.8 / section / 1000

        # 综合比载
        g = math.sqrt(g1**2 + g2**2)

        # 弧垂 (m)
        sag = g * span_length**2 / (8 * max_stress)

        return {
            'sag_m': sag,
            'max_stress_mpa': max_stress,
            'span_length_m': span_length,
            'specific_load_n_m_mm2': g,
            'safety_factor': safety_factor
        }

    @staticmethod
    def conductor_selection(
        transmission_power: float,
        voltage: float,
        line_length: float,
        max_voltage_drop: float = 10.0,
        economic_current_density: float = 1.15
    ) -> Dict[str, any]:
        """
        导线截面选择

        Args:
            transmission_power: 输送功率 (MW)
            voltage: 额定电压 (kV)
            line_length: 线路长度 (km)
            max_voltage_drop: 最大允许电压降 (%)
            economic_current_density: 经济电流密度 (A/mm²)

        Returns:
            导线选择结果
        """
        # 计算电流
        current = transmission_power * 1000 / (math.sqrt(3) * voltage)

        # 按经济电流密度选择
        required_section = current / economic_current_density

        # 选择标准截面
        selected_conductor = None
        for cond_type, data in TransmissionLineDesign.CONDUCTOR_DATA.items():
            if data['section'] >= required_section:
                selected_conductor = cond_type
                break

        if not selected_conductor:
            selected_conductor = 'LGJ-800'

        # 载流量校验
        conductor = TransmissionLineDesign.CONDUCTOR_DATA[selected_conductor]

        # 电压降校验
        r = 0.0315 / (conductor['section'] / 100)
        voltage_drop = math.sqrt(3) * current * r * line_length / (voltage * 1000) * 100

        return {
            'selected_conductor': selected_conductor,
            'section_mm2': conductor['section'],
            'calculated_current_a': current,
            'required_section_mm2': required_section,
            'voltage_drop_percent': voltage_drop,
            'meets_requirement': voltage_drop <= max_voltage_drop
        }

    @staticmethod
    def tower_load_calculation(
        span_length: float,
        conductor_type: str,
        wind_pressure: float = 350,
        ice_thickness: float = 0
    ) -> Dict[str, float]:
        """
        杆塔荷载计算

        Args:
            span_length: 档距 (m)
            conductor_type: 导线型号
            wind_pressure: 风压 (Pa)
            ice_thickness: 覆冰厚度 (mm)

        Returns:
            杆塔荷载
        """
        conductor = TransmissionLineDesign.CONDUCTOR_DATA.get(conductor_type)
        if not conductor:
            raise ValueError(f"未知导线型号: {conductor_type}")

        diameter = conductor['diameter'] / 1000  # m
        weight = conductor['weight']  # kg/km

        # 垂直荷载 (N)
        vertical_load = weight * 9.8 * span_length / 1000

        # 风荷载 (N)
        wind_load = wind_pressure * diameter * span_length

        # 综合荷载 (N)
        resultant_load = math.sqrt(vertical_load**2 + wind_load**2)

        return {
            'vertical_load_n': vertical_load,
            'wind_load_n': wind_load,
            'resultant_load_n': resultant_load,
            'span_length_m': span_length
        }

    @staticmethod
    def insulation_coordination(
        voltage: float,
        altitude: float = 0,
        pollution_level: str = 'II级'
    ) -> Dict[str, any]:
        """
        绝缘配合设计

        Args:
            voltage: 额定电压 (kV)
            altitude: 海拔高度 (m)
            pollution_level: 污秽等级

        Returns:
            绝缘配合参数
        """
        # 基准绝缘子片数
        base_insulators = {
            35: 3,
            66: 5,
            110: 7,
            220: 13,
            330: 19,
            500: 28,
        }

        # 污秽修正系数
        pollution_factor = {
            'I级': 1.0,
            'II级': 1.1,
            'III级': 1.2,
            'IV级': 1.3,
        }

        base_count = base_insulators.get(int(voltage), 7)
        factor = pollution_factor.get(pollution_level, 1.1)

        # 海拔修正
        altitude_factor = 1 + (altitude - 1000) / 1000 * 0.1 if altitude > 1000 else 1.0

        # 绝缘子片数
        insulator_count = int(base_count * factor * altitude_factor) + 1

        # 绝缘子串长度 (mm)
        insulator_length = insulator_count * 146  # 标准盘形绝缘子高度

        return {
            'insulator_count': insulator_count,
            'insulator_string_length_mm': insulator_length,
            'base_count': base_count,
            'pollution_factor': factor,
            'altitude_factor': altitude_factor
        }

    @staticmethod
    def grounding_design_tower(
        soil_resistivity: float,
        tower_type: str = 'concrete_pole',
        lightning_activity: str = 'moderate'
    ) -> Dict[str, any]:
        """
        杆塔接地设计

        Args:
            soil_resistivity: 土壤电阻率 (Ω·m)
            tower_type: 杆塔类型
            lightning_activity: 雷电活动强度

        Returns:
            接地设计参数
        """
        # 接地电阻要求值
        grounding_requirements = {
            'concrete_pole': 30,
            'iron_tower': 15,
        }

        required_r = grounding_requirements.get(tower_type, 30)

        # 水平接地体长度估算
        horizontal_length = 2 * math.pi * soil_resistivity / required_r

        # 垂直接地极数量
        vertical_rod_length = 2.5  # m
        vertical_rod_resistance = soil_resistivity / (2 * math.pi * vertical_rod_length) * math.log(4 * vertical_rod_length / 0.05)

        # 并联数量
        num_vertical = max(1, int(vertical_rod_resistance / required_r))

        return {
            'required_resistance_ohm': required_r,
            'horizontal_length_m': horizontal_length,
            'vertical_rod_count': num_vertical,
            'vertical_rod_length_m': vertical_rod_length,
            'estimated_resistance_ohm': soil_resistivity / (2 * math.pi * horizontal_length) * math.log(horizontal_length**2 / (0.8 * 0.01))
        }

