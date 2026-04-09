#!/usr/bin/env python3
"""
储能充放电循环优化器
核心：给定电价序列，找出收益最大的不重叠循环组合
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class CycleOptimizerResult:
    """单个充放电循环的优化结果"""
    charge_start: datetime
    charge_end: datetime
    charge_len: int
    charge_price: float
    discharge_start: datetime
    discharge_end: datetime
    discharge_len: int
    discharge_price: float
    spread: float
    profit_per_mwh: float


class CycleOptimizer:
    """循环优化器"""

    def __init__(self) -> None:
        self.hourly_prices: List[tuple[datetime, float]] = []

    def load_excel(self, filepath: str) -> "CycleOptimizer":
        """
        加载Excel格式电价数据

        Args:
            filepath: Excel文件路径

        Returns:
            self（链式调用）
        """
        logger.info("加载: %s", filepath)
        df = pd.read_excel(filepath, header=None)

        all_prices: List[tuple[datetime, float]] = []

        col_idx = 1
        while col_idx < df.shape[1]:
            date_val = df.iloc[2, col_idx]
            if pd.notna(date_val) and "日前" not in str(date_val):
                try:
                    date = pd.to_datetime(date_val)
                    real_prices = pd.to_numeric(
                        df.iloc[3:, col_idx + 1].values, errors="coerce"
                    )

                    for hour_idx, price in enumerate(real_prices):
                        if not np.isnan(price):
                            dt = date + timedelta(hours=hour_idx)
                            all_prices.append((dt, float(price)))
                except Exception:
                    pass
                col_idx += 2
            else:
                col_idx += 1

        all_prices.sort(key=lambda x: x[0])
        self.hourly_prices = all_prices

        if self.hourly_prices:
            logger.info(
                "加载了 %d 个小时数据，时间范围: %s ~ %s",
                len(self.hourly_prices),
                self.hourly_prices[0][0],
                self.hourly_prices[-1][0],
            )
        else:
            logger.warning("未加载到任何电价数据")

        return self

    def find_all_cycles(
        self, min_spread: float = 50
    ) -> List[CycleOptimizerResult]:
        """
        找出所有可能的充放电循环

        规则：
        - 充电在低价区间（连续几小时均价低）
        - 放电在高价位
        - 充电时长通常2-6小时
        - 放电时长通常2-6小时
        - 允许跨天：今天充，明天放

        Args:
            min_spread: 最小价差阈值（元/MWh）

        Returns:
            所有满足条件的候选循环列表
        """
        if not self.hourly_prices:
            return []

        prices = [p for _, p in self.hourly_prices]
        times = [t for t, _ in self.hourly_prices]
        n = len(prices)

        all_cycles: List[CycleOptimizerResult] = []

        for charge_len in [2, 3, 4, 5, 6]:  # 充电时长2-6小时
            for discharge_len in [2, 3, 4, 5, 6]:  # 放电时长2-6小时
                for start_idx in range(n - charge_len - discharge_len):
                    charge_prices = prices[start_idx : start_idx + charge_len]
                    charge_start = times[start_idx]
                    charge_end = times[start_idx + charge_len - 1]
                    avg_charge = np.mean(charge_prices)

                    discharge_start_idx = start_idx + charge_len
                    discharge_end_idx = discharge_start_idx + discharge_len
                    if discharge_end_idx > n:
                        continue

                    discharge_prices = prices[
                        discharge_start_idx:discharge_end_idx
                    ]
                    discharge_start = times[discharge_start_idx]
                    discharge_end = times[discharge_end_idx - 1]
                    avg_discharge = np.mean(discharge_prices)

                    spread = avg_discharge - avg_charge

                    if spread >= min_spread:
                        all_cycles.append(
                            CycleOptimizerResult(
                                charge_start=charge_start,
                                charge_end=charge_end,
                                charge_len=charge_len,
                                charge_price=avg_charge,
                                discharge_start=discharge_start,
                                discharge_end=discharge_end,
                                discharge_len=discharge_len,
                                discharge_price=avg_discharge,
                                spread=spread,
                                profit_per_mwh=spread,
                            )
                        )

        logger.debug(
            "找到 %d 个候选循环（价差≥%.0f）", len(all_cycles), min_spread
        )
        return all_cycles

    def select_non_overlapping_cycles(
        self, cycles: List[CycleOptimizerResult]
    ) -> List[CycleOptimizerResult]:
        """
        选择不重叠的最优循环组合
        使用贪心算法：按结束时间排序，依次选择不重叠的

        Args:
            cycles: 所有候选循环

        Returns:
            不重叠的最优循环组合
        """
        if not cycles:
            return []

        sorted_cycles = sorted(cycles, key=lambda x: x.discharge_end)

        selected: List[CycleOptimizerResult] = []
        current_end = datetime(1970, 1, 1)

        for cycle in sorted_cycles:
            if cycle.charge_start > current_end:
                selected.append(cycle)
                current_end = cycle.discharge_end

        return selected

    def optimize(self, min_spread: float = 100) -> List[CycleOptimizerResult]:
        """
        主优化流程：找出所有候选循环并选择最优不重叠组合

        Args:
            min_spread: 最小价差阈值（元/MWh）

        Returns:
            最优不重叠循环组合，按收益降序排列
        """
        all_cycles = self.find_all_cycles(min_spread=min_spread)
        selected = self.select_non_overlapping_cycles(all_cycles)
        selected.sort(key=lambda x: x.spread, reverse=True)
        return selected

    def export_json(
        self, cycles: List[CycleOptimizerResult], output_path: str
    ) -> str:
        """
        导出循环结果到JSON文件

        Args:
            cycles: 循环结果列表
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        data = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "total_cycles": len(cycles),
            "total_spread": round(sum(c.spread for c in cycles), 2),
            "cycles": [
                {
                    "charge_start": c.charge_start.isoformat(),
                    "charge_end": c.charge_end.isoformat(),
                    "charge_len": c.charge_len,
                    "charge_price": round(c.charge_price, 2),
                    "discharge_start": c.discharge_start.isoformat(),
                    "discharge_end": c.discharge_end.isoformat(),
                    "discharge_len": c.discharge_len,
                    "discharge_price": round(c.discharge_price, 2),
                    "spread": round(c.spread, 2),
                }
                for c in cycles
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info("已导出 %d 个循环到: %s", len(cycles), output_path)
        return output_path
