#!/usr/bin/env python3
"""
YFinance股票数据源 - 从Yahoo Finance获取美股、港股、A股数据
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def get_stock_info(symbol: str) -> Dict:
    """获取股票基本信息"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'pb_ratio': info.get('priceToBook', 'N/A'),
            'current_price': info.get('currentPrice', 'N/A'),
            '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
        }
    except Exception as e:
        return {'error': str(e)}

def get_historical_data(symbol: str, period: str = "1mo") -> pd.DataFrame:
    """
    获取历史价格数据
    
    Args:
        symbol: 股票代码 (如 AAPL, 0700.HK, 000001.SS)
        period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        return hist
    except Exception as e:
        print(f"获取历史数据失败: {e}")
        return pd.DataFrame()

def get_multiple_stocks(symbols: List[str]) -> Dict:
    """批量获取多只股票数据"""
    data = {}
    for symbol in symbols:
        data[symbol] = get_stock_info(symbol)
    return data

def format_stock_report(data: Dict) -> str:
    """格式化股票报告"""
    if 'error' in data:
        return f"❌ 获取失败: {data['error']}"
    
    lines = [
        f"\n{'='*60}",
        f"📊 {data.get('name', 'N/A')} ({data.get('symbol', 'N/A')})",
        f"{'='*60}",
        f"",
        f"行业: {data.get('sector', 'N/A')} / {data.get('industry', 'N/A')}",
        f"当前价格: {data.get('current_price', 'N/A')}",
        f"市值: {data.get('market_cap', 'N/A')}",
        f"",
        f"估值指标:",
        f"  PE: {data.get('pe_ratio', 'N/A')}",
        f"  PB: {data.get('pb_ratio', 'N/A')}",
        f"  股息率: {data.get('dividend_yield', 'N/A')}",
        f"",
        f"52周范围: {data.get('52_week_low', 'N/A')} - {data.get('52_week_high', 'N/A')}",
        f"{'='*60}",
    ]
    
    return "\n".join(lines)

# 常用股票代码示例
SAMPLE_STOCKS = {
    '美股': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'],
    '港股': ['0700.HK', '3690.HK', '1810.HK', '9988.HK'],
    'A股': ['000001.SS', '000002.SZ', '600519.SS'],  # 上证、深证后缀
}

if __name__ == "__main__":
    # 测试
    print("🔄 测试YFinance...")
    
    # 测试苹果股票
    aapl = get_stock_info('AAPL')
    print(format_stock_report(aapl))
    
    print("\n✅ YFinance 测试完成")
