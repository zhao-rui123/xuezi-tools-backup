#!/usr/bin/env python3
"""
test_price_loader.py - PriceLoader 单元测试（mock数据，无真实Excel）
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch

import sys
sys.path.insert(0, '.')
from core.price_loader import PriceLoader


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_excel_df():
    """
    模拟国网电费清单格式 DataFrame（2天 × 24点/天 = 48数据行）。

    国网格式解析逻辑（参考 price_loader.py）：
      - 遍历列，从 date_val = df.iloc[2, col_idx] 读日期
      - 相邻列 df.iloc[3:, col_idx + 1] 为电价
      - 标题行 df.iloc[0, col_idx] 含 "日前"
    """
    rows = []

    # ---- 行0: 标题行 ----
    # 结构: [空, "2024-01-01日前", 空, "2024-01-02日前", 空]
    rows.append(["", "2024-01-01日前", "", "2024-01-02日前", ""])

    # ---- 行1: 空行 ----
    rows.append(["", "", "", "", ""])

    # ---- 行2: 日期行 ----
    # 结构: [空, "2024-01-01", 空, "2024-01-02", 空]
    rows.append(["", "2024-01-01", "", "2024-01-02", ""])

    # ---- 行3+: 数据行（每天24点 × 2天）----
    # price_loader 读取 col_idx 和 col_idx+1（电价列）
    for point in range(24):
        dt1 = datetime(2024, 1, 1, hour=point)
        dt2 = datetime(2024, 1, 2, hour=point)
        p1 = round(0.50 + (point / 24.0) * 0.50, 4)   # 0.50 ~ 1.00
        p2 = round(0.55 + (point / 24.0) * 0.45, 4)   # 0.55 ~ 1.00
        # [空, 时间str, 电价, 时间str, 电价]
        rows.append(["", str(dt1), p1, str(dt2), p2])

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
