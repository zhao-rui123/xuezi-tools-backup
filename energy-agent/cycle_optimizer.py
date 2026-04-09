#!/usr/bin/env python3
"""
储能充放电循环优化器
核心：给定电价序列，找出收益最大的不重叠循环组合
算法：动态规划（加权区间调度）+ 二分查找
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class CycleResult:
    """单个充放电循环的优化结果"""
    charge_start: datetime
    charge_end: datetime       # 充电结束时点（含）
    charge_len: int            # 充电时长（小时）
    charge_price: float        # 充电均价（元/MWh）
    discharge_start: datetime  # 放电开始时点（含）
    discharge_end: datetime    # 放电结束时点（含）
    discharge_len: int        # 放电时长（小时）
    discharge_price: float    # 放电均价（元/MWh）
    spread: float             # 价差（元/MWh）
    profit_per_mwh: float      # 每MWh利润 = spread

    def interval_start(self) -> datetime:
        return self.charge_start

    def interval_end(self) -> datetime:
        return self.discharge_end


class CycleOptimizer:
    """循环优化器：动态规划找最大收益的不重叠循环组合"""

    def __init__(self) -> None:
        self.hourly_prices: List[Tuple[datetime, float]] = []

    def load_excel(self, filepath: str) -> "CycleOptimizer":
        """
        加载Excel格式电价数据（仅读取"日前"列，1小时间隔）

        Args:
            filepath: Excel文件路径

        Returns:
            self（链式调用）
        """
        logger.info("加载: %s", filepath)
        df = pd.read_excel(filepath, header=None)

        all_prices: List[Tuple[datetime, float]] = []

        # 扫描所有列，每2列为一组（日前、实时）
        col_idx = 1
        while col_idx < df.shape[1]:
            label = df.iloc[1, col_idx]
            if label == "日前":
                date_val = df.iloc[2, col_idx]
                if pd.notna(date_val):
                    try:
                        date = pd.to_datetime(date_val)
                        for hour_idx in range(24):
                            price = df.iloc[3 + hour_idx, col_idx]
                            if pd.notna(price):
                                dt = date + timedelta(hours=hour_idx)
                                all_prices.append((dt, float(price)))
                    except Exception:
                        pass
            col_idx += 2

        all_prices.sort(key=lambda x: x[0])
        self.hourly_prices = all_prices

        if self.hourly_prices:
            logger.info(
                "加载了 %d 个小时数据（日前），时间范围: %s ~ %s",
                len(self.hourly_prices),
                self.hourly_prices[0][0],
                self.hourly_prices[-1][0],
            )
        else:
            logger.warning("未加载到任何电价数据")

        return self

    # ------------------------------------------------------------------
    # 核心算法
    # ------------------------------------------------------------------

    def find_all_cycles(self) -> List[CycleResult]:
        """
        枚举所有满足条件的候选循环（充电2-6小时，放电2-6小时）

        Returns:
            所有候选循环列表
        """
        if not self.hourly_prices:
            return []

        prices = [p for _, p in self.hourly_prices]
        times = [t for t, _ in self.hourly_prices]
        n = len(prices)

        all_cycles: List[CycleResult] = []

        # 充电时长2-6小时，放电时长2-6小时
        for charge_len in range(2, 7):          # 2,3,4,5,6
            for discharge_len in range(2, 7):   # 2,3,4,5,6
                total_len = charge_len + discharge_len
                for start_idx in range(n - total_len + 1):
                    # 充电时段 [start_idx, start_idx + charge_len)
                    charge_prices = prices[start_idx: start_idx + charge_len]
                    charge_start = times[start_idx]
                    charge_end = times[start_idx + charge_len - 1]
                    avg_charge = float(np.mean(charge_prices))

                    # 放电时段紧接在充电之后
                    discharge_start_idx = start_idx + charge_len
                    discharge_end_idx = discharge_start_idx + discharge_len
                    discharge_prices = prices[discharge_start_idx:discharge_end_idx]
                    discharge_start = times[discharge_start_idx]
                    discharge_end = times[discharge_end_idx - 1]
                    avg_discharge = float(np.mean(discharge_prices))

                    spread = avg_discharge - avg_charge

                    # 只保留正收益循环（动态筛选，后续DP再全局优化）
                    if spread > 0:
                        all_cycles.append(
                            CycleResult(
                                charge_start=charge_start,
                                charge_end=charge_end,
                                charge_len=charge_len,
                                charge_price=round(avg_charge, 4),
                                discharge_start=discharge_start,
                                discharge_end=discharge_end,
                                discharge_len=discharge_len,
                                discharge_price=round(avg_discharge, 4),
                                spread=round(spread, 4),
                                profit_per_mwh=round(spread, 4),
                            )
                        )

        logger.info("共枚举 %d 个正收益候选循环", len(all_cycles))
        return all_cycles

    def select_best_cycles_dp(
        self, cycles: List[CycleResult]
    ) -> List[CycleResult]:
        """
        加权区间调度 DP：选总利润最大的不重叠循环组合

        状态定义：
          dp[i] = 到第 i 个循环（按 discharge_end 排序）为止的最大总利润
                  （包含第 i 个或不包含）

        转移：
          dp[i] = max(dp[i-1], profit[i] + dp[p(i)])
          其中 p(i) = 右侧最近不重叠循环的索引

        Returns:
            最优循环组合（按时间顺序排列）
        """
        if not cycles:
            return []

        # 按 discharge_end 升序排序
        sorted_cycles = sorted(cycles, key=lambda x: x.discharge_end)
        m = len(sorted_cycles)

        # 预处理：找每个循环右侧最近不重叠循环的索引
        # 二分查找：找最后一个 discharge_end < sorted_cycles[i].charge_start 的索引
        import bisect
        end_times = [c.discharge_end for c in sorted_cycles]

        predecessor_idx: List[int] = []
        for c in sorted_cycles:
            # 找 end_times 中 < c.charge_start 的最大索引
            idx = bisect.bisect_right(end_times, c.charge_start) - 1
            predecessor_idx.append(idx)  # -1 表示没有不重叠的前置循环

        # DP
        dp = [0.0] * m
        choice = [False] * m  # choice[i]=True 表示选第 i 个循环

        for i in range(m):
            # 不选第 i 个循环
            not_take = dp[i - 1] if i > 0 else 0.0

            # 选第 i 个循环：利润 + dp[p(i)]
            profit_i = sorted_cycles[i].profit_per_mwh
            prev_dp = dp[predecessor_idx[i]] if predecessor_idx[i] >= 0 else 0.0
            take = profit_i + prev_dp

            if take > not_take:
                dp[i] = take
                choice[i] = True
            else:
                dp[i] = not_take
                choice[i] = False

        # 回溯：重建最优解
        selected: List[CycleResult] = []
        i = m - 1
        while i >= 0:
            if choice[i]:
                selected.append(sorted_cycles[i])
                i = predecessor_idx[i] - 1 if predecessor_idx[i] >= 0 else -1
            else:
                i -= 1

        selected.reverse()  # 时间正序
        return selected

    def optimize(self) -> List[CycleResult]:
        """
        主优化流程：
          1. 枚举所有候选循环（正收益）
          2. DP 选总利润最大的不重叠组合

        Returns:
            最优不重叠循环组合
        """
        all_cycles = self.find_all_cycles()
        selected = self.select_best_cycles_dp(all_cycles)
        logger.info("DP 最优解：%d 个循环，总利润 %.2f 元/MWh",
                    len(selected),
                    sum(c.profit_per_mwh for c in selected))
        return selected

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    def get_top_n_cycles(
        self, n: int = 5
    ) -> List[CycleResult]:
        """
        返回利润最高的 top-n 单个循环（用于测试验证）
        注意：这只是单个循环排名，不是最优组合

        Returns:
            按利润降序的前 n 个循环
        """
        all_cycles = self.find_all_cycles()
        return sorted(all_cycles, key=lambda x: x.profit_per_mwh, reverse=True)[:n]

    def export_json(
        self, cycles: List[CycleResult], output_path: str
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
            "version": "2.0",
            "generated_at": datetime.now().isoformat(),
            "total_cycles": len(cycles),
            "total_profit": round(sum(c.profit_per_mwh for c in cycles), 4),
            "cycles": [
                {
                    "charge_start": c.charge_start.isoformat(),
                    "charge_end": c.charge_end.isoformat(),
                    "charge_len": c.charge_len,
                    "charge_price": c.charge_price,
                    "discharge_start": c.discharge_start.isoformat(),
                    "discharge_end": c.discharge_end.isoformat(),
                    "discharge_len": c.discharge_len,
                    "discharge_price": c.discharge_price,
                    "spread": c.spread,
                    "profit_per_mwh": c.profit_per_mwh,
                }
                for c in cycles
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info("已导出 %d 个循环到: %s", len(cycles), output_path)
        return output_path
