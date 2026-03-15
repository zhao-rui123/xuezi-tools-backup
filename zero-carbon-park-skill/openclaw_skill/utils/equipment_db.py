"""
设备数据库模块
============
包含节能设备、新能源设备的产品参数和选型数据
"""

from typing import Dict, List, Optional


class EquipmentDatabase:
    """设备数据库类"""
    
    # 光伏组件数据库
    PV_MODULES = {
        'mono_540w': {
            'type': '单晶硅',
            'power': 540,
            'efficiency': 0.208,
            'voc': 49.5,
            'isc': 13.8,
            'dimensions': (2278, 1134, 35),
            'weight': 28.5,
            'temp_coefficient': -0.35,
            'warranty_product': 12,
            'warranty_power': 25,
            'price_per_w': 1.8,
        },
        'mono_550w': {
            'type': '单晶硅',
            'power': 550,
            'efficiency': 0.211,
            'voc': 49.8,
            'isc': 13.9,
            'dimensions': (2278, 1134, 35),
            'weight': 28.5,
            'temp_coefficient': -0.35,
            'warranty_product': 12,
            'warranty_power': 25,
            'price_per_w': 1.75,
        },
        'mono_600w': {
            'type': '单晶硅',
            'power': 600,
            'efficiency': 0.215,
            'voc': 51.2,
            'isc': 14.5,
            'dimensions': (2384, 1303, 35),
            'weight': 32.0,
            'temp_coefficient': -0.35,
            'warranty_product': 12,
            'warranty_power': 25,
            'price_per_w': 1.7,
        },
        'hjt_700w': {
            'type': 'HJT异质结',
            'power': 700,
            'efficiency': 0.225,
            'voc': 53.5,
            'isc': 15.2,
            'dimensions': (2384, 1303, 35),
            'weight': 32.5,
            'temp_coefficient': -0.26,
            'warranty_product': 15,
            'warranty_power': 30,
            'price_per_w': 2.2,
        },
        'topcon_580w': {
            'type': 'TOPCon',
            'power': 580,
            'efficiency': 0.220,
            'voc': 50.5,
            'isc': 14.2,
            'dimensions': (2278, 1134, 35),
            'weight': 28.5,
            'temp_coefficient': -0.30,
            'warranty_product': 15,
            'warranty_power': 30,
            'price_per_w': 1.9,
        },
    }
    
    # 逆变器数据库
    INVERTERS = {
        'string_50k': {
            'type': '组串式',
            'power': 50,
            'mppt_channels': 6,
            'max_efficiency': 0.986,
            'euro_efficiency': 0.984,
            'protection_rating': 'IP65',
            'cooling': '自然对流',
            'dimensions': (670, 580, 270),
            'weight': 42,
            'price': 12000,
        },
        'string_100k': {
            'type': '组串式',
            'power': 100,
            'mppt_channels': 10,
            'max_efficiency': 0.988,
            'euro_efficiency': 0.986,
            'protection_rating': 'IP65',
            'cooling': '智能风冷',
            'dimensions': (1050, 650, 320),
            'weight': 78,
            'price': 22000,
        },
        'string_136k': {
            'type': '组串式',
            'power': 136,
            'mppt_channels': 12,
            'max_efficiency': 0.990,
            'euro_efficiency': 0.988,
            'protection_rating': 'IP66',
            'cooling': '智能风冷',
            'dimensions': (1150, 700, 350),
            'weight': 95,
            'price': 28000,
        },
        'central_2.5mw': {
            'type': '集中式',
            'power': 2500,
            'mppt_channels': 2,
            'max_efficiency': 0.992,
            'euro_efficiency': 0.990,
            'protection_rating': 'IP54',
            'cooling': '温控风冷',
            'dimensions': (3500, 2200, 2500),
            'weight': 4500,
            'price': 350000,
        },
        'hybrid_50k': {
            'type': '光储混合',
            'power': 50,
            'battery_voltage': '600-850V',
            'max_efficiency': 0.985,
            'protection_rating': 'IP65',
            'cooling': '自然对流',
            'price': 35000,
        },
    }
    
    # 储能系统数据库
    BATTERY_SYSTEMS = {
        'lithium_100kwh': {
            'type': '磷酸铁锂',
            'capacity': 100,
            'power': 50,
            'voltage': 768,
            'round_trip_efficiency': 0.94,
            'cycle_life': 6000,
            'calendar_life': 15,
            'dimensions': (1200, 800, 2200),
            'weight': 1200,
            'price_per_kwh': 1200,
            'warranty': 10,
        },
        'lithium_215kwh': {
            'type': '磷酸铁锂',
            'capacity': 215,
            'power': 100,
            'voltage': 768,
            'round_trip_efficiency': 0.94,
            'cycle_life': 6000,
            'calendar_life': 15,
            'dimensions': (1400, 1200, 2400),
            'weight': 2500,
            'price_per_kwh': 1100,
            'warranty': 10,
        },
        'lithium_372kwh': {
            'type': '磷酸铁锂',
            'capacity': 372,
            'power': 186,
            'voltage': 1331,
            'round_trip_efficiency': 0.94,
            'cycle_life': 6000,
            'calendar_life': 15,
            'dimensions': (3000, 2400, 2600),
            'weight': 4200,
            'price_per_kwh': 1000,
            'warranty': 10,
        },
        'flow_vanadium_250kwh': {
            'type': '全钒液流',
            'capacity': 250,
            'power': 62.5,
            'voltage': 800,
            'round_trip_efficiency': 0.75,
            'cycle_life': 15000,
            'calendar_life': 20,
            'dimensions': (6000, 2400, 3000),
            'weight': 8000,
            'price_per_kwh': 2000,
            'warranty': 15,
        },
    }
    
    # 风力发电机数据库
    WIND_TURBINES = {
        'small_50kw': {
            'type': '小型风力发电',
            'power': 50,
            'rotor_diameter': 15,
            'cut_in_speed': 3,
            'rated_speed': 12,
            'cut_out_speed': 25,
            'survival_speed': 50,
            'hub_height': 18,
            'weight': 1200,
            'price': 300000,
        },
        'small_100kw': {
            'type': '小型风力发电',
            'power': 100,
            'rotor_diameter': 22,
            'cut_in_speed': 3,
            'rated_speed': 11,
            'cut_out_speed': 25,
            'survival_speed': 50,
            'hub_height': 24,
            'weight': 2500,
            'price': 550000,
        },
        'medium_500kw': {
            'type': '中型风力发电',
            'power': 500,
            'rotor_diameter': 40,
            'cut_in_speed': 3,
            'rated_speed': 12,
            'cut_out_speed': 25,
            'survival_speed': 52,
            'hub_height': 40,
            'weight': 15000,
            'price': 2500000,
        },
    }
    
    # 高效电机数据库
    EFFICIENT_MOTORS = {
        'ie3_7.5kw': {
            'power': 7.5,
            'efficiency_class': 'IE3',
            'efficiency': 0.93,
            'speed': 1470,
            'voltage': 380,
            'protection': 'IP55',
            'price': 3500,
        },
        'ie3_15kw': {
            'power': 15,
            'efficiency_class': 'IE3',
            'efficiency': 0.94,
            'speed': 1475,
            'voltage': 380,
            'protection': 'IP55',
            'price': 5800,
        },
        'ie3_30kw': {
            'power': 30,
            'efficiency_class': 'IE3',
            'efficiency': 0.95,
            'speed': 1480,
            'voltage': 380,
            'protection': 'IP55',
            'price': 9500,
        },
        'ie3_75kw': {
            'power': 75,
            'efficiency_class': 'IE3',
            'efficiency': 0.955,
            'speed': 1485,
            'voltage': 380,
            'protection': 'IP55',
            'price': 22000,
        },
        'ie4_7.5kw': {
            'power': 7.5,
            'efficiency_class': 'IE4',
            'efficiency': 0.945,
            'speed': 1470,
            'voltage': 380,
            'protection': 'IP55',
            'price': 5200,
        },
        'ie4_15kw': {
            'power': 15,
            'efficiency_class': 'IE4',
            'efficiency': 0.955,
            'speed': 1475,
            'voltage': 380,
            'protection': 'IP55',
            'price': 8500,
        },
    }
    
    # 变频器数据库
    VFDs = {
        'vfd_7.5kw': {
            'power': 7.5,
            'input_voltage': '380V',
            'output_voltage': '0-380V',
            'frequency_range': '0-400Hz',
            'efficiency': 0.97,
            'protection': 'IP20',
            'price': 2800,
        },
        'vfd_15kw': {
            'power': 15,
            'input_voltage': '380V',
            'output_voltage': '0-380V',
            'frequency_range': '0-400Hz',
            'efficiency': 0.97,
            'protection': 'IP20',
            'price': 4500,
        },
        'vfd_30kw': {
            'power': 30,
            'input_voltage': '380V',
            'output_voltage': '0-380V',
            'frequency_range': '0-400Hz',
            'efficiency': 0.97,
            'protection': 'IP20',
            'price': 7800,
        },
        'vfd_75kw': {
            'power': 75,
            'input_voltage': '380V',
            'output_voltage': '0-380V',
            'frequency_range': '0-400Hz',
            'efficiency': 0.97,
            'protection': 'IP20',
            'price': 16500,
        },
    }
    
    # 空压机数据库
    AIR_COMPRESSORS = {
        'screw_22kw': {
            'type': '螺杆式',
            'power': 22,
            'flow_rate': 3.5,
            'pressure': 0.8,
            'specific_power': 6.3,
            'efficiency_class': '一级能效',
            'cooling': '风冷',
            'price': 35000,
        },
        'screw_37kw': {
            'type': '螺杆式',
            'power': 37,
            'flow_rate': 6.2,
            'pressure': 0.8,
            'specific_power': 6.0,
            'efficiency_class': '一级能效',
            'cooling': '风冷',
            'price': 55000,
        },
        'screw_75kw': {
            'type': '螺杆式',
            'power': 75,
            'flow_rate': 13.0,
            'pressure': 0.8,
            'specific_power': 5.8,
            'efficiency_class': '一级能效',
            'cooling': '风冷',
            'price': 95000,
        },
        'vsd_37kw': {
            'type': '变频螺杆式',
            'power': 37,
            'flow_rate': 6.5,
            'pressure': 0.8,
            'specific_power': 5.5,
            'efficiency_class': '超一级能效',
            'cooling': '风冷',
            'price': 75000,
        },
    }
    
    # 热泵数据库
    HEAT_PUMPS = {
        'ashp_50kw': {
            'type': '空气源热泵',
            'heating_power': 50,
            'cop_at_7c': 3.5,
            'cop_at_minus_7c': 2.8,
            'voltage': 380,
            'refrigerant': 'R410A',
            'price': 45000,
        },
        'ashp_100kw': {
            'type': '空气源热泵',
            'heating_power': 100,
            'cop_at_7c': 3.5,
            'cop_at_minus_7c': 2.8,
            'voltage': 380,
            'refrigerant': 'R410A',
            'price': 78000,
        },
        'gshp_50kw': {
            'type': '地源热泵',
            'heating_power': 50,
            'cooling_power': 45,
            'heating_cop': 4.2,
            'cooling_cop': 5.0,
            'voltage': 380,
            'refrigerant': 'R410A',
            'price': 85000,
        },
        'wshp_100kw': {
            'type': '水源热泵',
            'heating_power': 100,
            'cooling_power': 90,
            'heating_cop': 4.5,
            'cooling_cop': 5.5,
            'voltage': 380,
            'refrigerant': 'R134a',
            'price': 120000,
        },
    }
    
    # 余热回收设备数据库
    WASTE_HEAT_EQUIPMENT = {
        'whb_500kw': {
            'type': '余热锅炉',
            'heat_recovery_power': 500,
            'inlet_temp': 400,
            'outlet_temp': 150,
            'steam_pressure': 1.0,
            'steam_output': 0.8,
            'efficiency': 0.65,
            'price': 400000,
        },
        'orc_200kw': {
            'type': 'ORC发电机组',
            'electrical_power': 200,
            'heat_input_power': 1000,
            'inlet_temp': 120,
            'outlet_temp': 70,
            'efficiency': 0.12,
            'price': 600000,
        },
        'hp_100kw': {
            'type': '余热驱动热泵',
            'heating_power': 100,
            'heat_source_temp': 80,
            'cop': 3.5,
            'price': 150000,
        },
    }
    
    # LED灯具数据库
    LED_LIGHTS = {
        'led_panel_40w': {
            'type': '面板灯',
            'power': 40,
            'luminous_flux': 4000,
            'efficacy': 100,
            'color_temp': 4000,
            'cri': 80,
            'lifespan': 50000,
            'price': 120,
        },
        'led_highbay_100w': {
            'type': '工矿灯',
            'power': 100,
            'luminous_flux': 12000,
            'efficacy': 120,
            'color_temp': 5000,
            'cri': 70,
            'lifespan': 50000,
            'price': 280,
        },
        'led_highbay_150w': {
            'type': '工矿灯',
            'power': 150,
            'luminous_flux': 18000,
            'efficacy': 120,
            'color_temp': 5000,
            'cri': 70,
            'lifespan': 50000,
            'price': 380,
        },
        'led_flood_200w': {
            'type': '投光灯',
            'power': 200,
            'luminous_flux': 24000,
            'efficacy': 120,
            'color_temp': 5000,
            'cri': 70,
            'lifespan': 50000,
            'price': 450,
        },
    }
    
    # 有源滤波器数据库
    ACTIVE_FILTERS = {
        'apf_50a': {
            'capacity': 50,
            'voltage': 380,
            'filter_range': '2-50次',
            'response_time': '小于10us',
            'efficiency': 0.97,
            'protection': 'IP20',
            'price': 25000,
        },
        'apf_100a': {
            'capacity': 100,
            'voltage': 380,
            'filter_range': '2-50次',
            'response_time': '小于10us',
            'efficiency': 0.97,
            'protection': 'IP20',
            'price': 42000,
        },
        'apf_150a': {
            'capacity': 150,
            'voltage': 380,
            'filter_range': '2-50次',
            'response_time': '小于10us',
            'efficiency': 0.97,
            'protection': 'IP20',
            'price': 58000,
        },
        'apf_300a': {
            'capacity': 300,
            'voltage': 380,
            'filter_range': '2-50次',
            'response_time': '小于10us',
            'efficiency': 0.97,
            'protection': 'IP20',
            'price': 95000,
        },
    }
    
    def __init__(self):
        pass
    
    def get_pv_module(self, model: str) -> Dict:
        """获取光伏组件参数"""
        return self.PV_MODULES.get(model, {})
    
    def get_inverter(self, model: str) -> Dict:
        """获取逆变器参数"""
        return self.INVERTERS.get(model, {})
    
    def get_battery_system(self, model: str) -> Dict:
        """获取储能系统参数"""
        return self.BATTERY_SYSTEMS.get(model, {})
    
    def get_wind_turbine(self, model: str) -> Dict:
        """获取风力发电机参数"""
        return self.WIND_TURBINES.get(model, {})
    
    def get_efficient_motor(self, model: str) -> Dict:
        """获取高效电机参数"""
        return self.EFFICIENT_MOTORS.get(model, {})
    
    def get_vfd(self, model: str) -> Dict:
        """获取变频器参数"""
        return self.VFDs.get(model, {})
    
    def get_air_compressor(self, model: str) -> Dict:
        """获取空压机参数"""
        return self.AIR_COMPRESSORS.get(model, {})
    
    def get_heat_pump(self, model: str) -> Dict:
        """获取热泵参数"""
        return self.HEAT_PUMPS.get(model, {})
    
    def get_waste_heat_equipment(self, model: str) -> Dict:
        """获取余热回收设备参数"""
        return self.WASTE_HEAT_EQUIPMENT.get(model, {})
    
    def get_led_light(self, model: str) -> Dict:
        """获取LED灯具参数"""
        return self.LED_LIGHTS.get(model, {})
    
    def get_active_filter(self, model: str) -> Dict:
        """获取有源滤波器参数"""
        return self.ACTIVE_FILTERS.get(model, {})
    
    def search_by_power(
        self,
        equipment_type: str,
        min_power: float = 0,
        max_power: float = float('inf')
    ) -> List[str]:
        """
        按功率搜索设备
        
        Args:
            equipment_type: 设备类型
            min_power: 最小功率
            max_power: 最大功率
        
        Returns:
            设备型号列表
        """
        databases = {
            'pv_module': self.PV_MODULES,
            'inverter': self.INVERTERS,
            'battery': self.BATTERY_SYSTEMS,
            'wind_turbine': self.WIND_TURBINES,
            'motor': self.EFFICIENT_MOTORS,
            'vfd': self.VFDs,
            'compressor': self.AIR_COMPRESSORS,
            'heat_pump': self.HEAT_PUMPS,
            'waste_heat': self.WASTE_HEAT_EQUIPMENT,
            'led': self.LED_LIGHTS,
            'apf': self.ACTIVE_FILTERS,
        }
        
        db = databases.get(equipment_type, {})
        results = []
        
        for model, params in db.items():
            power = params.get('power', 0)
            if min_power <= power <= max_power:
                results.append(model)
        
        return results
    
    def compare_equipment(
        self,
        equipment_type: str,
        models: List[str]
    ) -> Dict[str, any]:
        """
        对比多个设备
        
        Args:
            equipment_type: 设备类型
            models: 型号列表
        
        Returns:
            对比结果
        """
        databases = {
            'pv_module': self.PV_MODULES,
            'inverter': self.INVERTERS,
            'motor': self.EFFICIENT_MOTORS,
        }
        
        db = databases.get(equipment_type, {})
        comparison = []
        
        for model in models:
            if model in db:
                params = db[model]
                comparison.append({
                    'model': model,
                    'params': params,
                })
        
        return {
            'equipment_type': equipment_type,
            'comparison': comparison,
        }
    
    def get_recommendation(
        self,
        equipment_type: str,
        requirement: Dict[str, any]
    ) -> List[Dict[str, any]]:
        """
        根据需求推荐设备
        
        Args:
            equipment_type: 设备类型
            requirement: 需求参数
        
        Returns:
            推荐列表
        """
        recommendations = []
        
        if equipment_type == 'pv_module':
            target_power = requirement.get('target_power', 550)
            # 找最接近的功率
            for model, params in self.PV_MODULES.items():
                score = 100 - abs(params['power'] - target_power)
                recommendations.append({
                    'model': model,
                    'score': score,
                    'params': params,
                })
        
        elif equipment_type == 'inverter':
            target_power = requirement.get('target_power', 50)
            for model, params in self.INVERTERS.items():
                score = 100 - abs(params['power'] - target_power)
                if params['power'] >= target_power:
                    score += 20
                recommendations.append({
                    'model': model,
                    'score': score,
                    'params': params,
                })
        
        elif equipment_type == 'motor':
            target_power = requirement.get('target_power', 15)
            efficiency_class = requirement.get('efficiency_class', 'IE3')
            for model, params in self.EFFICIENT_MOTORS.items():
                if params['efficiency_class'] == efficiency_class:
                    score = 100 - abs(params['power'] - target_power)
                    recommendations.append({
                        'model': model,
                        'score': score,
                        'params': params,
                    })
        
        # 按评分排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:5]
