#!/usr/bin/env python3
"""
直流电缆选型计算器
专用于储能/光伏直流系统
"""

# 载流量表 (1~3kV XLPE铜芯, 空气中)
CABLE_CAPACITY = {
    70: 244,
    95: 296,
    120: 340,
    150: 388,
    185: 436,
    240: 643,
    300: 736,
}

# 温度校正系数 (90℃电缆)
TEMP_COEFF = {
    30: 1.00,
    35: 0.96,
    40: 0.92,
    45: 0.94,
    50: 0.89,
}

# 并线校正系数 (s=d, 空气中)
PARALLEL_COEFF = {
    1: 1.00,
    2: 0.90,
    3: 0.85,
    4: 0.82,
    5: 0.80,
    6: 0.79,
}

# 敷设方式校正
INSTALL_COEFF = {
    'air': 1.00,
    'cable_tray_good': 0.90,
    'cable_tray_poor': 0.85,
}

def calculate_cable(
    power_kw: float,
    voltage_min: float,
    cable_size: int,
    ambient_temp: int,
    install_type: str,
    parallel_count: int
) -> dict:
    """
    计算直流电缆选型
    
    Args:
        power_kw: 功率(kW)
        voltage_min: 最低电压(V)
        cable_size: 电缆截面(mm²)
        ambient_temp: 环境温度(℃)
        install_type: 敷设方式(air/cable_tray_good/cable_tray_poor)
        parallel_count: 并线根数
    
    Returns:
        计算结果字典
    """
    # 计算负载电流
    load_current = power_kw * 1000 / voltage_min
    
    # 获取基准载流量
    base_current = CABLE_CAPACITY.get(cable_size, 0)
    if base_current == 0:
        return {'error': f'不支持的电缆规格: {cable_size}mm²'}
    
    # 获取校正系数
    temp_coeff = TEMP_COEFF.get(ambient_temp, 0.94)  # 默认45℃
    install_coeff = INSTALL_COEFF.get(install_type, 0.90)
    parallel_coeff = PARALLEL_COEFF.get(parallel_count, 0.79)
    
    # 计算单根校正载流量
    single_current = base_current * temp_coeff * install_coeff
    
    # 计算总载流量
    total_current = single_current * parallel_count * parallel_coeff
    
    # 计算裕量
    margin = (total_current - load_current) / load_current * 100
    
    return {
        'load_current': round(load_current, 1),
        'base_current': base_current,
        'temp_coeff': temp_coeff,
        'install_coeff': install_coeff,
        'parallel_coeff': parallel_coeff,
        'single_current': round(single_current, 1),
        'total_current': round(total_current, 1),
        'margin_percent': round(margin, 1),
        'is_ok': total_current >= load_current,
        'recommendation': '满足要求' if total_current >= load_current else '不满足，需增加根数或增大截面'
    }

def print_result(result: dict):
    """打印计算结果"""
    if 'error' in result:
        print(f"❌ {result['error']}")
        return
    
    print("=" * 50)
    print("📊 直流电缆选型计算结果")
    print("=" * 50)
    print(f"负载电流: {result['load_current']} A")
    print(f"")
    print("校正系数:")
    print(f"  基准载流量: {result['base_current']} A")
    print(f"  温度校正: {result['temp_coeff']}")
    print(f"  敷设校正: {result['install_coeff']}")
    print(f"  并线校正: {result['parallel_coeff']}")
    print(f"")
    print(f"单根校正载流: {result['single_current']} A")
    print(f"总载流量: {result['total_current']} A")
    print(f"")
    print(f"裕量: {result['margin_percent']}%")
    print(f"结论: {'✅ ' + result['recommendation'] if result['is_ok'] else '❌ ' + result['recommendation']}")
    print("=" * 50)

if __name__ == '__main__':
    # 示例: 1562kW, 1164.8V, 240mm², 45℃, 电缆沟通风好, 3根
    result = calculate_cable(
        power_kw=1562,
        voltage_min=1164.8,
        cable_size=240,
        ambient_temp=45,
        install_type='cable_tray_good',
        parallel_count=3
    )
    print_result(result)
