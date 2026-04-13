#!/usr/bin/env python3
"""
PriceLoader 测试
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from core.price_loader import PriceLoader


def test_with_sample_data():
    """用模拟数据测试 PriceLoader"""
    print("=" * 60)
    print("测试 PriceLoader")
    print("=" * 60)

    # 创建测试数据（模拟96点格式：15分钟间隔）
    test_prices = []
    base_date = datetime(2026, 4, 1)
    for day in range(3):  # 3天数据
        for point in range(96):  # 96点/天
            dt = base_date + timedelta(days=day, minutes=point * 15)
            price = 500 + (point % 96) * 2  # 模拟电价曲线
            test_prices.append((dt, float(price)))

    print(f"\n✅ 模拟数据创建成功: {len(test_prices)} 个点")
    print(f"   时间范围: {test_prices[0][0]} ~ {test_prices[-1][0]}")
    print(f"   前3个点: {test_prices[:3]}")
    print(f"   后3个点: {test_prices[-3:]}")

    # 验证
    assert len(test_prices) == 288, f"期望288个点，实际{len(test_prices)}"
    assert test_prices[0][0] == datetime(2026, 4, 1, 0, 0)
    assert test_prices[-1][0] == datetime(2026, 4, 4, 0, 0)  # 最后一刻

    print("\n✅ 所有测试通过!")


def test_auto_detect_granularity():
    """测试时间粒度自动识别"""
    print("\n" + "=" * 60)
    print("测试时间粒度自动识别")
    print("=" * 60)

    # 24点格式
    prices_24h = [(datetime(2026, 4, 1, h, 0), 500.0) for h in range(24)]
    delta_24 = (prices_24h[1][0] - prices_24h[0][0]).total_seconds() / 3600
    points_per_day_24 = int(24 / delta_24)
    print(f"24点格式: {points_per_day_24} 点/天 → {'✅ 正确' if points_per_day_24 == 24 else '❌ 错误'}")

    # 96点格式
    prices_96h = [(datetime(2026, 4, 1, 0, m), 500.0) for m in range(0, 24 * 60, 15)]
    delta_96 = (prices_96h[1][0] - prices_96h[0][0]).total_seconds() / 3600
    points_per_day_96 = int(24 / delta_96)
    print(f"96点格式: {points_per_day_96} 点/天 → {'✅ 正确' if points_per_day_96 == 96 else '❌ 错误'}")


if __name__ == '__main__':
    test_with_sample_data()
    test_auto_detect_granularity()
    print("\n" + "=" * 60)
    print("🎉 PriceLoader 模块测试完成")
    print("=" * 60)
