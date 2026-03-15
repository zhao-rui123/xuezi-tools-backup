"""
OpenClaw 零碳园区技能包使用示例
==============================

本文件展示如何使用openclaw_skill技能包进行零碳园区方案设计
"""

# ==================== 示例1: 基础能源计算 ====================

def example_energy_base():
    """基础能源计算示例"""
    from core.energy_base import EnergyBase
    
    # 创建能源计算器
    energy = EnergyBase()
    
    # 1. 计算水管网压力损失
    print("=" * 50)
    print("示例1: 水管网压力损失计算")
    print("=" * 50)
    
    pressure_loss = energy.calculate_water_pressure_loss(
        flow_rate=100,  # m³/h
        pipe_diameter=150,  # mm
        pipe_length=500,  # m
        fittings_k=[0.5, 0.3, 1.0]  # 弯头、阀门等
    )
    print(f"压力损失: {pressure_loss['total_pressure_loss_kpa']:.2f} kPa")
    print(f"流速: {pressure_loss['velocity']:.2f} m/s")
    
    # 2. 计算水泵功率
    print("\n" + "=" * 50)
    print("示例2: 水泵功率计算")
    print("=" * 50)
    
    pump_power = energy.calculate_water_pump_power(
        flow_rate=100,
        head=50
    )
    print(f"轴功率: {pump_power['shaft_power_kw']:.2f} kW")
    print(f"推荐电机功率: {pump_power['recommended_motor_kw']} kW")
    
    # 3. 计算无功补偿
    print("\n" + "=" * 50)
    print("示例3: 无功补偿计算")
    print("=" * 50)
    
    pf_correction = energy.calculate_power_factor_correction(
        active_power=500,  # kW
        current_pf=0.75,
        target_pf=0.95
    )
    print(f"需要补偿容量: {pf_correction['compensation_required_kvar']:.2f} kvar")
    print(f"线损减少: {pf_correction['line_loss_reduction_percent']:.1f}%")
    
    # 4. 计算变压器损耗
    print("\n" + "=" * 50)
    print("示例4: 变压器损耗计算")
    print("=" * 50)
    
    transformer = energy.calculate_transformer_loss(
        capacity=1000,  # kVA
        load_rate=0.75
    )
    print(f"总损耗: {transformer['total_loss_kw']:.2f} kW")
    print(f"效率: {transformer['efficiency_percent']:.2f}%")
    print(f"经济负载率: {transformer['economic_load_rate']:.2f}")
    
    # 5. 计算采暖热负荷
    print("\n" + "=" * 50)
    print("示例5: 采暖热负荷计算")
    print("=" * 50)
    
    heating = energy.calculate_heating_load(
        area=10000,  # m²
        building_type='industrial'
    )
    print(f"热负荷: {heating['heat_load_kw']:.2f} kW")
    print(f"年采暖耗热: {heating['annual_heat_gj']:.2f} GJ")
    
    # 6. 综合能耗计算
    print("\n" + "=" * 50)
    print("示例6: 综合能耗计算")
    print("=" * 50)
    
    comprehensive = energy.calculate_comprehensive_energy(
        water_m3=10000,
        electricity_kwh=500000,
        gas_m3=50000,
        heat_gj=200
    )
    print(f"总折标煤: {comprehensive['total_coal_tce']:.2f} tce")
    print(f"总碳排放: {comprehensive['total_co2_t']:.2f} tCO2")


# ==================== 示例2: 碳排放核算 ====================

def example_carbon_calculation():
    """碳排放核算示例"""
    from core.carbon_calc import CarbonCalculator
    
    print("\n" + "=" * 50)
    print("示例7: 碳排放核算")
    print("=" * 50)
    
    # 创建碳排放计算器
    carbon = CarbonCalculator(region='east')
    
    # 1. 固定燃烧排放
    fuel_consumption = {
        'natural_gas': 100000,  # 1000m³
        'diesel': 50,  # t
    }
    stationary = carbon.calculate_stationary_combustion(fuel_consumption)
    print(f"固定燃烧排放: {stationary['total_emission_tco2']:.2f} tCO2")
    
    # 2. 外购电力排放
    electricity = carbon.calculate_purchased_electricity(
        electricity_mwh=1000,
        green_electricity_mwh=200
    )
    print(f"外购电力排放: {electricity['emission_tco2']:.2f} tCO2")
    print(f"绿电减排: {electricity['green_reduction_tco2']:.2f} tCO2")
    
    # 3. 总排放
    total = carbon.calculate_total_emissions()
    print(f"\n总排放量: {total['total_emissions_tco2']:.2f} tCO2")
    print(f"范围1占比: {total['scope1_percent']:.1f}%")
    print(f"范围2占比: {total['scope2_percent']:.1f}%")
    
    # 4. 碳减排措施
    measures = [
        {
            'name': '光伏系统',
            'type': 'renewable',
            'reduction_tco2': 500,
            'investment': 2000000,
            'annual_benefit': 400000,
        },
        {
            'name': '余热回收',
            'type': 'energy_efficiency',
            'reduction_tco2': 300,
            'investment': 800000,
            'annual_benefit': 200000,
        },
    ]
    
    reduction = carbon.calculate_reduction_measures(measures)
    print(f"\n减排措施:")
    print(f"  总减排量: {reduction['total_reduction_tco2']:.2f} tCO2")
    print(f"  总投资: {reduction['total_investment_yuan']:,.0f} 元")
    print(f"  投资回收期: {reduction['payback_period_years']:.1f} 年")


# ==================== 示例3: 行业数据库查询 ====================

def example_industry_database():
    """行业数据库查询示例"""
    from industries.industry_db import IndustryDatabase
    
    print("\n" + "=" * 50)
    print("示例8: 行业数据库查询")
    print("=" * 50)
    
    # 创建行业数据库
    db = IndustryDatabase()
    
    # 1. 获取行业列表
    industries = db.get_industry_list()
    print(f"支持的行业数量: {len(industries)}")
    
    # 2. 获取化工行业信息
    chemical = db.get_industry_info('chemical')
    print(f"\n化工行业名称: {chemical['name']}")
    print(f"子行业: {', '.join(chemical['sub_sectors'])}")
    
    # 3. 获取踏勘指导
    survey_guide = db.get_site_survey_guide('chemical')
    print(f"\n踏勘要点:")
    for item in survey_guide.get('key_info', [])[:5]:
        print(f"  - {item}")
    
    # 4. 获取节能措施
    measures = db.get_energy_saving_measures('chemical', 'high')
    print(f"\n高优先级节能措施:")
    for measure in measures:
        print(f"  - {measure}")
    
    # 5. 获取谐波信息
    harmonic = db.get_harmonic_info('steel')
    print(f"\n钢铁行业谐波特征:")
    print(f"  典型THD: {harmonic['typical_thd']}")
    print(f"  主要谐波次数: {harmonic['dominant_harmonics']}")
    
    # 6. 获取光伏储能建议
    renewable = db.get_renewable_recommendations('data_center')
    print(f"\n数据中心可再生能源建议:")
    print(f"  光伏适用性: {renewable['pv_suitability']}")
    print(f"  推荐安装位置: {', '.join(renewable['recommended_pv_locations'])}")


# ==================== 示例4: 光伏系统设计 ====================

def example_pv_design():
    """光伏系统设计示例"""
    from calculations.pv_wind import PVWindCalculator
    
    print("\n" + "=" * 50)
    print("示例9: 光伏系统设计")
    print("=" * 50)
    
    # 创建光伏风电计算器
    calc = PVWindCalculator()
    
    # 1. 计算最佳倾角
    print("\n1. 最佳倾角计算")
    tilt = calc.calculate_optimal_tilt(
        latitude=39.9,  # 北京
        optimization='annual'
    )
    print(f"  最佳倾角: {tilt['optimal_tilt_angle']:.1f}°")
    print(f"  建议: {tilt['recommendation']}")
    
    # 2. 详细倾角分析
    print("\n2. 详细倾角分析")
    detailed = calc.calculate_detailed_tilt_analysis(
        latitude=39.9,
        longitude=116.4
    )
    print(f"  可调倾角收益: {detailed['adjustable_benefit_percent']:.1f}%")
    print(f"  最终建议: 固定倾角{detailed['final_recommendation']['fixed_tilt']:.0f}°")
    
    # 3. 设计光伏阵列
    print("\n3. 光伏阵列设计")
    pv_design = calc.design_pv_array(
        capacity_kw=500,
        latitude=39.9,
        install_type='rooftop'
    )
    print(f"  装机容量: {pv_design['actual_capacity_kw']:.2f} kW")
    print(f"  组件数量: {pv_design['num_modules']}")
    print(f"  占用面积: {pv_design['pv_area_m2']:.0f} m²")
    print(f"  年发电量: {pv_design['annual_generation_kwh']:,.0f} kWh")
    print(f"  系统效率: {pv_design['system_efficiency']:.1f}%")
    
    # 4. 风光互补系统设计
    print("\n4. 风光互补系统设计")
    hybrid = calc.design_hybrid_system(
        latitude=39.9,
        longitude=116.4,
        avg_wind_speed=5.5,
        electricity_demand_kwh=1000000,
        renewable_target=0.5
    )
    print(f"  光伏容量: {hybrid['pv_system']['capacity_kw']:.2f} kW")
    print(f"  风电容量: {hybrid['wind_system']['capacity_kw']:.2f} kW")
    print(f"  储能容量: {hybrid['storage_system']['capacity_kwh']:.2f} kWh")
    print(f"  可再生能源占比: {hybrid['renewable_penetration_percent']:.1f}%")


# ==================== 示例5: 余热回收设计 ====================

def example_waste_heat():
    """余热回收设计示例"""
    from calculations.waste_heat import WasteHeatCalculator, HeatSource
    
    print("\n" + "=" * 50)
    print("示例10: 余热回收设计")
    print("=" * 50)
    
    # 创建余热计算器
    calc = WasteHeatCalculator()
    
    # 1. 单热源分析
    print("\n1. 单热源分析")
    source = HeatSource(
        name='窑炉烟气',
        temp_in=350,
        temp_out=150,
        flow_rate=5000,  # m³/h
        medium='flue_gas',
        operating_hours=8000
    )
    
    potential = calc.calculate_waste_heat_potential(source)
    print(f"  热源: {potential['source_name']}")
    print(f"  余热功率: {potential['heat_power_kw']:.2f} kW")
    print(f"  年余热量: {potential['annual_heat_gj']:.2f} GJ")
    print(f"  可回收热量: {potential['recoverable_annual_gj']:.2f} GJ")
    
    # 2. 设计回收系统
    print("\n2. 余热回收系统设计")
    system = calc.design_recovery_system(
        source_temp=350,
        source_power=potential['recoverable_power_kw'],
        application='power_generation'
    )
    print(f"  推荐技术: {system['technology_name']}")
    print(f"  发电功率: {system['power_output_kw']:.2f} kW")
    print(f"  投资额: {system['investment_yuan']:,.0f} 元")
    print(f"  投资回收期: {system['payback_period_years']:.1f} 年")
    
    # 3. 设备选型
    print("\n3. 余热回收设备选型")
    equipment = calc.select_equipment(source, {})
    for i, equip in enumerate(equipment[:3], 1):
        print(f"  {i}. {equip['technology_name']}")
        print(f"     适用温度: {equip['applicable_temp_range']}")
        print(f"     投资额: {equip['investment_yuan']:,.0f} 元")


# ==================== 示例6: 建筑节能计算 ====================

def example_building_energy():
    """建筑节能计算示例"""
    from calculations.building_energy import BuildingEnergyCalculator, BuildingEnvelope
    
    print("\n" + "=" * 50)
    print("示例11: 建筑节能计算")
    print("=" * 50)
    
    # 创建建筑节能计算器
    calc = BuildingEnergyCalculator()
    
    # 1. 定义围护结构
    envelope = BuildingEnvelope(
        wall_area=3000,
        roof_area=2000,
        window_area=800,
        floor_area=5000,
        wall_u=0.6,
        roof_u=0.5,
        window_u=2.8
    )
    
    # 2. 计算热损失
    print("\n1. 围护结构热损失")
    heat_loss = calc.calculate_envelope_heat_loss(envelope)
    print(f"  总热损失: {heat_loss['total_heat_loss_w']:.0f} W")
    print(f"  热损失指标: {heat_loss['heat_loss_index_w_m2']:.1f} W/m²")
    
    # 3. 计算年采暖负荷
    print("\n2. 年采暖负荷")
    heating = calc.calculate_annual_heating_load(envelope, 'cold')
    print(f"  年采暖负荷: {heating['annual_heating_load_kwh']:,.0f} kWh")
    print(f"  单位面积负荷: {heating['load_per_m2_kwh']:.1f} kWh/m²")
    print(f"  是否达标: {'是' if heating['compliance'] else '否'}")
    
    # 4. 围护结构优化
    print("\n3. 围护结构优化建议")
    optimization = calc.optimize_envelope(envelope, 'industrial_2020', 'cold')
    for rec in optimization['recommendations']:
        print(f"  - {rec['component']}: {rec['action']} (优先级: {rec['priority']})")
    print(f"  节能潜力: {optimization['saving_rate_percent']:.1f}%")
    
    # 5. 照明对比
    print("\n4. 照明方案对比")
    lighting = calc.compare_lighting_options(area=5000, required_illuminance=300)
    print(f"  推荐方案: {lighting['recommendation']}")
    for option in lighting['options']:
        print(f"  - {option['lamp_type']}: 10年总成本 {option['total_10y_cost']:,.0f} 元")


# ==================== 示例7: 谐波分析 ====================

def example_harmonic():
    """谐波分析示例"""
    from calculations.harmonic import HarmonicAnalyzer
    
    print("\n" + "=" * 50)
    print("示例12: 谐波分析")
    print("=" * 50)
    
    # 创建谐波分析器
    analyzer = HarmonicAnalyzer()
    
    # 1. 计算THD
    print("\n1. THD计算")
    harmonics = {5: 25, 7: 15, 11: 8, 13: 5}
    thd = analyzer.calculate_thd(harmonics)
    print(f"  THD: {thd['thd_percent']:.2f}%")
    print(f"  奇次谐波THD: {thd['odd_thd_percent']:.2f}%")
    
    # 2. 电流THD计算
    print("\n2. 电流THD计算")
    current_thd = analyzer.calculate_current_thd(
        fundamental_current=100,
        harmonics=harmonics
    )
    print(f"  基波电流: {current_thd['fundamental_current_a']:.1f} A")
    print(f"  有效值电流: {current_thd['rms_current_a']:.2f} A")
    print(f"  电流增加率: {current_thd['current_increase_percent']:.2f}%")
    
    # 3. 合规性检查
    print("\n3. 合规性检查")
    compliance = analyzer.check_compliance(harmonics, 'voltage_380v')
    print(f"  THD限值: {compliance['thd_limit']:.1f}%")
    print(f"  THD实测: {compliance['thd_measured']:.2f}%")
    print(f"  是否达标: {'是' if compliance['overall_compliance'] else '否'}")
    
    # 4. 谐波影响分析
    print("\n4. 谐波影响分析")
    impact = analyzer.analyze_harmonic_impact(
        thd_voltage=8.5,
        thd_current=20,
        transformer_capacity=1000,
        load_power=600
    )
    print(f"  严重程度: {impact['overall_severity']}")
    print(f"  需要治理: {'是' if impact['mitigation_required'] else '否'}")
    for item in impact['impacts'][:3]:
        print(f"  - {item['type']}: {item['value']} (严重度: {item['severity']})")
    
    # 5. 治理方案设计
    print("\n5. 谐波治理方案")
    mitigation = analyzer.design_mitigation_system(
        harmonics=harmonics,
        load_power=100,
        target_thd=5.0
    )
    print(f"  当前THD: {mitigation['current_thd_percent']:.2f}%")
    print(f"  目标THD: {mitigation['target_thd_percent']:.1f}%")
    print(f"  推荐方案: {mitigation['recommendation']}")
    print(f"  有源滤波器容量: {mitigation['options']['active_filter']['capacity_a']:.0f} A")
    print(f"  有源滤波器投资: {mitigation['options']['active_filter']['investment_yuan']:,.0f} 元")


# ==================== 示例8: 零碳园区方案设计 ====================

def example_scheme_design():
    """零碳园区方案设计示例"""
    from core.scheme_design import SchemeDesigner, SchemeConfig
    
    print("\n" + "=" * 50)
    print("示例13: 零碳园区方案设计")
    print("=" * 50)
    
    # 创建方案配置
    config = SchemeConfig(
        name='某工业园区',
        location=(39.9, 116.4),  # 北京
        area=50000,  # m²
        building_area=30000,  # m²
        annual_electricity=2000000,  # kWh
        annual_heat=5000,  # GJ
        annual_cooling=3000,  # GJ
        industry_type='chemical'
    )
    
    # 创建方案设计师
    designer = SchemeDesigner(config)
    
    # 生成综合方案
    print("\n生成综合零碳园区方案...")
    scheme = designer.generate_comprehensive_scheme(
        target_renewable_ratio=0.5
    )
    
    print(f"\n方案名称: {scheme['scheme_name']}")
    print(f"行业类型: {scheme['industry_type']}")
    
    # 光伏系统
    print(f"\n光伏系统:")
    print(f"  装机容量: {scheme['pv_system']['pv_capacity_kw']:.2f} kW")
    print(f"  年发电量: {scheme['pv_system']['annual_generation_kwh']:,.0f} kWh")
    print(f"  投资额: {scheme['pv_system']['investment_yuan']:,.0f} 元")
    
    # 储能系统
    print(f"\n储能系统:")
    print(f"  储能容量: {scheme['storage_system']['storage_capacity_kwh']:.2f} kWh")
    print(f"  投资额: {scheme['storage_system']['investment_yuan']:,.0f} 元")
    
    # 节能改造
    print(f"\n节能改造:")
    print(f"  年节电量: {scheme['energy_efficiency']['total_saving_kwh']:,.0f} kWh")
    print(f"  节能率: {scheme['energy_efficiency']['total_saving_rate']:.1f}%")
    
    # 汇总
    print(f"\n方案汇总:")
    summary = scheme['summary']
    print(f"  总投资: {summary['total_investment_million_yuan']:.2f} 万元")
    print(f"  年节约费用: {summary['annual_saving_yuan']:,.0f} 元")
    print(f"  投资回收期: {summary['payback_period_years']:.1f} 年")
    print(f"  年碳减排: {summary['carbon_reduction_tco2_per_year']:.2f} tCO2")
    print(f"  可再生能源占比: {summary['renewable_energy_ratio_percent']:.1f}%")
    
    # 导出报告
    print("\n导出方案报告...")
    report = designer.export_scheme_report()
    print(f"报告长度: {len(report)} 字符")


# ==================== 示例9: 地理工具使用 ====================

def example_geo_tools():
    """地理工具使用示例"""
    from utils.geo_tools import GeoTools
    
    print("\n" + "=" * 50)
    print("示例14: 地理工具")
    print("=" * 50)
    
    # 创建地理工具
    geo = GeoTools()
    
    # 1. 获取城市经纬度
    print("\n1. 获取城市经纬度")
    coords = geo.get_coordinates('北京')
    print(f"  北京: 纬度{coords[0]:.4f}°, 经度{coords[1]:.4f}°")
    
    # 2. 获取气候分区
    print("\n2. 获取气候分区")
    climate = geo.get_climate_zone(city_name='北京')
    print(f"  气候分区: {climate['name']}")
    print(f"  采暖度日数: {climate['heating_degree_days']}")
    
    # 3. 获取太阳辐射
    print("\n3. 获取太阳辐射")
    radiation = geo.get_solar_radiation(city_name='北京')
    print(f"  日均太阳辐射: {radiation:.2f} kWh/m²/day")
    
    # 4. 最佳光伏倾角
    print("\n4. 最佳光伏倾角")
    tilt = geo.get_optimal_pv_tilt(39.9)
    print(f"  最佳倾角: {tilt:.1f}°")
    
    # 5. 位置综合信息
    print("\n5. 位置综合信息")
    info = geo.get_location_info(39.9, 116.4)
    print(f"  最近城市: {info['nearest_city']['name']}")
    print(f"  太阳资源等级: {info['solar_resource']['resource_level']}")
    print(f"  推荐光伏倾角: {info['pv_recommendation']['optimal_tilt_angle']:.0f}°")


# ==================== 示例10: 设备数据库查询 ====================

def example_equipment_db():
    """设备数据库查询示例"""
    from utils.equipment_db import EquipmentDatabase
    
    print("\n" + "=" * 50)
    print("示例15: 设备数据库查询")
    print("=" * 50)
    
    # 创建设备数据库
    db = EquipmentDatabase()
    
    # 1. 查询光伏组件
    print("\n1. 光伏组件查询")
    module = db.get_pv_module('mono_550w')
    print(f"  型号: mono_550w")
    print(f"  功率: {module['power']} W")
    print(f"  效率: {module['efficiency']*100:.1f}%")
    print(f"  价格: {module['price_per_w']:.2f} 元/W")
    
    # 2. 按功率搜索电机
    print("\n2. 按功率搜索电机")
    motors = db.search_by_power('motor', 10, 30)
    print(f"  找到 {len(motors)} 款电机:")
    for motor in motors:
        params = db.get_efficient_motor(motor)
        print(f"    {motor}: {params['power']}kW, 效率{params['efficiency']*100:.1f}%")
    
    # 3. 设备推荐
    print("\n3. 设备推荐")
    recommendations = db.get_recommendation('inverter', {'target_power': 100})
    print(f"  推荐逆变器:")
    for rec in recommendations[:3]:
        print(f"    {rec['model']}: {rec['params']['power']}kW, "
              f"效率{rec['params']['max_efficiency']*100:.1f}%")


# ==================== 主函数 ====================

def run_all_examples():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("OpenClaw 零碳园区技能包 - 使用示例")
    print("=" * 60)
    
    example_energy_base()
    example_carbon_calculation()
    example_industry_database()
    example_pv_design()
    example_waste_heat()
    example_building_energy()
    example_harmonic()
    example_scheme_design()
    example_geo_tools()
    example_equipment_db()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成!")
    print("=" * 60)


if __name__ == '__main__':
    run_all_examples()
