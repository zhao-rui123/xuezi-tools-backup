"""
Stock Suite Core - 核心模块
"""

from .data_fetcher import (
    fetch_sina_quotes,
    fetch_xueqiu_quotes,
    fetch_tencent_kline,
    fetch_monthly_kline,
    fetch_market_index,
    get_stock_list,
    get_realtime_quote,
    get_stock_kline,
    get_stock_monthly,
)

from .technical_analysis import (
    calculate_ma,
    calculate_macd,
    calculate_kdj,
    calculate_rsi,
    calculate_boll,
    calculate_all_indicators,
    get_latest_indicators,
    get_all_signals,
    check_macd_golden_cross,
    check_kdj_golden_cross,
    check_ma_alignment,
    check_volume_increase,
)

from .pattern_recognition import (
    analyze_patterns,
    analyze_all_patterns,
    format_pattern_report,
    PatternResult,
)

from .support_resistance import (
    analyze_support_resistance,
    calculate_deviation_from_ma,
    get_trend_direction,
)

from .stock_classifier import (
    classify_stock,
    get_valuation_method,
    get_analysis_framework,
    StockTypeResult,
)

from .valuation import (
    analyze_pb_roe,
    analyze_peg,
    analyze_comprehensive,
    analyze_valuation,
    format_valuation_report,
    ValuationResult,
)

from .alert_engine import (
    run_alert_check,
    check_alerts,
    format_alert_report,
    AlertResult,
)

from .earnings_calendar import (
    check_upcoming_earnings,
    check_recent_announcements,
    format_earnings_calendar,
    format_recent_announcements,
    EarningsEvent,
    Announcement,
)

from .deep_analysis import (
    deep_analyze_stock,
    deep_analyze,
    format_deep_analysis,
    DeepAnalysisResult,
)

from .daily_report import (
    generate_daily_report,
    send_to_feishu,
)

__version__ = "3.0.0"

__all__ = [
    'fetch_sina_quotes',
    'fetch_xueqiu_quotes',
    'fetch_tencent_kline',
    'fetch_monthly_kline',
    'fetch_market_index',
    'get_stock_list',
    'get_realtime_quote',
    'get_stock_kline',
    'get_stock_monthly',
    'calculate_ma',
    'calculate_macd',
    'calculate_kdj',
    'calculate_rsi',
    'calculate_boll',
    'calculate_all_indicators',
    'get_latest_indicators',
    'get_all_signals',
    'analyze_patterns',
    'analyze_all_patterns',
    'analyze_support_resistance',
    'classify_stock',
    'analyze_valuation',
    'run_alert_check',
    'check_alerts',
    'check_upcoming_earnings',
    'check_recent_announcements',
    'deep_analyze_stock',
    'deep_analyze',
    'generate_daily_report',
    'send_to_feishu',
]
