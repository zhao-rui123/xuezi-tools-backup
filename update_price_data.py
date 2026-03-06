#!/usr/bin/env python3
"""
更新电价数据 - 添加2026年3月数据
保留2月数据，新增3月数据（只改价格）
"""

import re

# 2026年3月电价数据（从图片提取）
MARCH_PRICES = {
    "山东": {"deep": 0.1815, "valley": 0.2777, "flat": 0.6145, "high": 0.9506, "peak": 1.0948},
    "河南": {"deep": 0.2804, "valley": 0.4069, "flat": 0.7155, "high": 1.1196, "peak": 1.2323},
    "浙江": {"deep": 0.1829, "valley": 0.3507, "flat": 0.7793, "high": 1.2859, "peak": 1.4145},
    "广东": {"deep": 0.2205, "valley": 0.2797, "flat": 0.6906, "high": 1.1547, "peak": 1.4365},
    "江苏": {"deep": 0.2408, "valley": 0.3858, "flat": 0.6106, "high": 0.8872, "peak": 0.9759},
    "河北": {"deep": 0.2602, "valley": 0.3687, "flat": 0.6425, "high": 0.9163, "peak": 1.0492},
    "四川": {"deep": 0.3299, "valley": 0.3299, "flat": 0.6813, "high": 1.0326, "peak": 1.2200},
    "上海": {"deep": 0.1955, "valley": 0.3884, "flat": 0.7099, "high": 1.0956, "peak": 1.2052},
    "天津": {"deep": 0.25, "valley": 0.3559, "flat": 0.6934, "high": 1.0309, "peak": 1.1340},
    "湖南": {"deep": 0.25, "valley": 0.3102, "flat": 0.6546, "high": 0.9996, "peak": 1.0996},
    "重庆": {"deep": 0.25, "valley": 0.3438, "flat": 0.7187, "high": 1.0814, "peak": 1.1895},
    "安徽": {"deep": 0.25, "valley": 0.295, "flat": 0.5915, "high": 0.9466, "peak": 1.0413},
    "湖北": {"deep": 0.25, "valley": 0.4231, "flat": 0.6273, "high": 0.8198, "peak": 0.9415},
    "福建": {"deep": 0.25, "valley": 0.3342, "flat": 0.5653, "high": 0.7781, "peak": 0.8559},
    "北京": {"deep": 0.25, "valley": 0.4074, "flat": 0.6406, "high": 0.8738, "peak": 0.9612},
    "江西": {"deep": 0.3596, "valley": 0.4006, "flat": 0.6467, "high": 0.8928, "peak": 0.9821},
    "山西": {"deep": 0.25, "valley": 0.4095, "flat": 0.5656, "high": 0.7358, "peak": 0.8094},
    "陕西": {"deep": 0.25, "valley": 0.3715, "flat": 0.6078, "high": 0.8441, "peak": 0.9285},
    "贵州": {"deep": 0.25, "valley": 0.3495, "flat": 0.5918, "high": 0.8342, "peak": 0.9176},
    "广西": {"deep": 0.25, "valley": 0.4931, "flat": 0.6619, "high": 0.8307, "peak": 0.9138},
    "新疆": {"deep": 0.25, "valley": 0.3663, "flat": 0.5180, "high": 0.7099, "peak": 0.7809},
    "海南": {"deep": 0.25, "valley": 0.4184, "flat": 0.7376, "high": 1.1100, "peak": 1.2210},
    "辽宁": {"deep": 0.25, "valley": 0.3994, "flat": 0.4990, "high": 0.5985, "peak": 0.6584},
    "吉林": {"deep": 0.25, "valley": 0.4661, "flat": 0.6534, "high": 0.8407, "peak": 0.9248},
    "黑龙江": {"deep": 0.25, "valley": 0.4724, "flat": 0.6257, "high": 0.7790, "peak": 0.8569},
    "内蒙古西": {"deep": 0.25, "valley": 0.2900, "flat": 0.4524, "high": 0.6651, "peak": 0.7316},
    "内蒙古东": {"deep": 0.25, "valley": 0.3349, "flat": 0.4362, "high": 0.5688, "peak": 0.6257},
    "青海": {"deep": 0.25, "valley": 0.2575, "flat": 0.4422, "high": 0.6212, "peak": 0.6833},
    "甘肃": {"deep": 0.25, "valley": 0.2459, "flat": 0.4573, "high": 0.4979, "peak": 0.5477},
    "宁夏": {"deep": 0.25, "valley": 0.3399, "flat": 0.4956, "high": 0.4663, "peak": 0.5129},
    "云南": {"deep": 0.1985, "valley": 0.3970, "flat": 0.5955, "high": 0.8933, "peak": 0.9826},
    "西藏": {"deep": 0.1856, "valley": 0.3712, "flat": 0.5568, "high": 0.8352, "peak": 0.9187},
}

def add_march_data(content):
    """在2月数据后添加3月数据"""
    
    # 找到每个省份的2月数据块，在其后添加3月数据
    for province, prices in MARCH_PRICES.items():
        # 查找该省份的 "2": { 数据块 }
        pattern = rf'("{province}":\s*\{{[^}}]+"2026":\s*\{{[^}}]+"2":\s*\{{[^}}]+\}})'
        
        # 构建3月数据字符串
        march_data = f''',
      "3": {{
        "deepValley": {{ price: {prices["deep"]}, hours: [0,1,2,3,4,5], name: "深谷" }},
        "valley": {{ price: {prices["valley"]}, hours: [10,11,12,13,14,15], name: "低谷" }},
        "flat": {{ price: {prices["flat"]}, hours: [6,7,8,9,16,17,22,23], name: "平段" }},
        "high": {{ price: {prices["high"]}, hours: [18,19,20,21], name: "高峰" }},
        "peak": {{ price: {prices["peak"]}, hours: [], name: "尖峰" }},
        "cycles": {2 if (prices["high"] - prices["valley"]) > 0.7 else 1}
      }}'''
        
        # 在2月数据块后插入3月数据
        content = re.sub(pattern, r'\1' + march_data, content)
    
    return content

if __name__ == "__main__":
    # 读取原始文件
    with open('/Users/zhaoruicn/.openclaw/workspace/priceData-original.js', 'r') as f:
        content = f.read()
    
    # 添加3月数据
    updated = add_march_data(content)
    
    # 保存
    with open('/Users/zhaoruicn/.openclaw/workspace/priceData-updated.js', 'w') as f:
        f.write(updated)
    
    print("已生成更新后的 priceData.js")
