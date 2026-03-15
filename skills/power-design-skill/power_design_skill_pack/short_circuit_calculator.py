#!/usr/bin/env python3
"""
短路电流计算模块
基于《工业与民用配电设计手册》第四版
包含常见错误检查和正确计算流程
"""

import math
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ShortCircuitResult:
    """短路计算结果"""
    system_impedance: float      # 系统阻抗标幺值
    transformer_impedance: float # 变压器阻抗标幺值
    total_impedance: float       # 总阻抗标幺值
    short_circuit_current: float # 短路电流有名值 (kA)
    base_current: float          # 基准电流 (kA)


class ShortCircuitCalculator:
    """
    短路电流计算器
    
    使用标幺值法计算短路电流
    包含常见错误检查
    """
    
    def __init__(self, base_capacity: float = 100):
        """
        初始化计算器
        
        Args:
            base_capacity: 基准容量 (MVA)，默认100MVA
        """
        self.base_capacity = base_capacity
    
    def calculate_system_impedance(self, system_short_circuit_capacity: float) -> float:
        """
        计算系统阻抗标幺值
        
        公式: Xs = Sj / Ssc
        
        注意：必须从高压侧系统短路容量直接计算
        不能从低压侧短路电流反推
        
        Args:
            system_short_circuit_capacity: 系统短路容量 (MVA)
            
        Returns:
            系统阻抗标幺值
        """
        return self.base_capacity / system_short_circuit_capacity
    
    def calculate_transformer_impedance(
        self, 
        uk_percent: float, 
        transformer_capacity: float
    ) -> float:
        """
        计算变压器阻抗标幺值
        
        公式: Xt = (Uk%/100) × (Sj/Sn)
        
        Args:
            uk_percent: 阻抗电压百分比
            transformer_capacity: 变压器容量 (MVA)
            
        Returns:
            变压器阻抗标幺值
        """
        return (uk_percent / 100) * (self.base_capacity / transformer_capacity)
    
    def calculate_short_circuit_current(
        self,
        system_short_circuit_capacity: float,
        transformer_capacity: float,
        uk_percent: float,
        voltage_level: float,
        num_transformers: int = 1,
        operating_mode: str = "max"
    ) -> ShortCircuitResult:
        """
        计算短路电流
        
        关键要点：
        1. 系统阻抗从高压侧短路容量直接计算
        2. 最大运行方式要考虑变压器并联
        
        Args:
            system_short_circuit_capacity: 系统短路容量 (MVA)
            transformer_capacity: 单台变压器容量 (MVA)
            uk_percent: 阻抗电压百分比
            voltage_level: 电压等级 (kV)
            num_transformers: 变压器台数
            operating_mode: 运行方式 ("max"最大/"min"最小)
            
        Returns:
            短路计算结果
        """
        # 步骤1：计算系统阻抗
        Xs = self.calculate_system_impedance(system_short_circuit_capacity)
        
        # 步骤2：计算变压器阻抗（单台）
        Xt_single = self.calculate_transformer_impedance(uk_percent, transformer_capacity)
        
        # 步骤3：考虑运行方式（关键！）
        if operating_mode == "max" and num_transformers > 1:
            # 最大运行方式：并联运行，阻抗除以台数
            Xt = Xt_single / num_transformers
        else:
            # 最小运行方式：单台运行
            Xt = Xt_single
        
        # 步骤4：计算总阻抗
        Xtotal = Xs + Xt
        
        # 步骤5：计算基准电流
        base_current = self.base_capacity / (math.sqrt(3) * voltage_level)
        
        # 步骤6：计算短路电流
        short_circuit_current = base_current / Xtotal
        
        return ShortCircuitResult(
            system_impedance=Xs,
            transformer_impedance=Xt,
            total_impedance=Xtotal,
            short_circuit_current=short_circuit_current,
            base_current=base_current
        )


class ProtectionCalculator:
    """
    保护整定计算器
    """
    
    @staticmethod
    def calculate_overcurrent_protection(
        transformer_capacity: float,
        voltage_level: float,
        ct_ratio: float,
        reliability_coefficient: float = 1.2,
        return_coefficient: float = 0.85,
        connection_coefficient: float = 1.0
    ) -> Dict:
        """
        计算过电流保护整定值
        
        公式: Iop = Kk × Kjx × Ie / (Kf × nTA)
        
        关键要点：
        1. 用单台变压器容量计算额定电流
        2. 不要漏了接线系数Kjx
        
        Args:
            transformer_capacity: 单台变压器容量 (MVA)
            voltage_level: 电压等级 (kV)
            ct_ratio: CT变比
            reliability_coefficient: 可靠系数 Kk
            return_coefficient: 返回系数 Kf
            connection_coefficient: 接线系数 Kjx
            
        Returns:
            整定结果
        """
        # 计算额定电流（单台变压器）
        rated_current = (transformer_capacity * 1000) / (math.sqrt(3) * voltage_level)
        
        # 计算动作电流（一次侧）
        primary_current = (reliability_coefficient * connection_coefficient * rated_current) / return_coefficient
        
        # 计算二次侧整定值
        secondary_current = primary_current / ct_ratio
        
        return {
            "rated_current_A": round(rated_current, 1),
            "primary_setting_A": round(primary_current, 1),
            "secondary_setting_A": round(secondary_current, 2),
            "formula": "Iop = Kk × Kjx × Ie / (Kf × nTA)"
        }


# 测试代码
if __name__ == "__main__":
    print("=== 短路电流计算示例（110kV变电站）===")
    print()
    
    calculator = ShortCircuitCalculator()
    
    # 计算10kV母线短路电流
    print("1. 10kV母线短路电流（最大运行方式，两台并联）")
    result = calculator.calculate_short_circuit_current(
        system_short_circuit_capacity=2000,  # 110kV系统短路容量
        transformer_capacity=50,              # 单台50MVA
        uk_percent=10.5,
        voltage_level=10.5,                   # 10kV侧
        num_transformers=2,
        operating_mode="max"
    )
    
    print(f"   系统阻抗: {result.system_impedance:.4f}")
    print(f"   变压器阻抗: {result.transformer_impedance:.4f}")
    print(f"   总阻抗: {result.total_impedance:.4f}")
    print(f"   基准电流: {result.base_current:.2f} kA")
    print(f"   短路电流: {result.short_circuit_current:.2f} kA")
    print()
    
    # 计算过电流保护整定
    print("2. 主变35kV侧过电流保护整定")
    protection = ProtectionCalculator.calculate_overcurrent_protection(
        transformer_capacity=50,   # 单台50MVA
        voltage_level=35,          # 35kV侧
        ct_ratio=120               # 600/5
    )
    
    print(f"   额定电流: {protection['rated_current_A']} A")
    print(f"   一次侧动作电流: {protection['primary_setting_A']} A")
    print(f"   二次侧整定值: {protection['secondary_setting_A']} A")
