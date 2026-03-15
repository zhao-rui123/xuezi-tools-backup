
"""
电力设计技能包测试文件
验证各计算模块的正确性
"""

import unittest
import math
from power_design_skill import (
    LoadCalculation,
    ShortCircuitCalculation,
    CableSelection,
    ProtectionSetting,
    ReactivePowerCompensation,
    GroundingDesign,
    TransformerSelection,
    CircuitBreakerSelection,
    PowerDesignCalculator
)

class TestLoadCalculation(unittest.TestCase):
    """测试负荷计算模块"""

    def test_demand_coefficient_method(self):
        """测试需要系数法"""
        powers = [5.5, 7.5, 11, 15]
        result = LoadCalculation.demand_coefficient_method(
            powers, "风机、水泵", 0.38
        )

        # 验证计算结果
        self.assertGreater(result.active_power, 0)
        self.assertGreater(result.reactive_power, 0)
        self.assertGreater(result.apparent_power, 0)
        self.assertGreater(result.calculation_current, 0)
        self.assertGreater(result.power_factor, 0)

        # 验证功率三角形关系
        expected_s = math.sqrt(result.active_power**2 + result.reactive_power**2)
        self.assertAlmostEqual(result.apparent_power, expected_s, places=2)

    def test_utilization_coefficient_method(self):
        """测试利用系数法"""
        powers = [10, 15, 20]
        result = LoadCalculation.utilization_coefficient_method(
            powers, 0.4, 1.2, 0.8
        )

        self.assertGreater(result.active_power, 0)
        self.assertGreater(result.apparent_power, 0)

    def test_unit_index_method(self):
        """测试单位指标法"""
        result = LoadCalculation.unit_index_method(
            area=1000, unit_index=50, power_factor=0.9
        )

        expected_p = 1000 * 50 / 1000  # 50 kW
        self.assertAlmostEqual(result.active_power, expected_p, places=2)

    def test_equipment_power_conversion(self):
        """测试设备功率换算"""
        # 测试负载持续率换算
        converted = LoadCalculation.convert_equipment_power(10, 40)
        expected = 10 * math.sqrt(40 / 25)
        self.assertAlmostEqual(converted, expected, places=2)

    def test_simultaneity_factor(self):
        """测试同时系数"""
        load1 = LoadCalculation.demand_coefficient_method([10, 10], "照明")
        load2 = LoadCalculation.demand_coefficient_method([20, 20], "风机、水泵")

        total = LoadCalculation.calculate_with_simultaneity(
            [load1, load2], 0.9, 0.95
        )

        self.assertLess(total.active_power, load1.active_power + load2.active_power)

class TestShortCircuitCalculation(unittest.TestCase):
    """测试短路电流计算模块"""

    def test_per_unit_system(self):
        """测试标幺值法"""
        result = ShortCircuitCalculation.per_unit_system(
            system_capacity=500,
            base_capacity=100,
            base_voltage=10.5,
            transformer_capacity=10,
            uk_percent=4.5
        )

        self.assertGreater(result.three_phase_current, 0)
        self.assertGreater(result.two_phase_current, 0)
        self.assertGreater(result.single_phase_current, 0)
        self.assertGreater(result.short_circuit_capacity, 0)

        # 验证两相短路电流约为三相的0.866倍
        ratio = result.two_phase_current / result.three_phase_current
        self.assertAlmostEqual(ratio, math.sqrt(3) / 2, places=2)

    def test_ohmic_method(self):
        """测试有名值法"""
        result = ShortCircuitCalculation.ohmic_method(
            system_voltage=0.4,
            transformer_power=1000,
            uk_percent=4.5,
            line_length=100
        )

        self.assertGreater(result.three_phase_current, 0)
        self.assertGreater(result.short_circuit_capacity, 0)

class TestCableSelection(unittest.TestCase):
    """测试电缆选择模块"""

    def test_select_by_current(self):
        """测试按载流量选择"""
        result = CableSelection.select_by_current(100)

        self.assertIn(result.cross_section, [16, 25, 35, 50])
        self.assertGreaterEqual(result.current_carrying_capacity, 100)

    def test_calculate_voltage_drop(self):
        """测试电压降计算"""
        voltage_drop = CableSelection.calculate_voltage_drop(
            current=100,
            length=100,
            cross_section=35,
            voltage=380,
            power_factor=0.8
        )

        self.assertGreater(voltage_drop, 0)
        self.assertLess(voltage_drop, 10)  # 电压降应小于10%

    def test_thermal_stability_check(self):
        """测试热稳定校验"""
        # 应该通过的情况
        result1 = CableSelection.thermal_stability_check(10, 0.5, 50)
        self.assertTrue(result1)

        # 应该不通过的情况
        result2 = CableSelection.thermal_stability_check(50, 1, 10)
        self.assertFalse(result2)

    def test_select_cable(self):
        """测试综合选择"""
        result = CableSelection.select_cable(
            calculation_current=150,
            length=200,
            max_voltage_drop=5.0,
            short_circuit_current=15,
            protection_time=0.5
        )

        self.assertGreater(result.cross_section, 0)
        self.assertLessEqual(result.voltage_drop, 5.0)

class TestProtectionSetting(unittest.TestCase):
    """测试保护整定模块"""

    def test_instantaneous_overcurrent(self):
        """测试速断保护"""
        setting = ProtectionSetting.instantaneous_overcurrent(10000, 1.3)
        expected = 10000 * 1.3
        self.assertEqual(setting, expected)

    def test_time_overcurrent(self):
        """测试过流保护"""
        setting = ProtectionSetting.time_overcurrent(500, 1.5, 0.95, 1.2)
        expected = (1.2 * 1.5 / 0.95) * 500
        self.assertEqual(setting, expected)

    def test_time_grading(self):
        """测试时间级差"""
        time = ProtectionSetting.time_grading(0.3, 0.3)
        self.assertEqual(time, 0.6)

    def test_sensitivity_check(self):
        """测试灵敏度校验"""
        sensitivity = ProtectionSetting.sensitivity_check(2000, 500)
        self.assertEqual(sensitivity, 4.0)

        # 灵敏度应大于1.5
        self.assertGreater(sensitivity, 1.5)

    def test_motor_protection(self):
        """测试电动机保护"""
        result = ProtectionSetting.motor_protection(50, 7, 5)

        self.assertGreater(result.instantaneous_current, 0)
        self.assertGreater(result.time_delay_current, 0)
        self.assertEqual(result.time_delay, 0.3)

class TestReactivePowerCompensation(unittest.TestCase):
    """测试无功功率补偿模块"""

    def test_compensation_capacity(self):
        """测试补偿容量计算"""
        compensation = ReactivePowerCompensation.compensation_capacity(
            500, 0.7, 0.95
        )

        tan_phi1 = math.sqrt(1 - 0.7**2) / 0.7
        tan_phi2 = math.sqrt(1 - 0.95**2) / 0.95
        expected = 500 * (tan_phi1 - tan_phi2)

        self.assertAlmostEqual(compensation, expected, places=2)
        self.assertGreater(compensation, 0)

    def test_capacitor_output(self):
        """测试电容器实际输出"""
        output = ReactivePowerCompensation.capacitor_output(100, 0.38, 0.4)
        expected = 100 * (0.38 / 0.4)**2
        self.assertAlmostEqual(output, expected, places=2)

    def test_transformer_compensation(self):
        """测试变压器补偿估算"""
        compensation = ReactivePowerCompensation.transformer_compensation(
            1000, 0.7, 0.3
        )
        expected = 1000 * 0.7 * 0.3
        self.assertEqual(compensation, expected)

class TestGroundingDesign(unittest.TestCase):
    """测试接地设计模块"""

    def test_horizontal_grounding_resistance(self):
        """测试水平接地极"""
        resistance = GroundingDesign.horizontal_grounding_resistance(
            length=100, diameter=0.01, burial_depth=0.8, soil_resistivity=40
        )

        self.assertGreater(resistance, 0)

    def test_vertical_grounding_resistance(self):
        """测试垂直接地极"""
        resistance = GroundingDesign.vertical_grounding_resistance(
            length=2.5, diameter=0.05, soil_resistivity=40
        )

        self.assertGreater(resistance, 0)

    def test_grounding_grid_resistance(self):
        """测试接地网"""
        resistance = GroundingDesign.grounding_grid_resistance(
            area=2000, soil_resistivity=40, total_length=500
        )

        self.assertGreater(resistance, 0)

    def test_seasonal_correction(self):
        """测试季节修正"""
        corrected = GroundingDesign.seasonal_correction(100, 'dry')
        self.assertGreater(corrected, 100)

        corrected = GroundingDesign.seasonal_correction(100, 'wet')
        self.assertLess(corrected, 100)

class TestTransformerSelection(unittest.TestCase):
    """测试变压器选择模块"""

    def test_select_by_load(self):
        """测试按负荷选择"""
        capacity = TransformerSelection.select_by_load(650, 0.7, 1.2)

        # 验证选择了标准容量
        standard_capacities = [100, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500]
        self.assertIn(capacity, standard_capacities)

        # 验证容量足够
        self.assertGreaterEqual(capacity, 650 * 1.2 / 0.7)

    def test_economic_load_rate(self):
        """测试经济负载率"""
        rate = TransformerSelection.economic_load_rate(1.5, 10)
        expected = math.sqrt(1.5 / 10)
        self.assertAlmostEqual(rate, expected, places=2)

    def test_annual_energy_loss(self):
        """测试年电能损耗"""
        loss = TransformerSelection.annual_energy_loss(1.5, 10, 0.7)
        expected = (1.5 + 0.7**2 * 10) * 8760
        self.assertAlmostEqual(loss, expected, places=2)

    def test_voltage_regulation(self):
        """测试电压调整率"""
        regulation = TransformerSelection.voltage_regulation(4.5, 0.7, 0.8)
        self.assertGreater(regulation, 0)

class TestCircuitBreakerSelection(unittest.TestCase):
    """测试断路器选择模块"""

    def test_select_rated_current(self):
        """测试选择额定电流"""
        current = CircuitBreakerSelection.select_rated_current(150, 1.25)

        standard_currents = [6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 
                            125, 160, 200, 250, 315, 400, 500, 630, 800, 1000]
        self.assertIn(current, standard_currents)
        self.assertGreaterEqual(current, 150 * 1.25)

    def test_select_breaking_capacity(self):
        """测试选择分断能力"""
        capacity = CircuitBreakerSelection.select_breaking_capacity(20, 1.2)

        standard_capacities = [6, 10, 15, 20, 25, 35, 50, 65, 85, 100, 150]
        self.assertIn(capacity, standard_capacities)
        self.assertGreaterEqual(capacity, 20 * 1.2)

    def test_motor_circuit_breaker(self):
        """测试电动机保护断路器"""
        result = CircuitBreakerSelection.motor_circuit_breaker(50, 350, 5)

        self.assertIn(result['curve'], ['C', 'D'])
        self.assertGreater(result['rated_current'], 0)
        self.assertGreater(result['instantaneous'], 350)

class TestPowerDesignCalculator(unittest.TestCase):
    """测试综合计算器"""

    def test_calculate_distribution_system(self):
        """测试全套计算"""
        calculator = PowerDesignCalculator()

        equipment_data = [
            {"power": 7.5, "type": "冷加工机床", "count": 5},
            {"power": 5.5, "type": "风机、水泵", "count": 3},
        ]

        results = calculator.calculate_distribution_system(
            equipment_data, 0.38, 500
        )

        self.assertIn('loads', results)
        self.assertIn('total_load', results)
        self.assertIn('short_circuit', results)
        self.assertIn('transformer_check', results)
        self.assertIn('cables', results)
        self.assertIn('protections', results)

    def test_generate_calculation_report(self):
        """测试生成报告"""
        calculator = PowerDesignCalculator()

        equipment_data = [
            {"power": 7.5, "type": "冷加工机床", "count": 3},
        ]

        results = calculator.calculate_distribution_system(
            equipment_data, 0.38, 200
        )

        report = calculator.generate_calculation_report(results)

        self.assertIn('电力系统设计计算报告', report)
        self.assertIn('负荷计算结果', report)
        self.assertIn('短路电流计算结果', report)

if __name__ == '__main__':
    unittest.main(verbosity=2)
