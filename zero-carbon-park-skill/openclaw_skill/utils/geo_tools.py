"""
地理工具模块
==========
包含经纬度相关计算、太阳位置计算、气候数据查询
"""

import math
from typing import Dict, List, Tuple, Optional


class GeoTools:
    """地理工具类"""
    
    # 中国主要城市经纬度
    CHINA_CITIES = {
        '北京': (39.9042, 116.4074),
        '上海': (31.2304, 121.4737),
        '广州': (23.1291, 113.2644),
        '深圳': (22.5431, 114.0579),
        '天津': (39.3434, 117.3616),
        '重庆': (29.5630, 106.5516),
        '成都': (30.5728, 104.0668),
        '武汉': (30.5928, 114.3055),
        '西安': (34.3416, 108.9398),
        '杭州': (30.2741, 120.1551),
        '南京': (32.0603, 118.7969),
        '郑州': (34.7466, 113.6253),
        '济南': (36.6512, 117.1201),
        '青岛': (36.0671, 120.3826),
        '沈阳': (41.8057, 123.4315),
        '大连': (38.9140, 121.6147),
        '长春': (43.8171, 125.3235),
        '哈尔滨': (45.8038, 126.5350),
        '石家庄': (38.0428, 114.5149),
        '太原': (37.8706, 112.5489),
        '呼和浩特': (40.8414, 111.7519),
        '乌鲁木齐': (43.8256, 87.6168),
        '拉萨': (29.6500, 91.1000),
        '昆明': (25.0389, 102.7183),
        '贵阳': (26.6470, 106.6302),
        '南宁': (22.8170, 108.3665),
        '海口': (20.0440, 110.1999),
        '兰州': (36.0611, 103.8343),
        '银川': (38.4872, 106.2309),
        '西宁': (36.6171, 101.7782),
        '长沙': (28.2282, 112.9388),
        '南昌': (28.6820, 115.8579),
        '合肥': (31.8206, 117.2272),
        '福州': (26.0745, 119.2965),
        '厦门': (24.4798, 118.0894),
    }
    
    # 气候分区
    CLIMATE_ZONES = {
        'severe_cold': {
            'name': '严寒地区',
            'cities': ['哈尔滨', '长春', '沈阳', '呼和浩特', '乌鲁木齐'],
            'heating_degree_days': 4000,
            'cooling_degree_days': 100,
        },
        'cold': {
            'name': '寒冷地区',
            'cities': ['北京', '天津', '石家庄', '太原', '济南', '郑州', '西安', '兰州', '银川', '西宁'],
            'heating_degree_days': 2500,
            'cooling_degree_days': 200,
        },
        'hot_summer_cold_winter': {
            'name': '夏热冬冷地区',
            'cities': ['上海', '南京', '杭州', '合肥', '武汉', '长沙', '南昌', '成都', '重庆'],
            'heating_degree_days': 1500,
            'cooling_degree_days': 1200,
        },
        'hot_summer_warm_winter': {
            'name': '夏热冬暖地区',
            'cities': ['广州', '深圳', '福州', '厦门', '南宁', '海口'],
            'heating_degree_days': 300,
            'cooling_degree_days': 2000,
        },
        'mild': {
            'name': '温和地区',
            'cities': ['昆明', '贵阳', '拉萨'],
            'heating_degree_days': 800,
            'cooling_degree_days': 300,
        },
    }
    
    # 太阳辐射数据 (kWh/m²/day)
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
    
    def __init__(self):
        pass
    
    def get_coordinates(self, city_name: str) -> Optional[Tuple[float, float]]:
        """
        获取城市经纬度
        
        Args:
            city_name: 城市名称
        
        Returns:
            (纬度, 经度) 或 None
        """
        return self.CHINA_CITIES.get(city_name)
    
    def get_city_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        tolerance: float = 0.5
    ) -> Optional[str]:
        """
        根据经纬度查找城市
        
        Args:
            latitude: 纬度
            longitude: 经度
            tolerance: 容差 (度)
        
        Returns:
            城市名称或None
        """
        for city, (lat, lon) in self.CHINA_CITIES.items():
            if abs(lat - latitude) < tolerance and abs(lon - longitude) < tolerance:
                return city
        return None
    
    def get_climate_zone(self, city_name: str = None, latitude: float = None) -> Dict[str, any]:
        """
        获取气候分区
        
        Args:
            city_name: 城市名称
            latitude: 纬度 (如果未提供城市名)
        
        Returns:
            气候分区信息
        """
        if city_name:
            for zone_code, zone_info in self.CLIMATE_ZONES.items():
                if city_name in zone_info['cities']:
                    return {
                        'code': zone_code,
                        'name': zone_info['name'],
                        'heating_degree_days': zone_info['heating_degree_days'],
                        'cooling_degree_days': zone_info['cooling_degree_days'],
                    }
        
        # 根据纬度判断
        if latitude:
            if latitude >= 42:
                zone = 'severe_cold'
            elif latitude >= 35:
                zone = 'cold'
            elif latitude >= 28:
                zone = 'hot_summer_cold_winter'
            elif latitude >= 23:
                zone = 'hot_summer_warm_winter'
            else:
                zone = 'mild'
            
            zone_info = self.CLIMATE_ZONES[zone]
            return {
                'code': zone,
                'name': zone_info['name'],
                'heating_degree_days': zone_info['heating_degree_days'],
                'cooling_degree_days': zone_info['cooling_degree_days'],
            }
        
        return None
    
    def get_solar_radiation(self, city_name: str = None, latitude: float = None) -> float:
        """
        获取太阳辐射量
        
        Args:
            city_name: 城市名称
            latitude: 纬度
        
        Returns:
            日均太阳辐射量 (kWh/m²/day)
        """
        if city_name and city_name in self.SOLAR_RADIATION:
            return self.SOLAR_RADIATION[city_name]
        
        # 根据纬度估算
        if latitude:
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
        
        return 4.0  # 默认值
    
    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        计算两点间距离 (Haversine公式)
        
        Args:
            lat1, lon1: 第一点经纬度
            lat2, lon2: 第二点经纬度
        
        Returns:
            距离 (km)
        """
        R = 6371  # 地球半径 (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def calculate_azimuth(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        计算从第一点看第二点的方位角
        
        Args:
            lat1, lon1: 第一点经纬度
            lat2, lon2: 第二点经纬度
        
        Returns:
            方位角 (度，从正北顺时针)
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
        
        azimuth = math.degrees(math.atan2(x, y))
        
        # 转换为0-360度
        if azimuth < 0:
            azimuth += 360
        
        return azimuth
    
    def get_optimal_pv_tilt(self, latitude: float, optimization: str = 'annual') -> float:
        """
        获取最佳光伏倾角
        
        Args:
            latitude: 纬度
            optimization: 优化目标 (annual/winter/summer)
        
        Returns:
            最佳倾角 (度)
        """
        abs_lat = abs(latitude)
        
        if optimization == 'annual':
            # 全年最优
            if abs_lat < 25:
                return abs_lat
            elif abs_lat < 40:
                return abs_lat + 5
            else:
                return abs_lat + 10
        elif optimization == 'winter':
            # 冬季最优
            return abs_lat + 15
        elif optimization == 'summer':
            # 夏季最优
            return max(0, abs_lat - 15)
        
        return abs_lat
    
    def get_optimal_pv_azimuth(self, latitude: float) -> float:
        """
        获取最佳光伏方位角
        
        Args:
            latitude: 纬度
        
        Returns:
            最佳方位角 (度，正南为0)
        """
        # 北半球正南，南半球正北
        if latitude >= 0:
            return 0  # 正南
        else:
            return 180  # 正北
    
    def estimate_wind_resource(
        self,
        latitude: float,
        longitude: float,
        altitude: float = 0
    ) -> Dict[str, any]:
        """
        估算风资源
        
        Args:
            latitude: 纬度
            longitude: 经度
            altitude: 海拔 (m)
        
        Returns:
            风资源估算
        """
        # 简化估算 - 实际应用中应查询风资源数据库
        
        # 沿海地区风速较高
        # 简化: 根据纬度估算
        base_speed = 4.0
        
        # 纬度修正
        if latitude > 40:
            base_speed += 1.0
        elif latitude > 35:
            base_speed += 0.5
        
        # 海拔修正
        altitude_factor = 1 + altitude / 1000 * 0.1
        
        estimated_speed = base_speed * altitude_factor
        
        # 风功率密度
        air_density = 1.225 * (1 - altitude / 10000)  # 海拔越高密度越低
        power_density = 0.5 * air_density * estimated_speed ** 3
        
        # 资源等级
        if estimated_speed < 4:
            resource_class = '较差'
            suitability = '不建议'
        elif estimated_speed < 5:
            resource_class = '一般'
            suitability = '小型风电可考虑'
        elif estimated_speed < 6:
            resource_class = '良好'
            suitability = '适合分布式风电'
        else:
            resource_class = '优秀'
            suitability = '非常适合风电'
        
        return {
            'estimated_avg_wind_speed_ms': round(estimated_speed, 1),
            'power_density_w_m2': round(power_density, 1),
            'air_density_kg_m3': round(air_density, 3),
            'resource_class': resource_class,
            'suitability': suitability,
            'note': '此为粗略估算，实际项目需进行现场测风',
        }
    
    def get_nearby_cities(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 100
    ) -> List[Dict[str, any]]:
        """
        获取附近城市
        
        Args:
            latitude: 纬度
            longitude: 经度
            radius_km: 半径 (km)
        
        Returns:
            附近城市列表
        """
        nearby = []
        
        for city, (lat, lon) in self.CHINA_CITIES.items():
            distance = self.calculate_distance(latitude, longitude, lat, lon)
            if distance <= radius_km:
                nearby.append({
                    'name': city,
                    'latitude': lat,
                    'longitude': lon,
                    'distance_km': round(distance, 1),
                })
        
        # 按距离排序
        nearby.sort(key=lambda x: x['distance_km'])
        
        return nearby
    
    def get_location_info(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[str, any]:
        """
        获取位置综合信息
        
        Args:
            latitude: 纬度
            longitude: 经度
        
        Returns:
            位置综合信息
        """
        # 查找最近城市
        nearby = self.get_nearby_cities(latitude, longitude, 200)
        nearest_city = nearby[0] if nearby else None
        
        # 气候分区
        climate_zone = self.get_climate_zone(latitude=latitude)
        
        # 太阳辐射
        solar_radiation = self.get_solar_radiation(latitude=latitude)
        
        # 最佳光伏倾角
        pv_tilt = self.get_optimal_pv_tilt(latitude)
        
        # 风资源
        wind_resource = self.estimate_wind_resource(latitude, longitude)
        
        return {
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude,
            },
            'nearest_city': nearest_city,
            'climate_zone': climate_zone,
            'solar_resource': {
                'daily_radiation_kwh_m2': solar_radiation,
                'annual_radiation_kwh_m2': round(solar_radiation * 365, 0),
                'resource_level': '丰富' if solar_radiation > 4.5 else '良好' if solar_radiation > 3.8 else '一般',
            },
            'pv_recommendation': {
                'optimal_tilt_angle': round(pv_tilt, 0),
                'optimal_azimuth_angle': self.get_optimal_pv_azimuth(latitude),
                'capacity_factor_estimate': round(solar_radiation * 365 / 8760 * 100, 1),
            },
            'wind_resource': wind_resource,
            'nearby_cities': nearby[:5],
        }
