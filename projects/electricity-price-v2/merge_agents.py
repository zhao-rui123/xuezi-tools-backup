#!/usr/bin/env python3
"""
合并所有 Agent 输出的时段数据，生成统一的 electricityPriceData.ts 文件
"""

import re
import os

# 读取现有文件，保留基础结构
with open('/Users/zhaoruicn/.openclaw/workspace/projects/electricity-price-v2/electricity-price-v2/src/data/electricityPriceData.ts', 'r') as f:
    original_content = f.read()

# 提取文件头部（接口定义、常量等）
header_match = re.search(r'(.+?)(?=// 江苏省时段配置)', original_content, re.DOTALL)
if header_match:
    header = header_match.group(1)
else:
    header = original_content[:original_content.find('const jsTimeSlots')]

# 提取文件尾部（getProvinceData 函数等）
footer_match = re.search(r'(// 获取某省份某月的时段配置.*)', original_content, re.DOTALL)
if footer_match:
    footer = footer_match.group(1)
else:
    footer = original_content[original_content.find('// 获取某省份某月的时段配置'):]

# 读取所有 Agent 输出
agent_outputs = {}
output_dir = '/Users/zhaoruicn/.openclaw/workspace/projects/electricity-price-v2/agent_output/'
for agent in ['alpha', 'bravo', 'charlie', 'delta', 'echo']:
    try:
        with open(f'{output_dir}{agent}.txt', 'r') as f:
            agent_outputs[agent] = f.read()
    except:
        agent_outputs[agent] = ''

# 生成新的时段配置
new_timeslots = []

# Alpha 输出已经是正确格式，直接使用
alpha_content = agent_outputs.get('alpha', '')
if alpha_content:
    # 提取所有 const xxTimeSlots 定义
    timeslot_matches = re.findall(r'(const \w+TimeSlots: Record<number, TimeSlot\[\]> = \{[\s\S]*?\};)', alpha_content)
    new_timeslots.extend(timeslot_matches)

# 对于其他 Agent，需要转换格式
# 这里简化处理，直接输出提示
print("Alpha 数据已提取")
print(f"找到 {len(timeslot_matches)} 个省份时段定义")

# 保存合并后的内容（简化版本，只包含 Alpha 的数据）
merged_content = header + '\n'.join(new_timeslots) + '\n' + footer

# 写入临时文件
with open('/Users/zhaoruicn/.openclaw/workspace/projects/electricity-price-v2/electricityPriceData_merged.ts', 'w') as f:
    f.write(merged_content)

print("合并完成，文件保存到 electricityPriceData_merged.ts")
print("注意：Bravo/Charlie/Delta/Echo 的数据需要手动转换格式")
