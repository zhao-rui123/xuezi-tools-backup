"""
行业工艺参数数据库
================
涵盖12大高耗能行业的详细工艺参数、踏勘指导、节能建议
"""

from typing import Dict, List, Tuple, Optional


class IndustryDatabase:
    """行业数据库类"""
    
    # 12大高耗能行业详细数据
    INDUSTRIES = {
        'chemical': {
            'name': '化工行业',
            'name_en': 'Chemical Industry',
            'sub_sectors': ['基础化学原料', '化肥', '农药', '合成材料', '专用化学品'],
            
            # 工艺参数
            'process_params': {
                'typical_processes': ['合成氨', '甲醇', '乙烯', '烧碱', '纯碱', 'PVC'],
                'energy_intensity_kwh_per_t': {
                    '合成氨': 1200,
                    '甲醇': 800,
                    '乙烯': 600,
                    '烧碱': 2400,
                    '纯碱': 200,
                    'PVC': 500,
                },
                'heat_demand_gj_per_t': {
                    '合成氨': 12,
                    '甲醇': 8,
                    '乙烯': 15,
                    '烧碱': 3,
                    '纯碱': 5,
                    'PVC': 4,
                },
                'steam_pressure_mpa': [0.4, 1.0, 2.5, 4.0, 9.0],
                'typical_temp_range': '150-450°C',
            },
            
            # 主要用能设备
            'key_equipment': {
                '反应釜': {'power_range': '50-500kW', 'efficiency': '75-85%'},
                '压缩机': {'power_range': '200-2000kW', 'efficiency': '80-90%'},
                '泵': {'power_range': '10-200kW', 'efficiency': '70-85%'},
                '换热器': {'heat_transfer': 'high', 'efficiency': '85-95%'},
                '精馏塔': {'energy_intensive': True, 'optimization_potential': '20-30%'},
                '造粒机': {'power_range': '100-500kW', 'efficiency': '75-80%'},
            },
            
            # 余热资源
            'waste_heat': {
                'sources': ['反应热', '烟气', '蒸汽冷凝水', '高温物料'],
                'temp_range': '80-400°C',
                'recovery_potential': '15-25% of total energy',
                'typical_applications': ['余热锅炉', 'ORC发电', '预热进料', '吸收式制冷'],
            },
            
            # 用电特性
            'electricity_characteristics': {
                'load_type': '连续生产',
                'load_curve': '平稳',
                'power_factor': '0.85-0.92',
                'voltage_level': '10kV/35kV',
                'demand_factor': 0.75,
            },
            
            # 谐波特征
            'harmonic_profile': {
                'sources': ['变频器', '整流器', '电弧炉'],
                'typical_thd': '8-15%',
                'dominant_harmonics': [5, 7, 11, 13],
                'mitigation_required': True,
            },
            
            # 碳排放特征
            'carbon_profile': {
                'emission_intensity_tco2_per_t': {
                    '合成氨': 2.1,
                    '甲醇': 1.8,
                    '乙烯': 1.5,
                    '烧碱': 1.2,
                    '纯碱': 0.4,
                },
                'scope1_percent': 60,
                'scope2_percent': 35,
                'scope3_percent': 5,
            },
            
            # 踏勘要点
            'site_survey': {
                'key_info': [
                    '主要产品种类和产能',
                    '主要工艺流程图',
                    '各工序能耗数据',
                    '蒸汽管网压力等级',
                    '余热资源温度和流量',
                    '电机清单和功率',
                    '变压器容量和负载率',
                    '压缩空气系统参数',
                ],
                'measurement_points': [
                    '主要设备功率',
                    '蒸汽消耗量',
                    '循环水流量',
                    '反应温度',
                    '烟气温度',
                ],
                'documents_needed': [
                    '能源审计报告',
                    '生产工艺流程图',
                    '设备台账',
                    '能源消耗统计',
                    '电费单',
                ],
            },
            
            # 节能建议
            'energy_saving_measures': {
                'high_priority': [
                    '反应热回收',
                    '蒸汽冷凝水回收',
                    '电机变频改造',
                    '精馏塔优化',
                ],
                'medium_priority': [
                    '压缩空气系统优化',
                    '换热网络优化',
                    '余热发电',
                    '热泵应用',
                ],
                'low_priority': [
                    '照明改造',
                    '建筑保温',
                ],
            },
            
            # 光伏储能建议
            'renewable_recommendations': {
                'pv_suitability': '高',
                'recommended_pv_locations': ['厂房屋顶', '罐区遮阳棚', '停车场'],
                'pv_capacity_factor': '12-15%',
                'storage_recommendation': '建议配置储能，容量为光伏装机的20-30%',
                'storage_hours': 2,
            },
        },
        
        'steel': {
            'name': '钢铁行业',
            'name_en': 'Steel Industry',
            'sub_sectors': ['长流程钢铁', '短流程钢铁', '铁合金', '焦化'],
            
            'process_params': {
                'typical_processes': ['烧结', '球团', '炼铁', '炼钢', '轧钢'],
                'energy_intensity_kwh_per_t': {
                    '长流程': 650,
                    '短流程': 400,
                    '焦化': 150,
                },
                'heat_demand_gj_per_t': {
                    '长流程': 18,
                    '短流程': 5,
                },
                'typical_temp_range': '200-1600°C',
            },
            
            'key_equipment': {
                '高炉': {'energy_intensive': True, 'volume': '1000-5000m³'},
                '转炉': {'capacity': '50-300t', 'recovery': '煤气回收'},
                '电弧炉': {'power': '50-150MW', 'efficiency': ' improving'},
                '加热炉': {'fuel': '煤气/天然气', 'efficiency': '40-60%'},
                '轧机': {'power': '10-50MW', 'drives': 'DC/AC'},
            },
            
            'waste_heat': {
                'sources': ['高炉煤气', '转炉煤气', '焦炉煤气', '烧结烟气', '轧钢加热炉烟气'],
                'temp_range': '200-1000°C',
                'recovery_potential': '30-40% of total energy',
                'typical_applications': ['TRT发电', '干熄焦发电', '余热锅炉', '煤气发电'],
            },
            
            'electricity_characteristics': {
                'load_type': '连续生产',
                'load_curve': '高负荷连续',
                'power_factor': '0.85-0.95',
                'voltage_level': '35kV/110kV',
                'demand_factor': 0.85,
            },
            
            'harmonic_profile': {
                'sources': ['电弧炉', '大型变频器', '轧机'],
                'typical_thd': '10-20%',
                'dominant_harmonics': [2, 3, 5, 7],
                'mitigation_required': True,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_t': {
                    '长流程': 1.8,
                    '短流程': 0.5,
                },
                'scope1_percent': 75,
                'scope2_percent': 20,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '生产工艺流程(长流程/短流程)',
                    '粗钢产能',
                    '各工序能耗',
                    '煤气产生量和热值',
                    '余热资源',
                    '变压器容量',
                    '电机功率分布',
                ],
                'measurement_points': [
                    '高炉煤气流量和热值',
                    '转炉煤气回收量',
                    '焦炉煤气产量',
                    '各工序电耗',
                    '烟气温度',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    'TRT高炉煤气余压发电',
                    '干熄焦余热回收',
                    '烧结余热发电',
                    '转炉煤气回收',
                ],
                'medium_priority': [
                    '加热炉余热回收',
                    '电机变频改造',
                    '连铸坯热送热装',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '中',
                'recommended_pv_locations': ['厂房屋顶', '料场遮阳'],
                'storage_recommendation': '可配置储能用于调峰',
            },
        },
        
        'textile': {
            'name': '纺织行业',
            'name_en': 'Textile Industry',
            'sub_sectors': ['棉纺织', '毛纺织', '化纤', '印染', '服装'],
            
            'process_params': {
                'typical_processes': ['纺纱', '织造', '印染', '整理'],
                'energy_intensity_kwh_per_t': {
                    '纺纱': 800,
                    '织造': 600,
                    '印染': 2500,
                    '整理': 400,
                },
                'heat_demand_gj_per_t': {
                    '印染': 8,
                    '整理': 3,
                },
                'steam_pressure_mpa': [0.3, 0.6, 1.0],
                'typical_temp_range': '60-180°C',
            },
            
            'key_equipment': {
                '细纱机': {'power': '20-100kW', 'quantity': '大量'},
                '织布机': {'power': '1-5kW', 'quantity': '大量'},
                '印染设备': {'heat_demand': '高', 'steam_consumption': '大'},
                '定型机': {'temp': '150-200°C', 'exhaust_heat': '可回收'},
                '空压机': {'power': '50-200kW', 'load_factor': '60-80%'},
            },
            
            'waste_heat': {
                'sources': ['定型机废气', '染色机排水', '烘干机废气'],
                'temp_range': '60-150°C',
                'recovery_potential': '10-15% of heat demand',
                'typical_applications': ['预热进水', '加热生活用水', '热泵干燥'],
            },
            
            'electricity_characteristics': {
                'load_type': '连续生产',
                'load_curve': '较平稳',
                'power_factor': '0.80-0.88',
                'voltage_level': '10kV',
                'demand_factor': 0.70,
            },
            
            'harmonic_profile': {
                'sources': ['变频器', '直流驱动'],
                'typical_thd': '5-10%',
                'dominant_harmonics': [5, 7],
                'mitigation_required': False,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_t': {
                    '印染': 1.5,
                    '纺纱': 0.5,
                    '织造': 0.4,
                },
                'scope1_percent': 30,
                'scope2_percent': 65,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '产品类型和产能',
                    '主要生产设备',
                    '印染工艺参数',
                    '蒸汽消耗量',
                    '空压机系统',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '定型机余热回收',
                    '空压机系统优化',
                    '电机变频改造',
                ],
                'medium_priority': [
                    '染色机保温',
                    '照明改造',
                    '空调系统优化',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '高',
                'recommended_pv_locations': ['厂房屋顶', '仓库屋顶'],
                'storage_recommendation': '建议配置储能',
            },
        },
        
        'data_center': {
            'name': '数据中心',
            'name_en': 'Data Center',
            'sub_sectors': ['超大型', '大型', '中型', '边缘数据中心'],
            
            'process_params': {
                'typical_processes': ['IT设备', '制冷系统', '供配电', '其他'],
                'pue_range': [1.2, 2.0],
                'typical_pue': 1.5,
                'power_density_kw_per_rack': [3, 5, 8, 10, 15],
                'it_load_ratio': 0.65,
            },
            
            'key_equipment': {
                '服务器': {'heat_output': '100% of power', 'density': 'increasing'},
                'UPS': {'efficiency': '90-96%', 'loss': '4-10%'},
                '精密空调': {'cop': '3-5', 'redundancy': 'N+1'},
                '冷却塔': {'approach': '3-5°C', 'efficiency': '关键'},
                '柴油发电机': {'backup': 'required', 'test_run': 'monthly'},
            },
            
            'waste_heat': {
                'sources': ['服务器散热', 'UPS散热'],
                'temp_range': '25-45°C',
                'recovery_potential': '100% of IT load',
                'typical_applications': ['区域供热', '吸收式制冷', '热泵'],
            },
            
            'electricity_characteristics': {
                'load_type': '24小时连续',
                'load_curve': '平稳高负荷',
                'power_factor': '0.95-0.99',
                'voltage_level': '10kV/35kV/110kV',
                'demand_factor': 0.95,
            },
            
            'harmonic_profile': {
                'sources': ['UPS', '开关电源', '变频器'],
                'typical_thd': '5-15%',
                'dominant_harmonics': [5, 7, 11],
                'mitigation_required': True,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_mwh': 0.57,
                'scope1_percent': 5,
                'scope2_percent': 90,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    'IT负载容量',
                    '机柜数量和功率密度',
                    '当前PUE',
                    '制冷系统类型',
                    'UPS配置',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '自然冷却',
                    '热通道/冷通道封闭',
                    '变频空调',
                    '余热回收',
                ],
                'medium_priority': [
                    '高效UPS',
                    'LED照明',
                    '智能控制',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '中',
                'recommended_pv_locations': ['屋顶', '车棚'],
                'storage_recommendation': '必须配置储能用于备用电源',
                'storage_hours': 4,
            },
        },
        
        'nonferrous_metal': {
            'name': '有色金属',
            'name_en': 'Nonferrous Metal',
            'sub_sectors': ['铝冶炼', '铜冶炼', '铅锌冶炼', '稀有金属'],
            
            'process_params': {
                'typical_processes': ['电解', '熔炼', '精炼'],
                'energy_intensity_kwh_per_t': {
                    '原铝': 13500,
                    '精炼铜': 350,
                    '电解锌': 3200,
                },
                'heat_demand_gj_per_t': {
                    '熔炼': 5,
                    '精炼': 2,
                },
                'typical_temp_range': '200-1000°C',
            },
            
            'key_equipment': {
                '电解槽': {'power': '200-500kA', 'efficiency': '关键'},
                '熔炼炉': {'fuel': '天然气/煤气', 'efficiency': '30-50%'},
                '精炼炉': {'temp': '1000-1200°C', 'heat_loss': '大'},
            },
            
            'waste_heat': {
                'sources': ['熔炼炉烟气', '电解槽散热', '精炼炉废气'],
                'temp_range': '200-800°C',
                'recovery_potential': '20-30% of heat input',
                'typical_applications': ['余热锅炉', '预热炉料', '发电'],
            },
            
            'electricity_characteristics': {
                'load_type': '连续高负荷',
                'load_curve': '平稳',
                'power_factor': '0.90-0.98',
                'voltage_level': '35kV/110kV',
                'demand_factor': 0.90,
            },
            
            'harmonic_profile': {
                'sources': ['大功率整流器'],
                'typical_thd': '10-25%',
                'dominant_harmonics': [5, 7, 11, 13],
                'mitigation_required': True,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_t': {
                    '原铝': 12.8,
                    '精炼铜': 2.5,
                    '电解锌': 4.0,
                },
                'scope1_percent': 20,
                'scope2_percent': 75,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '金属种类和产能',
                    '电解槽电流强度',
                    '电流效率',
                    '熔炼炉类型和燃料',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '提高电流效率',
                    '余热回收',
                    '炉窑保温',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '高',
                'recommended_pv_locations': ['厂房屋顶', '空地'],
                'storage_recommendation': '建议配置',
            },
        },
        
        'metal_smelting': {
            'name': '金属冶炼',
            'name_en': 'Metal Smelting',
            'sub_sectors': ['黑色金属冶炼', '有色金属冶炼', '铸造'],
            
            'process_params': {
                'typical_processes': ['熔炼', '精炼', '铸造'],
                'energy_intensity_kwh_per_t': 500,
                'heat_demand_gj_per_t': 8,
                'typical_temp_range': '500-1600°C',
            },
            
            'key_equipment': {
                '电弧炉': {'power': '10-100MW', 'efficiency': ' improving'},
                '感应炉': {'power': '0.5-10MW', 'efficiency': '70-85%'},
                '冲天炉': {'fuel': '焦炭', 'efficiency': '40-50%'},
            },
            
            'waste_heat': {
                'sources': ['熔炼炉烟气', '铸件冷却'],
                'temp_range': '300-800°C',
                'recovery_potential': '25-35%',
                'typical_applications': ['余热锅炉', '预热炉料'],
            },
            
            'electricity_characteristics': {
                'load_type': '间歇/连续',
                'load_curve': '波动大',
                'power_factor': '0.85-0.95',
                'voltage_level': '10kV/35kV',
                'demand_factor': 0.65,
            },
            
            'harmonic_profile': {
                'sources': ['电弧炉', '感应炉', '变频器'],
                'typical_thd': '15-30%',
                'dominant_harmonics': [2, 3, 5, 7],
                'mitigation_required': True,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_t': 1.5,
                'scope1_percent': 50,
                'scope2_percent': 45,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '冶炼金属种类',
                    '炉窑类型和容量',
                    '燃料类型',
                    '年产量',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '炉窑保温',
                    '余热回收',
                    '变频控制',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '中',
                'recommended_pv_locations': ['厂房屋顶'],
                'storage_recommendation': '可选',
            },
        },
        
        'automotive': {
            'name': '汽车制造',
            'name_en': 'Automotive Manufacturing',
            'sub_sectors': ['整车制造', '零部件', '新能源汽车'],
            
            'process_params': {
                'typical_processes': ['冲压', '焊接', '涂装', '总装'],
                'energy_intensity_kwh_per_vehicle': 650,
                'heat_demand_gj_per_vehicle': 3,
                'typical_temp_range': '20-200°C',
            },
            
            'key_equipment': {
                '冲压机': {'power': '500-5000kW', 'efficiency': '85-90%'},
                '焊接机器人': {'power': '50-200kW', 'quantity': '大量'},
                '涂装线': {'energy_intensive': True, 'heat_demand': '大'},
                '空压机': {'power': '200-1000kW', 'load_factor': '70%'},
            },
            
            'waste_heat': {
                'sources': ['涂装烘干', '空压机', '冷却水'],
                'temp_range': '40-80°C',
                'recovery_potential': '10-15%',
                'typical_applications': ['预热', '生活热水'],
            },
            
            'electricity_characteristics': {
                'load_type': '两班/三班制',
                'load_curve': '有波动',
                'power_factor': '0.85-0.92',
                'voltage_level': '10kV',
                'demand_factor': 0.60,
            },
            
            'harmonic_profile': {
                'sources': ['变频器', '焊接设备'],
                'typical_thd': '5-12%',
                'dominant_harmonics': [5, 7, 11],
                'mitigation_required': False,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_vehicle': 0.5,
                'scope1_percent': 25,
                'scope2_percent': 70,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '年产能',
                    '生产工艺',
                    '主要设备',
                    '涂装工艺',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '空压机优化',
                    '涂装节能',
                    '电机变频',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '高',
                'recommended_pv_locations': ['厂房屋顶', '停车场'],
                'storage_recommendation': '建议配置',
            },
        },
        
        'new_energy_equipment': {
            'name': '新能源设备制造',
            'name_en': 'New Energy Equipment',
            'sub_sectors': ['光伏组件', '风电设备', '锂电池', '氢能设备'],
            
            'process_params': {
                'typical_processes': ['硅料制备', '电池片', '组件封装', '风机制造'],
                'energy_intensity_kwh_per_kw': {
                    '光伏组件': 150,
                    '锂电池': 80,
                },
                'clean_room_required': True,
                'typical_temp_range': '20-1000°C',
            },
            
            'key_equipment': {
                '单晶炉': {'power': '100-200kW', 'temp': '1400°C'},
                '扩散炉': {'power': '50-100kW', 'temp': '800-1000°C'},
                '层压机': {'power': '100-300kW', 'heat': '电加热'},
                '洁净空调': {'power': '大量', 'requirement': '严格'},
            },
            
            'waste_heat': {
                'sources': ['工艺热', '洁净室排风'],
                'temp_range': '40-80°C',
                'recovery_potential': '10-15%',
                'typical_applications': ['预热', '生活热水'],
            },
            
            'electricity_characteristics': {
                'load_type': '连续生产',
                'load_curve': '平稳',
                'power_factor': '0.90-0.95',
                'voltage_level': '10kV/35kV',
                'demand_factor': 0.75,
            },
            
            'harmonic_profile': {
                'sources': ['加热电源', '变频器'],
                'typical_thd': '5-10%',
                'dominant_harmonics': [5, 7],
                'mitigation_required': False,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_kw': 0.1,
                'scope1_percent': 20,
                'scope2_percent': 75,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '产品类型',
                    '产能规模',
                    '洁净度等级',
                    '工艺设备',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '洁净空调优化',
                    '工艺热回收',
                    '高效电机',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '高',
                'recommended_pv_locations': ['屋顶', '车棚'],
                'storage_recommendation': '建议配置',
            },
        },
        
        'petroleum': {
            'name': '石油石化',
            'name_en': 'Petroleum & Petrochemical',
            'sub_sectors': ['炼油', '乙烯', '合成树脂', '合成橡胶', '合成纤维'],
            
            'process_params': {
                'typical_processes': ['常减压', '催化裂化', '加氢', '乙烯裂解'],
                'energy_intensity_kwh_per_t': {
                    '炼油': 80,
                    '乙烯': 600,
                    '合成树脂': 400,
                },
                'heat_demand_gj_per_t': {
                    '炼油': 2,
                    '乙烯': 15,
                },
                'typical_temp_range': '100-900°C',
            },
            
            'key_equipment': {
                '加热炉': {'fuel': '燃料油/气', 'efficiency': '70-85%'},
                '裂解炉': {'temp': '800-900°C', 'energy_intensive': True},
                '压缩机': {'power': '1-50MW', 'driver': '电机/汽轮机'},
                '塔器': {'energy': '分离能耗', 'optimization': '有潜力'},
            },
            
            'waste_heat': {
                'sources': ['加热炉烟气', '裂解气', '工艺物流'],
                'temp_range': '100-500°C',
                'recovery_potential': '25-35%',
                'typical_applications': ['余热锅炉', '预热进料', '发电'],
            },
            
            'electricity_characteristics': {
                'load_type': '连续生产',
                'load_curve': '平稳高负荷',
                'power_factor': '0.90-0.95',
                'voltage_level': '35kV/110kV',
                'demand_factor': 0.85,
            },
            
            'harmonic_profile': {
                'sources': ['大功率变频器', '软启动'],
                'typical_thd': '5-10%',
                'dominant_harmonics': [5, 7, 11],
                'mitigation_required': False,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_t': {
                    '炼油': 0.3,
                    '乙烯': 1.8,
                },
                'scope1_percent': 55,
                'scope2_percent': 40,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '加工能力',
                    '主要装置',
                    '能耗数据',
                    '加热炉效率',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '加热炉效率提升',
                    '低温热回收',
                    '蒸汽系统优化',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '中',
                'recommended_pv_locations': ['屋顶', '空地'],
                'storage_recommendation': '可选',
            },
        },
        
        'food_processing': {
            'name': '食品加工',
            'name_en': 'Food Processing',
            'sub_sectors': ['粮食加工', '肉类加工', '乳制品', '饮料', '调味品'],
            
            'process_params': {
                'typical_processes': ['清洗', '加工', '杀菌', '包装', '冷藏'],
                'energy_intensity_kwh_per_t': 150,
                'heat_demand_gj_per_t': 2,
                'cold_demand_gj_per_t': 1,
                'typical_temp_range': '-25 to 150°C',
            },
            
            'key_equipment': {
                '锅炉': {'steam_pressure': '0.5-1.0MPa', 'efficiency': '80-90%'},
                '杀菌设备': {'temp': '120-140°C', 'steam': '消耗大'},
                '制冷机组': {'cop': '3-5', 'refrigerant': '氨/氟利昂'},
                '冷库': {'temp': '-25 to 4°C', 'insulation': '重要'},
                '空压机': {'power': '20-200kW', 'food_grade': 'required'},
            },
            
            'waste_heat': {
                'sources': ['杀菌排水', '冷凝水', '压缩机'],
                'temp_range': '40-90°C',
                'recovery_potential': '15-25%',
                'typical_applications': ['预热进水', '生活热水'],
            },
            
            'electricity_characteristics': {
                'load_type': '季节性波动',
                'load_curve': '有波动',
                'power_factor': '0.80-0.90',
                'voltage_level': '10kV',
                'demand_factor': 0.60,
            },
            
            'harmonic_profile': {
                'sources': ['变频器', '制冷压缩机'],
                'typical_thd': '5-10%',
                'dominant_harmonics': [5, 7],
                'mitigation_required': False,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_t': 0.3,
                'scope1_percent': 35,
                'scope2_percent': 60,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '产品种类',
                    '加工能力',
                    '冷链规模',
                    '蒸汽消耗',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '冷凝水回收',
                    '制冷系统优化',
                    '冷库保温',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '高',
                'recommended_pv_locations': ['屋顶', '冷库屋顶'],
                'storage_recommendation': '建议配置',
            },
        },
        
        'pharmaceutical': {
            'name': '医药制造',
            'name_en': 'Pharmaceutical Manufacturing',
            'sub_sectors': ['化学药', '中药', '生物药', '医疗器械'],
            
            'process_params': {
                'typical_processes': ['合成', '提取', '制剂', '包装', '质检'],
                'energy_intensity_kwh_per_t': 800,
                'heat_demand_gj_per_t': 5,
                'cold_demand_gj_per_t': 2,
                'clean_room_required': True,
                'typical_temp_range': '0-150°C',
            },
            
            'key_equipment': {
                '反应釜': {'power': '10-100kW', 'heating_cooling': 'required'},
                '提取罐': {'steam': '消耗大', 'temp': '60-100°C'},
                '冻干机': {'power': '50-200kW', 'refrigeration': '关键'},
                '洁净空调': {'power': '大量', 'requirement': '严格'},
                '纯水设备': {'power': '10-50kW', 'continuous': True},
            },
            
            'waste_heat': {
                'sources': ['蒸汽冷凝水', '洁净室排风', '制冷机组'],
                'temp_range': '30-80°C',
                'recovery_potential': '10-20%',
                'typical_applications': ['预热', '生活热水'],
            },
            
            'electricity_characteristics': {
                'load_type': '连续生产',
                'load_curve': '较平稳',
                'power_factor': '0.85-0.92',
                'voltage_level': '10kV',
                'demand_factor': 0.70,
            },
            
            'harmonic_profile': {
                'sources': ['变频器', '精密仪器'],
                'typical_thd': '3-8%',
                'dominant_harmonics': [5, 7],
                'mitigation_required': False,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_t': 1.0,
                'scope1_percent': 30,
                'scope2_percent': 65,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '药品类型',
                    'GMP等级',
                    '洁净面积',
                    '主要设备',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '洁净空调优化',
                    '冷凝水回收',
                    '制冷系统优化',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '高',
                'recommended_pv_locations': ['屋顶', '车棚'],
                'storage_recommendation': '建议配置',
            },
        },
        
        'electronics': {
            'name': '电子制造',
            'name_en': 'Electronics Manufacturing',
            'sub_sectors': ['集成电路', 'PCB', 'LED', '消费电子'],
            
            'process_params': {
                'typical_processes': ['晶圆制造', '封装测试', 'SMT', '组装'],
                'energy_intensity_kwh_per_m2': 800,
                'clean_room_required': True,
                'typical_temp_range': '20-25°C (恒温)',
            },
            
            'key_equipment': {
                '光刻机': {'power': '100-500kW', 'precision': '极高'},
                '刻蚀机': {'power': '50-200kW', 'vacuum': 'required'},
                '洁净空调': {'power': '非常大', 'requirement': '极严格'},
                '纯水系统': {'power': '大', 'quality': '超纯水'},
                '空压机': {'power': '大', 'quality': '无油'},
            },
            
            'waste_heat': {
                'sources': ['工艺冷却水', '洁净室排风', '空压机'],
                'temp_range': '25-40°C',
                'recovery_potential': '10-15%',
                'typical_applications': ['预热', '生活热水'],
            },
            
            'electricity_characteristics': {
                'load_type': '24小时连续',
                'load_curve': '平稳高负荷',
                'power_factor': '0.90-0.98',
                'voltage_level': '10kV/35kV',
                'demand_factor': 0.85,
            },
            
            'harmonic_profile': {
                'sources': ['精密电源', '变频器'],
                'typical_thd': '3-8%',
                'dominant_harmonics': [5, 7, 11],
                'mitigation_required': True,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_m2': 0.5,
                'scope1_percent': 10,
                'scope2_percent': 85,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '产品类型',
                    '洁净度等级',
                    '洁净面积',
                    '主要工艺设备',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '洁净空调优化',
                    '工艺冷却水优化',
                    '空压机优化',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '高',
                'recommended_pv_locations': ['屋顶', '车棚'],
                'storage_recommendation': '建议配置',
            },
        },
        
        'paper': {
            'name': '造纸行业',
            'name_en': 'Paper Industry',
            'sub_sectors': ['制浆', '造纸', '纸制品'],
            
            'process_params': {
                'typical_processes': ['备料', '制浆', '造纸', '涂布'],
                'energy_intensity_kwh_per_t': 600,
                'heat_demand_gj_per_t': 12,
                'steam_pressure_mpa': [0.3, 0.5, 1.0],
                'typical_temp_range': '60-150°C',
            },
            
            'key_equipment': {
                '蒸煮器': {'steam': '消耗大', 'temp': '150-170°C'},
                '造纸机': {'power': '大', 'width': '关键参数'},
                '干燥部': {'steam': '消耗最大', 'efficiency': '关键'},
                '空压机': {'power': '100-500kW', 'continuous': True},
            },
            
            'waste_heat': {
                'sources': ['干燥排气', '冷凝水', '黑液'],
                'temp_range': '60-100°C',
                'recovery_potential': '20-30%',
                'typical_applications': ['预热进水', '蒸发黑液'],
            },
            
            'electricity_characteristics': {
                'load_type': '连续生产',
                'load_curve': '较平稳',
                'power_factor': '0.85-0.92',
                'voltage_level': '10kV',
                'demand_factor': 0.75,
            },
            
            'harmonic_profile': {
                'sources': ['变频器', '直流驱动'],
                'typical_thd': '5-12%',
                'dominant_harmonics': [5, 7],
                'mitigation_required': False,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_t': 0.8,
                'scope1_percent': 40,
                'scope2_percent': 55,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '纸种和产能',
                    '造纸机规格',
                    '蒸汽消耗',
                    '黑液处理',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '干燥部余热回收',
                    '冷凝水回收',
                    '变频驱动',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '高',
                'recommended_pv_locations': ['屋顶', '原料棚'],
                'storage_recommendation': '建议配置',
            },
        },
        
        'cement': {
            'name': '水泥行业',
            'name_en': 'Cement Industry',
            'sub_sectors': ['熟料生产', '水泥粉磨', '混凝土'],
            
            'process_params': {
                'typical_processes': ['生料制备', '熟料煅烧', '水泥粉磨'],
                'energy_intensity_kwh_per_t': 100,
                'heat_demand_gj_per_t': 3.5,
                'typical_temp_range': '200-1450°C',
            },
            
            'key_equipment': {
                '回转窑': {'fuel': '煤/替代燃料', 'temp': '1450°C'},
                '原料磨': {'power': '1000-5000kW', 'type': '立磨/球磨'},
                '水泥磨': {'power': '1000-5000kW', 'efficiency': '关键'},
                '预热器': {'stages': '4-6级', 'efficiency': '关键'},
                '冷却机': {'heat_recovery': '重要'},
            },
            
            'waste_heat': {
                'sources': ['窑头废气', '窑尾废气', '冷却机废气'],
                'temp_range': '250-400°C',
                'recovery_potential': '30-40%',
                'typical_applications': ['余热发电', '原料烘干'],
            },
            
            'electricity_characteristics': {
                'load_type': '连续生产',
                'load_curve': '平稳',
                'power_factor': '0.85-0.92',
                'voltage_level': '10kV/35kV',
                'demand_factor': 0.80,
            },
            
            'harmonic_profile': {
                'sources': ['大功率变频器'],
                'typical_thd': '5-10%',
                'dominant_harmonics': [5, 7, 11],
                'mitigation_required': False,
            },
            
            'carbon_profile': {
                'emission_intensity_tco2_per_t': 0.8,
                'scope1_percent': 60,
                'scope2_percent': 35,
                'scope3_percent': 5,
            },
            
            'site_survey': {
                'key_info': [
                    '熟料产能',
                    '窑型规格',
                    '余热发电情况',
                    '替代燃料使用',
                ],
            },
            
            'energy_saving_measures': {
                'high_priority': [
                    '余热发电',
                    '高效粉磨',
                    '替代燃料',
                ],
            },
            
            'renewable_recommendations': {
                'pv_suitability': '中',
                'recommended_pv_locations': ['矿山', '厂房屋顶'],
                'storage_recommendation': '可选',
            },
        },
    }
    
    def __init__(self):
        """初始化行业数据库"""
        pass
    
    def get_industry_list(self) -> List[str]:
        """获取行业列表"""
        return list(self.INDUSTRIES.keys())
    
    def get_industry_info(self, industry_code: str) -> Dict:
        """
        获取行业详细信息
        
        Args:
            industry_code: 行业代码
        
        Returns:
            行业详细信息
        """
        return self.INDUSTRIES.get(industry_code, {})
    
    def get_industry_by_name(self, name: str) -> Optional[str]:
        """
        根据名称查找行业代码
        
        Args:
            name: 行业名称(中英文均可)
        
        Returns:
            行业代码或None
        """
        for code, info in self.INDUSTRIES.items():
            if name in [info.get('name', ''), info.get('name_en', '')]:
                return code
        return None
    
    def get_site_survey_guide(self, industry_code: str) -> Dict:
        """
        获取踏勘指导
        
        Args:
            industry_code: 行业代码
        
        Returns:
            踏勘指导信息
        """
        industry = self.INDUSTRIES.get(industry_code, {})
        return industry.get('site_survey', {})
    
    def get_energy_saving_measures(self, industry_code: str, priority: str = None) -> List[str]:
        """
        获取节能措施建议
        
        Args:
            industry_code: 行业代码
            priority: 优先级 (high/medium/low)
        
        Returns:
            节能措施列表
        """
        industry = self.INDUSTRIES.get(industry_code, {})
        measures = industry.get('energy_saving_measures', {})
        
        if priority:
            return measures.get(f'{priority}_priority', [])
        
        # 返回所有措施
        all_measures = []
        for p in ['high_priority', 'medium_priority', 'low_priority']:
            all_measures.extend(measures.get(p, []))
        return all_measures
    
    def get_harmonic_info(self, industry_code: str) -> Dict:
        """
        获取谐波信息
        
        Args:
            industry_code: 行业代码
        
        Returns:
            谐波特征信息
        """
        industry = self.INDUSTRIES.get(industry_code, {})
        return industry.get('harmonic_profile', {})
    
    def get_renewable_recommendations(self, industry_code: str) -> Dict:
        """
        获取可再生能源建议
        
        Args:
            industry_code: 行业代码
        
        Returns:
            光伏储能建议
        """
        industry = self.INDUSTRIES.get(industry_code, {})
        return industry.get('renewable_recommendations', {})
    
    def get_carbon_profile(self, industry_code: str) -> Dict:
        """
        获取碳排放特征
        
        Args:
            industry_code: 行业代码
        
        Returns:
            碳排放信息
        """
        industry = self.INDUSTRIES.get(industry_code, {})
        return industry.get('carbon_profile', {})
    
    def search_industries_by_equipment(self, equipment_name: str) -> List[str]:
        """
        根据设备名称搜索相关行业的行业
        
        Args:
            equipment_name: 设备名称
        
        Returns:
            相关行业代码列表
        """
        results = []
        for code, info in self.INDUSTRIES.items():
            equipment = info.get('key_equipment', {})
            if equipment_name in equipment:
                results.append(code)
        return results
    
    def compare_industries(self, industry_codes: List[str], metric: str = 'energy_intensity') -> Dict:
        """
        对比多个行业的指标
        
        Args:
            industry_codes: 行业代码列表
            metric: 对比指标
        
        Returns:
            对比结果
        """
        comparison = {}
        for code in industry_codes:
            industry = self.INDUSTRIES.get(code, {})
            if metric == 'energy_intensity':
                value = industry.get('process_params', {}).get('energy_intensity_kwh_per_t', 0)
            elif metric == 'carbon_intensity':
                value = industry.get('carbon_profile', {}).get('emission_intensity_tco2_per_t', 0)
            else:
                value = None
            
            comparison[code] = {
                'name': industry.get('name', ''),
                'value': value
            }
        
        return comparison
