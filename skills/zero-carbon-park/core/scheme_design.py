"""
方案设计生成模块
==============
零碳园区整体方案设计与生成
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class SchemeConfig:
    """方案配置类"""
    # 园区基本信息
    name: str = ""
    location: Tuple[float, float] = (0, 0)  # (纬度, 经度)
    area: float = 0  # m²
    building_area: float = 0  # m²
    
    # 能源需求
    annual_electricity: float = 0  # kWh
    annual_heat: float = 0  # GJ
    annual_cooling: float = 0  # GJ
    annual_water: float = 0  # m³
    annual_gas: float = 0  # m³
    
    # 行业类型
    industry_type: str = ""
    
    # 现有设施
    existing_transformer: float = 0  # kVA
    existing_boiler: float = 0  # kW
    existing_chiller: float = 0  # kW


@dataclass
class SchemeResult:
    """方案结果类"""
    config: SchemeConfig = field(default_factory=SchemeConfig)
    
    # 光伏方案
    pv_capacity: float = 0  # kW
    pv_annual_generation: float = 0  # kWh
    pv_area: float = 0  # m²
    pv_investment: float = 0  # 元
    
    # 风电方案
    wind_capacity: float = 0  # kW
    wind_annual_generation: float = 0  # kWh
    wind_investment: float = 0  # 元
    
    # 储能方案
    storage_capacity: float = 0  # kWh
    storage_power: float = 0  # kW
    storage_investment: float = 0  # 元
    
    # 余热回收
    waste_heat_recovery: float = 0  # kW
    waste_heat_investment: float = 0  # 元
    
    # 节能改造
    energy_saving_potential: float = 0  # kWh/年
    energy_saving_investment: float = 0  # 元
    
    # 汇总
    total_investment: float = 0  # 元
    annual_saving: float = 0  # 元
    payback_period: float = 0  # 年
    carbon_reduction: float = 0  # tCO2/年


class SchemeDesigner:
    """零碳园区方案设计师"""
    
    # 投资单价 (元/单位)
    UNIT_COST = {
        'pv_rooftop': 3500,  # 元/kW
        'pv_ground': 4000,
        'pv_bipv': 5000,
        'wind_small': 6000,  # 小型风电 元/kW
        'wind_medium': 5500,
        'storage_lithium': 1200,  # 元/kWh
        'storage_flow': 2000,
        'waste_heat_boiler': 800,  # 元/kW
        'waste_heat_orc': 3000,
        'heat_pump': 2500,  # 元/kW
        'led_lighting': 150,  # 元/m²
        'inverter_ac': 300,  # 元/kW
        'smart_control': 50,  # 元/m²
    }
    
    # 电价
    ELECTRICITY_PRICE = {
        'industrial': 0.8,  # 元/kWh
        'commercial': 1.0,
        'residential': 0.55,
    }
    
    def __init__(self, config: SchemeConfig = None):
        self.config = config or SchemeConfig()
        self.result = SchemeResult(config=self.config)
    
    def set_config(self, config: SchemeConfig):
        """设置配置"""
        self.config = config
        self.result = SchemeResult(config=config)
    
    # ==================== 光伏方案设计 ====================
    
    def design_pv_system(
        self,
        available_area: float = None,  # m²
        install_type: str = 'rooftop',  # rooftop/ground/bipv
        module_efficiency: float = 0.21,
        system_loss: float = 0.15
    ) -> Dict[str, any]:
        """
        设计光伏系统
        
        Args:
            available_area: 可用面积，None则自动估算
            install_type: 安装类型
            module_efficiency: 组件效率
            system_loss: 系统损失率
        """
        # 估算可用面积
        if available_area is None:
            if self.config.building_area > 0:
                # 屋顶可用面积约60%
                available_area = self.config.building_area * 0.6
            else:
                available_area = self.config.area * 0.3
        
        # 组件功率密度 (W/m²)
        power_density = 1000 * module_efficiency * 0.85  # 考虑间距
        
        # 装机容量
        pv_capacity = available_area * power_density / 1000  # kW
        
        # 年发电量计算
        # 获取当地峰值日照时数
        latitude = self.config.location[0]
        peak_sun_hours = self._estimate_peak_sun_hours(latitude)
        
        annual_generation = (pv_capacity * peak_sun_hours * 365 * 
                           (1 - system_loss))
        
        # 投资
        unit_cost = self.UNIT_COST.get(f'pv_{install_type}', 3500)
        investment = pv_capacity * unit_cost
        
        # 自发自用率估算
        self_consumption_rate = min(0.8, self.config.annual_electricity / 
                                   (annual_generation * 1.2))
        
        self.result.pv_capacity = round(pv_capacity, 2)
        self.result.pv_annual_generation = round(annual_generation, 0)
        self.result.pv_area = round(available_area, 0)
        self.result.pv_investment = round(investment, 0)
        
        return {
            'pv_capacity_kw': round(pv_capacity, 2),
            'pv_area_m2': round(available_area, 0),
            'annual_generation_kwh': round(annual_generation, 0),
            'peak_sun_hours': peak_sun_hours,
            'system_efficiency': round((1 - system_loss) * 100, 1),
            'investment_yuan': round(investment, 0),
            'unit_cost_yuan_per_kw': unit_cost,
            'self_consumption_rate': round(self_consumption_rate * 100, 1),
            'annual_saving_yuan': round(annual_generation * self_consumption_rate * 
                                       self.ELECTRICITY_PRICE['industrial'], 0),
        }
    
    def _estimate_peak_sun_hours(self, latitude: float) -> float:
        """根据纬度估算峰值日照时数"""
        # 简化估算
        if abs(latitude) < 20:
            return 5.5
        elif abs(latitude) < 30:
            return 5.0
        elif abs(latitude) < 40:
            return 4.5
        else:
            return 4.0
    
    # ==================== 风电方案设计 ====================
    
    def design_wind_system(
        self,
        avg_wind_speed: float = None,  # m/s
        turbine_type: str = 'small',  # small/medium
        hub_height: float = 30  # m
    ) -> Dict[str, any]:
        """
        设计风电系统
        """
        # 根据地区估算平均风速
        if avg_wind_speed is None:
            avg_wind_speed = self._estimate_wind_speed()
        
        # 简化计算 - 风速与功率关系
        # P = 0.5 * ρ * A * v³ * Cp
        # 假设: 空气密度1.225, Cp=0.35
        
        if avg_wind_speed < 4:
            # 风速太低，不适合风电
            return {'suitable': False, 'reason': '平均风速过低'}
        
        # 估算装机容量 (简化)
        # 假设园区可用风电场地
        wind_area = self.config.area * 0.1  # 10%面积
        
        if turbine_type == 'small':
            unit_capacity = 50  # kW/台
            spacing = 100  # m
        else:
            unit_capacity = 500
            spacing = 200
        
        # 可安装台数
        num_turbines = int(wind_area / (spacing ** 2))
        wind_capacity = num_turbines * unit_capacity
        
        # 年发电量 (简化: 2000等效满发小时)
        capacity_factor = min(0.35, (avg_wind_speed / 10) ** 3 * 0.3)
        annual_hours = 8760 * capacity_factor
        annual_generation = wind_capacity * annual_hours
        
        # 投资
        unit_cost = self.UNIT_COST.get(f'wind_{turbine_type}', 6000)
        investment = wind_capacity * unit_cost
        
        self.result.wind_capacity = round(wind_capacity, 2)
        self.result.wind_annual_generation = round(annual_generation, 0)
        self.result.wind_investment = round(investment, 0)
        
        return {
            'suitable': True,
            'wind_capacity_kw': round(wind_capacity, 2),
            'num_turbines': num_turbines,
            'avg_wind_speed_ms': avg_wind_speed,
            'capacity_factor': round(capacity_factor * 100, 1),
            'annual_generation_kwh': round(annual_generation, 0),
            'investment_yuan': round(investment, 0),
            'annual_saving_yuan': round(annual_generation * 
                                       self.ELECTRICITY_PRICE['industrial'], 0),
        }
    
    def _estimate_wind_speed(self) -> float:
        """估算当地平均风速"""
        # 简化 - 根据地区估算
        # 实际应用中应该查询风资源数据库
        latitude = self.config.location[0]
        longitude = self.config.location[1]
        
        # 北方和沿海地区风速较高
        if latitude > 35:
            return 5.5
        elif latitude > 25:
            return 4.5
        else:
            return 4.0
    
    # ==================== 储能方案设计 ====================
    
    def design_storage_system(
        self,
        storage_type: str = 'lithium',
        backup_hours: float = 2,
        peak_shaving: bool = True
    ) -> Dict[str, any]:
        """
        设计储能系统
        
        Args:
            storage_type: 储能类型 lithium/flow/lead_acid
            backup_hours: 备电时长
            peak_shaving: 是否用于削峰填谷
        """
        # 储能容量设计
        # 基于光伏装机和用电负荷
        
        pv_capacity = self.result.pv_capacity
        daily_electricity = self.config.annual_electricity / 365
        
        # 储能功率 (kW)
        # 建议为光伏装机的30-50%
        storage_power = pv_capacity * 0.4 if pv_capacity > 0 else daily_electricity / 24 * 0.3
        
        # 储能容量 (kWh)
        storage_capacity = storage_power * backup_hours
        
        # 投资
        unit_cost = self.UNIT_COST.get(f'storage_{storage_type}', 1200)
        investment = storage_capacity * unit_cost
        
        # 收益估算
        benefits = {}
        if peak_shaving:
            # 削峰填谷收益
            peak_price = 1.2  # 峰时电价
            valley_price = 0.4  # 谷时电价
            daily_cycles = 1
            annual_arbitrage = (storage_capacity * daily_cycles * 
                              (peak_price - valley_price) * 300)  # 300天
            benefits['peak_shaving'] = round(annual_arbitrage, 0)
        
        self.result.storage_capacity = round(storage_capacity, 2)
        self.result.storage_power = round(storage_power, 2)
        self.result.storage_investment = round(investment, 0)
        
        return {
            'storage_power_kw': round(storage_power, 2),
            'storage_capacity_kwh': round(storage_capacity, 2),
            'backup_hours': backup_hours,
            'storage_type': storage_type,
            'investment_yuan': round(investment, 0),
            'unit_cost_yuan_per_kwh': unit_cost,
            'annual_benefits_yuan': benefits,
            'total_annual_benefit_yuan': sum(benefits.values()),
        }
    
    # ==================== 余热回收方案 ====================
    
    def design_waste_heat_recovery(
        self,
        heat_source_temp: float,  # °C
        heat_sink_temp: float = 60,  # °C
        recovery_efficiency: float = 0.6
    ) -> Dict[str, any]:
        """
        设计余热回收系统
        """
        # 估算可回收余热量
        # 基于行业类型和用能情况
        industry = self.config.industry_type
        
        # 各行业余热占比估算
        waste_heat_ratio = {
            'chemical': 0.25,
            'steel': 0.35,
            'cement': 0.30,
            'nonferrous_metal': 0.28,
            'paper': 0.20,
            'textile': 0.15,
            'food_processing': 0.18,
            'pharmaceutical': 0.15,
            'petroleum': 0.30,
            'data_center': 0.40,  # 数据中心余热
        }
        
        ratio = waste_heat_ratio.get(industry, 0.2)
        
        # 估算余热资源量
        if self.config.annual_electricity > 0:
            # 基于用电量估算
            total_heat_input = self.config.annual_electricity * 0.5  # 假设50%转化为热
            waste_heat_potential = total_heat_input * ratio / 8760  # kW
        else:
            waste_heat_potential = 0
        
        # 可回收热量
        recoverable_heat = waste_heat_potential * recovery_efficiency
        
        # 投资估算
        if heat_source_temp > 300:
            # 高温余热 - 余热锅炉
            unit_cost = self.UNIT_COST['waste_heat_boiler']
        else:
            # 中低温余热 - ORC或热泵
            unit_cost = self.UNIT_COST['waste_heat_orc']
        
        investment = recoverable_heat * unit_cost
        
        # 年节能效益
        annual_saving_kwh = recoverable_heat * 4000  # 4000运行小时
        annual_saving_yuan = annual_saving_kwh * 0.3  # 按供热成本
        
        self.result.waste_heat_recovery = round(recoverable_heat, 2)
        self.result.waste_heat_investment = round(investment, 0)
        
        return {
            'waste_heat_potential_kw': round(waste_heat_potential, 2),
            'recoverable_heat_kw': round(recoverable_heat, 2),
            'heat_source_temp_c': heat_source_temp,
            'recovery_efficiency': round(recovery_efficiency * 100, 1),
            'investment_yuan': round(investment, 0),
            'annual_saving_kwh': round(annual_saving_kwh, 0),
            'annual_saving_yuan': round(annual_saving_yuan, 0),
        }
    
    # ==================== 节能改造方案 ====================
    
    def design_energy_efficiency(
        self,
        measures: List[str] = None
    ) -> Dict[str, any]:
        """
        设计节能改造方案
        
        Args:
            measures: 节能措施列表
        """
        if measures is None:
            measures = ['lighting', 'hvac', 'motor', 'compressed_air', 'smart_control']
        
        total_saving = 0
        total_investment = 0
        measure_details = []
        
        annual_electricity = self.config.annual_electricity
        building_area = self.config.building_area or self.config.area * 0.3
        
        for measure in measures:
            if measure == 'lighting':
                # LED照明改造
                saving_rate = 0.5  # 节电50%
                lighting_load = annual_electricity * 0.1  # 照明占10%
                saving = lighting_load * saving_rate
                investment = building_area * self.UNIT_COST['led_lighting']
                
            elif measure == 'hvac':
                # 暖通系统优化
                saving_rate = 0.2
                hvac_load = annual_electricity * 0.25
                saving = hvac_load * saving_rate
                investment = building_area * 100  # 系统优化投资
                
            elif measure == 'motor':
                # 电机系统节能
                saving_rate = 0.15
                motor_load = annual_electricity * 0.35
                saving = motor_load * saving_rate
                investment = motor_load * self.UNIT_COST['inverter_ac']
                
            elif measure == 'compressed_air':
                # 压缩空气系统
                saving_rate = 0.2
                air_load = annual_electricity * 0.15
                saving = air_load * saving_rate
                investment = air_load * 200
                
            elif measure == 'smart_control':
                # 智能控制系统
                saving_rate = 0.1
                saving = annual_electricity * saving_rate
                investment = building_area * self.UNIT_COST['smart_control']
                
            else:
                continue
            
            total_saving += saving
            total_investment += investment
            
            measure_details.append({
                'measure': measure,
                'saving_kwh': round(saving, 0),
                'saving_rate': round(saving_rate * 100, 1),
                'investment_yuan': round(investment, 0),
            })
        
        self.result.energy_saving_potential = round(total_saving, 0)
        self.result.energy_saving_investment = round(total_investment, 0)
        
        return {
            'total_saving_kwh': round(total_saving, 0),
            'total_saving_rate': round(total_saving / annual_electricity * 100, 1),
            'total_investment_yuan': round(total_investment, 0),
            'annual_saving_yuan': round(total_saving * self.ELECTRICITY_PRICE['industrial'], 0),
            'measures': measure_details,
        }
    
    # ==================== 综合方案生成 ====================
    
    def generate_comprehensive_scheme(
        self,
        target_renewable_ratio: float = 0.5,
        budget_limit: float = None
    ) -> Dict[str, any]:
        """
        生成综合零碳园区方案
        
        Args:
            target_renewable_ratio: 目标可再生能源占比
            budget_limit: 预算上限
        """
        # 执行各子系统设计
        pv_result = self.design_pv_system()
        wind_result = self.design_wind_system()
        storage_result = self.design_storage_system()
        
        # 余热回收 (如果有工艺用热)
        if self.config.industry_type in ['chemical', 'steel', 'cement', 'petroleum']:
            waste_heat_result = self.design_waste_heat_recovery(heat_source_temp=200)
        else:
            waste_heat_result = {'recoverable_heat_kw': 0, 'investment_yuan': 0}
        
        # 节能改造
        efficiency_result = self.design_energy_efficiency()
        
        # 汇总投资
        total_investment = (
            pv_result.get('investment_yuan', 0) +
            wind_result.get('investment_yuan', 0) +
            storage_result.get('investment_yuan', 0) +
            waste_heat_result.get('investment_yuan', 0) +
            efficiency_result.get('total_investment_yuan', 0)
        )
        
        # 汇总年收益
        total_annual_saving = (
            pv_result.get('annual_saving_yuan', 0) +
            wind_result.get('annual_saving_yuan', 0) +
            sum(storage_result.get('annual_benefits_yuan', {}).values()) +
            waste_heat_result.get('annual_saving_yuan', 0) +
            efficiency_result.get('annual_saving_yuan', 0)
        )
        
        # 投资回收期
        payback = total_investment / total_annual_saving if total_annual_saving > 0 else float('inf')
        
        # 碳减排量
        carbon_reduction = (
            (pv_result.get('annual_generation_kwh', 0) +
             wind_result.get('annual_generation_kwh', 0)) * 0.0005703 +
            waste_heat_result.get('annual_saving_kwh', 0) * 0.0005703 +
            efficiency_result.get('total_saving_kwh', 0) * 0.0005703
        )
        
        # 可再生能源占比
        total_generation = (pv_result.get('annual_generation_kwh', 0) +
                          wind_result.get('annual_generation_kwh', 0))
        renewable_ratio = (total_generation / self.config.annual_electricity 
                         if self.config.annual_electricity > 0 else 0)
        
        self.result.total_investment = round(total_investment, 0)
        self.result.annual_saving = round(total_annual_saving, 0)
        self.result.payback_period = round(payback, 1)
        self.result.carbon_reduction = round(carbon_reduction, 2)
        
        return {
            'scheme_name': f"{self.config.name}零碳园区方案",
            'location': self.config.location,
            'industry_type': self.config.industry_type,
            
            'pv_system': pv_result,
            'wind_system': wind_result,
            'storage_system': storage_result,
            'waste_heat_system': waste_heat_result,
            'energy_efficiency': efficiency_result,
            
            'summary': {
                'total_investment_yuan': round(total_investment, 0),
                'total_investment_million_yuan': round(total_investment / 10000, 2),
                'annual_saving_yuan': round(total_annual_saving, 0),
                'payback_period_years': round(payback, 1),
                'carbon_reduction_tco2_per_year': round(carbon_reduction, 2),
                'renewable_energy_ratio_percent': round(renewable_ratio * 100, 1),
            },
            
            'implementation_phases': self._generate_phases(),
        }
    
    def _generate_phases(self) -> List[Dict]:
        """生成实施阶段建议"""
        return [
            {
                'phase': 1,
                'name': '基础节能改造',
                'duration': '6-12个月',
                'measures': ['LED照明', '智能控制', '压缩空气优化'],
                'priority': '高',
            },
            {
                'phase': 2,
                'name': '光伏系统建设',
                'duration': '3-6个月',
                'measures': ['屋顶光伏', '车棚光伏'],
                'priority': '高',
            },
            {
                'phase': 3,
                'name': '储能系统部署',
                'duration': '2-4个月',
                'measures': ['锂电池储能'],
                'priority': '中',
            },
            {
                'phase': 4,
                'name': '余热回收',
                'duration': '6-12个月',
                'measures': ['余热锅炉', 'ORC发电'],
                'priority': '中',
            },
            {
                'phase': 5,
                'name': '风电补充',
                'duration': '12-18个月',
                'measures': ['分布式风电'],
                'priority': '低',
            },
        ]
    
    def export_scheme_report(self) -> str:
        """导出方案报告 (Markdown格式)"""
        scheme = self.generate_comprehensive_scheme()
        
        report = f"""# {scheme['scheme_name']}

## 一、项目概况

- **项目地点**: 纬度{self.config.location[0]:.2f}°, 经度{self.config.location[1]:.2f}°
- **行业类型**: {self.config.industry_type}
- **园区面积**: {self.config.area:,.0f} m²
- **建筑面积**: {self.config.building_area:,.0f} m²

## 二、能源现状

- **年用电量**: {self.config.annual_electricity:,.0f} kWh
- **年用热量**: {self.config.annual_heat:,.0f} GJ
- **年用冷量**: {self.config.annual_cooling:,.0f} GJ

## 三、零碳方案设计

### 3.1 光伏发电系统

- **装机容量**: {scheme['pv_system']['pv_capacity_kw']:.2f} kW
- **占用面积**: {scheme['pv_system']['pv_area_m2']:,.0f} m²
- **年发电量**: {scheme['pv_system']['annual_generation_kwh']:,.0f} kWh
- **投资额**: {scheme['pv_system']['investment_yuan']:,.0f} 元

### 3.2 风力发电系统

- **装机容量**: {scheme['wind_system'].get('wind_capacity_kw', 0):.2f} kW
- **年发电量**: {scheme['wind_system'].get('annual_generation_kwh', 0):,.0f} kWh
- **投资额**: {scheme['wind_system'].get('investment_yuan', 0):,.0f} 元

### 3.3 储能系统

- **储能功率**: {scheme['storage_system']['storage_power_kw']:.2f} kW
- **储能容量**: {scheme['storage_system']['storage_capacity_kwh']:.2f} kWh
- **投资额**: {scheme['storage_system']['investment_yuan']:,.0f} 元

### 3.4 余热回收

- **回收功率**: {scheme['waste_heat_system'].get('recoverable_heat_kw', 0):.2f} kW
- **投资额**: {scheme['waste_heat_system'].get('investment_yuan', 0):,.0f} 元

### 3.5 节能改造

- **年节电量**: {scheme['energy_efficiency']['total_saving_kwh']:,.0f} kWh
- **节能率**: {scheme['energy_efficiency']['total_saving_rate']:.1f}%
- **投资额**: {scheme['energy_efficiency']['total_investment_yuan']:,.0f} 元

## 四、投资与收益

- **总投资**: {scheme['summary']['total_investment_yuan']:,.0f} 元 ({scheme['summary']['total_investment_million_yuan']:.2f} 万元)
- **年节约费用**: {scheme['summary']['annual_saving_yuan']:,.0f} 元
- **投资回收期**: {scheme['summary']['payback_period_years']:.1f} 年
- **年碳减排**: {scheme['summary']['carbon_reduction_tco2_per_year']:.2f} tCO₂
- **可再生能源占比**: {scheme['summary']['renewable_energy_ratio_percent']:.1f}%

## 五、实施建议

"""
        for phase in scheme['implementation_phases']:
            report += f"""
### 阶段{phase['phase']}: {phase['name']}

- **实施周期**: {phase['duration']}
- **主要措施**: {', '.join(phase['measures'])}
- **优先级**: {phase['priority']}
"""
        
        return report
