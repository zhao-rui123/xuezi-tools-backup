#!/usr/bin/env python3
"""
电价加载器 - 国网电费清单Excel解析
输入：国网电费清单Excel（多天、96点/天或24点/天）
输出：标准时间序列 [(datetime, price), ...]
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple


class PriceLoader:
    """电价加载器"""

    def __init__(self):
        self.prices: List[Tuple[datetime, float]] = []

    def load_excel(self, filepath: str) -> List[Tuple[datetime, float]]:
        """
        加载Excel格式电价数据

        Args:
            filepath: Excel文件路径

        Returns:
            List[Tuple[datetime, price]] - 时间序列
        """
        print(f"📂 加载: {filepath}")
        df = pd.read_excel(filepath, header=None)

        # 收集所有小时级别的电价（跨多天）
        all_prices = []

        col_idx = 1
        while col_idx < df.shape[1]:
            date_val = df.iloc[2, col_idx]
            if pd.notna(date_val) and '日前' not in str(date_val):
                try:
                    date = pd.to_datetime(date_val)
                    # 实时电价列 (相邻两列：日期+实时电价)
                    real_prices = pd.to_numeric(df.iloc[3:, col_idx + 1].values, errors='coerce')

                    for hour_idx, price in enumerate(real_prices):
                        if not np.isnan(price):
                            dt = date + timedelta(hours=hour_idx)
                            all_prices.append((dt, float(price)))
                except Exception as e:
                    print(f"⚠️ 解析列 {col_idx} 失败: {e}")
                    pass
                col_idx += 2
            else:
                col_idx += 1

        # 按时间排序
        all_prices.sort(key=lambda x: x[0])
        self.prices = all_prices

        # 自动识别时间粒度
        if len(self.prices) >= 2:
            delta = (self.prices[1][0] - self.prices[0][0]).total_seconds() / 3600
            if delta > 0:
                points_per_day = int(24 / delta)
            else:
                points_per_day = 24
        else:
            points_per_day = 24

        print(f"✅ 加载了 {len(self.prices)} 个价格数据点")
        print(f"   时间范围: {self.prices[0][0]} ~ {self.prices[-1][0]}")
        print(f"   识别格式: {'96点(15分钟)' if points_per_day == 96 else '24点(1小时)'}")

        return self.prices

    def get_prices(self) -> List[Tuple[datetime, float]]:
        """获取加载的价格序列"""
        return self.prices

    def get_date_range(self) -> Tuple[datetime, datetime]:
        """获取时间范围"""
        if not self.prices:
            return None, None
        return self.prices[0][0], self.prices[-1][0]

    def filter_by_date(self, start: datetime, end: datetime) -> List[Tuple[datetime, float]]:
        """按日期过滤"""
        return [(dt, p) for dt, p in self.prices if start <= dt <= end]


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 -m core.price_loader <电价Excel文件>")
        sys.exit(1)

    filepath = sys.argv[1]
    loader = PriceLoader()
    prices = loader.load_excel(filepath)

    print(f"\n📊 前5条数据:")
    for dt, price in prices[:5]:
        print(f"   {dt.strftime('%Y-%m-%d %H:%M')} -> {price}")

    print(f"\n📊 后5条数据:")
    for dt, price in prices[-5:]:
        print(f"   {dt.strftime('%Y-%m-%d %H:%M')} -> {price}")


if __name__ == '__main__':
    main()
