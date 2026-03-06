#!/usr/bin/env python3
"""
生成2026年3月电价数据
基于图片中的31省份电价表
"""

import json

# 从图片提取的2026年3月电价数据（两部制，1-10kV）
# 格式：省份: {尖峰, 高峰, 平段, 低谷, 深谷, 峰谷价差}
MARCH_2026_PRICES = {
    # 广东各地区
    "广东-珠三角五市": {"peak": 1.4365, "high": 1.1547, "flat": 0.6906, "valley": 0.2797, "deep": None, "diff": 1.1568},
    "广东-江门": {"peak": 1.4283, "high": 1.1482, "flat": 0.6868, "valley": 0.2782, "deep": None, "diff": 1.1501},
    "广东-惠州": {"peak": 1.3807, "high": 1.1100, "flat": 0.6642, "valley": 0.2696, "deep": None, "diff": 1.1111},
    "广东-东西两翼": {"peak": 1.2548, "high": 1.0093, "flat": 0.6051, "valley": 0.2472, "deep": None, "diff": 1.0076},
    "广东-粤北": {"peak": 1.1508, "high": 0.9262, "flat": 0.5562, "valley": 0.2286, "deep": None, "diff": 0.9222},
    
    # 其他省份
    "山东": {"peak": 1.0948, "high": 0.9506, "flat": 0.6145, "valley": 0.2777, "deep": 0.1815, "diff": 0.9133},
    "上海(大工业用电)": {"peak": None, "high": 1.0956, "flat": 0.7099, "valley": 0.3884, "deep": 0.1955, "diff": 0.9001},
    "浙江(大工业用电)": {"peak": None, "high": 1.2859, "flat": 0.7793, "valley": 0.3507, "deep": None, "diff": 0.9352},
    "四川": {"peak": 1.2200, "high": 1.0326, "flat": 0.6813, "valley": 0.3299, "deep": None, "diff": 0.8901},
    "天津": {"peak": None, "high": 1.0309, "flat": 0.6934, "valley": 0.3559, "deep": None, "diff": 0.675},
    "浙江(一般工商业)": {"peak": None, "high": 1.1690, "flat": 0.7793, "valley": 0.3507, "deep": None, "diff": 0.8183},
    "湖南": {"peak": None, "high": 0.9996, "flat": 0.6546, "valley": 0.3102, "deep": None, "diff": 0.6894},
    "重庆": {"peak": None, "high": 1.0814, "flat": 0.7187, "valley": 0.3438, "deep": None, "diff": 0.7376},
    "海南(35kV以下)": {"peak": None, "high": 1.1100, "flat": 0.7376, "valley": 0.4184, "deep": None, "diff": 0.6916},
    "河北南": {"peak": 1.0492, "high": 0.9163, "flat": 0.6425, "valley": 0.3687, "deep": 0.3452, "diff": 0.704},
    "安徽": {"peak": None, "high": 0.9466, "flat": 0.5915, "valley": 0.295, "deep": None, "diff": 0.6516},
    "冀北": {"peak": 1.0273, "high": 0.8931, "flat": 0.6169, "valley": 0.3407, "deep": 0.3170, "diff": 0.7103},
    "河南": {"peak": None, "high": 1.1196, "flat": 0.7155, "valley": 0.4069, "deep": None, "diff": 0.7127},
    "上海(一般工商业)": {"peak": None, "high": 0.9729, "flat": 0.6332, "valley": 0.3500, "deep": None, "diff": 0.6229},
    "陕西(不含榆林地区)": {"peak": None, "high": 0.8441, "flat": 0.6078, "valley": 0.3715, "deep": None, "diff": 0.4726},
    "江西": {"peak": None, "high": 0.8928, "flat": 0.6467, "valley": 0.4006, "deep": 0.3596, "diff": 0.5332},
    "贵州": {"peak": None, "high": 0.8342, "flat": 0.5918, "valley": 0.3495, "deep": None, "diff": 0.4847},
    "湖北": {"peak": 0.9415, "high": 0.8198, "flat": 0.6273, "valley": 0.4231, "deep": None, "diff": 0.5184},
    "福建": {"peak": None, "high": 0.7781, "flat": 0.5653, "valley": 0.3342, "deep": None, "diff": 0.4439},
    "北京": {"peak": None, "high": 0.8738, "flat": 0.6406, "valley": 0.4074, "deep": None, "diff": 0.4664},
    "江苏": {"peak": None, "high": 0.8872, "flat": 0.6106, "valley": 0.3858, "deep": None, "diff": 0.5014},
    "内蒙古西": {"peak": None, "high": 0.6651, "flat": 0.4524, "valley": 0.2900, "deep": None, "diff": 0.3751},
    "吉林": {"peak": None, "high": 0.8407, "flat": 0.6534, "valley": 0.4661, "deep": None, "diff": 0.3746},
    "青海": {"peak": None, "high": 0.6212, "flat": 0.4422, "valley": 0.2575, "deep": None, "diff": 0.3637},
    "广西": {"peak": None, "high": 0.8307, "flat": 0.6619, "valley": 0.4931, "deep": None, "diff": 0.3376},
    "新疆": {"peak": None, "high": 0.7099, "flat": 0.5180, "valley": 0.3663, "deep": None, "diff": 0.3436},
    "山西": {"peak": None, "high": 0.7358, "flat": 0.5656, "valley": 0.4095, "deep": None, "diff": 0.3263},
    "辽宁": {"peak": None, "high": 0.5985, "flat": 0.4990, "valley": 0.3994, "deep": None, "diff": 0.1991},
    "黑龙江": {"peak": None, "high": 0.7790, "flat": 0.6257, "valley": 0.4724, "deep": None, "diff": 0.3066},
    "甘肃": {"peak": None, "high": 0.4979, "flat": 0.4573, "valley": 0.2459, "deep": None, "diff": 0.252},
    "内蒙古东": {"peak": None, "high": 0.5688, "flat": 0.4362, "valley": 0.3349, "deep": None, "diff": 0.2339},
    "宁夏": {"peak": None, "high": 0.4663, "flat": 0.4956, "valley": 0.3399, "deep": None, "diff": 0.1264},
    "云南": {"peak": None, "high": None, "flat": None, "valley": None, "deep": None, "diff": None},  # 暂未公布
}

# 时段配置（根据各省实际政策）
# 这里需要为每个省份配置具体的小时分布

def generate_march_data():
    """生成3月电价数据结构"""
    result = {}
    
    for province, prices in MARCH_2026_PRICES.items():
        if prices["high"] is None:
            continue  # 跳过未公布的省份
            
        # 构建电价数据结构
        # 注意：这里需要根据实际政策设置hours数组
        # 暂时使用通用配置，实际需要按省份调整
        
        data = {
            "deepValley": {"price": prices["deep"], "hours": [0,1,2,3,4,5] if prices["deep"] else [], "name": "深谷"},
            "valley": {"price": prices["valley"], "hours": [10,11,12,13,14,15], "name": "低谷"},
            "flat": {"price": prices["flat"], "hours": [6,7,8,9,16,17,22,23], "name": "平段"},
            "high": {"price": prices["high"], "hours": [18,19,20,21], "name": "高峰"},
            "peak": {"price": prices["peak"], "hours": [], "name": "尖峰"},
            "cycles": 2 if prices["diff"] > 0.7 else 1  # 价差大于0.7元可两充两放
        }
        
        # 如果深谷电价不存在，将深谷时段并入低谷
        if prices["deep"] is None:
            data["deepValley"]["hours"] = []
            
        result[province] = data
    
    return result

if __name__ == "__main__":
    data = generate_march_data()
    print(json.dumps(data, ensure_ascii=False, indent=2))
