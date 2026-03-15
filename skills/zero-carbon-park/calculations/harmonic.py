"""
谐波分析与治理模块
================
包含谐波计算、谐波源识别、治理方案设计
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class HarmonicSource:
    """谐波源数据类"""
    name: str
    power: float  # kW
    harmonic_spectrum: Dict[int, float]  # {谐波次数: 含有率%}
    typical_thd: float  # 典型THD


class HarmonicAnalyzer:
    """谐波分析器"""
    
    # 典型谐波源频谱
    TYPICAL_HARMONIC_SOURCES = {
        'vfd_6pulse': {
            'name': '6脉波变频器',
            'harmonics': {5: 65, 7: 40, 11: 15, 13: 10, 17: 6, 19: 5},
            'typical_thd': 80,
        },
        'vfd_12pulse': {
            'name': '12脉波变频器',
            'harmonics': {11: 25, 13: 20, 23: 8, 25: 6},
            'typical_thd': 35,
        },
        'vfd_18pulse': {
            'name': '18脉波变频器',
            'harmonics': {17: 15, 19: 12, 35: 4, 37: 3},
            'typical_thd': 20,
        },
        'rectifier_6pulse': {
            'name': '6脉波整流器',
            'harmonics': {5: 70, 7: 45, 11: 18, 13: 12, 17: 7, 19: 6},
            'typical_thd': 85,
        },
        'rectifier_12pulse': {
            'name': '12脉波整流器',
            'harmonics': {11: 28, 13: 22, 23: 9, 25: 7},
            'typical_thd': 38,
        },
        'ups': {
            'name': 'UPS电源',
            'harmonics': {5: 35, 7: 25, 11: 12, 13: 8},
            'typical_thd': 45,
        },
        'led_driver': {
            'name': 'LED驱动电源',
            'harmonics': {3: 55, 5: 35, 7: 20, 9: 15},
            'typical_thd': 70,
        },
        'welding_machine': {
            'name': '电焊机',
            'harmonics': {3: 40, 5: 60, 7: 35, 9: 20},
            'typical_thd': 75,
        },
        'arc_furnace': {
            'name': '电弧炉',
            'harmonics': {2: 15, 3: 35, 5: 45, 7: 30, 11: 15},
            'typical_thd': 65,
        },
        'induction_motor': {
            'name': '感应电机(变频)',
            'harmonics': {5: 25, 7: 15, 11: 8, 13: 5},
            'typical_thd': 32,
        },
        'dc_drive': {
            'name': '直流调速',
            'harmonics': {5: 55, 7: 35, 11: 12, 13: 8},
            'typical_thd': 65,
        },
        'switching_power_supply': {
            'name': '开关电源',
            'harmonics': {3: 60, 5: 40, 7: 25, 9: 15},
            'typical_thd': 75,
        },
    }
    
    # 谐波限值标准 (GB/T 14549)
    HARMONIC_LIMITS = {
        'voltage_380v': {
            'thd': 5.0,
            'odd_harmonics': {3: 4.0, 5: 6.0, 7: 5.0, 9: 1.2, 11: 3.5, 13: 3.0},
            'even_harmonics': 2.0,
        },
        'voltage_6kv': {
            'thd': 4.0,
            'odd_harmonics': {3: 3.2, 5: 4.0, 7: 3.2, 9: 1.0, 11: 2.4, 13: 2.0},
            'even_harmonics': 1.6,
        },
        'voltage_10kv': {
            'thd': 4.0,
            'odd_harmonics': {3: 3.2, 5: 4.0, 7: 3.2, 9: 1.0, 11: 2.4, 13: 2.0},
            'even_harmonics': 1.6,
        },
        'voltage_35kv': {
            'thd': 3.0,
            'odd_harmonics': {3: 2.4, 5: 3.2, 7: 2.4, 9: 0.8, 11: 1.6, 13: 1.2},
            'even_harmonics': 1.2,
        },
    }
    
    # 治理设备参数
    MITIGATION_EQUIPMENT = {
        'passive_filter': {
            'name': '无源滤波器',
            'filterable_harmonics': [5, 7, 11, 13],
            'efficiency': 0.85,
            'cost_per_kvar': 150,
            'response_time': 'ms',
        },
        'active_filter': {
            'name': '有源滤波器(APF)',
            'filterable_harmonics': '2-50次',
            'efficiency': 0.95,
            'cost_per_a': 200,
            'response_time': 'us',
        },
        'hybrid_filter': {
            'name': '混合滤波器',
            'filterable_harmonics': '2-50次',
            'efficiency': 0.90,
            'cost_per_kvar': 250,
            'response_time': 'ms',
        },
        'active_frontend': {
            'name': '有源前端(AFE)',
            'filterable_harmonics': '2-50次',
            'efficiency': 0.98,
            'cost_percent_premium': 30,
            'response_time': 'real-time',
        },
        '12pulse_converter': {
            'name': '12脉波变换器',
            'filterable_harmonics': '5,7次消除',
            'efficiency': 0.95,
            'cost_percent_premium': 20,
        },
        '18pulse_converter': {
            'name': '18脉波变换器',
            'filterable_harmonics': '5,7,11,13次消除',
            'efficiency': 0.95,
            'cost_percent_premium': 35,
        },
    }
    
    def __init__(self):
        pass
    
    # ==================== 谐波计算 ====================
    
    def calculate_thd(
        self,
        harmonics: Dict[int, float]
    ) -> Dict[str, float]:
        """
        计算总谐波畸变率
        
        Args:
            harmonics: {谐波次数: 含有率%}
        
        Returns:
            THD计算结果
        """
        # 电压THD计算 (各次谐波平方和开方)
        sum_squares = sum(h ** 2 for h in harmonics.values())
        thd = math.sqrt(sum_squares)
        
        # 奇次谐波THD
        odd_harmonics = {k: v for k, v in harmonics.items() if k % 2 == 1}
        odd_thd = math.sqrt(sum(h ** 2 for h in odd_harmonics.values()))
        
        # 偶次谐波THD
        even_harmonics = {k: v for k, v in harmonics.items() if k % 2 == 0}
        even_thd = math.sqrt(sum(h ** 2 for h in even_harmonics.values())) if even_harmonics else 0
        
        # 各次谐波占比
        harmonic_distribution = {k: round(v / thd * 100, 1) for k, v in harmonics.items()}
        
        return {
            'thd_percent': round(thd, 2),
            'odd_thd_percent': round(odd_thd, 2),
            'even_thd_percent': round(even_thd, 2),
            'harmonics': harmonics,
            'harmonic_distribution': harmonic_distribution,
        }
    
    def calculate_current_thd(
        self,
        fundamental_current: float,
        harmonics: Dict[int, float]
    ) -> Dict[str, float]:
        """
        计算电流THD和有效值
        
        Args:
            fundamental_current: 基波电流 (A)
            harmonics: {谐波次数: 含有率%}
        
        Returns:
            电流谐波分析
        """
        # 电流THD
        thd_result = self.calculate_thd(harmonics)
        
        # 各次谐波电流
        harmonic_currents = {}
        for order, percent in harmonics.items():
            harmonic_currents[order] = fundamental_current * percent / 100
        
        # 总电流有效值
        sum_squares = fundamental_current ** 2 + sum(i ** 2 for i in harmonic_currents.values())
        rms_current = math.sqrt(sum_squares)
        
        # 电流增加率
        current_increase = (rms_current - fundamental_current) / fundamental_current * 100
        
        return {
            'fundamental_current_a': fundamental_current,
            'rms_current_a': round(rms_current, 2),
            'thd_percent': thd_result['thd_percent'],
            'current_increase_percent': round(current_increase, 2),
            'harmonic_currents_a': {k: round(v, 2) for k, v in harmonic_currents.items()},
        }
    
    def aggregate_harmonics(
        self,
        sources: List[HarmonicSource],
        diversity_factor: float = 0.8
    ) -> Dict[str, any]:
        """
        聚合多个谐波源的谐波
        
        Args:
            sources: 谐波源列表
            diversity_factor: 参差系数
        
        Returns:
            聚合后的谐波分析
        """
        # 收集所有谐波次数
        all_orders = set()
        for source in sources:
            all_orders.update(source.harmonic_spectrum.keys())
        
        # 聚合各次谐波 (考虑参差)
        aggregated = {}
        for order in sorted(all_orders):
            # 各源该次谐波电流的平方和
            sum_squares = 0
            for source in sources:
                if order in source.harmonic_spectrum:
                    # 估算电流
                    current = source.power / 0.38 / 1.732  # 简化估算
                    harmonic_current = current * source.harmonic_spectrum[order] / 100
                    sum_squares += harmonic_current ** 2
            
            # 考虑参差
            aggregated[order] = math.sqrt(sum_squares) * diversity_factor
        
        # 转换为含有率
        fundamental = sum(s.power for s in sources) / 0.38 / 1.732
        aggregated_percent = {k: round(v / fundamental * 100, 2) for k, v in aggregated.items()}
        
        # 计算聚合THD
        thd_result = self.calculate_thd(aggregated_percent)
        
        return {
            'aggregated_harmonics_percent': aggregated_percent,
            'total_thd_percent': thd_result['thd_percent'],
            'number_of_sources': len(sources),
            'diversity_factor': diversity_factor,
        }
    
    # ==================== 谐波影响分析 ====================
    
    def analyze_harmonic_impact(
        self,
        thd_voltage: float,
        thd_current: float,
        transformer_capacity: float,
        load_power: float
    ) -> Dict[str, any]:
        """
        分析谐波影响
        
        Args:
            thd_voltage: 电压THD (%)
            thd_current: 电流THD (%)
            transformer_capacity: 变压器容量 (kVA)
            load_power: 负载功率 (kW)
        
        Returns:
            谐波影响分析
        """
        impacts = []
        
        # 变压器损耗增加
        # ΔP = P_cu * (THD_I)²
        transformer_loading = load_power / transformer_capacity
        additional_loss = transformer_loading ** 2 * thd_current ** 2 / 10000 * 100
        impacts.append({
            'type': '变压器损耗增加',
            'value': f'{round(additional_loss, 1)}%',
            'severity': '高' if additional_loss > 10 else '中' if additional_loss > 5 else '低',
        })
        
        # 电缆发热
        cable_derating = 1 / (1 + (thd_current / 100) ** 2)
        impacts.append({
            'type': '电缆载流量下降',
            'value': f'{round((1-cable_derating)*100, 1)}%',
            'severity': '高' if cable_derating < 0.85 else '中' if cable_derating < 0.92 else '低',
        })
        
        # 电机影响
        motor_derating = 1 - 0.05 * (thd_voltage / 100) ** 2
        impacts.append({
            'type': '电机效率下降',
            'value': f'{round((1-motor_derating)*100, 1)}%',
            'severity': '中' if thd_voltage > 8 else '低',
        })
        
        # 电容器影响
        capacitor_stress = 1 + thd_voltage / 100
        impacts.append({
            'type': '电容器过电压',
            'value': f'{round((capacitor_stress-1)*100, 1)}%',
            'severity': '高' if capacitor_stress > 1.15 else '中' if capacitor_stress > 1.1 else '低',
        })
        
        # 继电保护影响
        impacts.append({
            'type': '继电保护误动作风险',
            'value': '存在',
            'severity': '高' if thd_voltage > 10 else '中' if thd_voltage > 5 else '低',
        })
        
        # 通信干扰
        impacts.append({
            'type': '通信干扰',
            'value': '可能',
            'severity': '中' if thd_voltage > 8 else '低',
        })
        
        # 综合评估
        overall_severity = '严重' if thd_voltage > 10 or thd_current > 30 else \
                         '中等' if thd_voltage > 5 or thd_current > 15 else '轻微'
        
        return {
            'thd_voltage_percent': thd_voltage,
            'thd_current_percent': thd_current,
            'impacts': impacts,
            'overall_severity': overall_severity,
            'mitigation_required': thd_voltage > 5 or thd_current > 20,
        }
    
    # ==================== 谐波治理设计 ====================
    
    def check_compliance(
        self,
        harmonics: Dict[int, float],
        voltage_level: str = 'voltage_380v'
    ) -> Dict[str, any]:
        """
        检查谐波是否达标
        
        Args:
            harmonics: 谐波含有率
            voltage_level: 电压等级
        
        Returns:
            合规性检查结果
        """
        limits = self.HARMONIC_LIMITS.get(voltage_level, self.HARMONIC_LIMITS['voltage_380v'])
        
        # 检查THD
        thd_result = self.calculate_thd(harmonics)
        thd_ok = thd_result['thd_percent'] <= limits['thd']
        
        # 检查各次谐波
        violations = []
        for order, value in harmonics.items():
            if order % 2 == 1:  # 奇次
                limit = limits['odd_harmonics'].get(order, 2.0)
            else:  # 偶次
                limit = limits['even_harmonics']
            
            if value > limit:
                violations.append({
                    'order': order,
                    'measured': value,
                    'limit': limit,
                    'excess_percent': round((value - limit) / limit * 100, 1),
                })
        
        return {
            'thd_measured': thd_result['thd_percent'],
            'thd_limit': limits['thd'],
            'thd_compliance': thd_ok,
            'individual_compliance': len(violations) == 0,
            'violations': violations,
            'overall_compliance': thd_ok and len(violations) == 0,
        }
    
    def design_mitigation_system(
        self,
        harmonics: Dict[int, float],
        load_power: float,
        voltage: float = 380,
        target_thd: float = 5.0
    ) -> Dict[str, any]:
        """
        设计谐波治理方案
        
        Args:
            harmonics: 谐波含有率
            load_power: 负载功率 (kW)
            voltage: 电压 (V)
            target_thd: 目标THD
        
        Returns:
            治理方案
        """
        # 计算基波电流
        fundamental_current = load_power * 1000 / voltage / 1.732
        
        # 当前THD
        current_thd = self.calculate_current_thd(fundamental_current, harmonics)
        
        # 需要补偿的谐波电流
        harmonic_currents = current_thd['harmonic_currents_a']
        total_harmonic_current = math.sqrt(sum(i**2 for i in harmonic_currents.values()))
        
        # 方案1: 有源滤波器
        apf_capacity = total_harmonic_current * 1.2  # 留20%裕量
        apf_cost = apf_capacity * self.MITIGATION_EQUIPMENT['active_filter']['cost_per_a']
        
        # 方案2: 无源滤波器 (针对主要谐波)
        dominant_harmonics = sorted(harmonics.items(), key=lambda x: x[1], reverse=True)[:2]
        passive_filters = []
        passive_cost = 0
        for order, _ in dominant_harmonics:
            filter_capacity = harmonic_currents.get(order, 0) * voltage * 1.732 / 1000  # kVAR
            passive_filters.append({
                'order': order,
                'capacity_kvar': round(filter_capacity, 1),
            })
            passive_cost += filter_capacity * self.MITIGATION_EQUIPMENT['passive_filter']['cost_per_kvar']
        
        # 方案3: 混合滤波器
        hybrid_cost = apf_capacity * 0.5 * self.MITIGATION_EQUIPMENT['hybrid_filter']['cost_per_kvar']
        
        # 推荐方案
        if current_thd['thd_percent'] > 50:
            recommendation = 'active_filter'
            reason = 'THD过高，建议采用有源滤波器'
        elif len(dominant_harmonics) <= 2 and current_thd['thd_percent'] < 30:
            recommendation = 'passive_filter'
            reason = '谐波次数集中，可采用无源滤波器'
        else:
            recommendation = 'hybrid_filter'
            reason = '建议采用混合滤波器'
        
        return {
            'current_thd_percent': current_thd['thd_percent'],
            'target_thd_percent': target_thd,
            'fundamental_current_a': round(fundamental_current, 1),
            'total_harmonic_current_a': round(total_harmonic_current, 2),
            'options': {
                'active_filter': {
                    'capacity_a': round(apf_capacity, 0),
                    'investment_yuan': round(apf_cost, 0),
                    'features': ['响应快', '滤波范围广', '可动态补偿'],
                },
                'passive_filter': {
                    'filters': passive_filters,
                    'investment_yuan': round(passive_cost, 0),
                    'features': ['成本低', '可靠性高', '维护简单'],
                },
                'hybrid_filter': {
                    'capacity_a': round(apf_capacity * 0.5, 0),
                    'investment_yuan': round(hybrid_cost, 0),
                    'features': ['综合性能优', '性价比高'],
                },
            },
            'recommendation': recommendation,
            'reason': reason,
        }
    
    def get_source_mitigation_options(
        self,
        source_type: str
    ) -> List[Dict[str, str]]:
        """
        获取谐波源的治理选项
        
        Args:
            source_type: 谐波源类型代码
        
        Returns:
            治理选项列表
        """
        source = self.TYPICAL_HARMONIC_SOURCES.get(source_type, {})
        thd = source.get('typical_thd', 50)
        
        options = []
        
        if 'vfd' in source_type:
            options.append({
                'method': 'multi_pulse_converter',
                'description': '改用多脉波变频器',
                'effectiveness': 'THD降至20-35%',
                'cost': '增加20-35%',
            })
            options.append({
                'method': 'active_frontend',
                'description': '采用有源前端变频器',
                'effectiveness': 'THD<5%',
                'cost': '增加30%',
            })
            options.append({
                'method': 'dc_reactor',
                'description': '加装直流电抗器',
                'effectiveness': 'THD降低30%',
                'cost': '低成本',
            })
        
        if 'rectifier' in source_type:
            options.append({
                'method': 'multi_pulse_converter',
                'description': '改用多脉波整流器',
                'effectiveness': 'THD降至20-35%',
                'cost': '适中',
            })
            options.append({
                'method': 'active_filter',
                'description': '加装APF',
                'effectiveness': 'THD<5%',
                'cost': '较高',
            })
        
        if 'ups' in source_type:
            options.append({
                'method': 'active_filter',
                'description': '加装APF',
                'effectiveness': 'THD<5%',
                'cost': '适中',
            })
        
        if 'led' in source_type:
            options.append({
                'method': 'better_driver',
                'description': '选用高品质驱动电源',
                'effectiveness': 'THD<20%',
                'cost': '增加10%',
            })
        
        return options
    
    # ==================== 行业谐波特征 ====================
    
    def get_industry_harmonic_profile(
        self,
        industry_type: str
    ) -> Dict[str, any]:
        """
        获取行业谐波特征
        
        Args:
            industry_type: 行业类型
        
        Returns:
            行业谐波特征
        """
        profiles = {
            'chemical': {
                'main_sources': ['变频器', '大功率整流器'],
                'typical_thd': '8-15%',
                'dominant_harmonics': [5, 7, 11, 13],
                'mitigation_priority': '中',
                'typical_solutions': ['APF', '多脉波整流'],
            },
            'steel': {
                'main_sources': ['电弧炉', '轧机', '大功率变频器'],
                'typical_thd': '10-20%',
                'dominant_harmonics': [2, 3, 5, 7],
                'mitigation_priority': '高',
                'typical_solutions': ['SVC', 'APF', 'TSC'],
            },
            'data_center': {
                'main_sources': ['UPS', '开关电源'],
                'typical_thd': '5-15%',
                'dominant_harmonics': [5, 7, 11],
                'mitigation_priority': '中',
                'typical_solutions': ['12脉波UPS', 'APF'],
            },
            'nonferrous_metal': {
                'main_sources': ['大功率整流器'],
                'typical_thd': '10-25%',
                'dominant_harmonics': [5, 7, 11, 13],
                'mitigation_priority': '高',
                'typical_solutions': ['多脉波整流', 'APF'],
            },
            'automotive': {
                'main_sources': ['变频器', '焊接设备'],
                'typical_thd': '5-12%',
                'dominant_harmonics': [5, 7, 11],
                'mitigation_priority': '低',
                'typical_solutions': ['直流电抗器', 'APF'],
            },
        }
        
        return profiles.get(industry_type, {
            'main_sources': ['变频器'],
            'typical_thd': '5-10%',
            'dominant_harmonics': [5, 7],
            'mitigation_priority': '低',
            'typical_solutions': ['直流电抗器'],
        })
