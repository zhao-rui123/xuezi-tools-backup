
"""
工业与民用配电设计手册（第四版）技能包
Power Distribution Design Skill Pack based on 
"Industrial and Civil Power Distribution Design Manual" 4th Edition

本技能包严格依据《工业与民用配电设计手册》第四版的内容编写，
涵盖了供配电系统设计的全流程计算方法。

主要功能模块：
1. 负荷计算模块
2. 短路电流计算模块
3. 电气设备选择模块
4. 电缆截面选择模块
5. 继电保护整定模块
6. 无功功率补偿模块
7. 接地设计模块
8. 电压降计算模块
9. 变压器选择模块
"""

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ==================== 数据类定义 ====================

@dataclass
class LoadCalculationResult:
    """负荷计算结果"""
    active_power: float  # 有功功率 P (kW)
    reactive_power: float  # 无功功率 Q (kvar)
    apparent_power: float  # 视在功率 S (kVA)
    calculation_current: float  # 计算电流 I (A)
    power_factor: float  # 功率因数

@dataclass
class ShortCircuitResult:
    """短路电流计算结果"""
    three_phase_current: float  # 三相短路电流 (kA)
    two_phase_current: float  # 两相短路电流 (kA)
    single_phase_current: float  # 单相短路电流 (kA)
    short_circuit_capacity: float  # 短路容量 (MVA)

@dataclass
class CableSelectionResult:
    """电缆选择结果"""
    cross_section: float  # 截面积 (mm²)
    current_carrying_capacity: float  # 载流量 (A)
    voltage_drop: float  # 电压降 (%)
    thermal_stability: bool  # 热稳定校验

@dataclass
class ProtectionSettingResult:
    """保护整定结果"""
    instantaneous_current: float  # 速断电流 (A)
    time_delay_current: float  # 过流定值 (A)
    time_delay: float  # 延时时间 (s)
    sensitivity: float  # 灵敏度

# ==================== 1. 负荷计算模块 ====================

class LoadCalculation:
    """
    负荷计算模块
    依据《工业与民用配电设计手册》第四版 第1章
    """

    # 常用设备需要系数表（来自手册表1.4-1）
    DEMAND_FACTORS = {
        '冷加工机床': {'Kd': 0.14, 'cosφ': 0.5, 'tanφ': 1.73},
        '热加工机床': {'Kd': 0.24, 'cosφ': 0.6, 'tanφ': 1.33},
        '风机、水泵': {'Kd': 0.75, 'cosφ': 0.8, 'tanφ': 0.75},
        '通风机': {'Kd': 0.75, 'cosφ': 0.8, 'tanφ': 0.75},
        '压缩机': {'Kd': 0.75, 'cosφ': 0.8, 'tanφ': 0.75},
        '起重机': {'Kd': 0.25, 'cosφ': 0.5, 'tanφ': 1.73},
        '电焊机': {'Kd': 0.35, 'cosφ': 0.6, 'tanφ': 1.33},
        '电阻炉': {'Kd': 0.8, 'cosφ': 0.95, 'tanφ': 0.33},
        '照明': {'Kd': 0.9, 'cosφ': 0.9, 'tanφ': 0.48},
        '住宅': {'Kd': 0.5, 'cosφ': 0.9, 'tanφ': 0.48},
        '办公楼': {'Kd': 0.7, 'cosφ': 0.9, 'tanφ': 0.48},
        '商场': {'Kd': 0.75, 'cosφ': 0.9, 'tanφ': 0.48},
        '医院': {'Kd': 0.6, 'cosφ': 0.8, 'tanφ': 0.75},
        '学校': {'Kd': 0.6, 'cosφ': 0.9, 'tanφ': 0.48},
    }

    @staticmethod
    def convert_equipment_power(rated_power: float, duty_cycle: float = 25) -> float:
        """
        将设备功率换算到统一负载持续率

        公式: Pe = Pn × √(εn / ε25)

        Args:
            rated_power: 额定功率 (kW)
            duty_cycle: 负载持续率 (%)

        Returns:
            换算后的设备功率 (kW)
        """
        if duty_cycle == 25:
            return rated_power
        return rated_power * math.sqrt(duty_cycle / 25)

    @staticmethod
    def demand_coefficient_method(
        equipment_powers: List[float],
        equipment_type: str,
        voltage: float = 0.38
    ) -> LoadCalculationResult:
        """
        需要系数法计算负荷

        公式（手册式1.4-1~1.4-4）:
        Pc = Kd × Pe
        Qc = Pc × tanφ
        Sc = √(Pc² + Qc²)
        Ic = Sc / (√3 × Un)

        Args:
            equipment_powers: 设备功率列表 (kW)
            equipment_type: 设备类型
            voltage: 额定电压 (kV)

        Returns:
            负荷计算结果
        """
        params = LoadCalculation.DEMAND_FACTORS.get(
            equipment_type, 
            {'Kd': 0.5, 'cosφ': 0.8, 'tanφ': 0.75}
        )

        Kd = params['Kd']
        cosφ = params['cosφ']
        tanφ = params['tanφ']

        # 设备总容量
        Pe = sum(equipment_powers)

        # 计算负荷
        Pc = Kd * Pe
        Qc = Pc * tanφ
        Sc = math.sqrt(Pc**2 + Qc**2)
        Ic = Sc / (math.sqrt(3) * voltage)

        return LoadCalculationResult(
            active_power=Pc,
            reactive_power=Qc,
            apparent_power=Sc,
            calculation_current=Ic,
            power_factor=cosφ
        )

    @staticmethod
    def utilization_coefficient_method(
        equipment_powers: List[float],
        utilization_coefficient: float = 0.4,
        max_coefficient: float = 1.2,
        power_factor: float = 0.8
    ) -> LoadCalculationResult:
        """
        利用系数法计算负荷

        公式（手册式1.5-1~1.5-4）:
        Pav = Ku × Pe
        Pc = Km × Pav

        Args:
            equipment_powers: 设备功率列表 (kW)
            utilization_coefficient: 利用系数 Ku
            max_coefficient: 最大系数 Km
            power_factor: 功率因数

        Returns:
            负荷计算结果
        """
        Pe = sum(equipment_powers)
        tanφ = math.sqrt(1 - power_factor**2) / power_factor

        # 平均负荷
        Pav = utilization_coefficient * Pe
        Qav = Pav * tanφ

        # 计算负荷
        Pc = max_coefficient * Pav
        Qc = max_coefficient * Qav
        Sc = math.sqrt(Pc**2 + Qc**2)
        Ic = Sc / (math.sqrt(3) * 0.38)

        return LoadCalculationResult(
            active_power=Pc,
            reactive_power=Qc,
            apparent_power=Sc,
            calculation_current=Ic,
            power_factor=power_factor
        )

    @staticmethod
    def unit_index_method(area: float, unit_index: float, power_factor: float = 0.9) -> LoadCalculationResult:
        """
        单位指标法计算负荷

        公式: Pc = Pe' × A

        Args:
            area: 建筑面积 (m²)
            unit_index: 单位指标 (W/m²)
            power_factor: 功率因数

        Returns:
            负荷计算结果
        """
        Pc = area * unit_index / 1000  # 转换为kW
        tanφ = math.sqrt(1 - power_factor**2) / power_factor
        Qc = Pc * tanφ
        Sc = math.sqrt(Pc**2 + Qc**2)
        Ic = Sc / (math.sqrt(3) * 0.38)

        return LoadCalculationResult(
            active_power=Pc,
            reactive_power=Qc,
            apparent_power=Sc,
            calculation_current=Ic,
            power_factor=power_factor
        )

    @staticmethod
    def calculate_with_simultaneity(
        load_results: List[LoadCalculationResult],
        simultaneity_factor_p: float = 0.9,
        simultaneity_factor_q: float = 0.95
    ) -> LoadCalculationResult:
        """
        考虑同时系数的总负荷计算

        Args:
            load_results: 各组负荷计算结果
            simultaneity_factor_p: 有功同时系数
            simultaneity_factor_q: 无功同时系数

        Returns:
            总负荷计算结果
        """
        total_p = sum(r.active_power for r in load_results)
        total_q = sum(r.reactive_power for r in load_results)

        Pc = simultaneity_factor_p * total_p
        Qc = simultaneity_factor_q * total_q
        Sc = math.sqrt(Pc**2 + Qc**2)
        Ic = Sc / (math.sqrt(3) * 0.38)
        pf = Pc / Sc if Sc > 0 else 1.0

        return LoadCalculationResult(
            active_power=Pc,
            reactive_power=Qc,
            apparent_power=Sc,
            calculation_current=Ic,
            power_factor=pf
        )

# ==================== 2. 短路电流计算模块 ====================

class ShortCircuitCalculation:
    """
    短路电流计算模块
    依据《工业与民用配电设计手册》第四版 第4章

    高压系统采用标幺值法
    低压系统采用有名值法（欧姆法）
    """

    @staticmethod
    def per_unit_system(
        system_capacity: float,  # 系统短路容量 (MVA)
        base_capacity: float = 100,  # 基准容量 (MVA)
        base_voltage: float = 10.5,  # 基准电压 (kV)
        line_length: float = 0,  # 线路长度 (km)
        line_impedance: float = 0.08,  # 线路单位阻抗 (Ω/km)
        transformer_capacity: float = 0,  # 变压器容量 (MVA)
        uk_percent: float = 4.5  # 变压器阻抗电压百分比
    ) -> ShortCircuitResult:
        """
        标幺值法计算短路电流（高压系统）

        公式（手册式4.2-1~4.2-15）:
        Xs* = Sb / Ss
        Xt* = (uk% / 100) × (Sb / Sn)
        Ik = Ib / Xtotal*

        Args:
            system_capacity: 系统短路容量 (MVA)
            base_capacity: 基准容量 (MVA)
            base_voltage: 基准电压 (kV)
            line_length: 线路长度 (km)
            line_impedance: 线路单位阻抗 (Ω/km)
            transformer_capacity: 变压器容量 (MVA)
            uk_percent: 变压器阻抗电压百分比

        Returns:
            短路电流计算结果
        """
        # 基准电流
        base_current = base_capacity / (math.sqrt(3) * base_voltage)

        # 系统阻抗标幺值
        Xs_pu = base_capacity / system_capacity if system_capacity > 0 else 0

        # 线路阻抗标幺值
        Zb = base_voltage**2 / base_capacity
        Xl_pu = (line_length * line_impedance) / Zb if line_length > 0 else 0

        # 变压器阻抗标幺值
        Xt_pu = (uk_percent / 100) * (base_capacity / transformer_capacity) if transformer_capacity > 0 else 0

        # 总阻抗
        X_total = Xs_pu + Xl_pu + Xt_pu

        # 三相短路电流
        Ik3 = base_current / X_total if X_total > 0 else 0

        # 两相短路电流
        Ik2 = math.sqrt(3) / 2 * Ik3

        # 单相短路电流（近似）
        Ik1 = Ik3 / math.sqrt(3)

        # 短路容量
        Sk = math.sqrt(3) * base_voltage * Ik3

        return ShortCircuitResult(
            three_phase_current=Ik3,
            two_phase_current=Ik2,
            single_phase_current=Ik1,
            short_circuit_capacity=Sk
        )

    @staticmethod
    def ohmic_method(
        system_voltage: float = 0.4,  # 系统电压 (kV)
        transformer_power: float = 1000,  # 变压器容量 (kVA)
        uk_percent: float = 4.5,  # 阻抗电压百分比
        line_length: float = 50,  # 线路长度 (m)
        cable_resistance: float = 0.193,  # 电缆单位电阻 (mΩ/m)
        cable_reactance: float = 0.08  # 电缆单位电抗 (mΩ/m)
    ) -> ShortCircuitResult:
        """
        有名值法（欧姆法）计算短路电流（低压系统）

        公式（手册式4.6-1~4.6-15）:
        Ik = c × Un / (√3 × Zk)

        Args:
            system_voltage: 系统电压 (kV)
            transformer_power: 变压器容量 (kVA)
            uk_percent: 阻抗电压百分比
            line_length: 线路长度 (m)
            cable_resistance: 电缆单位电阻 (mΩ/m)
            cable_reactance: 电缆单位电抗 (mΩ/m)

        Returns:
            短路电流计算结果
        """
        c = 1.05  # 电压系数

        # 变压器阻抗
        Zt = uk_percent / 100 * (system_voltage**2 / transformer_power) * 1000  # 转换为mΩ

        # 线路阻抗
        Rl = line_length * cable_resistance / 1000  # 转换为Ω
        Xl = line_length * cable_reactance / 1000

        # 总阻抗
        Z_total = math.sqrt((Zt + Rl)**2 + Xl**2)

        # 三相短路电流
        Ik3 = c * system_voltage / (math.sqrt(3) * Z_total / 1000)  # kA

        # 两相短路电流
        Ik2 = math.sqrt(3) / 2 * Ik3

        # 单相短路电流
        Ik1 = Ik3 / math.sqrt(3)

        # 短路容量
        Sk = math.sqrt(3) * system_voltage * Ik3

        return ShortCircuitResult(
            three_phase_current=Ik3,
            two_phase_current=Ik2,
            single_phase_current=Ik1,
            short_circuit_capacity=Sk
        )

# ==================== 3. 电缆截面选择模块 ====================

class CableSelection:
    """
    电缆截面选择模块
    依据《工业与民用配电设计手册》第四版 第9章
    """

    # 铜芯电缆载流量表（环境温度30℃，空气中敷设）
    # 截面积: [载流量(A)]
    CURRENT_CARRYING_CAPACITY = {
        1.5: 19,
        2.5: 26,
        4: 34,
        6: 44,
        10: 60,
        16: 80,
        25: 105,
        35: 130,
        50: 160,
        70: 200,
        95: 240,
        120: 275,
        150: 310,
        185: 355,
        240: 420,
        300: 480,
    }

    # 铜电阻率表 (Ω·mm²/m)
    COPPER_RESISTIVITY = {
        20: 0.0172,
        70: 0.0206,
        90: 0.0220,
    }

    @staticmethod
    def select_by_current(
        calculation_current: float,
        ambient_temperature: float = 30,
        installation_method: str = 'air'
    ) -> CableSelectionResult:
        """
        按载流量选择电缆截面

        Args:
            calculation_current: 计算电流 (A)
            ambient_temperature: 环境温度 (℃)
            installation_method: 敷设方式

        Returns:
            电缆选择结果
        """
        # 温度校正系数
        temp_factor = 1.0
        if ambient_temperature > 30:
            temp_factor = math.sqrt((70 - ambient_temperature) / (70 - 30))

        # 敷设方式校正系数
        method_factor = 1.0
        if installation_method == 'conduit':
            method_factor = 0.8
        elif installation_method == 'buried':
            method_factor = 0.9

        required_capacity = calculation_current / (temp_factor * method_factor)

        # 选择最小截面
        selected_section = None
        selected_capacity = None

        for section, capacity in sorted(CableSelection.CURRENT_CARRYING_CAPACITY.items()):
            if capacity >= required_capacity:
                selected_section = section
                selected_capacity = capacity * temp_factor * method_factor
                break

        if selected_section is None:
            selected_section = 300
            selected_capacity = CableSelection.CURRENT_CARRYING_CAPACITY[300] * temp_factor * method_factor

        return CableSelectionResult(
            cross_section=selected_section,
            current_carrying_capacity=selected_capacity,
            voltage_drop=0,
            thermal_stability=True
        )

    @staticmethod
    def calculate_voltage_drop(
        current: float,
        length: float,
        cross_section: float,
        voltage: float = 380,
        power_factor: float = 0.8,
        material: str = 'copper'
    ) -> float:
        """
        计算线路电压降

        公式（手册式9.4-1~9.4-4）:
        ΔU% = (√3 × I × L × (Rcosφ + Xsinφ)) / (10 × Un) × 100%

        Args:
            current: 电流 (A)
            length: 线路长度 (m)
            cross_section: 截面积 (mm²)
            voltage: 电压 (V)
            power_factor: 功率因数
            material: 导体材料

        Returns:
            电压降百分比 (%)
        """
        # 电阻率
        if material == 'copper':
            rho = 0.0172  # Ω·mm²/m
        else:
            rho = 0.0283  # 铝

        # 单位电阻和电抗
        R = rho / cross_section  # Ω/m
        X = 0.08 / 1000  # 电抗约0.08mΩ/m

        sinφ = math.sqrt(1 - power_factor**2)

        # 电压降
        delta_U = math.sqrt(3) * current * (length / 1000) * (R * power_factor + X * sinφ)
        delta_U_percent = (delta_U / (voltage / 1000)) * 100

        return delta_U_percent

    @staticmethod
    def thermal_stability_check(
        short_circuit_current: float,
        protection_time: float,
        cross_section: float,
        material: str = 'copper'
    ) -> bool:
        """
        热稳定校验

        公式（手册式9.5-1）:
        Smin = (I∞ × √t) / C

        Args:
            short_circuit_current: 短路电流 (kA)
            protection_time: 保护动作时间 (s)
            cross_section: 电缆截面积 (mm²)
            material: 导体材料

        Returns:
            是否满足热稳定要求
        """
        # 热稳定系数
        if material == 'copper':
            C = 143  # 铜芯电缆
        else:
            C = 94  # 铝芯电缆

        # 最小截面积
        Smin = (short_circuit_current * 1000 * math.sqrt(protection_time)) / C

        return cross_section >= Smin

    @staticmethod
    def select_cable(
        calculation_current: float,
        length: float,
        voltage: float = 380,
        power_factor: float = 0.8,
        max_voltage_drop: float = 5.0,
        short_circuit_current: float = 10,
        protection_time: float = 0.5
    ) -> CableSelectionResult:
        """
        综合选择电缆截面

        Args:
            calculation_current: 计算电流 (A)
            length: 线路长度 (m)
            voltage: 电压 (V)
            power_factor: 功率因数
            max_voltage_drop: 最大允许电压降 (%)
            short_circuit_current: 短路电流 (kA)
            protection_time: 保护动作时间 (s)

        Returns:
            电缆选择结果
        """
        # 1. 按载流量初选
        cable = CableSelection.select_by_current(calculation_current)

        # 2. 校验电压降
        voltage_drop = CableSelection.calculate_voltage_drop(
            calculation_current, length, cable.cross_section, voltage, power_factor
        )

        # 如果电压降超标，增大截面
        while voltage_drop > max_voltage_drop and cable.cross_section < 300:
            next_sections = [s for s in CableSelection.CURRENT_CARRYING_CAPACITY.keys() 
                           if s > cable.cross_section]
            if next_sections:
                cable.cross_section = min(next_sections)
                voltage_drop = CableSelection.calculate_voltage_drop(
                    calculation_current, length, cable.cross_section, voltage, power_factor
                )
            else:
                break

        # 3. 热稳定校验
        thermal_ok = CableSelection.thermal_stability_check(
            short_circuit_current, protection_time, cable.cross_section
        )

        cable.voltage_drop = voltage_drop
        cable.thermal_stability = thermal_ok

        return cable

# ==================== 4. 继电保护整定模块 ====================

class ProtectionSetting:
    """
    继电保护整定模块
    依据《工业与民用配电设计手册》第四版 第7章
    """

    @staticmethod
    def instantaneous_overcurrent(
        max_short_circuit_current: float,
        reliability_factor: float = 1.3
    ) -> float:
        """
        电流速断保护整定

        公式（手册式7.3-1）:
        Iop = Krel × Ik.max

        Args:
            max_short_circuit_current: 最大短路电流 (A)
            reliability_factor: 可靠系数

        Returns:
            速断保护定值 (A)
        """
        return reliability_factor * max_short_circuit_current

    @staticmethod
    def time_overcurrent(
        max_load_current: float,
        self_starting_factor: float = 1.5,
        return_coefficient: float = 0.95,
        reliability_factor: float = 1.2
    ) -> float:
        """
        过电流保护整定

        公式（手册式7.3-2）:
        Iop = (Krel × Kast / Kr) × IL.max

        Args:
            max_load_current: 最大负荷电流 (A)
            self_starting_factor: 自启动系数
            return_coefficient: 返回系数
            reliability_factor: 可靠系数

        Returns:
            过流保护定值 (A)
        """
        return (reliability_factor * self_starting_factor / return_coefficient) * max_load_current

    @staticmethod
    def time_grading(
        downstream_time: float,
        time_step: float = 0.3
    ) -> float:
        """
        时间级差配合

        Args:
            downstream_time: 下级保护动作时间 (s)
            time_step: 时间级差 (s)

        Returns:
            本级保护动作时间 (s)
        """
        return downstream_time + time_step

    @staticmethod
    def sensitivity_check(
        min_short_circuit_current: float,
        protection_setting: float
    ) -> float:
        """
        灵敏度校验

        公式（手册式7.3-3）:
        Ksen = Ik.min / Iop

        Args:
            min_short_circuit_current: 最小短路电流 (A)
            protection_setting: 保护定值 (A)

        Returns:
            灵敏度系数
        """
        return min_short_circuit_current / protection_setting if protection_setting > 0 else 0

    @staticmethod
    def motor_protection(
        motor_rated_current: float,
        starting_current_multiple: float = 7,
        starting_time: float = 5
    ) -> ProtectionSettingResult:
        """
        电动机保护整定

        Args:
            motor_rated_current: 电动机额定电流 (A)
            starting_current_multiple: 启动电流倍数
            starting_time: 启动时间 (s)

        Returns:
            保护整定结果
        """
        # 长延时整定
        long_delay_current = motor_rated_current

        # 瞬时整定（躲过启动电流）
        instantaneous_current = 1.35 * starting_current_multiple * motor_rated_current

        # 短延时整定
        time_delay_current = 1.2 * motor_rated_current
        time_delay = 0.3

        # 灵敏度
        sensitivity = 8.0 / instantaneous_current if instantaneous_current > 0 else 0

        return ProtectionSettingResult(
            instantaneous_current=instantaneous_current,
            time_delay_current=time_delay_current,
            time_delay=time_delay,
            sensitivity=sensitivity
        )

# ==================== 5. 无功功率补偿模块 ====================

class ReactivePowerCompensation:
    """
    无功功率补偿模块
    依据《工业与民用配电设计手册》第四版 第1.11节
    """

    @staticmethod
    def compensation_capacity(
        active_power: float,
        cos_phi1: float,
        cos_phi2: float
    ) -> float:
        """
        计算无功补偿容量

        公式（手册式1.11-7）:
        Qc = P × (tanφ1 - tanφ2)

        Args:
            active_power: 有功功率 (kW)
            cos_phi1: 补偿前功率因数
            cos_phi2: 补偿后功率因数

        Returns:
            补偿容量 (kvar)
        """
        tan_phi1 = math.sqrt(1 - cos_phi1**2) / cos_phi1
        tan_phi2 = math.sqrt(1 - cos_phi2**2) / cos_phi2

        Qc = active_power * (tan_phi1 - tan_phi2)

        return Qc

    @staticmethod
    def capacitor_output(
        rated_capacity: float,
        actual_voltage: float,
        rated_voltage: float
    ) -> float:
        """
        计算电容器实际输出容量

        公式（手册式1.11-12）:
        Q = QN × (U / UN)²

        Args:
            rated_capacity: 额定容量 (kvar)
            actual_voltage: 实际电压 (kV)
            rated_voltage: 额定电压 (kV)

        Returns:
            实际输出容量 (kvar)
        """
        return rated_capacity * (actual_voltage / rated_voltage)**2

    @staticmethod
    def transformer_compensation(
        transformer_capacity: float,
        load_factor: float = 0.7,
        compensation_rate: float = 0.3
    ) -> float:
        """
        变压器无功补偿容量估算

        公式: Qc = S × β × k

        Args:
            transformer_capacity: 变压器容量 (kVA)
            load_factor: 负载率
            compensation_rate: 补偿率

        Returns:
            补偿容量 (kvar)
        """
        return transformer_capacity * load_factor * compensation_rate

# ==================== 6. 接地设计模块 ====================

class GroundingDesign:
    """
    接地设计模块
    依据《工业与民用配电设计手册》第四版 第14章
    """

    # 土壤电阻率参考值 (Ω·m)
    SOIL_RESISTIVITY = {
        '沼泽地': 5,
        '黑土': 20,
        '粘土': 40,
        '砂质粘土': 80,
        '黄土': 150,
        '砂土': 300,
        '多石土壤': 500,
        '岩石': 1000,
    }

    @staticmethod
    def horizontal_grounding_resistance(
        length: float,
        diameter: float,
        burial_depth: float,
        soil_resistivity: float
    ) -> float:
        """
        水平接地极接地电阻计算

        公式（手册式14.6-1）:
        R = (ρ / (2πL)) × ln(L² / (hd))

        Args:
            length: 接地极长度 (m)
            diameter: 接地极直径 (m)
            burial_depth: 埋设深度 (m)
            soil_resistivity: 土壤电阻率 (Ω·m)

        Returns:
            接地电阻 (Ω)
        """
        R = (soil_resistivity / (2 * math.pi * length)) * math.log(length**2 / (burial_depth * diameter))
        return R

    @staticmethod
    def vertical_grounding_resistance(
        length: float,
        diameter: float,
        soil_resistivity: float
    ) -> float:
        """
        垂直接地极接地电阻计算

        公式（手册式14.6-2）:
        R = (ρ / (2πL)) × ln(4L / d)

        Args:
            length: 接地极长度 (m)
            diameter: 接地极直径 (m)
            soil_resistivity: 土壤电阻率 (Ω·m)

        Returns:
            接地电阻 (Ω)
        """
        R = (soil_resistivity / (2 * math.pi * length)) * math.log(4 * length / diameter)
        return R

    @staticmethod
    def grounding_grid_resistance(
        area: float,
        soil_resistivity: float,
        total_length: float
    ) -> float:
        """
        接地网接地电阻计算

        公式（手册式14.6-3）:
        R = 0.5 × ρ / √S

        Args:
            area: 接地网面积 (m²)
            soil_resistivity: 土壤电阻率 (Ω·m)
            total_length: 接地体总长度 (m)

        Returns:
            接地电阻 (Ω)
        """
        R = 0.5 * soil_resistivity / math.sqrt(area)
        return R

    @staticmethod
    def seasonal_correction(
        resistivity: float,
        season: str = 'dry'
    ) -> float:
        """
        季节系数修正

        Args:
            resistivity: 测量电阻率 (Ω·m)
            season: 季节

        Returns:
            修正后电阻率 (Ω·m)
        """
        factors = {
            'wet': 0.8,
            'normal': 1.0,
            'dry': 1.3,
            'frozen': 1.8,
        }

        return resistivity * factors.get(season, 1.0)

# ==================== 7. 变压器选择模块 ====================

class TransformerSelection:
    """
    变压器选择模块
    依据《工业与民用配电设计手册》第四版 第3章
    """

    @staticmethod
    def select_by_load(
        apparent_power: float,
        load_factor: float = 0.7,
        growth_factor: float = 1.2
    ) -> float:
        """
        按负荷选择变压器容量

        公式: Sn ≥ Pc / β

        Args:
            apparent_power: 计算负荷 (kVA)
            load_factor: 负载率
            growth_factor: 发展系数

        Returns:
            变压器容量 (kVA)
        """
        required_capacity = apparent_power * growth_factor / load_factor

        # 选择标准容量
        standard_capacities = [100, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 
                              1250, 1600, 2000, 2500]

        for capacity in standard_capacities:
            if capacity >= required_capacity:
                return capacity

        return 2500

    @staticmethod
    def economic_load_rate(
        no_load_loss: float,
        load_loss: float
    ) -> float:
        """
        计算经济负载率

        公式: β = √(P0 / Pk)

        Args:
            no_load_loss: 空载损耗 (kW)
            load_loss: 负载损耗 (kW)

        Returns:
            经济负载率
        """
        if load_loss > 0:
            return math.sqrt(no_load_loss / load_loss)
        return 0.5

    @staticmethod
    def annual_energy_loss(
        no_load_loss: float,
        load_loss: float,
        load_factor: float,
        operating_hours: float = 8760
    ) -> float:
        """
        计算年电能损耗

        公式: ΔW = (P0 + β² × Pk) × T

        Args:
            no_load_loss: 空载损耗 (kW)
            load_loss: 负载损耗 (kW)
            load_factor: 负载率
            operating_hours: 运行小时数

        Returns:
            年电能损耗 (kWh)
        """
        return (no_load_loss + load_factor**2 * load_loss) * operating_hours

    @staticmethod
    def voltage_regulation(
        uk_percent: float,
        load_factor: float,
        power_factor: float
    ) -> float:
        """
        计算电压调整率

        公式: ΔU% = β × (uk% × cosφ + ur% × sinφ)

        Args:
            uk_percent: 阻抗电压百分比
            load_factor: 负载率
            power_factor: 功率因数

        Returns:
            电压调整率 (%)
        """
        sinφ = math.sqrt(1 - power_factor**2)
        ur_percent = uk_percent * 0.1  # 近似值

        return load_factor * (uk_percent * power_factor + ur_percent * sinφ)

# ==================== 8. 断路器选择模块 ====================

class CircuitBreakerSelection:
    """
    断路器选择模块
    依据《工业与民用配电设计手册》第四版 第5章和第11章
    """

    @staticmethod
    def select_rated_current(
        calculation_current: float,
        margin: float = 1.25
    ) -> float:
        """
        选择断路器额定电流

        Args:
            calculation_current: 计算电流 (A)
            margin: 裕量系数

        Returns:
            断路器额定电流 (A)
        """
        required_current = calculation_current * margin

        # 标准额定电流系列
        standard_currents = [6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 
                            125, 160, 200, 250, 315, 400, 500, 630, 800, 1000]

        for current in standard_currents:
            if current >= required_current:
                return current

        return 1000

    @staticmethod
    def select_breaking_capacity(
        short_circuit_current: float,
        margin: float = 1.2
    ) -> float:
        """
        选择断路器分断能力

        Args:
            short_circuit_current: 短路电流 (kA)
            margin: 裕量系数

        Returns:
            分断能力 (kA)
        """
        required_capacity = short_circuit_current * margin

        # 标准分断能力系列
        standard_capacities = [6, 10, 15, 20, 25, 35, 50, 65, 85, 100, 150]

        for capacity in standard_capacities:
            if capacity >= required_capacity:
                return capacity

        return 150

    @staticmethod
    def motor_circuit_breaker(
        motor_rated_current: float,
        starting_current: float,
        starting_time: float = 5
    ) -> Dict:
        """
        电动机保护断路器选择

        Args:
            motor_rated_current: 电动机额定电流 (A)
            starting_current: 启动电流 (A)
            starting_time: 启动时间 (s)

        Returns:
            断路器参数
        """
        # 额定电流
        rated_current = CircuitBreakerSelection.select_rated_current(motor_rated_current, 1.1)

        # 长延时整定
        long_delay = motor_rated_current

        # 瞬时整定（躲过启动电流）
        instantaneous = 1.35 * starting_current

        # 脱扣曲线
        if starting_current / motor_rated_current <= 6:
            curve = 'C'
        else:
            curve = 'D'

        return {
            'rated_current': rated_current,
            'long_delay': long_delay,
            'instantaneous': instantaneous,
            'curve': curve,
            'starting_time': starting_time
        }

# ==================== 9. 主计算类 ====================

class PowerDesignCalculator:
    """
    电力设计综合计算器
    整合所有计算模块，提供一站式计算服务
    """

    def __init__(self):
        self.load_calc = LoadCalculation()
        self.short_calc = ShortCircuitCalculation()
        self.cable_select = CableSelection()
        self.protection = ProtectionSetting()
        self.compensation = ReactivePowerCompensation()
        self.grounding = GroundingDesign()
        self.transformer = TransformerSelection()
        self.breaker = CircuitBreakerSelection()

    def calculate_distribution_system(
        self,
        equipment_data: List[Dict],
        system_voltage: float = 0.38,
        transformer_capacity: float = 1000
    ) -> Dict:
        """
        计算配电系统全套参数

        Args:
            equipment_data: 设备数据列表
                [{"power": 10, "type": "风机、水泵", "count": 5}, ...]
            system_voltage: 系统电压 (kV)
            transformer_capacity: 变压器容量 (kVA)

        Returns:
            计算结果字典
        """
        results = {
            'loads': [],
            'total_load': None,
            'short_circuit': None,
            'transformer_check': None,
            'cables': [],
            'protections': []
        }

        # 1. 计算各组负荷
        for equipment in equipment_data:
            powers = [equipment['power']] * equipment['count']
            load = self.load_calc.demand_coefficient_method(
                powers, equipment['type'], system_voltage
            )
            results['loads'].append({
                'name': equipment['type'],
                'result': load
            })

        # 2. 计算总负荷
        load_results = [item['result'] for item in results['loads']]
        results['total_load'] = self.load_calc.calculate_with_simultaneity(load_results)

        # 3. 计算短路电流
        results['short_circuit'] = self.short_calc.ohmic_method(
            system_voltage, transformer_capacity
        )

        # 4. 变压器校验
        results['transformer_check'] = {
            'load_rate': results['total_load'].apparent_power / transformer_capacity * 100,
            'is_suitable': results['total_load'].apparent_power <= transformer_capacity * 0.85
        }

        # 5. 电缆和保护选择
        for load in results['loads']:
            cable = self.cable_select.select_cable(
                load['result'].calculation_current,
                50,  # 假设线路长度50m
                short_circuit_current=results['short_circuit'].three_phase_current
            )
            results['cables'].append({
                'name': load['name'],
                'cable': cable
            })

            protection = self.protection.motor_protection(
                load['result'].calculation_current
            )
            results['protections'].append({
                'name': load['name'],
                'protection': protection
            })

        return results

    def generate_calculation_report(self, results: Dict) -> str:
        """
        生成计算报告

        Args:
            results: 计算结果

        Returns:
            计算报告文本
        """
        report = []
        report.append("=" * 60)
        report.append("电力系统设计计算报告")
        report.append("依据《工业与民用配电设计手册》第四版")
        report.append("=" * 60)

        # 负荷计算
        report.append("\n一、负荷计算结果")
        report.append("-" * 60)
        for load in results['loads']:
            report.append(f"\n{load['name']}:")
            report.append(f"  有功功率 P = {load['result'].active_power:.2f} kW")
            report.append(f"  无功功率 Q = {load['result'].reactive_power:.2f} kvar")
            report.append(f"  视在功率 S = {load['result'].apparent_power:.2f} kVA")
            report.append(f"  计算电流 I = {load['result'].calculation_current:.2f} A")
            report.append(f"  功率因数 cosφ = {load['result'].power_factor:.2f}")

        # 总负荷
        if results['total_load']:
            report.append(f"\n总计算负荷:")
            report.append(f"  有功功率 P = {results['total_load'].active_power:.2f} kW")
            report.append(f"  无功功率 Q = {results['total_load'].reactive_power:.2f} kvar")
            report.append(f"  视在功率 S = {results['total_load'].apparent_power:.2f} kVA")
            report.append(f"  计算电流 I = {results['total_load'].calculation_current:.2f} A")

        # 短路电流
        if results['short_circuit']:
            report.append("\n二、短路电流计算结果")
            report.append("-" * 60)
            report.append(f"  三相短路电流: {results['short_circuit'].three_phase_current:.2f} kA")
            report.append(f"  两相短路电流: {results['short_circuit'].two_phase_current:.2f} kA")
            report.append(f"  单相短路电流: {results['short_circuit'].single_phase_current:.2f} kA")
            report.append(f"  短路容量: {results['short_circuit'].short_circuit_capacity:.2f} MVA")

        # 变压器校验
        if results['transformer_check']:
            report.append("\n三、变压器校验")
            report.append("-" * 60)
            report.append(f"  负载率: {results['transformer_check']['load_rate']:.1f}%")
            report.append(f"  是否满足: {'是' if results['transformer_check']['is_suitable'] else '否'}")

        # 电缆选择
        report.append("\n四、电缆截面选择")
        report.append("-" * 60)
        for cable in results['cables']:
            report.append(f"\n{cable['name']}:")
            report.append(f"  电缆截面: {cable['cable'].cross_section} mm²")
            report.append(f"  载流量: {cable['cable'].current_carrying_capacity:.1f} A")
            report.append(f"  电压降: {cable['cable'].voltage_drop:.2f}%")
            report.append(f"  热稳定校验: {'通过' if cable['cable'].thermal_stability else '不通过'}")

        # 保护整定
        report.append("\n五、保护整定")
        report.append("-" * 60)
        for protection in results['protections']:
            report.append(f"\n{protection['name']}:")
            report.append(f"  速断电流: {protection['protection'].instantaneous_current:.1f} A")
            report.append(f"  过流定值: {protection['protection'].time_delay_current:.1f} A")
            report.append(f"  延时时间: {protection['protection'].time_delay:.1f} s")
            report.append(f"  灵敏度: {protection['protection'].sensitivity:.2f}")

        report.append("\n" + "=" * 60)
        report.append("计算完成")
        report.append("=" * 60)

        return "\n".join(report)


# ==================== 10. 便捷函数 ====================

def calculate_load(
    powers: List[float],
    equipment_type: str = "风机、水泵",
    voltage: float = 0.38
) -> LoadCalculationResult:
    """便捷函数：计算负荷"""
    return LoadCalculation.demand_coefficient_method(powers, equipment_type, voltage)

def calculate_short_circuit(
    system_voltage: float = 0.4,
    transformer_power: float = 1000,
    line_length: float = 50
) -> ShortCircuitResult:
    """便捷函数：计算短路电流"""
    return ShortCircuitCalculation.ohmic_method(system_voltage, transformer_power)

def select_cable(
    current: float,
    length: float,
    voltage: float = 380,
    max_voltage_drop: float = 5.0
) -> CableSelectionResult:
    """便捷函数：选择电缆"""
    return CableSelection.select_cable(current, length, voltage, max_voltage_drop=max_voltage_drop)

def compensate_reactive_power(
    active_power: float,
    cos_phi1: float,
    cos_phi2: float = 0.95
) -> float:
    """便捷函数：计算无功补偿容量"""
    return ReactivePowerCompensation.compensation_capacity(active_power, cos_phi1, cos_phi2)

def design_grounding(
    area: float,
    soil_type: str = "粘土"
) -> float:
    """便捷函数：设计接地系统"""
    resistivity = GroundingDesign.SOIL_RESISTIVITY.get(soil_type, 40)
    return GroundingDesign.grounding_grid_resistance(area, resistivity, 100)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 创建计算器实例
    calculator = PowerDesignCalculator()

    # 定义设备数据
    equipment_data = [
        {"power": 7.5, "type": "冷加工机床", "count": 10},
        {"power": 5.5, "type": "风机、水泵", "count": 5},
        {"power": 2.0, "type": "照明", "count": 20},
    ]

    # 执行全套计算
    results = calculator.calculate_distribution_system(
        equipment_data,
        system_voltage=0.38,
        transformer_capacity=500
    )

    # 生成计算报告
    report = calculator.generate_calculation_report(results)
    print(report)
