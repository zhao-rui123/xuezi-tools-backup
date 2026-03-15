
"""
电力设计技能包使用示例 - 完整版
展示所有功能模块的使用方法
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
    SteelPlantPowerDesign,
    TransmissionLineDesign,
    ExcelExporter,
    calculate_load,
    calculate_short_circuit,
    select_cable,
    compensate_reactive_power,
    design_grounding,
    export_to_excel,
)

def example_1_basic_load_calculation():
    """示例1：基本负荷计算"""
    print("=" * 70)
    print("示例1：基本负荷计算")
    print("=" * 70)

    fan_powers = [5.5, 7.5, 11, 15]
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

def example_2_steel_plant_load():
    """示例2：钢铁企业负荷计算"""
    print("\n" + "=" * 70)
    print("示例2：钢铁企业负荷计算 - 按单位产品耗电量")
    print("=" * 70)

    steel_design = SteelPlantPowerDesign()

    # 计算年产100万吨转炉钢的负荷
    result = steel_design.calculate_by_unit_production(
        production_capacity=1000000,  # 1百万吨
        product_type="转炉钢",
        operating_hours=7000
    )

    print(f"\n年产量: 1,000,000 吨转炉钢")
    print(f"有功功率 P: {result.active_power:.2f} kW")
    print(f"视在功率 S: {result.apparent_power:.2f} kVA")
    print(f"计算电流 I: {result.calculation_current:.2f} A")

def example_3_arc_furnace():
    """示例3：电弧炉负荷计算"""
    print("\n" + "=" * 70)
    print("示例3：电弧炉负荷计算")
    print("=" * 70)

    steel_design = SteelPlantPowerDesign()

    result = steel_design.arc_furnace_load(
        furnace_capacity=100,  # 100吨电弧炉
        transformer_power=80,  # 80MVA变压器
        operating_mode='normal'
    )

    print(f"\n电弧炉容量: 100 吨")
    print(f"变压器容量: 80 MVA")
    print(f"有功功率: {result['active_power_mw']:.2f} MW")
    print(f"无功功率: {result['reactive_power_mvar']:.2f} Mvar")
    print(f"视在功率: {result['apparent_power_mva']:.2f} MVA")
    print(f"功率因数: {result['power_factor']:.2f}")

def example_4_harmonic_calculation():
    """示例4：谐波计算"""
    print("\n" + "=" * 70)
    print("示例4：电弧炉谐波计算")
    print("=" * 70)

    steel_design = SteelPlantPowerDesign()

    harmonics = steel_design.harmonic_calculation(
        fundamental_current=1000  # 基波电流1000A
    )

    print(f"\n基波电流: 1000 A")
    print("各次谐波电流:")
    for order, current in harmonics.items():
        if order != 'THD':
            print(f"  {order}次谐波: {current:.1f} A ({current/1000*100:.1f}%)")
    print(f"\n总谐波畸变率 THD: {harmonics['THD']:.2f}%")

def example_5_rolling_mill_impact():
    """示例5：轧钢机冲击负荷计算"""
    print("\n" + "=" * 70)
    print("示例5：轧钢机冲击负荷计算")
    print("=" * 70)

    steel_design = SteelPlantPowerDesign()

    result = steel_design.rolling_mill_impact_load(
        motor_power=5000,  # 5000kW电动机
        load_factor=0.6,
        impact_factor=2.5
    )

    print(f"\n电动机总功率: 5000 kW")
    print(f"负载率: 60%")
    print(f"冲击系数: 2.5")
    print(f"平均负荷: {result['average_power_kw']:.2f} kW")
    print(f"冲击负荷: {result['impact_power_kw']:.2f} kW")
    print(f"无功冲击: {result['impact_reactive_kvar']:.2f} kvar")

def example_6_transmission_line_params():
    """示例6：送电线路电气参数计算"""
    print("\n" + "=" * 70)
    print("示例6：送电线路电气参数计算")
    print("=" * 70)

    line_design = TransmissionLineDesign()

    result = line_design.electrical_parameters(
        conductor_type="LGJ-240",
        line_length=50,  # 50km
        voltage=220,  # 220kV
        num_circuits=1
    )

    print(f"\n导线型号: LGJ-240")
    print(f"线路长度: 50 km")
    print(f"额定电压: 220 kV")
    print(f"\n电阻: {result['resistance_ohm']:.2f} Ω")
    print(f"电抗: {result['reactance_ohm']:.2f} Ω")
    print(f"电纳: {result['susceptance_s']:.6f} S")
    print(f"波阻抗: {result['wave_impedance_ohm']:.2f} Ω")
    print(f"自然功率: {result['natural_power_mw']:.2f} MW")

def example_7_sag_calculation():
    """示例7：导线弧垂计算"""
    print("\n" + "=" * 70)
    print("示例7：导线弧垂计算")
    print("=" * 70)

    line_design = TransmissionLineDesign()

    result = line_design.sag_calculation(
        span_length=300,  # 300m档距
        conductor_type="LGJ-240",
        weather_condition="I类(轻冰区)",
        safety_factor=2.5
    )

    print(f"\n档距: 300 m")
    print(f"导线型号: LGJ-240")
    print(f"气象条件: I类(轻冰区)")
    print(f"安全系数: 2.5")
    print(f"\n弧垂: {result['sag_m']:.2f} m")
    print(f"最大使用应力: {result['max_stress_mpa']:.2f} MPa")

def example_8_conductor_selection():
    """示例8：导线截面选择"""
    print("\n" + "=" * 70)
    print("示例8：导线截面选择")
    print("=" * 70)

    line_design = TransmissionLineDesign()

    result = line_design.conductor_selection(
        transmission_power=100,  # 100MW
        voltage=220,  # 220kV
        line_length=50,  # 50km
        max_voltage_drop=10.0,
        economic_current_density=1.15
    )

    print(f"\n输送功率: 100 MW")
    print(f"额定电压: 220 kV")
    print(f"线路长度: 50 km")
    print(f"\n推荐导线型号: {result['selected_conductor']}")
    print(f"导线截面: {result['section_mm2']:.1f} mm²")
    print(f"计算电流: {result['calculated_current_a']:.1f} A")
    print(f"电压降: {result['voltage_drop_percent']:.2f}%")
    print(f"是否满足要求: {'是' if result['meets_requirement'] else '否'}")

def example_9_tower_load():
    """示例9：杆塔荷载计算"""
    print("\n" + "=" * 70)
    print("示例9：杆塔荷载计算")
    print("=" * 70)

    line_design = TransmissionLineDesign()

    result = line_design.tower_load_calculation(
        span_length=300,
        conductor_type="LGJ-240",
        wind_pressure=350,
        ice_thickness=0
    )

    print(f"\n档距: 300 m")
    print(f"导线型号: LGJ-240")
    print(f"风压: 350 Pa")
    print(f"\n垂直荷载: {result['vertical_load_n']:.1f} N")
    print(f"风荷载: {result['wind_load_n']:.1f} N")
    print(f"综合荷载: {result['resultant_load_n']:.1f} N")

def example_10_insulation_coordination():
    """示例10：绝缘配合设计"""
    print("\n" + "=" * 70)
    print("示例10：绝缘配合设计")
    print("=" * 70)

    line_design = TransmissionLineDesign()

    result = line_design.insulation_coordination(
        voltage=220,  # 220kV
        altitude=0,
        pollution_level="II级"
    )

    print(f"\n额定电压: 220 kV")
    print(f"海拔高度: 0 m")
    print(f"污秽等级: II级")
    print(f"\n绝缘子片数: {result['insulator_count']} 片")
    print(f"绝缘子串长度: {result['insulator_string_length_mm']:.0f} mm")

def example_11_tower_grounding():
    """示例11：杆塔接地设计"""
    print("\n" + "=" * 70)
    print("示例11：杆塔接地设计")
    print("=" * 70)

    line_design = TransmissionLineDesign()

    result = line_design.grounding_design_tower(
        soil_resistivity=100,  # 100Ω·m
        tower_type="concrete_pole",
        lightning_activity="moderate"
    )

    print(f"\n土壤电阻率: 100 Ω·m")
    print(f"杆塔类型: 混凝土电杆")
    print(f"\n接地电阻要求: ≤{result['required_resistance_ohm']} Ω")
    print(f"水平接地体长度: {result['horizontal_length_m']:.1f} m")
    print(f"垂直接地极数量: {result['vertical_rod_count']} 根")

def example_12_excel_export():
    """示例12：导出到Excel"""
    print("\n" + "=" * 70)
    print("示例12：计算结果导出到Excel")
    print("=" * 70)

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

    # 导出到Excel
    exporter = ExcelExporter()
    filepath = exporter.export_full_report(results, "电力设计计算报告.xlsx")

    print(f"\n计算结果已导出到: {filepath}")
    print("\n导出内容包括:")
    print("  - 负荷计算结果")
    print("  - 短路电流计算结果")
    print("  - 变压器校验结果")
    print("  - 电缆选择结果")
    print("  - 保护整定结果")

def example_13_comprehensive_steel_plant():
    """示例13：钢铁企业综合设计"""
    print("\n" + "=" * 70)
    print("示例13：钢铁企业综合设计")
    print("=" * 70)

    steel_design = SteelPlantPowerDesign()

    # 计算各工序负荷
    processes = [
        ("生铁", 2000000),  # 200万吨生铁
        ("转炉钢", 1500000),  # 150万吨转炉钢
        ("热轧板", 1200000),  # 120万吨热轧板
        ("冷轧板", 800000),  # 80万吨冷轧板
    ]

    total_power = 0
    print("\n各工序负荷计算:")
    print("-" * 50)

    for product, capacity in processes:
        result = steel_design.calculate_by_unit_production(capacity, product)
        print(f"{product}: {result.active_power/1000:.2f} MW")
        total_power += result.active_power

    print("-" * 50)
    print(f"总负荷: {total_power/1000:.2f} MW")

    # 无功补偿计算
    compensation = steel_design.reactive_power_compensation_sizing(
        load_power=total_power,
        current_pf=0.75,
        target_pf=0.95,
        load_type='arc_furnace'
    )

    print(f"\n无功补偿容量: {compensation['compensation_capacity_kvar']/1000:.2f} Mvar")

def example_14_transmission_line_design():
    """示例14：送电线路综合设计"""
    print("\n" + "=" * 70)
    print("示例14：送电线路综合设计")
    print("=" * 70)

    line_design = TransmissionLineDesign()

    # 线路参数
    voltage = 220  # kV
    length = 80  # km
    power = 200  # MW

    print(f"\n线路设计参数:")
    print(f"  额定电压: {voltage} kV")
    print(f"  线路长度: {length} km")
    print(f"  输送功率: {power} MW")

    # 导线选择
    conductor = line_design.conductor_selection(power, voltage, length)
    print(f"\n导线选择:")
    print(f"  推荐型号: {conductor['selected_conductor']}")
    print(f"  导线截面: {conductor['section_mm2']:.1f} mm²")

    # 电气参数
    params = line_design.electrical_parameters(
        conductor['selected_conductor'], length, voltage
    )
    print(f"\n电气参数:")
    print(f"  线路电阻: {params['resistance_ohm']:.2f} Ω")
    print(f"  线路电抗: {params['reactance_ohm']:.2f} Ω")
    print(f"  电压降: {conductor['voltage_drop_percent']:.2f}%")

    # 绝缘配合
    insulation = line_design.insulation_coordination(voltage)
    print(f"\n绝缘配合:")
    print(f"  绝缘子片数: {insulation['insulator_count']} 片")

    # 弧垂计算
    sag = line_design.sag_calculation(400, conductor['selected_conductor'])
    print(f"\n弧垂计算(档距400m):")
    print(f"  弧垂: {sag['sag_m']:.2f} m")

if __name__ == "__main__":
    # 运行所有示例
    example_1_basic_load_calculation()
    example_2_steel_plant_load()
    example_3_arc_furnace()
    example_4_harmonic_calculation()
    example_5_rolling_mill_impact()
    example_6_transmission_line_params()
    example_7_sag_calculation()
    example_8_conductor_selection()
    example_9_tower_load()
    example_10_insulation_coordination()
    example_11_tower_grounding()
    example_12_excel_export()
    example_13_comprehensive_steel_plant()
    example_14_transmission_line_design()

    print("\n" + "=" * 70)
    print("所有示例运行完成！")
    print("=" * 70)
