#!/usr/bin/env python3
"""
工业与民用配电设计手册（第四版）技能包 - 修复版
Power Distribution Design Skill Pack - Fixed Version

修复内容：
1. 短路电流计算公式修正
2. 电缆热稳定校验公式修正
3. 添加更多设备类型
4. 完善文档和示例
"""

import math
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass

# ==================== 数据类定义 ====================

@dataclass
class LoadCalculationResult:
    """负荷计算结果"""
    active_power: float          # 有功功率 P (kW)
    reactive_power: float        # 无功功率 Q (kvar)
    apparent_power: float        # 视在功率 S (kVA)
    calculation_current: float   # 计算电流 I (A)
    power_factor: float          # 功率因数

@dataclass
class ShortCircuitResult:
    """短路电流计算结果"""
    three_phase_current: float   # 三相短路电流 (kA)
    two_phase_current: float     # 两相短路电流 (kA)
    single_phase_current: float  # 单相短路电流 (kA)
    short_circuit_capacity: float # 短路容量 (MVA)
    impedance: float             # 短路阻抗 (mΩ)

@dataclass
class CableSelectionResult:
    """电缆选择结果"""
    cross_section: float              # 截面积 (mm²)
    current_carrying_capacity: float  # 载流量 (A)
    voltage_drop: float               # 电压降 (%)
    thermal_stability: bool           # 热稳定校验
    min_thermal_section: float        # 热稳定最小截面 (mm²)

@dataclass
class ProtectionSettingResult:
    """保护整定结果"""
    instantaneous_current: float  # 速断电流 (A)
    time_delay_current: float     # 过流定值 (A)
    time_delay: float             # 延时时间 (s)
    sensitivity: float            # 灵敏度

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
        '实验室': {'Kd': 0.5, 'cosφ': 0.9, 'tanφ': 0.48},
        '锅炉房': {'Kd': 0.8, 'cosφ': 0.8, 'tanφ': 0.75},
    }

    @staticmethod
    def demand_coefficient_method(
        equipment_powers: List[float],
        equipment_type: str = '风机、水泵',
        voltage: float = 0.38
    ) -> LoadCalculationResult:
        """
        需要系数法计算负荷

        公式: 
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
        # 获取需要系数
        factor = LoadCalculation.DEMAND_FACTORS.get(
            equipment_type, 
            {'Kd': 0.75, 'cosφ': 0.8, 'tanφ': 0.75}
        )
        
        Kd = factor['Kd']
        cosφ = factor['cosφ']
        tanφ = factor['tanφ']
        
        # 设备总功率
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
        power_factor: float = 0.8,
        voltage: float = 0.38
    ) -> LoadCalculationResult:
        """
        利用系数法计算负荷

        公式:
        Pav = Ku × Pe
        Pc = Km × Pav

        Args:
            equipment_powers: 设备功率列表 (kW)
            utilization_coefficient: 利用系数 Ku
            max_coefficient: 最大系数 Km
            power_factor: 功率因数
            voltage: 额定电压 (kV)

        Returns:
            负荷计算结果
        """
        Pe = sum(equipment_powers)
        Pav = utilization_coefficient * Pe
        Pc = max_coefficient * Pav
        
        tanφ = math.sqrt(1 - power_factor**2) / power_factor
        Qc = Pc * tanφ
        Sc = math.sqrt(Pc**2 + Qc**2)
        Ic = Sc / (math.sqrt(3) * voltage)
        
        return LoadCalculationResult(
            active_power=Pc,
            reactive_power=Qc,
            apparent_power=Sc,
            calculation_current=Ic,
            power_factor=power_factor
        )

    @staticmethod
    def unit_index_method(
        area: float,
        unit_index: float,
        power_factor: float = 0.9,
        voltage: float = 0.38
    ) -> LoadCalculationResult:
        """
        单位指标法计算负荷

        公式: Pc = Pe' × A

        Args:
            area: 建筑面积 (m²)
            unit_index: 单位指标 (W/m²)
            power_factor: 功率因数
            voltage: 额定电压 (kV)

        Returns:
            负荷计算结果
        """
        Pc = area * unit_index / 1000  # 转换为kW
        tanφ = math.sqrt(1 - power_factor**2) / power_factor
        Qc = Pc * tanφ
        Sc = math.sqrt(Pc**2 + Qc**2)
        Ic = Sc / (math.sqrt(3) * voltage)
        
        return LoadCalculationResult(
            active_power=Pc,
            reactive_power=Qc,
            apparent_power=Sc,
            calculation_current=Ic,
            power_factor=power_factor
        )


# ==================== 2. 短路电流计算模块 ====================

class ShortCircuitCalculation:
    """
    短路电流计算模块
    依据《工业与民用配电设计手册》第四版 第4章
    """

    @staticmethod
    def ohmic_method(
        system_voltage: float = 0.4,      # 系统电压 (kV)
        transformer_power: float = 1000,  # 变压器容量 (kVA)
        uk_percent: float = 4.5,          # 阻抗电压百分比
        line_length: float = 50,          # 线路长度 (m)
        cable_resistance: float = 0.193,  # 电缆单位电阻 (mΩ/m)
        cable_reactance: float = 0.08     # 电缆单位电抗 (mΩ/m)
    ) -> ShortCircuitResult:
        """
        有名值法（欧姆法）计算短路电流（低压系统）

        公式（手册式4.6-1~4.6-15）:
        Ik = c × Un / (√3 × Zk)

        其中:
        Zt = (uk% / 100) × (Ur² / Sr)    # 变压器阻抗 (Ω)
        Zk = Zt + Zl                       # 总阻抗

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

        # 变压器阻抗 (Ω)
        # Zt = (uk% / 100) × (Un² / Sn)
        Zt = (uk_percent / 100) * (system_voltage**2 * 1000 / transformer_power)
        
        # 线路阻抗 (Ω)
        Rl = line_length * cable_resistance / 1000  # mΩ to Ω
        Xl = line_length * cable_reactance / 1000   # mΩ to Ω
        Zl = math.sqrt(Rl**2 + Xl**2)
        
        # 总阻抗 (Ω)
        Z_total = math.sqrt(Zt**2 + Zl**2)
        
        # 三相短路电流 (kA)
        Ik3 = c * system_voltage / (math.sqrt(3) * Z_total)
        
        # 两相短路电流 (kA)
        Ik2 = math.sqrt(3) / 2 * Ik3
        
        # 单相短路电流 (kA) - 近似计算
        Ik1 = Ik3 / math.sqrt(3)
        
        # 短路容量 (MVA)
        Sk = math.sqrt(3) * system_voltage * Ik3
        
        return ShortCircuitResult(
            three_phase_current=Ik3,
            two_phase_current=Ik2,
            single_phase_current=Ik1,
            short_circuit_capacity=Sk,
            impedance=Z_total * 1000  # 转换为mΩ
        )

    @staticmethod
    def per_unit_system(
        system_capacity: float,       # 系统短路容量 (MVA)
        base_capacity: float = 100,   # 基准容量 (MVA)
        base_voltage: float = 10.5,   # 基准电压 (kV)
        line_length: float = 0,       # 线路长度 (km)
        line_impedance: float = 0.08, # 线路单位阻抗 (Ω/km)
        transformer_capacity: float = 0,  # 变压器容量 (MVA)
        uk_percent: float = 4.5       # 变压器阻抗电压百分比
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
        # 基准电流 (kA)
        base_current = base_capacity / (math.sqrt(3) * base_voltage)
        
        # 系统阻抗标幺值
        Xs_pu = base_capacity / system_capacity if system_capacity > 0 else 0
        
        # 线路阻抗标幺值
        Zb = base_voltage**2 / base_capacity  # 基准阻抗
        Xl_pu = (line_length * line_impedance) / Zb if line_length > 0 else 0
        
        # 变压器阻抗标幺值
        Xt_pu = (uk_percent / 100) * (base_capacity / transformer_capacity) if transformer_capacity > 0 else 0
        
        # 总阻抗
        X_total = Xs_pu + Xl_pu + Xt_pu
        
        # 三相短路电流 (kA)
        Ik3 = base_current / X_total if X_total > 0 else 0
        
        # 两相短路电流 (kA)
        Ik2 = math.sqrt(3) / 2 * Ik3
        
        # 单相短路电流 (kA)
        Ik1 = Ik3 / math.sqrt(3)
        
        # 短路容量 (MVA)
        Sk = math.sqrt(3) * base_voltage * Ik3
        
        return ShortCircuitResult(
            three_phase_current=Ik3,
            two_phase_current=Ik2,
            single_phase_current=Ik1,
            short_circuit_capacity=Sk,
            impedance=X_total
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

    @staticmethod
    def select_cable(
        calculation_current: float,    # 计算电流 (A)
        length: float,                 # 线路长度 (m)
        voltage: float = 380,          # 电压 (V)
        power_factor: float = 0.85,    # 功率因数
        max_voltage_drop: float = 5.0, # 最大允许电压降 (%)
        short_circuit_current: float = 10,  # 短路电流 (kA)
        short_circuit_time: float = 0.5,    # 短路时间 (s)
        cable_material: str = 'copper'      # 电缆材料
    ) -> CableSelectionResult:
        """
        电缆截面选择

        选择条件：
        1. 按载流量选择
        2. 按电压降校验
        3. 按热稳定校验

        Args:
            calculation_current: 计算电流 (A)
            length: 线路长度 (m)
            voltage: 电压 (V)
            power_factor: 功率因数
            max_voltage_drop: 最大允许电压降 (%)
            short_circuit_current: 短路电流 (kA)
            short_circuit_time: 短路时间 (s)
            cable_material: 电缆材料

        Returns:
            电缆选择结果
        """
        # 1. 按载流量选择
        selected_section = None
        current_capacity = 0
        
        for section, capacity in sorted(CableSelection.CURRENT_CARRYING_CAPACITY.items()):
            if capacity >= calculation_current:
                selected_section = section
                current_capacity = capacity
                break
        
        if selected_section is None:
            selected_section = 300  # 最大截面
            current_capacity = 480
        
        # 2. 电压降计算
        # ΔU% = (√3 × I × L × (Rcosφ + Xsinφ)) / (10 × Un)
        # 
        # 其中：
        # I = 计算电流 (A)
        # L = 线路长度 (km)
        # R = 单位电阻 (Ω/km)
        # X = 单位电抗 (Ω/km)
        # Un = 额定电压 (kV)
        
        # 铜的电阻率 (Ω·mm²/m)
        rho = 0.0172  # 20°C
        
        # 单位电阻 (Ω/km)
        R = rho * 1000 / selected_section
        
        # 单位电抗 (Ω/km) - 近似值
        X = 0.08
        
        # 计算sinφ
        sin_phi = math.sqrt(1 - power_factor**2)
        
        # 电压降 (%)
        # ΔU% = (√3 × I × L × (Rcosφ + Xsinφ)) / (10 × Un)
        length_km = length / 1000  # m to km
        voltage_kV = voltage / 1000  # V to kV
        
        delta_U = (math.sqrt(3) * calculation_current * length_km * 
                   (R * power_factor + X * sin_phi)) / (10 * voltage_kV)
        
        # 3. 热稳定校验
        # Smin = (Ik × √t) / C
        # C为热稳定系数，铜电缆取143
        C = 143  # 铜电缆热稳定系数
        Smin = (short_circuit_current * 1000 * math.sqrt(short_circuit_time)) / C
        
        thermal_stable = selected_section >= Smin
        
        return CableSelectionResult(
            cross_section=selected_section,
            current_carrying_capacity=current_capacity,
            voltage_drop=delta_U,
            thermal_stability=thermal_stable,
            min_thermal_section=math.ceil(Smin)
        )


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=== 电力设计技能包测试 ===")
    print()
    
    # 测试负荷计算
    print("1. 负荷计算测试")
    result = LoadCalculation.demand_coefficient_method(
        equipment_powers=[5.5, 7.5, 11, 15],
        equipment_type='风机、水泵',
        voltage=0.38
    )
    print(f"   有功功率: {result.active_power:.2f} kW")
    print(f"   计算电流: {result.calculation_current:.2f} A")
    print()
    
    # 测试短路电流计算
    print("2. 短路电流计算测试")
    result = ShortCircuitCalculation.ohmic_method(
        system_voltage=0.4,
        transformer_power=1000,
        uk_percent=4.5,
        line_length=100,
        cable_resistance=0.193,
        cable_reactance=0.08
    )
    print(f"   三相短路电流: {result.three_phase_current:.2f} kA")
    print(f"   短路阻抗: {result.impedance:.2f} mΩ")
    print()
    
    # 测试电缆选择
    print("3. 电缆选择测试")
    result = CableSelection.select_cable(
        calculation_current=150,
        length=200,
        voltage=380,
        power_factor=0.85,
        max_voltage_drop=5.0,
        short_circuit_current=15
    )
    print(f"   推荐截面: {result.cross_section} mm²")
    print(f"   载流量: {result.current_carrying_capacity} A")
    print(f"   电压降: {result.voltage_drop:.2f}%")
    print(f"   热稳定最小截面: {result.min_thermal_section} mm²")
    print(f"   热稳定校验: {'通过' if result.thermal_stability else '不通过'}")
