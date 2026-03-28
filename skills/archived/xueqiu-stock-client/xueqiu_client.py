#!/usr/bin/env python3
"""
雪球 API 客户端
支持实时行情、资金流向、社区热度等数据
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import httpx
except ImportError:
    print("请先安装依赖：pip install httpx")
    raise

# 自选股配置（不带前缀）
WATCHLIST_XUEQIU = {
    "002460": "赣锋锂业",
    "002738": "中矿资源",
    "000792": "盐湖股份",
    "002240": "盛新锂能",
    "000725": "京东方 A",
    "600707": "彩虹股份",
    "688981": "中芯国际"
}


class XueqiuClient:
    """雪球 API 客户端"""
    
    BASE_URL = "https://stock.xueqiu.com"
    
    def __init__(self, cookie: str = None):
        self.cookie = cookie or self._get_cookie_from_config()
        if not self.cookie:
            raise ValueError("请提供雪球 Cookie")
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Cookie": self.cookie,
            "Accept": "application/json",
            "Origin": "https://xueqiu.com",
            "Referer": "https://xueqiu.com/"
        }
        self._client = None
    
    def _get_cookie_from_config(self) -> Optional[str]:
        """从配置文件读取 Cookie"""
        config_path = Path("~/.openclaw/workspace/config/xueqiu.ini").expanduser()
        if config_path.exists():
            content = config_path.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if line.strip().startswith('cookie'):
                    return line.split('=', 1)[1].strip()
        return None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(headers=self.headers, timeout=30.0, follow_redirects=True)
        return self._client
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """获取单只股票实时行情"""
        try:
            client = await self._get_client()
            
            # 雪球股票代码格式：SH600519, SZ002460
            if not symbol.startswith(('SH', 'SZ')):
                if symbol.startswith('6') or symbol.startswith('688'):
                    symbol = f"SH{symbol}"
                else:
                    symbol = f"SZ{symbol}"
            
            url = f"{self.BASE_URL}/v5/stock/realtime/quotec.json"
            params = {"symbol": symbol}
            
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # 雪球 API 返回 {"data": [...]}
                if isinstance(data, dict) and "data" in data:
                    data_list = data["data"]
                    if isinstance(data_list, list) and len(data_list) > 0:
                        quote = data_list[0]
                    else:
                        return None
                else:
                    return None
                
                return {
                    "symbol": symbol,
                    "name": WATCHLIST_XUEQIU.get(symbol.replace("SH", "").replace("SZ", ""), quote.get("name", "")),
                    "current": float(quote.get("current", 0)),
                    "change": float(quote.get("chg", 0)),
                    "percent": float(quote.get("percent", 0)),
                    "high": float(quote.get("high", 0)),
                    "low": float(quote.get("low", 0)),
                    "open": float(quote.get("open", 0)),
                    "prev_close": float(quote.get("prev_close", 0)),
                    "volume": float(quote.get("volume", 0)),
                    "amount": float(quote.get("amount", 0)),
                    "market_capital": float(quote.get("market_capital", 0)),
                    "pe_ttm": float(quote.get("pe_ttm", 0)) if quote.get("pe_ttm") else None,
                    "pb": float(quote.get("pb", 0)) if quote.get("pb") else None,
                    "source": "xueqiu",
                    "fetch_time": datetime.now().isoformat()
                }
            
            return None
        except Exception as e:
            print(f"❌ 获取 {symbol} 行情失败：{e}")
            return None
    
    async def get_quotes(self, symbols: List[str]) -> List[Dict]:
        """获取多只股票实时行情"""
        results = []
        for symbol in symbols:
            quote = await self.get_quote(symbol)
            if quote:
                results.append(quote)
        return results


async def test_client():
    """测试客户端"""
    print("🧪 测试雪球 API 客户端\n")
    
    async with XueqiuClient() as client:
        print("📊 获取自选股行情...")
        quotes = await client.get_quotes(list(WATCHLIST_XUEQIU.keys()))
        
        if quotes:
            print(f"\n✅ 成功获取 {len(quotes)} 只股票行情")
            print("\n📈 自选股行情:")
            print("=" * 60)
            
            total_change = 0
            for q in quotes:
                code = q["symbol"].replace("SH", "").replace("SZ", "")
                name = WATCHLIST_XUEQIU.get(code, q.get("name", code))
                emoji = "🔴" if q["percent"] > 0 else "🟢" if q["percent"] < 0 else "⚪"
                print(f"{name:12s} {q['current']:8.2f} {emoji} {q['percent']:+.2f}%  ({code})")
                total_change += q["percent"]
            
            print("=" * 60)
            print(f"📊 平均涨跌幅：{total_change/len(quotes):+.2f}%")
            print(f"📡 数据源：雪球 API")
        else:
            print("❌ 获取失败")


if __name__ == "__main__":
    asyncio.run(test_client())
