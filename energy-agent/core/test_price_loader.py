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
def mock_prices():
    """直接构造内存价格序列，绕过 Excel 解析逻辑"""
    prices = []
    base = datetime(2024, 1, 1)
    for i in range(96):          # 96点/天 × 2天
        dt = base + timedelta(minutes=i * 15)
        price = 0.5 + (i / 96) * 0.5   # 0.5 ~ 1.0 模拟波动
        prices.append((dt, round(price, 4)))
    return prices


@pytest.fixture
def mock_excel_df():
    """
    模拟国网电费清单格式的 DataFrame（国网格式：列对=日期+电价）。
    使用小数据量(24点/天)加快测试。
    """
    # 两天，每天24点(1小时粒度)，共48行数据 + 3行表头
    num_days = 2
    num_points = 24

    rows = []
    # 行0: 标题行 ("日前"列)
    rows.append([""] + [f"2024-01-0{day+1}日前"] * num_days)
    # 行1: 空行
    rows.append([""] + [""] * num_days)
    # 行2: 日期行
    rows.append([""] + [f"2024-01-0{day+1}" for day in range(num_days)])
    # 行3+: 电价数据
    for point_idx in range(num_points):
        row = [""]
        for day in range(num_days):
            # 真实电价数据只出现在 "日期+1" 列（第2列和第4列位置）
            # 列对结构: [空, 日期列, 空, 电价列, 空] for 2 days
            price = round(0.5 + (point_idx / 24) * 0.5, 4)
            row.append("")       # 日期列（时间由point_idx决定）
            row.append(price)    # 电价列
        rows.append(row)

    df = pd.DataFrame(rows)
    return df


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

    def test_load_excel_prices_are_float(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
            assert all(isinstance(p, float) for _, p in price_loader.prices)
            assert all(p > 0 for _, p in price_loader.prices)


class TestGetPrices:
    def test_get_prices_empty(self, price_loader):
        assert price_loader.get_prices() == []

    def test_get_prices_after_load(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
        result = price_loader.get_prices()
        assert result == price_loader.prices
        assert all(isinstance(dt, datetime) for dt, _ in result)
        assert all(isinstance(p, float) for _, p in result)


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
    def test_filter_by_date_within_range(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 2, 23, 59, 59)
        filtered = price_loader.filter_by_date(start, end)
        assert len(filtered) > 0
        assert all(start <= dt <= end for dt, _ in filtered)

    def test_filter_by_date_no_match(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
        # 不存在的时间段
        filtered = price_loader.filter_by_date(datetime(2023, 1, 1), datetime(2023, 1, 2))
        assert filtered == []

    def test_filter_by_date_empty_prices(self, price_loader):
        filtered = price_loader.filter_by_date(datetime(2024, 1, 1), datetime(2024, 1, 2))
        assert filtered == []

    def test_filter_by_date_first_day_only(self, price_loader, mock_excel_df):
        with patch("pandas.read_excel", return_value=mock_excel_df):
            price_loader.load_excel("dummy.xlsx")
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 1, 23, 59, 59)
        filtered = price_loader.filter_by_date(start, end)
        assert len(filtered) > 0
        assert all(datetime(2024, 1, 1) <= dt <= end for dt, _ in filtered)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
