
"""
OpenClaw集成模块 - 完整版
整合所有设计手册的计算功能

使用方法：
    from openclaw_integration import PowerDesignSkill

    skill = PowerDesignSkill()
    result = skill.execute("calculate_load", {
        "powers": [5.5, 7.5, 11],
        "equipment_type": "风机、水泵"
    })
"""

from typing import Dict, Any, List
import json
import os

# 导入所有模块
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
)

class PowerDesignSkill:
    """
    电力设计技能类 - 完整版
    提供OpenClaw接口的电力设计计算功能
    整合三本设计手册的内容
    """

    def __init__(self):
        self.calculator = PowerDesignCalculator()
        self.steel_design = SteelPlantPowerDesign()
        self.transmission_design = TransmissionLineDesign()
        self.excel_exporter = ExcelExporter()
        self.name = "power_design_complete"
        self.version = "2.0.0"
        self.description = "整合三本设计手册的完整电力设计计算技能"

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力列表"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "functions": [
                # 基础功能
                {
                    "name": "calculate_load",
                    "description": "负荷计算",
                    "parameters": {
                        "powers": {"type": "list", "description": "设备功率列表(kW)"},
                        "equipment_type": {"type": "string", "description": "设备类型"},
                        "voltage": {"type": "float", "description": "额定电压(kV)", "default": 0.38}
                    }
                },
                {
                    "name": "calculate_short_circuit",
                    "description": "短路电流计算",
                    "parameters": {
                        "system_voltage": {"type": "float", "description": "系统电压(kV)", "default": 0.4},
                        "transformer_power": {"type": "float", "description": "变压器容量(kVA)", "default": 1000}
                    }
                },
                {
                    "name": "select_cable",
                    "description": "电缆截面选择",
                    "parameters": {
                        "current": {"type": "float", "description": "计算电流(A)"},
                        "length": {"type": "float", "description": "线路长度(m)"},
                        "voltage": {"type": "float", "description": "电压(V)", "default": 380},
                        "max_voltage_drop": {"type": "float", "description": "最大允许电压降(%)", "default": 5.0}
                    }
                },
                {
                    "name": "compensate_reactive_power",
                    "description": "无功功率补偿计算",
                    "parameters": {
                        "active_power": {"type": "float", "description": "有功功率(kW)"},
                        "cos_phi1": {"type": "float", "description": "补偿前功率因数"},
                        "cos_phi2": {"type": "float", "description": "补偿后功率因数", "default": 0.95}
                    }
                },
                {
                    "name": "design_grounding",
                    "description": "接地设计",
                    "parameters": {
                        "area": {"type": "float", "description": "接地网面积(m²)"},
                        "soil_type": {"type": "string", "description": "土壤类型", "default": "粘土"}
                    }
                },
                {
                    "name": "select_transformer",
                    "description": "变压器选择",
                    "parameters": {
                        "apparent_power": {"type": "float", "description": "计算负荷(kVA)"},
                        "load_factor": {"type": "float", "description": "负载率", "default": 0.7}
                    }
                },
                {
                    "name": "protection_setting",
                    "description": "保护整定计算",
                    "parameters": {
                        "motor_current": {"type": "float", "description": "电动机额定电流(A)"},
                        "starting_current": {"type": "float", "description": "启动电流(A)"}
                    }
                },
                {
                    "name": "full_system_design",
                    "description": "全套配电系统设计",
                    "parameters": {
                        "equipment_data": {"type": "list", "description": "设备数据列表"},
                        "transformer_capacity": {"type": "float", "description": "变压器容量(kVA)"}
                    }
                },
                # 钢铁企业功能
                {
                    "name": "steel_plant_load",
                    "description": "钢铁企业负荷计算",
                    "parameters": {
                        "production_capacity": {"type": "float", "description": "年产量(t)"},
                        "product_type": {"type": "string", "description": "产品类型"},
                        "operating_hours": {"type": "float", "description": "年运行小时数", "default": 7000}
                    }
                },
                {
                    "name": "arc_furnace_load",
                    "description": "电弧炉负荷计算",
                    "parameters": {
                        "furnace_capacity": {"type": "float", "description": "炉子容量(t)"},
                        "transformer_power": {"type": "float", "description": "变压器容量(MVA)"}
                    }
                },
                {
                    "name": "harmonic_calculation",
                    "description": "谐波计算",
                    "parameters": {
                        "fundamental_current": {"type": "float", "description": "基波电流(A)"}
                    }
                },
                {
                    "name": "rolling_mill_impact",
                    "description": "轧钢机冲击负荷计算",
                    "parameters": {
                        "motor_power": {"type": "float", "description": "电动机总功率(kW)"},
                        "load_factor": {"type": "float", "description": "负载率", "default": 0.6}
                    }
                },
                # 送电线路功能
                {
                    "name": "transmission_line_params",
                    "description": "送电线路电气参数计算",
                    "parameters": {
                        "conductor_type": {"type": "string", "description": "导线型号"},
                        "line_length": {"type": "float", "description": "线路长度(km)"},
                        "voltage": {"type": "float", "description": "额定电压(kV)"}
                    }
                },
                {
                    "name": "sag_calculation",
                    "description": "导线弧垂计算",
                    "parameters": {
                        "span_length": {"type": "float", "description": "档距(m)"},
                        "conductor_type": {"type": "string", "description": "导线型号"}
                    }
                },
                {
                    "name": "conductor_selection",
                    "description": "导线截面选择",
                    "parameters": {
                        "transmission_power": {"type": "float", "description": "输送功率(MW)"},
                        "voltage": {"type": "float", "description": "额定电压(kV)"},
                        "line_length": {"type": "float", "description": "线路长度(km)"}
                    }
                },
                {
                    "name": "tower_load",
                    "description": "杆塔荷载计算",
                    "parameters": {
                        "span_length": {"type": "float", "description": "档距(m)"},
                        "conductor_type": {"type": "string", "description": "导线型号"}
                    }
                },
                {
                    "name": "insulation_coordination",
                    "description": "绝缘配合设计",
                    "parameters": {
                        "voltage": {"type": "float", "description": "额定电压(kV)"},
                        "altitude": {"type": "float", "description": "海拔高度(m)", "default": 0}
                    }
                },
                {
                    "name": "tower_grounding",
                    "description": "杆塔接地设计",
                    "parameters": {
                        "soil_resistivity": {"type": "float", "description": "土壤电阻率(Ω·m)"},
                        "tower_type": {"type": "string", "description": "杆塔类型", "default": "concrete_pole"}
                    }
                },
                # Excel导出功能
                {
                    "name": "export_to_excel",
                    "description": "导出计算结果到Excel",
                    "parameters": {
                        "calculator_results": {"type": "dict", "description": "计算器结果"},
                        "output_dir": {"type": "string", "description": "输出目录", "default": None},
                        "filename": {"type": "string", "description": "文件名", "default": None}
                    }
                },
            ]
        }

    def execute(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定函数"""
        try:
            # 基础功能
            if function_name == "calculate_load":
                return self._calculate_load(parameters)
            elif function_name == "calculate_short_circuit":
                return self._calculate_short_circuit(parameters)
            elif function_name == "select_cable":
                return self._select_cable(parameters)
            elif function_name == "compensate_reactive_power":
                return self._compensate_reactive_power(parameters)
            elif function_name == "design_grounding":
                return self._design_grounding(parameters)
            elif function_name == "select_transformer":
                return self._select_transformer(parameters)
            elif function_name == "protection_setting":
                return self._protection_setting(parameters)
            elif function_name == "full_system_design":
                return self._full_system_design(parameters)
            # 钢铁企业功能
            elif function_name == "steel_plant_load":
                return self._steel_plant_load(parameters)
            elif function_name == "arc_furnace_load":
                return self._arc_furnace_load(parameters)
            elif function_name == "harmonic_calculation":
                return self._harmonic_calculation(parameters)
            elif function_name == "rolling_mill_impact":
                return self._rolling_mill_impact(parameters)
            # 送电线路功能
            elif function_name == "transmission_line_params":
                return self._transmission_line_params(parameters)
            elif function_name == "sag_calculation":
                return self._sag_calculation(parameters)
            elif function_name == "conductor_selection":
                return self._conductor_selection(parameters)
            elif function_name == "tower_load":
                return self._tower_load(parameters)
            elif function_name == "insulation_coordination":
                return self._insulation_coordination(parameters)
            elif function_name == "tower_grounding":
                return self._tower_grounding(parameters)
            # Excel导出功能
            elif function_name == "export_to_excel":
                return self._export_to_excel(parameters)
            else:
                return {"error": f"未知函数: {function_name}"}
        except Exception as e:
            return {"error": str(e)}

    # ========== 基础功能实现 ==========

    def _calculate_load(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """负荷计算"""
        powers = params.get("powers", [])
        equipment_type = params.get("equipment_type", "风机、水泵")
        voltage = params.get("voltage", 0.38)

        result = calculate_load(powers, equipment_type, voltage)

        return {
            "success": True,
            "data": {
                "active_power_kw": round(result.active_power, 2),
                "reactive_power_kvar": round(result.reactive_power, 2),
                "apparent_power_kva": round(result.apparent_power, 2),
                "calculation_current_a": round(result.calculation_current, 2),
                "power_factor": round(result.power_factor, 2)
            }
        }

    def _calculate_short_circuit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """短路电流计算"""
        system_voltage = params.get("system_voltage", 0.4)
        transformer_power = params.get("transformer_power", 1000)

        result = calculate_short_circuit(system_voltage, transformer_power)

        return {
            "success": True,
            "data": {
                "three_phase_current_ka": round(result.three_phase_current, 2),
                "two_phase_current_ka": round(result.two_phase_current, 2),
                "single_phase_current_ka": round(result.single_phase_current, 2),
                "short_circuit_capacity_mva": round(result.short_circuit_capacity, 2)
            }
        }

    def _select_cable(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """电缆选择"""
        current = params.get("current", 100)
        length = params.get("length", 50)
        voltage = params.get("voltage", 380)
        max_voltage_drop = params.get("max_voltage_drop", 5.0)

        result = select_cable(current, length, voltage, max_voltage_drop)

        return {
            "success": True,
            "data": {
                "cross_section_mm2": result.cross_section,
                "current_carrying_capacity_a": round(result.current_carrying_capacity, 1),
                "voltage_drop_percent": round(result.voltage_drop, 2),
                "thermal_stability": "通过" if result.thermal_stability else "不通过"
            }
        }

    def _compensate_reactive_power(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """无功补偿计算"""
        active_power = params.get("active_power", 500)
        cos_phi1 = params.get("cos_phi1", 0.7)
        cos_phi2 = params.get("cos_phi2", 0.95)

        compensation = compensate_reactive_power(active_power, cos_phi1, cos_phi2)

        return {
            "success": True,
            "data": {
                "compensation_capacity_kvar": round(compensation, 2),
                "active_power_kw": active_power,
                "cos_phi_before": cos_phi1,
                "cos_phi_after": cos_phi2
            }
        }

    def _design_grounding(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """接地设计"""
        area = params.get("area", 1000)
        soil_type = params.get("soil_type", "粘土")

        resistance = design_grounding(area, soil_type)

        soil_resistivity = GroundingDesign.SOIL_RESISTIVITY.get(soil_type, 40)

        return {
            "success": True,
            "data": {
                "grounding_resistance_ohm": round(resistance, 2),
                "soil_type": soil_type,
                "soil_resistivity_ohm_m": soil_resistivity,
                "meets_requirement": resistance <= 4
            }
        }

    def _select_transformer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """变压器选择"""
        apparent_power = params.get("apparent_power", 500)
        load_factor = params.get("load_factor", 0.7)

        capacity = TransformerSelection.select_by_load(apparent_power, load_factor)
        actual_load_rate = apparent_power / capacity * 100

        return {
            "success": True,
            "data": {
                "calculated_load_kva": apparent_power,
                "selected_capacity_kva": capacity,
                "load_rate_percent": round(actual_load_rate, 1),
                "is_suitable": actual_load_rate <= 85
            }
        }

    def _protection_setting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """保护整定"""
        motor_current = params.get("motor_current", 50)
        starting_current = params.get("starting_current", 350)

        result = ProtectionSetting.motor_protection(motor_current, starting_current / motor_current)

        return {
            "success": True,
            "data": {
                "motor_rated_current_a": motor_current,
                "starting_current_a": starting_current,
                "instantaneous_setting_a": round(result.instantaneous_current, 1),
                "time_delay_setting_a": round(result.time_delay_current, 1),
                "time_delay_s": result.time_delay
            }
        }

    def _full_system_design(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """全套系统设计"""
        equipment_data = params.get("equipment_data", [])
        transformer_capacity = params.get("transformer_capacity", 500)

        results = self.calculator.calculate_distribution_system(
            equipment_data, 0.38, transformer_capacity
        )

        report = self.calculator.generate_calculation_report(results)

        return {
            "success": True,
            "data": {
                "total_active_power_kw": round(results['total_load'].active_power, 2) if results['total_load'] else 0,
                "total_apparent_power_kva": round(results['total_load'].apparent_power, 2) if results['total_load'] else 0,
                "short_circuit_current_ka": round(results['short_circuit'].three_phase_current, 2) if results['short_circuit'] else 0,
                "transformer_load_rate": round(results['transformer_check']['load_rate'], 1) if results['transformer_check'] else 0
            },
            "full_report": report
        }

    # ========== 钢铁企业功能实现 ==========

    def _steel_plant_load(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """钢铁企业负荷计算"""
        production_capacity = params.get("production_capacity", 1000000)
        product_type = params.get("product_type", "转炉钢")
        operating_hours = params.get("operating_hours", 7000)

        result = self.steel_design.calculate_by_unit_production(
            production_capacity, product_type, operating_hours
        )

        return {
            "success": True,
            "data": {
                "active_power_kw": round(result.active_power, 2),
                "reactive_power_kvar": round(result.reactive_power, 2),
                "apparent_power_kva": round(result.apparent_power, 2),
                "calculation_current_a": round(result.calculation_current, 2),
                "power_factor": round(result.power_factor, 2),
                "product_type": product_type,
                "production_capacity_t": production_capacity
            }
        }

    def _arc_furnace_load(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """电弧炉负荷计算"""
        furnace_capacity = params.get("furnace_capacity", 100)
        transformer_power = params.get("transformer_power", 50)

        result = self.steel_design.arc_furnace_load(furnace_capacity, transformer_power)

        return {
            "success": True,
            "data": result
        }

    def _harmonic_calculation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """谐波计算"""
        fundamental_current = params.get("fundamental_current", 1000)

        result = self.steel_design.harmonic_calculation(fundamental_current)

        return {
            "success": True,
            "data": result
        }

    def _rolling_mill_impact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """轧钢机冲击负荷计算"""
        motor_power = params.get("motor_power", 5000)
        load_factor = params.get("load_factor", 0.6)

        result = self.steel_design.rolling_mill_impact_load(motor_power, load_factor)

        return {
            "success": True,
            "data": result
        }

    # ========== 送电线路功能实现 ==========

    def _transmission_line_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """送电线路电气参数计算"""
        conductor_type = params.get("conductor_type", "LGJ-240")
        line_length = params.get("line_length", 50)
        voltage = params.get("voltage", 220)

        result = self.transmission_design.electrical_parameters(
            conductor_type, line_length, voltage
        )

        return {
            "success": True,
            "data": result
        }

    def _sag_calculation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """导线弧垂计算"""
        span_length = params.get("span_length", 300)
        conductor_type = params.get("conductor_type", "LGJ-240")

        result = self.transmission_design.sag_calculation(span_length, conductor_type)

        return {
            "success": True,
            "data": result
        }

    def _conductor_selection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """导线截面选择"""
        transmission_power = params.get("transmission_power", 100)
        voltage = params.get("voltage", 220)
        line_length = params.get("line_length", 50)

        result = self.transmission_design.conductor_selection(
            transmission_power, voltage, line_length
        )

        return {
            "success": True,
            "data": result
        }

    def _tower_load(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """杆塔荷载计算"""
        span_length = params.get("span_length", 300)
        conductor_type = params.get("conductor_type", "LGJ-240")

        result = self.transmission_design.tower_load_calculation(span_length, conductor_type)

        return {
            "success": True,
            "data": result
        }

    def _insulation_coordination(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """绝缘配合设计"""
        voltage = params.get("voltage", 220)
        altitude = params.get("altitude", 0)

        result = self.transmission_design.insulation_coordination(voltage, altitude)

        return {
            "success": True,
            "data": result
        }

    def _tower_grounding(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """杆塔接地设计"""
        soil_resistivity = params.get("soil_resistivity", 100)
        tower_type = params.get("tower_type", "concrete_pole")

        result = self.transmission_design.grounding_design_tower(soil_resistivity, tower_type)

        return {
            "success": True,
            "data": result
        }

    # ========== Excel导出功能实现 ==========

    def _export_to_excel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """导出到Excel"""
        calculator_results = params.get("calculator_results", {})
        output_dir = params.get("output_dir", None)
        filename = params.get("filename", None)

        try:
            exporter = ExcelExporter(output_dir)
            filepath = exporter.export_full_report(calculator_results, filename)

            return {
                "success": True,
                "data": {
                    "filepath": filepath,
                    "message": f"计算结果已成功导出到: {filepath}"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 创建技能实例的便捷函数
def create_skill() -> PowerDesignSkill:
    """创建电力设计技能实例"""
    return PowerDesignSkill()


# 命令行接口
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python openclaw_integration.py <function_name> [parameters_json]")
        print("\n可用函数:")
        skill = PowerDesignSkill()
        capabilities = skill.get_capabilities()
        for func in capabilities["functions"]:
            print(f"  - {func['name']}: {func['description']}")
        sys.exit(1)

    function_name = sys.argv[1]
    parameters = {}

    if len(sys.argv) > 2:
        parameters = json.loads(sys.argv[2])

    skill = PowerDesignSkill()
    result = skill.execute(function_name, parameters)

    print(json.dumps(result, ensure_ascii=False, indent=2))
