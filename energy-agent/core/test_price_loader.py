#!/usr/bin/env python3
"""
test_price_loader.py - PriceLoader 单元测试（mock数据，无真实Excel）
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, '.')
from core.price_loader import PriceLoader


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_excel_df():
    """
    构造一个模拟国网电费清单格式的 DataFrame：
    - 行0: 标题行
    - 行1: 空或辅助行
    - 行2: 日期行（两个日期）
    - 行3+: 实时电价数据（96点/天 × 2天 = 192行）
    结构示意（简化）：
      |  列0  |   列1   |  列2   |   列3   |
      |       | 2024-01-01 |      | 2024-01-02 |
      |       | 实时电价  |       | 实时电价  |
    """
    num_points = 96  # 96点/天
    num_days = 2

    rows = []
    # 行0: 标题行
    rows.append([""] + [f"2024-01-0{day+1}日前" for day in range(num_days) for _ in range(2)])
    # 行1: 空行
    rows.append([""] + [""] * (num_days * 2))
    # 行2: 日期行
    rows.append([""] + [f"2024-01-0{day+1}" for day in range(num_days) for _ in range(2)])
    # 行3+: 实时电价（每行一个时间点）
    for point_idx in range(num_points):
        row = [""]
        for day in range(num_days):
            date = datetime(2024, 1, day + 1)
            dt = date + timedelta(minutes=point_idx * 15)
            price = 0.5 + (point_idx / 96) * 0.5  # 0.5 ~ 1.0 模拟电价波动
            row.append(str(dt))  # 时间列
            row.append(round(price, 4))  # 电价列
        rows.append(row)

    return pd.DataFrame(rows)


@pytest.fixture
def price_loader():
    return PriceLoader()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPriceLoaderInit:
    def test_init_empty(self, price_loader):
        assert price_loader.prices == []


class TestLoadExcelMock:
    def test_load_excel_returns_list(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            result = price_loader.load_excel("dummy.xlsx")
            assert isinstance(result, list)
            assert len(result) > 0

    def test_load_excel_populates_prices(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
            assert len(price_loader.prices) > 0

    def test_load_excel_sorted_by_datetime(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
            dts = [dt for dt, _ in price_loader.prices]
            assert dts == sorted(dts)

    def test_load_excel_no_duplicates(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
            dts = [dt for dt, _ in price_loader.prices]
            assert len(dts) == len(set(dts))


class TestGetPrices:
    def test_get_prices_empty(self, price_loader):
        assert price_loader.get_prices() == []

    def test_get_prices_after_load(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
        assert price_loader.get_prices() == price_loader.prices
        assert all(isinstance(dt, datetime) for dt, _ in price_loader.get_prices())
        assert all(isinstance(p, float) for _, p in price_loader.get_prices())


class TestGetDateRange:
    def test_get_date_range_empty(self, price_loader):
        start, end = price_loader.get_date_range()
        assert start is None
        assert end is None

    def test_get_date_range_after_load(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
        start, end = price_loader.get_date_range()
        assert start is not None
        assert end is not None
        assert start < end


class TestFilterByDate:
    def test_filter_by_date_exact_match(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
        # 取第一天
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 1, 23, 59, 59)
        filtered = price_loader.filter_by_date(start, end)
        assert len(filtered) > 0
        assert all(datetime(2024, 1, 1) <= dt <= end for dt, _ in filtered)

    def test_filter_by_date_range(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 2, 23, 59, 59)
        filtered = price_loader.filter_by_date(start, end)
        assert len(filtered) > 0
        assert all(start <= dt <= end for dt, _ in filtered)

    def test_filter_by_date_no_match(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
        # 过滤不存在的时间段
        filtered = price_loader.filter_by_date(datetime(2023, 1, 1), datetime(2023, 1, 2))
        assert len(filtered) == 0

    def test_filter_by_date_empty_prices(self, price_loader):
        filtered = price_loader.filter_by_date(datetime(2024, 1, 1), datetime(2024, 1, 2))
        assert filtered == []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
