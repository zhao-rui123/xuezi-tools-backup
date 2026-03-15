"""
OpenClaw 零碳园区建设技能包
===========================

一个专业的零碳园区规划与节能诊断工具包，涵盖：
- 水电气暖基础能源计算
- 工业节能与建筑节能计算
- 余热余冷回收与产品选型
- 光伏风电新能源系统设计
- 12大高耗能行业工艺参数库
- 踏勘指导与节能诊断
- 谐波分析与治理
- 碳排放核算
- 完整方案设计生成

作者: OpenClaw Team
版本: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "OpenClaw Team"

from .core.energy_base import EnergyBase
from .core.carbon_calc import CarbonCalculator
from .core.scheme_design import SchemeDesigner
from .industries.industry_db import IndustryDatabase
from .calculations.pv_wind import PVWindCalculator
from .calculations.waste_heat import WasteHeatCalculator
from .calculations.building_energy import BuildingEnergyCalculator
from .calculations.harmonic import HarmonicAnalyzer
from .utils.geo_tools import GeoTools
from .utils.equipment_db import EquipmentDatabase

__all__ = [
    'EnergyBase',
    'CarbonCalculator', 
    'SchemeDesigner',
    'IndustryDatabase',
    'PVWindCalculator',
    'WasteHeatCalculator',
    'BuildingEnergyCalculator',
    'HarmonicAnalyzer',
    'GeoTools',
    'EquipmentDatabase',
]
