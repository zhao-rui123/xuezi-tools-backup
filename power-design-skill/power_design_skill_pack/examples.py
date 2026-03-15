
"""
电力设计技能包使用示例
演示如何使用各个计算模块
"""

from power_design_skill import (
    PowerDesignCalculator,
    LoadCalculation,
    ShortCircuitCalculation,
    CableSelection,
    ProtectionSetting,
    ReactivePowerCompensation,
    GroundingDesign,
    TransformerSelection,
    CircuitBreakerSelection,
    calculate_load,
    calculate_short_circuit,
    select_cable,
    compensate_reactive_power,
    design_grounding
)

def example_1_basic_load_calculation():
    """示例1：基本负荷计算"""
    print("=" * 60)
    print("示例1：基本负荷计算")
    print("=" * 60)

    # 使用需要系数法计算风机负荷
    fan_powers = [5.5, 7.5, 11, 15]  # 4台风机的功率 (kW)
    result = LoadCalculation.demand_coefficient_method(
        equipment_powers=fan_powers,
        equipment_type="风机、水泵",
        voltage=0.38
    )

    print(f"\n设备总容量: {sum(fan_powers)} kW")
    print(f"有功功率 P: {result.active_power:.2f} kW")
    print(f"无功功率 Q: {result.reactive_power:.2f} kvar")
    print(f"视在功率 S: {result.apparent_power:.2f} kVA")
    print(f"计算电流 I: {result.calculation_current:.2f} A")
    print(f"功率因数: {result.power_factor:.2f}")

def example_2_short_circuit_calculation():
    """示例2：短路电流计算"""
    print("\n" + "=" * 60)
    print("示例2：短路电流计算")
    print("=" * 60)

    # 低压系统短路电流计算
    result = ShortCircuitCalculation.ohmic_method(
        system_voltage=0.4,  # 380V系统
        transformer_power=1000,  # 1000kVA变压器
        uk_percent=4.5,
        line_length=100,  # 线路长度100m
        cable_resistance=0.193,  # 电缆电阻 mΩ/m
        cable_reactance=0.08  # 电缆电抗 mΩ/m
    )

    print(f"\n三相短路电流: {result.three_phase_current:.2f} kA")
    print(f"两相短路电流: {result.two_phase_current:.2f} kA")
    print(f"单相短路电流: {result.single_phase_current:.2f} kA")
    print(f"短路容量: {result.short_circuit_capacity:.2f} MVA")

def example_3_cable_selection():
    """示例3：电缆截面选择"""
    print("\n" + "=" * 60)
    print("示例3：电缆截面选择")
    print("=" * 60)

    # 选择电缆
    result = CableSelection.select_cable(
        calculation_current=150,  # 计算电流150A
        length=200,  # 线路长度200m
        voltage=380,
        power_factor=0.85,
        max_voltage_drop=5.0,  # 最大允许电压降5%
        short_circuit_current=15,  # 短路电流15kA
        protection_time=0.5  # 保护动作时间0.5s
    )

    print(f"\n推荐电缆截面: {result.cross_section} mm²")
    print(f"载流量: {result.current_carrying_capacity:.1f} A")
    print(f"电压降: {result.voltage_drop:.2f}%")
    print(f"热稳定校验: {'通过' if result.thermal_stability else '不通过'}")

def example_4_protection_setting():
    """示例4：保护整定计算"""
    print("\n" + "=" * 60)
    print("示例4：保护整定计算")
    print("=" * 60)

    # 电动机保护整定
    motor_current = 50  # 电动机额定电流50A
    result = ProtectionSetting.motor_protection(
        motor_rated_current=motor_current,
        starting_current_multiple=7,
        starting_time=5
    )

    print(f"\n电动机额定电流: {motor_current} A")
    print(f"速断保护定值: {result.instantaneous_current:.1f} A")
    print(f"过流保护定值: {result.time_delay_current:.1f} A")
    print(f"延时时间: {result.time_delay:.1f} s")
    print(f"灵敏度: {result.sensitivity:.2f}")

    # 灵敏度校验
    min_short_circuit = 800  # 最小短路电流800A
    sensitivity = ProtectionSetting.sensitivity_check(
        min_short_circuit_current=min_short_circuit,
        protection_setting=result.instantaneous_current
    )
    print(f"\n灵敏度校验:")
    print(f"  最小短路电流: {min_short_circuit} A")
    print(f"  灵敏度系数: {sensitivity:.2f}")
    print(f"  是否满足要求: {'是' if sensitivity >= 1.5 else '否'}")

def example_5_reactive_compensation():
    """示例5：无功功率补偿"""
    print("\n" + "=" * 60)
    print("示例5：无功功率补偿")
    print("=" * 60)

    # 计算补偿容量
    active_power = 500  # 有功功率500kW
    cos_phi1 = 0.7  # 补偿前功率因数
    cos_phi2 = 0.95  # 补偿后功率因数

    compensation = ReactivePowerCompensation.compensation_capacity(
        active_power=active_power,
        cos_phi1=cos_phi1,
        cos_phi2=cos_phi2
    )

    print(f"\n有功功率: {active_power} kW")
    print(f"补偿前功率因数: {cos_phi1}")
    print(f"补偿后功率因数: {cos_phi2}")
    print(f"所需补偿容量: {compensation:.2f} kvar")

    # 变压器补偿估算
    transformer_capacity = 1000  # 1000kVA变压器
    estimated_comp = ReactivePowerCompensation.transformer_compensation(
        transformer_capacity=transformer_capacity,
        load_factor=0.7,
        compensation_rate=0.3
    )
    print(f"\n变压器容量: {transformer_capacity} kVA")
    print(f"估算补偿容量: {estimated_comp:.2f} kvar")

def example_6_grounding_design():
    """示例6：接地设计"""
    print("\n" + "=" * 60)
    print("示例6：接地设计")
    print("=" * 60)

    # 接地网设计
    area = 2000  # 接地网面积2000m²
    soil_resistivity = 40  # 粘土电阻率40Ω·m

    resistance = GroundingDesign.grounding_grid_resistance(
        area=area,
        soil_resistivity=soil_resistivity,
        total_length=500
    )

    print(f"\n接地网面积: {area} m²")
    print(f"土壤电阻率: {soil_resistivity} Ω·m")
    print(f"接地电阻: {resistance:.2f} Ω")
    print(f"是否满足要求(R≤4Ω): {'是' if resistance <= 4 else '否'}")

    # 垂直接地极
    vertical_r = GroundingDesign.vertical_grounding_resistance(
        length=2.5,  # 2.5m接地极
        diameter=0.05,  # 直径50mm
        soil_resistivity=soil_resistivity
    )
    print(f"\n垂直接地极接地电阻: {vertical_r:.2f} Ω")

def example_7_transformer_selection():
    """示例7：变压器选择"""
    print("\n" + "=" * 60)
    print("示例7：变压器选择")
    print("=" * 60)

    # 按负荷选择变压器
    apparent_power = 650  # 计算负荷650kVA
    capacity = TransformerSelection.select_by_load(
        apparent_power=apparent_power,
        load_factor=0.7,
        growth_factor=1.2
    )

    print(f"\n计算负荷: {apparent_power} kVA")
    print(f"推荐变压器容量: {capacity} kVA")
    print(f"负载率: {apparent_power/capacity*100:.1f}%")

    # 经济负载率
    economic_rate = TransformerSelection.economic_load_rate(
        no_load_loss=1.5,  # 空载损耗1.5kW
        load_loss=10  # 负载损耗10kW
    )
    print(f"\n经济负载率: {economic_rate*100:.1f}%")

    # 年电能损耗
    annual_loss = TransformerSelection.annual_energy_loss(
        no_load_loss=1.5,
        load_loss=10,
        load_factor=0.7
    )
    print(f"年电能损耗: {annual_loss:.0f} kWh")

def example_8_circuit_breaker_selection():
    """示例8：断路器选择"""
    print("\n" + "=" * 60)
    print("示例8：断路器选择")
    print("=" * 60)

    # 配电用断路器
    calculation_current = 150  # 计算电流150A
    short_circuit_current = 20  # 短路电流20kA

    rated_current = CircuitBreakerSelection.select_rated_current(
        calculation_current=calculation_current,
        margin=1.25
    )

    breaking_capacity = CircuitBreakerSelection.select_breaking_capacity(
        short_circuit_current=short_circuit_current,
        margin=1.2
    )

    print(f"\n计算电流: {calculation_current} A")
    print(f"推荐断路器额定电流: {rated_current} A")
    print(f"短路电流: {short_circuit_current} kA")
    print(f"推荐分断能力: {breaking_capacity} kA")

    # 电动机保护断路器
    motor_current = 50
    starting_current = 350
    motor_breaker = CircuitBreakerSelection.motor_circuit_breaker(
        motor_rated_current=motor_current,
        starting_current=starting_current,
        starting_time=5
    )

    print(f"\n电动机额定电流: {motor_current} A")
    print(f"启动电流: {starting_current} A")
    print(f"断路器额定电流: {motor_breaker['rated_current']} A")
    print(f"长延时整定: {motor_breaker['long_delay']:.1f} A")
    print(f"瞬时整定: {motor_breaker['instantaneous']:.1f} A")
    print(f"脱扣曲线: {motor_breaker['curve']}型")

def example_9_comprehensive_calculation():
    """示例9：综合计算"""
    print("\n" + "=" * 60)
    print("示例9：综合计算 - 完整配电系统设计")
    print("=" * 60)

    # 创建计算器
    calculator = PowerDesignCalculator()

    # 定义设备数据
    equipment_data = [
        {"power": 7.5, "type": "冷加工机床", "count": 8},
        {"power": 5.5, "type": "风机、水泵", "count": 6},
        {"power": 15, "type": "起重机", "count": 2},
        {"power": 2.0, "type": "照明", "count": 30},
    ]

    # 执行全套计算
    results = calculator.calculate_distribution_system(
        equipment_data=equipment_data,
        system_voltage=0.38,
        transformer_capacity=630
    )

    # 生成并打印报告
    report = calculator.generate_calculation_report(results)
    print(report)

def example_10_convenience_functions():
    """示例10：便捷函数使用"""
    print("\n" + "=" * 60)
    print("示例10：便捷函数使用")
    print("=" * 60)

    # 便捷函数计算负荷
    powers = [10, 15, 20, 25]
    load = calculate_load(powers, "风机、水泵")
    print(f"\n负荷计算:")
    print(f"  视在功率: {load.apparent_power:.2f} kVA")
    print(f"  计算电流: {load.calculation_current:.2f} A")

    # 便捷函数计算短路电流
    short = calculate_short_circuit(
        system_voltage=0.4,
        transformer_power=800
    )
    print(f"\n短路电流:")
    print(f"  三相短路: {short.three_phase_current:.2f} kA")

    # 便捷函数选择电缆
    cable = select_cable(
        current=120,
        length=150,
        max_voltage_drop=5
    )
    print(f"\n电缆选择:")
    print(f"  截面: {cable.cross_section} mm²")
    print(f"  电压降: {cable.voltage_drop:.2f}%")

    # 便捷函数计算无功补偿
    compensation = compensate_reactive_power(
        active_power=400,
        cos_phi1=0.75,
        cos_phi2=0.95
    )
    print(f"\n无功补偿:")
    print(f"  补偿容量: {compensation:.2f} kvar")

    # 便捷函数设计接地
    grounding_r = design_grounding(
        area=1500,
        soil_type="砂质粘土"
    )
    print(f"\n接地设计:")
    print(f"  接地电阻: {grounding_r:.2f} Ω")

if __name__ == "__main__":
    # 运行所有示例
    example_1_basic_load_calculation()
    example_2_short_circuit_calculation()
    example_3_cable_selection()
    example_4_protection_setting()
    example_5_reactive_compensation()
    example_6_grounding_design()
    example_7_transformer_selection()
    example_8_circuit_breaker_selection()
    example_9_comprehensive_calculation()
    example_10_convenience_functions()
