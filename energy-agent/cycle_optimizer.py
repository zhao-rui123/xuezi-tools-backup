#!/usr/bin/env python3
"""
储能充放电循环优化器 v2.0 — Opus 重新设计

核心思路：加权区间调度（Weighted Interval Scheduling）
=========================================================

旧算法的5个致命bug：
1. 数据是1小时间隔，代码却用 points_per_hour=4（15分钟假设）
2. charge_end = times[start + charge_len - 1]，导致2小时充电显示为同一时刻
3. 只考虑"充电紧接放电"，错过了凌晨充→傍晚放的最优机会
4. 贪心按价差排序选择，不保证全局最优
5. 充放电时段在结果中出现重叠

新算法设计：
-----------
Phase 1: 枚举所有候选"充电窗口"和"放电窗口"
Phase 2: 组合成候选循环（充电结束 ≤ 放电开始，且收益 > 0）
Phase 3: 用动态规划（加权区间调度）选出总收益最大的不重叠组合

时间复杂度：O(W² · log W)，W = 候选窗口数
"""
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from bisect import bisect_right

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# 数据结构
# ─────────────────────────────────────────────

@dataclass
class TimeWindow:
    """一个连续时间窗口"""
    start_idx: int          # 在价格序列中的起始索引
    end_idx: int            # 结束索引（exclusive，即 [start, end)）
    start_time: datetime
    end_time: datetime      # 窗口结束时刻（= 最后一个点的时间 + interval）
    avg_price: float
    duration_hours: float

@dataclass
class Cycle:
    """一个完整的充放电循环"""
    charge: TimeWindow
    discharge: TimeWindow
    spread: float           # 放电均价 - 充电均价
    profit_per_mwh: float   # = spread（简化模型，不含效率损耗）

    @property
    def charge_start(self) -> datetime:
        return self.charge.start_time

    @property
    def charge_end(self) -> datetime:
        return self.charge.end_time

    @property
    def discharge_start(self) -> datetime:
        return self.discharge.start_time

    @property
    def discharge_end(self) -> datetime:
        return self.discharge.end_time

    @property
    def overall_start_idx(self) -> int:
        return self.charge.start_idx

    @property
    def overall_end_idx(self) -> int:
        return self.discharge.end_idx


# ─────────────────────────────────────────────
# 核心优化器
# ─────────────────────────────────────────────

class CycleOptimizer:
    """
    储能循环优化器 v2.0

    用法：
        optimizer = CycleOptimizer()
        optimizer.load_prices(filepath)
        results = optimizer.optimize()
    """

    def __init__(
        self,
        min_hours: int = 2,
        max_hours: int = 6,
        efficiency: float = 0.85,
        top_n_windows: int = 0,
    ):
        """
        Args:
            min_hours: 最短充/放电时长（小时）
            max_hours: 最长充/放电时长（小时）
            efficiency: 充放电往返效率（0~1），用于计算实际收益
            top_n_windows: 每种时长保留的最优窗口数（0=不限制，用于大数据集加速）
        """
        self.min_hours = min_hours
        self.max_hours = max_hours
        self.efficiency = efficiency
        self.top_n_windows = top_n_windows

        self.prices: List[float] = []
        self.times: List[datetime] = []
        self.interval_hours: float = 1.0  # 自动检测
        self.points_per_hour: int = 1

    # ─── 数据加载 ───

    def load_prices(self, filepath: str) -> "CycleOptimizer":
        """
        加载Excel电价数据（兼容1小时和15分钟间隔）

        Excel格式：
        - Row 1: 星期几
        - Row 2: 日前/实时
        - Row 3: 日期
        - Row 4+: 每行一个时段的电价
        - 每天占2列（日前价, 实时价），我们取实时价
        """
        logger.info("📂 加载: %s", filepath)
        df = pd.read_excel(filepath, header=None)

        all_prices: List[Tuple[datetime, float]] = []

        col_idx = 1
        while col_idx < df.shape[1]:
            # Row 3 (index 2) 是日期行
            date_val = df.iloc[2, col_idx]
            if pd.isna(date_val):
                col_idx += 1
                continue

            # 跳过"合计"等非日期列
            date_str = str(date_val)
            if any(kw in date_str for kw in ['合计', '均值', 'DIV']):
                col_idx += 1
                continue

            try:
                date = pd.to_datetime(date_val)
            except Exception:
                col_idx += 1
                continue

            # 检查 Row 2 判断是日前还是实时
            type_val = str(df.iloc[1, col_idx]) if pd.notna(df.iloc[1, col_idx]) else ""

            if type_val == "实时":
                # 这是实时价格列，直接读取
                price_col = col_idx
            elif type_val == "日前":
                # 日前列，实时在下一列
                if col_idx + 1 < df.shape[1]:
                    next_type = str(df.iloc[1, col_idx + 1]) if pd.notna(df.iloc[1, col_idx + 1]) else ""
                    if next_type == "实时":
                        price_col = col_idx + 1
                        col_idx += 2
                        # 读取实时价格
                        self._read_column_prices(df, date, price_col, all_prices)
                        continue
                col_idx += 1
                continue
            else:
                col_idx += 1
                continue

            self._read_column_prices(df, date, price_col, all_prices)
            col_idx += 1

        if not all_prices:
            logger.warning("⚠️ 未加载到任何电价数据")
            return self

        # 排序去重
        all_prices.sort(key=lambda x: x[0])
        self.times = [t for t, _ in all_prices]
        self.prices = [p for _, p in all_prices]

        # 自动检测时间间隔
        if len(self.times) >= 2:
            delta_hours = (self.times[1] - self.times[0]).total_seconds() / 3600
            if delta_hours > 0:
                self.interval_hours = delta_hours
                self.points_per_hour = round(1.0 / delta_hours)
            else:
                self.interval_hours = 1.0
                self.points_per_hour = 1
        else:
            self.interval_hours = 1.0
            self.points_per_hour = 1

        n_days = len(self.prices) / (24 * self.points_per_hour)
        logger.info(
            "✅ 加载 %d 个数据点，%.0f 天，间隔 %.0f 分钟（%d 点/小时）",
            len(self.prices), n_days,
            self.interval_hours * 60, self.points_per_hour,
        )
        logger.info(
            "   时间范围: %s ~ %s",
            self.times[0].strftime("%Y-%m-%d %H:%M"),
            self.times[-1].strftime("%Y-%m-%d %H:%M"),
        )

        return self

    def _read_column_prices(
        self, df, date: datetime, col_idx: int,
        out: List[Tuple[datetime, float]]
    ):
        """读取一列的价格数据"""
        # Row 4+ (index 3+) 是价格数据，直到遇到"均值"行
        for row_idx in range(3, df.shape[0]):
            time_label = df.iloc[row_idx, 0]
            if pd.isna(time_label) or str(time_label) == '均值':
                break

            price_val = df.iloc[row_idx, col_idx]
            if pd.isna(price_val):
                continue

            try:
                price = float(price_val)
            except (ValueError, TypeError):
                continue

            # 从时段标签解析小时偏移
            # 格式: "00:00-01:00" 或 "00:00" 或 "0:15"
            label = str(time_label)
            try:
                hour_part = label.split('-')[0].strip()
                parts = hour_part.split(':')
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
                dt = date + timedelta(hours=hour, minutes=minute)
                out.append((dt, price))
            except (ValueError, IndexError):
                # 尝试用行索引推算
                row_offset = row_idx - 3
                dt = date + timedelta(hours=row_offset * self.interval_hours)
                out.append((dt, price))

    # ─── Phase 1: 枚举候选窗口 ───

    def _enumerate_windows(self, is_charge: bool) -> List[TimeWindow]:
        """
        枚举所有可能的连续时间窗口

        Args:
            is_charge: True=充电窗口（找低价），False=放电窗口（找高价）

        Returns:
            候选窗口列表
        """
        n = len(self.prices)
        windows: List[TimeWindow] = []

        for hours in range(self.min_hours, self.max_hours + 1):
            length = hours * self.points_per_hour  # 数据点数
            if length > n:
                continue

            # 用滑动窗口计算均价
            # 预计算前缀和
            prefix = [0.0] * (n + 1)
            for i in range(n):
                prefix[i + 1] = prefix[i] + self.prices[i]

            hour_windows: List[TimeWindow] = []
            for i in range(n - length + 1):
                j = i + length  # exclusive end
                avg = (prefix[j] - prefix[i]) / length
                start_time = self.times[i]
                # end_time = 窗口结束时刻 = 最后一个数据点时间 + 一个间隔
                end_time = self.times[j - 1] + timedelta(hours=self.interval_hours)

                hour_windows.append(TimeWindow(
                    start_idx=i,
                    end_idx=j,
                    start_time=start_time,
                    end_time=end_time,
                    avg_price=avg,
                    duration_hours=hours,
                ))

            # 可选：只保留最优的 top_n 个窗口（加速大数据集）
            if self.top_n_windows > 0 and len(hour_windows) > self.top_n_windows:
                if is_charge:
                    hour_windows.sort(key=lambda w: w.avg_price)
                else:
                    hour_windows.sort(key=lambda w: -w.avg_price)
                hour_windows = hour_windows[:self.top_n_windows]

            windows.extend(hour_windows)

        logger.debug(
            "枚举了 %d 个%s窗口",
            len(windows), "充电" if is_charge else "放电",
        )
        return windows

    # ─── Phase 2: 组合候选循环 ───

    def _build_candidate_cycles(
        self,
        charge_windows: List[TimeWindow],
        discharge_windows: List[TimeWindow],
    ) -> List[Cycle]:
        """
        将充电窗口和放电窗口组合成候选循环

        约束：
        - 充电结束 ≤ 放电开始（先充后放，不重叠）
        - 收益 > 0（考虑效率损耗后）

        优化：
        - 放电窗口按 start_idx 排序，用二分查找快速定位
        - 对每个充电窗口，只考虑其后最优的若干放电窗口
        """
        # 放电窗口按 start_idx 排序
        discharge_sorted = sorted(discharge_windows, key=lambda w: w.start_idx)
        discharge_starts = [w.start_idx for w in discharge_sorted]

        cycles: List[Cycle] = []

        for cw in charge_windows:
            # 找到所有 start_idx >= cw.end_idx 的放电窗口
            pos = bisect_right(discharge_starts, cw.end_idx - 1)

            # 从 pos 开始，找收益最高的放电窗口
            # 但不需要遍历所有——只取价差 > 0 的
            for k in range(pos, len(discharge_sorted)):
                dw = discharge_sorted[k]

                # 实际收益 = 放电收入 × 效率 - 充电成本
                spread = dw.avg_price * self.efficiency - cw.avg_price
                if spread <= 0:
                    continue

                cycles.append(Cycle(
                    charge=cw,
                    discharge=dw,
                    spread=round(spread, 2),
                    profit_per_mwh=round(spread, 2),
                ))

        logger.debug("组合了 %d 个候选循环（收益>0）", len(cycles))
        return cycles

    # ─── Phase 3: 加权区间调度 DP ───

    def _select_optimal_cycles(self, cycles: List[Cycle]) -> List[Cycle]:
        """
        加权区间调度（Weighted Interval Scheduling）

        目标：选出总收益最大的不重叠循环子集

        算法：
        1. 按整体结束索引排序
        2. 对每个循环 i，二分找到与它不冲突的最晚结束循环 p(i)
        3. DP: dp[i] = max(dp[i-1], profit[i] + dp[p(i)])
        4. 回溯找出选中的循环

        时间复杂度：O(C log C)，C = 候选循环数
        """
        if not cycles:
            return []

        # 按整体结束索引排序
        cycles_sorted = sorted(cycles, key=lambda c: c.overall_end_idx)
        n = len(cycles_sorted)

        # 提取结束索引数组，用于二分查找
        end_indices = [c.overall_end_idx for c in cycles_sorted]

        # 计算 p(i)：与循环 i 不冲突的最晚结束循环的索引
        # 循环 i 的开始 = charge.start_idx
        # 不冲突 = 前一个循环的 discharge.end_idx <= 当前循环的 charge.start_idx
        p = [-1] * n
        for i in range(n):
            target = cycles_sorted[i].overall_start_idx
            # 找最大的 j 使得 end_indices[j] <= target
            lo, hi = 0, i - 1
            result = -1
            while lo <= hi:
                mid = (lo + hi) // 2
                if end_indices[mid] <= target:
                    result = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            p[i] = result

        # DP
        dp = [0.0] * (n + 1)  # dp[i] = 考虑前 i 个循环的最大收益
        for i in range(1, n + 1):
            profit_i = cycles_sorted[i - 1].spread
            include = profit_i + (dp[p[i - 1] + 1] if p[i - 1] >= 0 else 0)
            exclude = dp[i - 1]
            dp[i] = max(include, exclude)

        # 回溯找出选中的循环
        selected: List[Cycle] = []
        i = n
        while i > 0:
            profit_i = cycles_sorted[i - 1].spread
            include = profit_i + (dp[p[i - 1] + 1] if p[i - 1] >= 0 else 0)
            if include >= dp[i - 1]:
                selected.append(cycles_sorted[i - 1])
                i = p[i - 1] + 1  # 跳到不冲突的位置
            else:
                i -= 1

        selected.reverse()  # 按时间顺序
        return selected

    # ─── 主入口 ───

    def optimize(self, min_spread: float = 0) -> List[Cycle]:
        """
        主优化流程

        Args:
            min_spread: 最小价差过滤（默认0，不预设阈值）

        Returns:
            最优不重叠循环组合，按时间顺序
        """
        if not self.prices:
            logger.warning("没有价格数据，请先调用 load_prices()")
            return []

        logger.info("🔄 Phase 1: 枚举候选窗口...")
        charge_windows = self._enumerate_windows(is_charge=True)
        discharge_windows = self._enumerate_windows(is_charge=False)

        logger.info("🔄 Phase 2: 组合候选循环...")
        candidates = self._build_candidate_cycles(charge_windows, discharge_windows)

        # 可选：过滤最小价差
        if min_spread > 0:
            before = len(candidates)
            candidates = [c for c in candidates if c.spread >= min_spread]
            logger.info("   价差过滤: %d → %d（≥%.0f）", before, len(candidates), min_spread)

        # 候选数量可能很大，做剪枝
        candidates = self._prune_candidates(candidates)

        logger.info("🔄 Phase 3: 动态规划求解最优组合...")
        selected = self._select_optimal_cycles(candidates)

        total_profit = sum(c.spread for c in selected)
        logger.info(
            "✅ 选出 %d 个循环，总收益 %.2f 元/MWh",
            len(selected), total_profit,
        )

        return selected

    def _prune_candidates(self, candidates: List[Cycle]) -> List[Cycle]:
        """
        剪枝：减少候选循环数量，保证 DP 可在合理时间内完成

        策略：
        - 对于同一充电窗口，只保留收益最高的 K 个放电窗口
        - 对于同一放电窗口，只保留成本最低的 K 个充电窗口
        """
        if len(candidates) <= 50000:
            return candidates

        logger.info("   候选循环 %d 个，执行剪枝...", len(candidates))

        # 按充电窗口分组，每组保留 top 20
        from collections import defaultdict
        by_charge: dict = defaultdict(list)
        for c in candidates:
            key = (c.charge.start_idx, c.charge.end_idx)
            by_charge[key].append(c)

        pruned = []
        for key, group in by_charge.items():
            group.sort(key=lambda c: -c.spread)
            pruned.extend(group[:20])

        logger.info("   剪枝后: %d 个候选循环", len(pruned))
        return pruned

    # ─── 导出 ───

    def export_json(self, cycles: List[Cycle], output_path: str) -> str:
        """导出结果到 JSON"""
        data = {
            "version": "2.0",
            "algorithm": "weighted_interval_scheduling_dp",
            "generated_at": datetime.now().isoformat(),
            "data_info": {
                "total_points": len(self.prices),
                "interval_minutes": int(self.interval_hours * 60),
                "points_per_hour": self.points_per_hour,
                "time_range": f"{self.times[0].strftime('%Y-%m-%d')} ~ {self.times[-1].strftime('%Y-%m-%d')}",
            },
            "parameters": {
                "min_hours": self.min_hours,
                "max_hours": self.max_hours,
                "efficiency": self.efficiency,
            },
            "summary": {
                "total_cycles": len(cycles),
                "total_profit_per_mwh": round(sum(c.spread for c in cycles), 2),
                "avg_spread": round(
                    sum(c.spread for c in cycles) / len(cycles), 2
                ) if cycles else 0,
            },
            "cycles": [
                {
                    "charge_start": c.charge_start.strftime("%Y-%m-%d %H:%M"),
                    "charge_end": c.charge_end.strftime("%Y-%m-%d %H:%M"),
                    "charge_hours": c.charge.duration_hours,
                    "charge_avg_price": round(c.charge.avg_price, 2),
                    "discharge_start": c.discharge_start.strftime("%Y-%m-%d %H:%M"),
                    "discharge_end": c.discharge_end.strftime("%Y-%m-%d %H:%M"),
                    "discharge_hours": c.discharge.duration_hours,
                    "discharge_avg_price": round(c.discharge.avg_price, 2),
                    "spread": c.spread,
                    "profit_per_mwh": c.profit_per_mwh,
                }
                for c in cycles
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info("📄 已导出到: %s", output_path)
        return output_path

    def print_summary(self, cycles: List[Cycle]):
        """打印结果摘要"""
        if not cycles:
            print("❌ 没有找到有效循环")
            return

        total = sum(c.spread for c in cycles)
        print(f"\n{'='*70}")
        print(f"  储能充放电优化结果 (v2.0 加权区间调度)")
        print(f"{'='*70}")
        print(f"  数据: {len(self.prices)} 点, 间隔 {int(self.interval_hours*60)} 分钟")
        print(f"  效率: {self.efficiency*100:.0f}%")
        print(f"  循环数: {len(cycles)}")
        print(f"  总收益: {total:.2f} 元/MWh")
        print(f"  平均价差: {total/len(cycles):.2f} 元/MWh")
        print(f"{'='*70}")

        for i, c in enumerate(cycles, 1):
            print(
                f"  #{i:3d}  "
                f"充电 {c.charge_start.strftime('%m-%d %H:%M')}~{c.charge_end.strftime('%H:%M')} "
                f"({c.charge.duration_hours}h, ¥{c.charge.avg_price:.1f})  →  "
                f"放电 {c.discharge_start.strftime('%m-%d %H:%M')}~{c.discharge_end.strftime('%H:%M')} "
                f"({c.discharge.duration_hours}h, ¥{c.discharge.avg_price:.1f})  "
                f"价差 {c.spread:.1f}"
            )

        print(f"{'='*70}\n")


# ─────────────────────────────────────────────
# 向后兼容：保留旧接口名
# ─────────────────────────────────────────────

@dataclass
class CycleOptimizerResult:
    """向后兼容旧接口"""
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


def convert_to_legacy(cycles: List[Cycle]) -> List[CycleOptimizerResult]:
    """将新格式转换为旧格式，兼容下游代码"""
    return [
        CycleOptimizerResult(
            charge_start=c.charge_start,
            charge_end=c.charge_end,
            charge_len=int(c.charge.duration_hours),
            charge_price=round(c.charge.avg_price, 2),
            discharge_start=c.discharge_start,
            discharge_end=c.discharge_end,
            discharge_len=int(c.discharge.duration_hours),
            discharge_price=round(c.discharge.avg_price, 2),
            spread=c.spread,
            profit_per_mwh=c.profit_per_mwh,
        )
        for c in cycles
    ]


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main():
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    if len(sys.argv) < 2:
        print("用法: python3 cycle_optimizer.py <电价Excel文件> [输出JSON路径]")
        sys.exit(1)

    filepath = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "cycles_v2.json"

    optimizer = CycleOptimizer(
        min_hours=2,
        max_hours=6,
        efficiency=0.85,
    )
    optimizer.load_prices(filepath)
    cycles = optimizer.optimize()
    optimizer.print_summary(cycles)
    optimizer.export_json(cycles, output)


if __name__ == "__main__":
    main()
