#!/usr/bin/env python3
"""
为所有省份添加2026年3月电价数据
"""

import re

# 2026年3月电价数据（31省份）
MARCH_2026_PRICES = {
    "山东": {"deep": 0.1815, "valley": 0.2777, "flat": 0.6145, "high": 0.9506, "peak": 1.0948, "cycles": 2},
    "河南": {"deep": 0.2804, "valley": 0.4069, "flat": 0.7155, "high": 1.1196, "peak": 1.2323, "cycles": 1},
    "浙江": {"deep": 0.1829, "valley": 0.3507, "flat": 0.7793, "high": 1.2859, "peak": 1.4145, "cycles": 2},
    "广东": {"deep": 0.2205, "valley": 0.2797, "flat": 0.6906, "high": 1.1547, "peak": 1.4365, "cycles": 2},
    "江苏": {"deep": 0.2408, "valley": 0.3858, "flat": 0.6106, "high": 0.8872, "peak": 0.9759, "cycles": 2},
    "河北": {"deep": 0.2602, "valley": 0.3687, "flat": 0.6425, "high": 0.9163, "peak": 1.0492, "cycles": 1},
    "四川": {"deep": 0.3299, "valley": 0.3299, "flat": 0.6813, "high": 1.0326, "peak": 1.2200, "cycles": 2},
    "上海": {"deep": 0.1955, "valley": 0.3884, "flat": 0.7099, "high": 1.0956, "peak": 1.2052, "cycles": 2},
    "北京": {"deep": 0.25, "valley": 0.4074, "flat": 0.6406, "high": 0.8738, "peak": 0.9612, "cycles": 1},
    "天津": {"deep": 0.25, "valley": 0.3559, "flat": 0.6934, "high": 1.0309, "peak": 1.1340, "cycles": 1},
    "湖北": {"deep": 0.25, "valley": 0.4231, "flat": 0.6273, "high": 0.8198, "peak": 0.9415, "cycles": 1},
    "湖南": {"deep": 0.25, "valley": 0.3102, "flat": 0.6546, "high": 0.9996, "peak": 1.0996, "cycles": 1},
    "安徽": {"deep": 0.25, "valley": 0.295, "flat": 0.5915, "high": 0.9466, "peak": 1.0413, "cycles": 1},
    "福建": {"deep": 0.25, "valley": 0.3342, "flat": 0.5653, "high": 0.7781, "peak": 0.8559, "cycles": 1},
    "江西": {"deep": 0.3596, "valley": 0.4006, "flat": 0.6467, "high": 0.8928, "peak": 0.9821, "cycles": 1},
    "山西": {"deep": 0.25, "valley": 0.4095, "flat": 0.5656, "high": 0.7358, "peak": 0.8094, "cycles": 1},
    "陕西": {"deep": 0.25, "valley": 0.3715, "flat": 0.6078, "high": 0.8441, "peak": 0.9285, "cycles": 1},
    "重庆": {"deep": 0.25, "valley": 0.3438, "flat": 0.7187, "high": 1.0814, "peak": 1.1895, "cycles": 1},
    "贵州": {"deep": 0.25, "valley": 0.3495, "flat": 0.5918, "high": 0.8342, "peak": 0.9176, "cycles": 1},
    "广西": {"deep": 0.25, "valley": 0.4931, "flat": 0.6619, "high": 0.8307, "peak": 0.9138, "cycles": 1},
    "海南": {"deep": 0.25, "valley": 0.4184, "flat": 0.7376, "high": 1.1100, "peak": 1.2210, "cycles": 1},
    "辽宁": {"deep": 0.25, "valley": 0.3994, "flat": 0.4990, "high": 0.5985, "peak": 0.6584, "cycles": 1},
    "吉林": {"deep": 0.25, "valley": 0.4661, "flat": 0.6534, "high": 0.8407, "peak": 0.9248, "cycles": 1},
    "黑龙江": {"deep": 0.25, "valley": 0.4724, "flat": 0.6257, "high": 0.7790, "peak": 0.8569, "cycles": 1},
    "内蒙古西": {"deep": 0.25, "valley": 0.2900, "flat": 0.4524, "high": 0.6651, "peak": 0.7316, "cycles": 1},
    "内蒙古东": {"deep": 0.25, "valley": 0.3349, "flat": 0.4362, "high": 0.5688, "peak": 0.6257, "cycles": 1},
    "青海": {"deep": 0.25, "valley": 0.2575, "flat": 0.4422, "high": 0.6212, "peak": 0.6833, "cycles": 1},
    "甘肃": {"deep": 0.25, "valley": 0.2459, "flat": 0.4573, "high": 0.4979, "peak": 0.5477, "cycles": 1},
    "宁夏": {"deep": 0.25, "valley": 0.3399, "flat": 0.4956, "high": 0.4663, "peak": 0.5129, "cycles": 1},
    "云南": {"deep": 0.1985, "valley": 0.3970, "flat": 0.5955, "high": 0.8933, "peak": 0.9826, "cycles": 1},
    "西藏": {"deep": 0.1856, "valley": 0.3712, "flat": 0.5568, "high": 0.8352, "peak": 0.9187, "cycles": 1},
    "新疆": {"deep": 0.25, "valley": 0.3663, "flat": 0.5180, "high": 0.7099, "peak": 0.7809, "cycles": 1}
}

def add_march_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 为每个省份添加3月数据
    for province, prices in MARCH_2026_PRICES.items():
        # 构建3月数据字符串
        march_data = f''',
      "3": {{
        "deepValley": {{ price: {prices['deep']}, hours: [0,1,2,3,4,5], name: "深谷" }},
        "valley": {{ price: {prices['valley']}, hours: [10,11,12,13,14,15], name: "低谷" }},
        "flat": {{ price: {prices['flat']}, hours: [6,7,8,9,16,17,22,23], name: "平段" }},
        "high": {{ price: {prices['high']}, hours: [18,19,20,21], name: "高峰" }},
        "peak": {{ price: {prices['peak']}, hours: [], name: "尖峰" }},
        "cycles": {prices['cycles']}
      }}'''
        
        # 查找该省份的 "2": { ... } 数据块（最后一个2月数据）
        pattern = rf'("{province}":\s*\{{[\s\S]*?"2":\s*\{{[\s\S]*?"cycles":\s*\d+\s*\}})'
        
        match = re.search(pattern, content)
        if match:
            # 在2月数据块后插入3月数据
            end_pos = match.end()
            content = content[:end_pos] + march_data + content[end_pos:]
            print(f"✅ 已添加 {province} 的3月数据")
        else:
            print(f"❌ 未找到 {province} 的2月数据")
    
    # 保存修改后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ 完成！已为所有省份添加2026年3月电价数据")

if __name__ == "__main__":
    add_march_data('/usr/share/nginx/html/electricity/price-data.js')
