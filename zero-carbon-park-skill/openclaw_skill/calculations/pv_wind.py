"""
光伏风电计算模块
==============
包含光伏系统设计、最佳倾角计算、风电系统计算
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SolarPosition:
    """太阳位置数据"""
    altitude: float  # 太阳高度角 (度)
    azimuth: float  # 太阳方位角 (度)
    declination: float  # 太阳赤纬角 (度)
    hour_angle: float  # 时角 (度)


class PVWindCalculator:
    """光伏风电计算器"""
    
    # 中国主要城市太阳辐射数据 (kWh/m²/day)
    SOLAR_RADIATION = {
        '拉萨': 5.5,
        '西宁': 4.8,
        '银川': 4.6,
        '呼和浩特': 4.5,
        '北京': 4.2,
        '天津': 4.0,
        '石家庄': 4.1,
        '太原': 4.0,
        '济南': 4.0,
        '郑州': 3.9,
        '西安': 3.7,
        '兰州': 4.3,
        '乌鲁木齐': 4.0,
        '沈阳': 3.8,
        '长春': 3.9,
        '哈尔滨': 3.7,
        '上海': 3.6,
        '南京': 3.7,
        '杭州': 3.5,
        '合肥': 3.7,
        '福州': 3.6,
        '南昌': 3.5,
        '武汉': 3.6,
        '长沙': 3.4,
        '广州': 3.8,
        '南宁': 3.7,
        '海口': 4.5,
        '成都': 3.0,
        '贵阳': 3.2,
        '昆明': 4.4,
    }
    
    # 组件温度系数 (%/°C)
    TEMP_COEFFICIENT = {
        'mono_si': -0.35,
        'poly_si': -0.40,
        'thin_film': -0.25,
        'hjt': -0.26,
        'topcon': -0.30,
    }
    
    def __init__(self):
        pass
    
    # ==================== 太阳位置计算 ====================
    
    def calculate_solar_position(
        self,
        latitude: float,  # 纬度 (度)
        longitude: float,  # 经度 (度)
        day_of_year: int,  # 一年中的第几天 (1-365)
        hour: float,  # 小时 (0-24)
        timezone: int = 8  # 时区
    ) -> SolarPosition:
        """
        计算太阳位置
        
        Args:
            latitude: 纬度 (度)
            longitude: 经度 (度)
            day_of_year: 一年中的第几天
            hour: 小时
            timezone: 时区
        
        Returns:
            太阳位置数据
        """
        # 转换为弧度
        lat_rad = math.radians(latitude)
        
        # 太阳赤纬角 (度)
        declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
        decl_rad = math.radians(declination)
        
        # 时角 (度)
        solar_time = hour + (longitude - timezone * 15) / 15 * 1 + 0.0  # 简化
        hour_angle = 15 * (solar_time - 12)
        hour_rad = math.radians(hour_angle)
        
        # 太阳高度角
        sin_altitude = (math.sin(lat_rad) * math.sin(decl_rad) + 
                       math.cos(lat_rad) * math.cos(decl_rad) * math.cos(hour_rad))
        altitude = math.degrees(math.asin(sin_altitude))
        
        # 太阳方位角
        cos_azimuth = ((math.sin(decl_rad) - sin_altitude * math.sin(lat_rad)) / 
                      (math.cos(math.radians(altitude)) * math.cos(lat_rad)))
        # 限制范围
        cos_azimuth = max(-1, min(1, cos_azimuth))
        azimuth = math.degrees(math.acos(cos_azimuth))
        
        # 调整方位角 (下午为正值)
        if hour_angle > 0:
            azimuth = 360 - azimuth
        
        return SolarPosition(
            altitude=round(altitude, 2),
            azimuth=round(azimuth, 2),
            declination=round(declination, 2),
            hour_angle=round(hour_angle, 2)
        )
    
    # ==================== 最佳倾角计算 ====================
    
    def calculate_optimal_tilt(
        self,
        latitude: float,
        optimization: str = 'annual',  # annual/winter/summer
        consider_azimuth: bool = False,
        azimuth: float = 0  # 方位角，正南为0
    ) -> Dict[str, float]:
        """
        计算光伏最佳倾角
        
        Args:
            latitude: 纬度 (度)
            optimization: 优化目标 (annual-全年/winter-冬季/summer-夏季)
            consider_azimuth: 是否考虑方位角
            azimuth: 方位角 (度)
        
        Returns:
            最佳倾角信息
        """
        # 经验公式计算最佳倾角
        if optimization == 'annual':
            # 全年最优: 纬度 ± 5度
            if abs(latitude) < 25:
                optimal_tilt = latitude
            elif abs(latitude) < 40:
                optimal_tilt = latitude + 5
            else:
                optimal_tilt = latitude + 10
        elif optimization == 'winter':
            # 冬季最优: 纬度 + 15度
            optimal_tilt = abs(latitude) + 15
        elif optimization == 'summer':
            # 夏季最优: 纬度 - 15度
            optimal_tilt = max(0, abs(latitude) - 15)
        else:
            optimal_tilt = latitude
        
        # 考虑方位角的影响
        if consider_azimuth and azimuth != 0:
            # 非正南朝向，适当增加倾角补偿
            azimuth_deviation = abs(azimuth)
            if azimuth_deviation > 30:
                optimal_tilt += 5
        
        # 限制范围
        optimal_tilt = max(0, min(60, optimal_tilt))
        
        # 计算不同倾角的发电量差异
        tilt_comparison = []
        for tilt in [0, optimal_tilt-5, optimal_tilt, optimal_tilt+5, optimal_tilt+10, 45]:
            tilt = max(0, tilt)
            # 简化计算 - 相对发电量
            relative_output = self._estimate_relative_output(latitude, tilt)
            tilt_comparison.append({
                'tilt': tilt,
                'relative_output': round(relative_output, 3)
            })
        
        return {
            'latitude': latitude,
            'optimal_tilt_angle': round(optimal_tilt, 1),
            'optimization_target': optimization,
            'azimuth_considered': consider_azimuth,
            'tilt_comparison': tilt_comparison,
            'recommendation': f"建议采用{round(optimal_tilt, 0)}度倾角",
        }
    
    def _estimate_relative_output(self, latitude: float, tilt: float) -> float:
        """估算相对发电量"""
        # 简化模型
        lat_rad = math.radians(latitude)
        tilt_rad = math.radians(tilt)
        
        # 基于余弦定律的简化估算
        annual_factor = (math.cos(lat_rad - tilt_rad) + 
                        0.5 * math.cos(lat_rad + tilt_rad))
        
        return max(0.5, annual_factor)
    
    def calculate_detailed_tilt_analysis(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, any]:
        """
        详细倾角分析
        
        Args:
            latitude: 纬度
            longitude: 经度
        
        Returns:
            详细分析结果
        """
        # 各月最佳倾角
        monthly_optimal = []
        for month in range(1, 13):
            # 各月太阳赤纬角
            day_of_year = (month - 1) * 30 + 15
            declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
            
            # 该月最佳倾角 ≈ 纬度 - 赤纬角
            optimal = abs(latitude) - declination
            optimal = max(0, min(60, optimal))
            
            monthly_optimal.append({
                'month': month,
                'optimal_tilt': round(optimal, 1),
                'declination': round(declination, 1)
            })
        
        # 季节推荐
        seasonal_recommendations = {
            'spring': {'months': [3, 4, 5], 'tilt': round(abs(latitude) - 10, 0)},
            'summer': {'months': [6, 7, 8], 'tilt': round(max(0, abs(latitude) - 20), 0)},
            'autumn': {'months': [9, 10, 11], 'tilt': round(abs(latitude), 0)},
            'winter': {'months': [12, 1, 2], 'tilt': round(abs(latitude) + 15, 0)},
        }
        
        # 固定倾角 vs 可调倾角收益对比
        annual_fixed = self._estimate_annual_output(latitude, abs(latitude))
        
        # 简化的可调倾角收益 (每季度调整)
        seasonal_output = 0
        for season, data in seasonal_recommendations.items():
            seasonal_output += self._estimate_annual_output(latitude, data['tilt']) / 4
        
        adjustable_benefit = (seasonal_output - annual_fixed) / annual_fixed * 100
        
        return {
            'latitude': latitude,
            'longitude': longitude,
            'monthly_optimal_tilts': monthly_optimal,
            'seasonal_recommendations': seasonal_recommendations,
            'annual_fixed_tilt_output': round(annual_fixed, 3),
            'seasonal_adjustable_output': round(seasonal_output, 3),
            'adjustable_benefit_percent': round(adjustable_benefit, 1),
            'final_recommendation': {
                'fixed_tilt': round(abs(latitude) + 5, 0),
                'adjustable': adjustable_benefit > 5,
                'adjustable_schedule': '建议每季度调整一次' if adjustable_benefit > 5 else None,
            }
        }
    
    def _estimate_annual_output(self, latitude: float, tilt: float) -> float:
        """估算年发电量 (相对值)"""
        # 简化的年发电量估算
        total = 0
        for day in range(1, 366, 15):  # 每15天计算一次
            declination = 23.45 * math.sin(math.radians(360 * (284 + day) / 365))
            
            # 日平均太阳高度角
            noon_altitude = 90 - abs(latitude - declination)
            
            # 组件入射角
            incidence_angle = abs(noon_altitude - tilt)
            
            # 日发电量 (简化)
            daily_output = max(0, math.cos(math.radians(incidence_angle)))
            total += daily_output * 15
        
        return total
    
    # ==================== 光伏系统设计 ====================
    
    def design_pv_array(
        self,
        capacity_kw: float,
        module_power_wp: float = 550,
        module_efficiency: float = 0.21,
        tilt_angle: float = None,
        azimuth_angle: float = 0,
        latitude: float = 35,
        shading_factor: float = 0.05
    ) -> Dict[str, any]:
        """
        设计光伏阵列
        
        Args:
            capacity_kw: 目标装机容量 (kW)
            module_power_wp: 组件功率 (Wp)
            module_efficiency: 组件效率
            tilt_angle: 倾角，None则自动计算
            azimuth_angle: 方位角 (度)
            latitude: 纬度
            shading_factor: 遮挡损失系数
        
        Returns:
            阵列设计参数
        """
        # 自动计算最佳倾角
        if tilt_angle is None:
            tilt_angle = self.calculate_optimal_tilt(latitude)['optimal_tilt_angle']
        
        # 组件数量
        num_modules = int(capacity_kw * 1000 / module_power_wp)
        
        # 实际装机容量
        actual_capacity = num_modules * module_power_wp / 1000
        
        # 组件面积
        module_area = module_power_wp / (1000 * module_efficiency)  # m²
        total_module_area = num_modules * module_area
        
        # 阵列占地面积 (考虑间距)
        # 间距系数: 高度角的余切
        row_spacing_factor = 1.5 if latitude < 30 else (2.0 if latitude < 40 else 2.5)
        land_area = total_module_area * row_spacing_factor
        
        # 年发电量估算
        # 获取当地辐射量
        radiation = self._get_radiation_by_latitude(latitude)
        
        # 系统效率
        system_efficiency = (1 - shading_factor) * 0.95 * 0.98 * 0.98  # 遮挡、线损、逆变器、灰尘
        
        # 温度损失
        temp_loss = abs(self.TEMP_COEFFICIENT['mono_si']) * 20 / 100  # 假设平均温升20°C
        system_efficiency *= (1 - temp_loss)
        
        # 年发电量
        annual_generation = actual_capacity * radiation * 365 * system_efficiency
        
        # 组件排布
        modules_per_string = self._calculate_modules_per_string(module_power_wp)
        num_strings = math.ceil(num_modules / modules_per_string)
        
        return {
            'target_capacity_kw': capacity_kw,
            'actual_capacity_kw': round(actual_capacity, 2),
            'num_modules': num_modules,
            'module_power_wp': module_power_wp,
            'module_efficiency': module_efficiency,
            'tilt_angle': tilt_angle,
            'azimuth_angle': azimuth_angle,
            'total_module_area_m2': round(total_module_area, 0),
            'land_area_m2': round(land_area, 0),
            'modules_per_string': modules_per_string,
            'num_strings': num_strings,
            'annual_radiation_kwh_m2_day': radiation,
            'system_efficiency': round(system_efficiency * 100, 1),
            'annual_generation_kwh': round(annual_generation, 0),
            'capacity_factor': round(annual_generation / (actual_capacity * 8760) * 100, 1),
        }
    
    def _get_radiation_by_latitude(self, latitude: float) -> float:
        """根据纬度估算辐射量"""
        abs_lat = abs(latitude)
        if abs_lat < 25:
            return 4.5
        elif abs_lat < 30:
            return 4.3
        elif abs_lat < 35:
            return 4.0
        elif abs_lat < 40:
            return 3.8
        elif abs_lat < 45:
            return 3.6
        else:
            return 3.4
    
    def _calculate_modules_per_string(self, module_power: float, inverter_voltage: float = 1000) -> int:
        """计算每串组件数量"""
        # 假设组件Voc约50V (550W组件)
        module_voc = 50
        return int(inverter_voltage / module_voc * 0.9)  # 留10%裕量
    
    # ==================== 风电系统计算 ====================
    
    def calculate_wind_power(
        self,
        wind_speed: float,  # m/s
        rotor_diameter: float,  # m
        air_density: float = 1.225,  # kg/m³
        cp: float = 0.35  # 风能利用系数
    ) -> Dict[str, float]:
        """
        计算风力发电功率
        
        Args:
            wind_speed: 风速 (m/s)
            rotor_diameter: 风轮直径 (m)
            air_density: 空气密度
            cp: 风能利用系数
        
        Returns:
            功率计算结果
        """
        # 扫风面积
        area = math.pi * (rotor_diameter / 2) ** 2
        
        # 理论功率
        theoretical_power = 0.5 * air_density * area * wind_speed ** 3 / 1000  # kW
        
        # 实际功率
        actual_power = theoretical_power * cp
        
        return {
            'wind_speed_ms': wind_speed,
            'rotor_diameter_m': rotor_diameter,
            'swept_area_m2': round(area, 1),
            'theoretical_power_kw': round(theoretical_power, 2),
            'actual_power_kw': round(actual_power, 2),
            'power_coefficient': cp,
        }
    
    def design_wind_turbine(
        self,
        avg_wind_speed: float,
        target_capacity: float = None,
        turbine_type: str = 'small',
        hub_height: float = 30
    ) -> Dict[str, any]:
        """
        设计风力发电系统
        
        Args:
            avg_wind_speed: 平均风速 (m/s)
            target_capacity: 目标容量 (kW)
            turbine_type: 风机类型 (small/medium/large)
            hub_height: 轮毂高度 (m)
        
        Returns:
            风电系统设计
        """
        # 风速随高度变化 (风切变)
        # v2 = v1 * (h2/h1)^alpha, alpha ≈ 0.14
        reference_height = 10
        adjusted_wind_speed = avg_wind_speed * (hub_height / reference_height) ** 0.14
        
        # 风机参数
        turbine_specs = {
            'small': {'power': 50, 'diameter': 15, 'cut_in': 3, 'rated': 12, 'cut_out': 25},
            'medium': {'power': 500, 'diameter': 40, 'cut_in': 3, 'rated': 12, 'cut_out': 25},
            'large': {'power': 2000, 'diameter': 80, 'cut_in': 3, 'rated': 12, 'cut_out': 25},
        }
        
        spec = turbine_specs.get(turbine_type, turbine_specs['small'])
        
        # 计算年发电量
        # 简化: 使用容量系数
        if adjusted_wind_speed < spec['cut_in']:
            capacity_factor = 0
        elif adjusted_wind_speed >= spec['rated']:
            capacity_factor = 0.35
        else:
            # 简化线性插值
            capacity_factor = 0.35 * (adjusted_wind_speed - spec['cut_in']) / (spec['rated'] - spec['cut_in'])
        
        annual_hours = 8760
        annual_generation = spec['power'] * capacity_factor * annual_hours
        
        # 如果需要特定容量
        num_turbines = 1
        if target_capacity:
            num_turbines = max(1, round(target_capacity / spec['power']))
            total_capacity = num_turbines * spec['power']
            total_generation = annual_generation * num_turbines
        else:
            total_capacity = spec['power']
            total_generation = annual_generation
        
        # 占地面积 (简化: 5D x 10D 间距)
        spacing = spec['diameter'] * 5
        land_area_per_turbine = spacing * spec['diameter'] * 10
        total_land_area = land_area_per_turbine * num_turbines
        
        return {
            'turbine_type': turbine_type,
            'num_turbines': num_turbines,
            'unit_capacity_kw': spec['power'],
            'total_capacity_kw': total_capacity,
            'rotor_diameter_m': spec['diameter'],
            'hub_height_m': hub_height,
            'avg_wind_speed_ms': avg_wind_speed,
            'adjusted_wind_speed_ms': round(adjusted_wind_speed, 2),
            'cut_in_speed_ms': spec['cut_in'],
            'rated_speed_ms': spec['rated'],
            'cut_out_speed_ms': spec['cut_out'],
            'capacity_factor': round(capacity_factor * 100, 1),
            'annual_generation_kwh': round(total_generation, 0),
            'land_area_m2': round(total_land_area, 0),
        }
    
    def analyze_wind_resource(
        self,
        wind_speed_data: List[float],
        measurement_height: float = 10
    ) -> Dict[str, any]:
        """
        分析风资源
        
        Args:
            wind_speed_data: 风速数据列表 (m/s)
            measurement_height: 测量高度 (m)
        
        Returns:
            风资源分析结果
        """
        if not wind_speed_data:
            return {}
        
        # 基本统计
        avg_speed = sum(wind_speed_data) / len(wind_speed_data)
        max_speed = max(wind_speed_data)
        min_speed = min(wind_speed_data)
        
        # 风速分布 (简化Weibull分析)
        # 计算标准差
        variance = sum((x - avg_speed) ** 2 for x in wind_speed_data) / len(wind_speed_data)
        std_dev = math.sqrt(variance)
        
        # 风功率密度 (W/m²)
        air_density = 1.225
        power_density = 0.5 * air_density * avg_speed ** 3
        
        # 风资源等级
        if avg_speed < 4:
            resource_class = '差'
            suitability = '不适合'
        elif avg_speed < 5:
            resource_class = '一般'
            suitability = '小型风电可考虑'
        elif avg_speed < 6:
            resource_class = '良好'
            suitability = '适合分布式风电'
        elif avg_speed < 7:
            resource_class = '优秀'
            suitability = '非常适合'
        else:
            resource_class = '极佳'
            suitability = '极佳风资源'
        
        return {
            'avg_wind_speed_ms': round(avg_speed, 2),
            'max_wind_speed_ms': round(max_speed, 2),
            'min_wind_speed_ms': round(min_speed, 2),
            'std_deviation': round(std_dev, 2),
            'power_density_w_m2': round(power_density, 1),
            'measurement_height_m': measurement_height,
            'resource_class': resource_class,
            'suitability': suitability,
        }
    
    # ==================== 综合能源系统 ====================
    
    def design_hybrid_system(
        self,
        latitude: float,
        longitude: float,
        avg_wind_speed: float,
        electricity_demand_kwh: float,
        renewable_target: float = 0.5
    ) -> Dict[str, any]:
        """
        设计风光互补系统
        
        Args:
            latitude: 纬度
            longitude: 经度
            avg_wind_speed: 平均风速
            electricity_demand_kwh: 年用电量需求
            renewable_target: 可再生能源占比目标
        
        Returns:
            混合能源系统设计
        """
        # 目标可再生能源发电量
        target_generation = electricity_demand_kwh * renewable_target
        
        # 光伏设计
        pv_tilt = self.calculate_optimal_tilt(latitude)['optimal_tilt_angle']
        
        # 估算光伏年等效满发小时数
        pv_hours = self._estimate_pv_hours(latitude)
        
        # 风电年等效满发小时数
        wind_hours = self._estimate_wind_hours(avg_wind_speed)
        
        # 风光比例 (根据资源情况)
        if avg_wind_speed >= 5.5:
            wind_ratio = 0.3
        elif avg_wind_speed >= 4.5:
            wind_ratio = 0.2
        else:
            wind_ratio = 0.1
        
        pv_ratio = 1 - wind_ratio
        
        # 计算装机容量
        pv_generation = target_generation * pv_ratio
        wind_generation = target_generation * wind_ratio
        
        pv_capacity = pv_generation / pv_hours
        wind_capacity = wind_generation / wind_hours
        
        # 储能配置 (20%光伏装机，2小时)
        storage_capacity = pv_capacity * 0.2 * 2
        
        return {
            'location': {'latitude': latitude, 'longitude': longitude},
            'electricity_demand_kwh': electricity_demand_kwh,
            'renewable_target': renewable_target,
            'target_generation_kwh': target_generation,
            'pv_system': {
                'capacity_kw': round(pv_capacity, 2),
                'tilt_angle': pv_tilt,
                'annual_generation_kwh': round(pv_generation, 0),
                'capacity_factor': round(pv_hours / 8760 * 100, 1),
            },
            'wind_system': {
                'capacity_kw': round(wind_capacity, 2),
                'annual_generation_kwh': round(wind_generation, 0),
                'capacity_factor': round(wind_hours / 8760 * 100, 1),
            },
            'storage_system': {
                'capacity_kwh': round(storage_capacity, 2),
                'power_kw': round(pv_capacity * 0.2, 2),
                'duration_hours': 2,
            },
            'total_renewable_capacity_kw': round(pv_capacity + wind_capacity, 2),
            'total_renewable_generation_kwh': round(pv_generation + wind_generation, 0),
            'renewable_penetration_percent': round((pv_generation + wind_generation) / electricity_demand_kwh * 100, 1),
        }
    
    def _estimate_pv_hours(self, latitude: float) -> float:
        """估算光伏年等效满发小时数"""
        radiation = self._get_radiation_by_latitude(latitude)
        system_efficiency = 0.82
        return radiation * 365 * system_efficiency
    
    def _estimate_wind_hours(self, avg_wind_speed: float) -> float:
        """估算风电年等效满发小时数"""
        if avg_wind_speed < 4:
            return 1000
        elif avg_wind_speed < 5:
            return 1500
        elif avg_wind_speed < 6:
            return 2000
        elif avg_wind_speed < 7:
            return 2500
        else:
            return 3000
