# Zero Carbon Park - 零碳园区建设技能包

## 描述

专业的零碳园区规划与节能诊断 Python 工具包，为能源工程师、节能服务公司和园区管理者提供水电气暖基础计算、碳排放核算、光伏风电设计、余热回收等全面的技术计算和方案设计支持。

## 功能

### 水电气暖基础计算
- **水系统**: 管网压力损失、水泵功率与选型、节能改造效益
- **电气系统**: 无功补偿、变压器损耗分析、电缆选型
- **暖通系统**: 采暖热负荷、空调冷负荷、节能改造

### 碳排放核算
- 范围1/2/3 排放计算（固定燃烧、移动源、外购电力/热力、上游排放）
- 减排措施评估与碳中和路径规划
- 产品碳足迹核算

### 光伏风电设计
- 基于经纬度的最佳倾角计算
- 光伏阵列设计与发电量估算
- 风光互补系统设计

### 余热余冷回收
- 余热潜力计算
- 回收系统设计
- 设备选型

### 行业数据库
- 覆盖 12+ 高耗能行业：化工、钢铁、纺织、数据中心、有色金属、石油石化、水泥等
- 行业踏勘指导、节能措施推荐、谐波信息、光伏储能建议

### 建筑节能
- 围护结构热损失计算
- 年采暖/空调负荷计算
- 围护结构优化与照明方案对比

### 谐波分析
- THD 计算与合规性检查
- 谐波影响分析
- 治理方案设计

### 零碳园区方案设计
- 综合方案生成（目标可再生能源比例规划）
- 方案报告导出

### 地理与设备工具
- 城市坐标、气候分区、太阳辐射数据查询
- 节能设备数据库（光伏组件、逆变器、电机等）

## 使用方法

```python
import sys
sys.path.insert(0, '/path/to/zero-carbon-park')

from openclaw_skill import EnergyBase, CarbonCalculator, PVWindCalculator

# 基础能源计算
energy = EnergyBase()
result = energy.calculate_power_factor_correction(
    active_power=500, current_pf=0.75, target_pf=0.95
)
print(f"需要补偿: {result['compensation_required_kvar']:.2f} kvar")

# 碳排放计算
carbon = CarbonCalculator(region='east')
fuel = {'natural_gas': 100000, 'diesel': 50}
result = carbon.calculate_stationary_combustion(fuel)

# 光伏最佳倾角
pv = PVWindCalculator()
tilt = pv.calculate_optimal_tilt(latitude=39.9)
print(f"最佳倾角: {tilt['optimal_tilt_angle']:.1f}°")
```

## 依赖

- Python >= 3.x
- 无强制外部依赖（纯 Python 实现核心计算逻辑）
