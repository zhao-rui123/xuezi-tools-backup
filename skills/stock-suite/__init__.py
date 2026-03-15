"""
Stock Suite - 股票分析工具 v3.0 (整合版)
整合了 stock-analysis-pro 和 stock-screener 的全部功能

功能:
- 实时行情监控（A股+港股）
- 技术指标分析（MA、MACD、KDJ、RSI、布林带）
- 技术形态识别（杯柄、双底、头肩底等）
- 支撑阻力分析
- 估值分析（PB-ROE、PEG、综合估值）
- 深度分析（盈利能力、成长性、财务健康、估值分位）
- 股票分类（周期股/成长股/价值股）
- 实时预警（价格突破、均线突破、异常波动）
- 财报日历
- 统一监控面板

作者: 雪子助手
版本: 3.0.0
"""

from .core import (
    generate_daily_report,
    send_to_feishu,
    deep_analyze,
    analyze_patterns,
    analyze_valuation,
    check_alerts,
    check_upcoming_earnings,
    check_recent_announcements,
    get_stock_list,
    fetch_sina_quotes,
    fetch_market_index,
    classify_stock,
)

__version__ = "3.0.0"
__author__ = "雪子助手"

__all__ = [
    'generate_daily_report',
    'send_to_feishu',
    'deep_analyze',
    'analyze_patterns',
    'analyze_valuation',
    'check_alerts',
    'check_upcoming_earnings',
    'check_recent_announcements',
    'get_stock_list',
    'fetch_sina_quotes',
    'fetch_market_index',
    'classify_stock',
]
