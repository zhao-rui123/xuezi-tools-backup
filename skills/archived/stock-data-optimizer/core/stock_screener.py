#!/usr/bin/env python3
"""
股票筛选器 - Token 优化的股票筛选
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

import pandas as pd

from config.config import SELF_SELECTED_STOCKS, FILTER_CONDITIONS
from core.data_fetcher import DataFetcher
from core.token_optimizer import TokenOptimizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('stock-screener')


class StockScreener:
    """Token 优化的股票筛选器"""
    
    def __init__(self):
        self.fetcher = DataFetcher()
        self.optimizer = TokenOptimizer()
        self.self_selected = SELF_SELECTED_STOCKS
    
    def filter_by_conditions(self, stocks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据条件筛选股票
        0 Token 消耗（纯本地计算）
        """
        conditions = FILTER_CONDITIONS
        filtered = []
        
        for stock in stocks_data:
            # 检查 ROE
            if stock.get("roe", 0) < conditions["roe_min"]:
                continue
            
            # 检查 PE
            if stock.get("pe", 999) > conditions["pe_max"]:
                continue
            
            # 检查 PB
            if stock.get("pb", 999) > conditions["pb_max"]:
                continue
            
            filtered.append(stock)
        
        return filtered
    
    def get_self_selected_data(self) -> List[Dict[str, Any]]:
        """
        获取自选股数据（从缓存或实时）
        """
        results = []
        today = datetime.now().strftime("%Y%m%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        for stock in self.self_selected:
            code = stock["code"]
            
            # 获取日线数据
            df = self.fetcher.fetch_daily_prices(code, yesterday, today)
            if df is not None and len(df) > 0:
                latest = df.iloc[0]
                stock_data = {
                    "ts_code": code,
                    "name": stock["name"],
                    "industry": stock["industry"],
                    "close": latest.get("close", 0),
                    "change": latest.get("change", 0),
                    "pct_chg": latest.get("pct_chg", 0),
                    "vol": latest.get("vol", 0),
                    "amount": latest.get("amount", 0),
                }
                
                # 获取财务指标
                fin_df = self.fetcher.fetch_financial_indicators(code)
                if fin_df is not None and len(fin_df) > 0:
                    fin = fin_df.iloc[0]
                    stock_data["roe"] = fin.get("roe", 0)
                    stock_data["pe"] = fin.get("q_sales_yoy", 0)  # 使用替代字段
                    stock_data["pb"] = fin.get("bps", 0)
                
                results.append(stock_data)
        
        return results
    
    def screen_stocks(self, use_self_selected: bool = True) -> Dict[str, Any]:
        """
        筛选股票（方案 A：0 Token）
        """
        logger.info("开始筛选股票...")
        
        # 1. 获取数据
        if use_self_selected:
            stocks_data = self.get_self_selected_data()
        else:
            # 获取全市场数据（需要预计算）
            stocks_data = []
        
        logger.info(f"获取到 {len(stocks_data)} 只股票数据")
        
        # 2. 本地筛选（0 Token）
        filtered = self.filter_by_conditions(stocks_data)
        logger.info(f"筛选后剩余 {len(filtered)} 只股票")
        
        # 3. 返回结果
        return {
            "total": len(stocks_data),
            "filtered": len(filtered),
            "stocks": filtered,
            "conditions": FILTER_CONDITIONS,
            "timestamp": datetime.now().isoformat(),
        }
    
    def analyze_stocks(self, stocks_data: List[Dict[str, Any]]) -> str:
        """
        分析股票（方案 B：低 Token）
        返回压缩后的数据，供大模型分析
        """
        # 1. 筛选
        filtered = self.filter_by_conditions(stocks_data)
        
        # 2. 压缩数据
        compressed = self.optimizer.compress_for_analysis(filtered, "analysis")
        
        # 3. 估算 Token
        tokens = self.optimizer.estimate_tokens(compressed)
        
        logger.info(f"分析数据 Token 估算: {tokens}")
        
        return compressed
    
    def generate_prompt(self, compressed_data: str, analysis_type: str = "filter") -> str:
        """
        生成大模型提示词
        """
        if analysis_type == "filter":
            return f"""请根据以下股票数据进行筛选分析：

数据格式：代码,名称,收盘价,涨跌幅,PE,PB,ROE

{compressed_data}

筛选条件：
- ROE > 10%
- PE < 50
- PB < 10

请输出符合条件的股票，并给出推荐理由。"""
        
        elif analysis_type == "recommend":
            return f"""作为股票分析师，请分析以下股票：

{compressed_data}

请提供：
1. 每只股票的技术分析
2. 估值分析
3. 投资建议（买入/持有/卖出）
4. 风险提示"""
        
        return compressed_data


if __name__ == "__main__":
    screener = StockScreener()
    
    # 测试筛选
    print("=== 测试股票筛选（0 Token）===")
    result = screener.screen_stocks()
    print(f"\n总股票数: {result['total']}")
    print(f"筛选后: {result['filtered']}")
    print(f"\n筛选结果:")
    for stock in result['stocks']:
        print(f"  - {stock['name']} ({stock['ts_code']}): 收{stock['close']}, 涨{stock['pct_chg']:.2f}%")
    
    # 测试分析
    print("\n=== 测试股票分析（低 Token）===")
    compressed = screener.analyze_stocks(result['stocks'])
    print(f"\n压缩后数据:\n{compressed}")
