#!/usr/bin/env python3
"""
Tushare Pro 股票数据源
替代新浪财经，提供专业金融数据
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import tushare as ts
    import pandas as pd
except ImportError:
    print("请先安装依赖: pip install tushare pandas")
    raise


class TushareStockClient:
    """Tushare 股票数据客户端"""
    
    def __init__(self, token: str = None):
        """
        初始化客户端
        
        Args:
            token: Tushare Pro Token，如未提供则从环境变量或配置文件读取
        """
        self.token = token or self._get_token_from_config()
        if not self.token:
            raise ValueError("请提供 Tushare Token 或配置环境变量 TUSHARE_TOKEN")
        
        self.pro = ts.pro_api(self.token)
        self._cache = {}
        
    def _get_token_from_config(self) -> Optional[str]:
        """从配置文件或环境变量获取 Token"""
        # 优先环境变量
        token = os.environ.get("TUSHARE_TOKEN")
        if token:
            return token
        
        # 尝试从配置文件读取
        config_path = Path("~/.openclaw/workspace/config/tushare.ini").expanduser()
        if config_path.exists():
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)
            return config.get("tushare", "token", fallback=None)
        
        return None
    
    def get_realtime_quote(self, ts_code: str) -> Optional[Dict]:
        """
        获取单只股票实时行情
        
        Args:
            ts_code: 股票代码，如 "002460.SZ"
        
        Returns:
            股票实时行情数据
        """
        try:
            # 使用每日行情接口（Tushare实时行情需要积分）
            today = datetime.now().strftime("%Y%m%d")
            df = self.pro.daily(ts_code=ts_code, start_date=today, end_date=today)
            
            if df is None or df.empty:
                return None
            
            row = df.iloc[0]
            return {
                "ts_code": row["ts_code"],
                "trade_date": row["trade_date"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "pre_close": float(row["pre_close"]),
                "change": float(row["change"]),
                "pct_change": float(row["pct_chg"]),
                "volume": int(row["vol"]),
                "amount": float(row["amount"]),
                "source": "tushare",
                "fetch_time": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ 获取 {ts_code} 行情失败: {e}")
            return None
    
    def get_realtime_quotes(self, ts_codes: List[str]) -> List[Dict]:
        """
        获取多只股票实时行情
        
        Args:
            ts_codes: 股票代码列表
        
        Returns:
            股票行情列表
        """
        results = []
        for code in ts_codes:
            quote = self.get_realtime_quote(code)
            if quote:
                results.append(quote)
        return results
    
    def get_daily(self, ts_code: str, start_date: str = None, end_date: str = None, 
                  limit: int = 30) -> Optional[pd.DataFrame]:
        """
        获取日K线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            limit: 返回条数限制
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                start = datetime.strptime(end_date, "%Y%m%d") - timedelta(days=limit)
                start_date = start.strftime("%Y%m%d")
            
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            if df is not None and not df.empty:
                df = df.sort_values("trade_date", ascending=True)
                df.columns = ["ts_code", "trade_date", "open", "high", "low", "close", 
                             "pre_close", "change", "pct_change", "volume", "amount"]
            
            return df
        except Exception as e:
            print(f"❌ 获取 {ts_code} 日K线失败: {e}")
            return None
    
    def get_stock_basic(self, ts_code: str = None, name: str = None) -> Optional[Dict]:
        """
        获取股票基本信息
        
        Args:
            ts_code: 股票代码
            name: 股票名称
        
        Returns:
            股票基本信息
        """
        try:
            if ts_code:
                df = self.pro.stock_basic(ts_code=ts_code)
            elif name:
                df = self.pro.stock_basic(name=name)
            else:
                return None
            
            if df is None or df.empty:
                return None
            
            row = df.iloc[0]
            return {
                "ts_code": row["ts_code"],
                "symbol": row["symbol"],
                "name": row["name"],
                "area": row["area"],
                "industry": row["industry"],
                "market": row["market"],
                "list_date": row["list_date"]
            }
        except Exception as e:
            print(f"❌ 获取股票基本信息失败: {e}")
            return None
    
    def get_financial(self, ts_code: str, report_type: str = "income") -> Optional[pd.DataFrame]:
        """
        获取财务报表数据
        
        Args:
            ts_code: 股票代码
            report_type: 报表类型 (income=利润表, balance=资产负债表, cashflow=现金流量表)
        
        Returns:
            财务数据 DataFrame
        """
        try:
            if report_type == "income":
                df = self.pro.income(ts_code=ts_code, limit=4)
            elif report_type == "balance":
                df = self.pro.balancesheet(ts_code=ts_code, limit=4)
            elif report_type == "cashflow":
                df = self.pro.cashflow(ts_code=ts_code, limit=4)
            else:
                return None
            
            return df
        except Exception as e:
            print(f"❌ 获取财务报表失败: {e}")
            return None
    
    def get_key_indicators(self, ts_codes: List[str]) -> List[Dict]:
        """
        获取关键财务指标
        
        Args:
            ts_codes: 股票代码列表
        
        Returns:
            财务指标列表
        """
        results = []
        for code in ts_codes:
            try:
                # 获取最新财务指标
                df = self.pro.fina_indicator(ts_code=code, limit=1)
                if df is not None and not df.empty:
                    row = df.iloc[0]
                    results.append({
                        "ts_code": code,
                        "roe": float(row.get("roe", 0)),
                        "grossprofit_margin": float(row.get("grossprofit_margin", 0)),
                        "netprofit_margin": float(row.get("netprofit_margin", 0)),
                        "debt_to_assets": float(row.get("debt_to_assets", 0)),
                        "eps": float(row.get("eps", 0)),
                        "bps": float(row.get("bps", 0)),
                        "end_date": row.get("end_date", "")
                    })
            except Exception as e:
                print(f"❌ 获取 {code} 财务指标失败: {e}")
        
        return results
    
    def convert_to_sina_format(self, tushare_data: Dict) -> Dict:
        """
        将 Tushare 数据格式转换为新浪财经格式（兼容现有代码）
        
        Args:
            tushare_data: Tushare 返回的数据
        
        Returns:
            新浪财经格式的数据
        """
        return {
            "symbol": tushare_data["ts_code"].split(".")[0],
            "name": tushare_data.get("name", ""),
            "price": tushare_data.get("close", 0),
            "change": tushare_data.get("change", 0),
            "pct_change": tushare_data.get("pct_change", 0),
            "volume": tushare_data.get("volume", 0),
            "amount": tushare_data.get("amount", 0),
            "high": tushare_data.get("high", 0),
            "low": tushare_data.get("low", 0),
            "prev_close": tushare_data.get("pre_close", 0),
            "source": "tushare"
        }


# 自选股配置
WATCHLIST = {
    "002460.SZ": "赣锋锂业",
    "002738.SZ": "中矿资源", 
    "000792.SZ": "盐湖股份",
    "002240.SZ": "盛新锂能",
    "000725.SZ": "京东方A",
    "600707.SH": "彩虹股份",
    "688981.SH": "中芯国际"
}


def get_watchlist_quotes(client: TushareStockClient = None) -> List[Dict]:
    """
    获取自选股行情（兼容现有系统）
    
    Returns:
        自选股行情列表
    """
    if client is None:
        client = TushareStockClient()
    
    quotes = client.get_realtime_quotes(list(WATCHLIST.keys()))
    
    # 添加股票名称
    for quote in quotes:
        code = quote["ts_code"]
        quote["name"] = WATCHLIST.get(code, "Unknown")
    
    return quotes


if __name__ == "__main__":
    # 测试代码
    print("🧪 测试 Tushare 客户端...")
    
    try:
        client = TushareStockClient()
        print("✅ 客户端初始化成功")
        
        # 测试获取单只股票
        print("\n📊 测试获取赣锋锂业行情:")
        quote = client.get_realtime_quote("002460.SZ")
        if quote:
            print(f"  股票: {quote}")
        
        # 测试获取自选股
        print("\n📈 测试获取自选股列表:")
        quotes = get_watchlist_quotes(client)
        for q in quotes:
            print(f"  {q.get('name', 'Unknown')}: {q.get('close', 'N/A')}")
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("\n💡 提示: 请配置 TUSHARE_TOKEN 环境变量或创建配置文件")
