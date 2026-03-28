#!/usr/bin/env python3
"""
多数据源股票客户端
优先使用免费数据源，Tushare作为备选
支持：新浪财经(免费) + 东方财富(免费) + Tushare(付费/积分)
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

try:
    import httpx
    import pandas as pd
except ImportError:
    print("请先安装依赖: pip install httpx pandas")
    raise

# 自选股配置
WATCHLIST = {
    "002460": {"name": "赣锋锂业", "full_name": "江西赣锋锂业集团股份有限公司"},
    "002738": {"name": "中矿资源", "full_name": "中矿资源集团股份有限公司"},
    "000792": {"name": "盐湖股份", "full_name": "青海盐湖工业股份有限公司"},
    "002240": {"name": "盛新锂能", "full_name": "盛新锂能集团股份有限公司"},
    "000725": {"name": "京东方A", "full_name": "京东方科技集团股份有限公司"},
    "600707": {"name": "彩虹股份", "full_name": "彩虹显示器件股份有限公司"},
    "688981": {"name": "中芯国际", "full_name": "中芯国际集成电路制造有限公司"}
}


class SinaDataSource:
    """新浪财经数据源 - 免费"""
    
    BASE_URL = "https://hq.sinajs.cn"
    
    @staticmethod
    def format_code(code: str) -> str:
        """转换为新浪格式"""
        code = code.replace(".SZ", "").replace(".SH", "")
        if code.startswith("6") or code.startswith("688"):
            return f"sh{code}"
        else:
            return f"sz{code}"
    
    async def get_quotes(self, codes: List[str]) -> List[Dict]:
        """获取行情数据"""
        formatted_codes = [self.format_code(c) for c in codes]
        url = f"{self.BASE_URL}/list={','.join(formatted_codes)}"
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.encoding = 'gbk'
                
                results = []
                lines = response.text.strip().split('\n')
                
                for line in lines:
                    if '=' in line:
                        parts = line.split('=')
                        code_raw = parts[0].split('_')[-1]
                        data_str = parts[1].strip().strip('";')
                        
                        if data_str:
                            data = data_str.split(',')
                            if len(data) >= 33:
                                code = code_raw.replace('sh', '').replace('sz', '')
                                stock_info = WATCHLIST.get(code, {})
                                
                                results.append({
                                    "code": code,
                                    "name": data[0],
                                    "price": float(data[3]),
                                    "change": float(data[3]) - float(data[2]),
                                    "pct_change": round((float(data[3]) - float(data[2])) / float(data[2]) * 100, 2),
                                    "volume": int(int(data[8]) / 100),
                                    "amount": round(float(data[9]) / 10000, 2),
                                    "high": float(data[4]),
                                    "low": float(data[5]),
                                    "open": float(data[1]),
                                    "prev_close": float(data[2]),
                                    "source": "sina",
                                    "fetch_time": datetime.now().isoformat()
                                })
                
                return results
        except Exception as e:
            print(f"❌ 新浪数据源失败: {e}")
            return []


class EastMoneyDataSource:
    """东方财富数据源 - 免费"""
    
    BASE_URL = "https://push2.eastmoney.com/api"
    
    @staticmethod
    def format_code(code: str) -> str:
        """转换为东财格式"""
        code = code.replace(".SZ", "").replace(".SH", "")
        if code.startswith("6"):
            return f"1.{code}"
        elif code.startswith("688"):
            return f"1.{code}"
        else:
            return f"0.{code}"
    
    async def get_quotes(self, codes: List[str]) -> List[Dict]:
        """获取行情数据"""
        formatted_codes = [self.format_code(c) for c in codes]
        codes_str = ",".join(formatted_codes)
        
        url = f"{self.BASE_URL}/qt/stock/get"
        params = {
            "secid": codes_str,
            "fields": "f43,f44,f45,f46,f47,f48,f57,f58,f60,f170"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                results = []
                
                # 东财API一次只能查一只，需要循环
                for code in formatted_codes:
                    params["secid"] = code
                    response = await client.get(url, params=params)
                    data = response.json()
                    
                    if data.get("data"):
                        d = data["data"]
                        code_clean = code.replace("0.", "").replace("1.", "")
                        
                        # 东财数据字段特殊处理
                        price = d.get("f43", 0) / 100 if d.get("f43") else 0
                        prev_close = d.get("f60", 0) / 100 if d.get("f60") else 0
                        change = d.get("f170", 0) / 100 if d.get("f170") else 0
                        
                        results.append({
                            "code": code_clean,
                            "name": d.get("f58", ""),
                            "price": price,
                            "change": change,
                            "pct_change": round(change / prev_close * 100, 2) if prev_close else 0,
                            "volume": d.get("f47", 0),
                            "amount": d.get("f48", 0) / 10000 if d.get("f48") else 0,
                            "high": d.get("f44", 0) / 100 if d.get("f44") else 0,
                            "low": d.get("f45", 0) / 100 if d.get("f45") else 0,
                            "open": d.get("f46", 0) / 100 if d.get("f46") else 0,
                            "prev_close": prev_close,
                            "source": "eastmoney",
                            "fetch_time": datetime.now().isoformat()
                        })
                
                return results
        except Exception as e:
            print(f"❌ 东方财富数据源失败: {e}")
            return []


class MultiSourceStockClient:
    """多数据源股票客户端"""
    
    def __init__(self, preferred_source: str = "sina"):
        """
        初始化客户端
        
        Args:
            preferred_source: 优先数据源 (sina/eastmoney/tushare)
        """
        self.preferred_source = preferred_source
        self.datasources = {
            "sina": SinaDataSource(),
            "eastmoney": EastMoneyDataSource()
        }
        
        # 尝试初始化Tushare（如果有token）
        try:
            from .tushare_client import TushareStockClient
            token = os.environ.get("TUSHARE_TOKEN")
            if token:
                self.datasources["tushare"] = TushareStockClient(token)
                print("✅ Tushare数据源已加载")
        except:
            pass
    
    async def get_quotes(self, codes: List[str] = None, retry: bool = True) -> List[Dict]:
        """
        获取行情数据（自动切换数据源）
        
        Args:
            codes: 股票代码列表，默认使用自选股
            retry: 失败时是否尝试其他数据源
        
        Returns:
            行情数据列表
        """
        if codes is None:
            codes = list(WATCHLIST.keys())
        
        # 优先使用指定数据源
        datasource = self.datasources.get(self.preferred_source)
        if datasource:
            results = await datasource.get_quotes(codes)
            if results:
                return results
        
        # 失败时尝试其他数据源
        if retry:
            print(f"⚠️ {self.preferred_source} 数据源失败，尝试备用数据源...")
            for name, ds in self.datasources.items():
                if name != self.preferred_source:
                    results = await ds.get_quotes(codes)
                    if results:
                        print(f"✅ 使用 {name} 数据源成功")
                        return results
        
        print("❌ 所有数据源均失败")
        return []
    
    def get_watchlist(self) -> Dict:
        """获取自选股列表"""
        return WATCHLIST
    
    def format_report(self, quotes: List[Dict]) -> str:
        """格式化行情报告"""
        if not quotes:
            return "❌ 未获取到行情数据"
        
        lines = ["📈 自选股行情", "=" * 50]
        
        total_change = 0
        up_count = 0
        down_count = 0
        
        for q in quotes:
            symbol = q["code"]
            info = WATCHLIST.get(symbol, {})
            name = info.get("name", q.get("name", symbol))
            
            price = q.get("price", 0)
            change = q.get("change", 0)
            pct = q.get("pct_change", 0)
            
            total_change += pct
            if pct > 0:
                up_count += 1
                emoji = "🔴"
            elif pct < 0:
                down_count += 1
                emoji = "🟢"
            else:
                emoji = "⚪"
            
            pct_str = f"{emoji} {pct:+.2f}%"
            lines.append(f"{name:8s} {price:8.2f} {pct_str:12s} ({symbol})")
        
        lines.append("-" * 50)
        lines.append(f"📊 统计: 涨 {up_count} 只, 跌 {down_count} 只")
        lines.append(f"📊 平均涨跌幅: {total_change/len(quotes):+.2f}%")
        lines.append(f"📡 数据源: {quotes[0].get('source', 'unknown')}")
        
        return "\n".join(lines)


async def test_client():
    """测试客户端"""
    print("🧪 测试多数据源股票客户端\n")
    
    client = MultiSourceStockClient(preferred_source="sina")
    
    # 测试获取行情
    print("📊 获取自选股行情...")
    quotes = await client.get_quotes()
    
    if quotes:
        print(f"\n✅ 成功获取 {len(quotes)} 只股票行情")
        print(f"📡 数据源: {quotes[0].get('source', 'unknown')}")
        
        # 打印详细报告
        print("\n" + client.format_report(quotes))
    else:
        print("❌ 获取失败")


if __name__ == "__main__":
    asyncio.run(test_client())
