
"""
工业与民用配电设计手册（第四版）技能包 - 完整版
整合《钢铁企业电力设计手册》和《电力工程高压送电线路设计手册》

本技能包包含以下设计手册的内容：
1. 《工业与民用配电设计手册》第四版
2. 《钢铁企业电力设计手册》上、下册
3. 《电力工程高压送电线路设计手册》第二版

主要功能模块：
- 负荷计算模块
- 短路电流计算模块
- 电气设备选择模块
- 电缆截面选择模块
- 继电保护整定模块
- 无功功率补偿模块
- 接地设计模块
- 变压器选择模块
- 钢铁企业电力设计模块
- 高压送电线路设计模块
- Excel导出模块
"""

__version__ = "2.0.0"
__author__ = "AI Assistant"
__license__ = "MIT"

# 导入原有模块
from .power_design_skill import (
    LoadCalculation,
    ShortCircuitCalculation,
    CableSelection,
    ProtectionSetting,
    ReactivePowerCompensation,
    GroundingDesign,
    TransformerSelection,
    CircuitBreakerSelection,
    PowerDesignCalculator,
    LoadCalculationResult,
    ShortCircuitResult,
    CableSelectionResult,
    ProtectionSettingResult,
    calculate_load,
    calculate_short_circuit,
    select_cable,
    compensate_reactive_power,
    design_grounding,
)

# 导入钢铁企业和送电线路模块
from .steel_transmission_modules import (
    SteelPlantPowerDesign,
    TransmissionLineDesign,
)

# 导入Excel导出模块
from .excel_exporter import (
    ExcelExporter,
    export_to_excel,
)

__all__ = [
    # 原有模块
    'LoadCalculation',
    'ShortCircuitCalculation',
    'CableSelection',
    'ProtectionSetting',
    'ReactivePowerCompensation',
    'GroundingDesign',
    'TransformerSelection',
    'CircuitBreakerSelection',
    'PowerDesignCalculator',
    'LoadCalculationResult',
    'ShortCircuitResult',
    'CableSelectionResult',
    'ProtectionSettingResult',
    'calculate_load',
    'calculate_short_circuit',
    'select_cable',
    'compensate_reactive_power',
    'design_grounding',
    # 新增模块
    'SteelPlantPowerDesign',
    'TransmissionLineDesign',
    'ExcelExporter',
    'export_to_excel',
]
