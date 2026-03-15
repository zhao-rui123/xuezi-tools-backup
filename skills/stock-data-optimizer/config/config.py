#!/usr/bin/env python3
"""
股票数据优化器 - 配置文件
"""

import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"

# 确保目录存在
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Tushare API 配置
TUSHARE_CONFIG = {
    "token": "6d8f34a35c3b6a3c80e529f4ebcf11e707ff71c066062d5c4619eb35e5d9",
    "http_url": "http://lianghua.nanyangqiankun.top",
    "rate_limit": 0.1,  # 每秒调用间隔
}

# 缓存配置
CACHE_CONFIG = {
    "stocks_basic": {
        "file": CACHE_DIR / "stocks_basic.json",
        "update_time": "00:00",  # 每日更新时间
        "ttl_hours": 24,
    },
    "daily_prices": {
        "file": CACHE_DIR / "daily_prices.json",
        "update_time": "15:35",  # 收盘后更新
        "ttl_hours": 24,
    },
    "financial_indicators": {
        "file": CACHE_DIR / "financial_indicators.json",
        "update_time": "00:00",
        "ttl_hours": 24 * 7,  # 每周更新
    },
    "precomputed_metrics": {
        "file": CACHE_DIR / "precomputed_metrics.json",
        "update_time": "15:40",  # 收盘后计算
        "ttl_hours": 24,
    }
}

# 自选股列表
SELF_SELECTED_STOCKS = [
    {"code": "002460.SZ", "name": "赣锋锂业", "market": "A股", "industry": "锂电池"},
    {"code": "002738.SZ", "name": "中矿资源", "market": "A股", "industry": "锂矿/资源"},
    {"code": "000792.SZ", "name": "盐湖股份", "market": "A股", "industry": "盐湖提锂"},
    {"code": "002240.SZ", "name": "盛新锂能", "market": "A股", "industry": "锂电池材料"},
    {"code": "000822.SZ", "name": "山东海化", "market": "A股", "industry": "化工/纯碱"},
    {"code": "600707.SH", "name": "彩虹股份", "market": "A股", "industry": "面板/显示"},
]

# 筛选条件
FILTER_CONDITIONS = {
    "roe_min": 10,           # ROE 最低 10%
    "pe_max": 50,            # PE 最高 50
    "pb_max": 10,            # PB 最高 10
    "market_cap_min": 50,    # 市值最低 50亿
}

# Token 优化配置
TOKEN_OPTIMIZATION = {
    "max_stocks_per_request": 10,  # 每批最大股票数
    "compress_fields": True,       # 启用字段压缩
    "decimal_places": 2,           # 小数位数
    "include_history_days": 5,     # 包含历史天数
}
