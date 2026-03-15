#!/usr/bin/env python3
"""
股票数据获取器 - 从 Tushare 获取数据并缓存
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

import tushare as ts
import pandas as pd

from config.config import TUSHARE_CONFIG, CACHE_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('stock-data-optimizer')


class DataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        self.pro = ts.pro_api(TUSHARE_CONFIG["token"])
        self.pro._DataApi__token = TUSHARE_CONFIG["token"]
        self.pro._DataApi__http_url = TUSHARE_CONFIG["http_url"]
        self.rate_limit = TUSHARE_CONFIG["rate_limit"]
        self.last_call_time = 0
    
    def _rate_limit(self):
        """速率限制"""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_call_time = time.time()
    
    def _call_api(self, func_name: str, **kwargs) -> Optional[pd.DataFrame]:
        """调用 API 并处理速率限制"""
        self._rate_limit()
        try:
            func = getattr(self.pro, func_name)
            df = func(**kwargs)
            return df
        except Exception as e:
            logger.error(f"API调用失败 {func_name}: {e}")
            return None
    
    def fetch_stock_basic(self, force_update: bool = False) -> Optional[pd.DataFrame]:
        """获取股票基础信息"""
        cache_file = CACHE_CONFIG["stocks_basic"]["file"]
        
        # 检查缓存
        if not force_update and cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cache_time = datetime.fromisoformat(data.get("updated", "2000-01-01"))
                if datetime.now() - cache_time < timedelta(hours=24):
                    logger.info("使用缓存的股票基础信息")
                    return pd.DataFrame(data["data"])
        
        # 从 API 获取
        logger.info("从 Tushare 获取股票基础信息...")
        df = self._call_api("stock_basic", exchange='', list_status='L')
        
        if df is not None:
            # 保存到缓存
            cache_data = {
                "updated": datetime.now().isoformat(),
                "count": len(df),
                "data": df.to_dict('records')
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            logger.info(f"已缓存 {len(df)} 只股票基础信息")
        
        return df
    
    def fetch_daily_prices(self, ts_code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """获取日线行情"""
        return self._call_api("daily", ts_code=ts_code, start_date=start_date, end_date=end_date)
    
    def fetch_financial_indicators(self, ts_code: str) -> Optional[pd.DataFrame]:
        """获取财务指标"""
        return self._call_api("fina_indicator", ts_code=ts_code)
    
    def fetch_batch_daily(self, ts_codes: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """批量获取日线数据"""
        results = {}
        for code in ts_codes:
            df = self.fetch_daily_prices(code, start_date, end_date)
            if df is not None:
                results[code] = df
        return results
    
    def update_all_cache(self) -> Dict[str, Any]:
        """更新所有缓存"""
        results = {
            "stocks_basic": False,
            "daily_prices": False,
            "errors": []
        }
        
        # 1. 更新股票基础信息
        try:
            df = self.fetch_stock_basic(force_update=True)
            if df is not None:
                results["stocks_basic"] = True
                results["stocks_count"] = len(df)
        except Exception as e:
            results["errors"].append(f"stocks_basic: {e}")
        
        return results


if __name__ == "__main__":
    fetcher = DataFetcher()
    
    # 测试获取股票基础信息
    print("测试获取股票基础信息...")
    df = fetcher.fetch_stock_basic()
    if df is not None:
        print(f"✅ 成功获取 {len(df)} 只股票")
        print(df.head())
    else:
        print("❌ 获取失败")
