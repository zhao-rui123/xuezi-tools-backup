#!/usr/bin/env python3
"""
测试股票报告生成（不发送）
"""

import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace')

# 导入并运行生成报告（不发送）
from stock_feishu_push_fusion import generate_report

print("生成股票报告...")
report = generate_report()
print(report)
print("\n" + "="*60)
print("报告生成完成！")
print(f"报告长度: {len(report)} 字符")
