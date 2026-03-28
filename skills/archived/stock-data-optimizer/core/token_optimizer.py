#!/usr/bin/env python3
"""
Token 优化器 - 压缩数据以减少 Token 消耗
"""

import json
from typing import Dict, List, Any, Optional
import pandas as pd

from config.config import TOKEN_OPTIMIZATION


class TokenOptimizer:
    """Token 优化器"""
    
    def __init__(self):
        self.config = TOKEN_OPTIMIZATION
    
    def compress_stock_data(self, stock_data: Dict[str, Any]) -> str:
        """
        压缩单只股票数据为 CSV 格式
        输入: {"code": "002460.SZ", "name": "赣锋锂业", "close": 69.5, ...}
        输出: "002460.SZ,赣锋锂业,69.5,-0.95,25.3,3.2,15.2"
        """
        fields = [
            stock_data.get("ts_code", ""),
            stock_data.get("name", ""),
            str(round(stock_data.get("close", 0), self.config["decimal_places"])),
            str(round(stock_data.get("pct_chg", 0), self.config["decimal_places"])),
            str(round(stock_data.get("pe", 0), self.config["decimal_places"])),
            str(round(stock_data.get("pb", 0), self.config["decimal_places"])),
            str(round(stock_data.get("roe", 0), self.config["decimal_places"])),
        ]
        return ",".join(fields)
    
    def compress_batch(self, stocks_data: List[Dict[str, Any]]) -> str:
        """
        压缩多只股票数据
        格式: CSV 头部 + 数据行
        """
        if not stocks_data:
            return ""
        
        # CSV 头部
        header = "code,name,close,change,pe,pb,roe"
        
        # 数据行
        rows = [self.compress_stock_data(stock) for stock in stocks_data]
        
        return header + "\n" + "\n".join(rows)
    
    def compress_for_analysis(self, stocks_data: List[Dict[str, Any]], 
                              analysis_type: str = "filter") -> str:
        """
        根据分析类型压缩数据
        
        analysis_type:
        - "filter": 筛选（精简字段）
        - "analysis": 分析（中等字段）
        - "deep": 深度分析（完整字段）
        """
        if analysis_type == "filter":
            # 精简字段：代码、名称、关键指标
            return self.compress_batch(stocks_data)
        
        elif analysis_type == "analysis":
            # 中等字段：添加趋势、成交量
            header = "code,name,close,change,pe,pb,roe,vol,amount,trend"
            rows = []
            for stock in stocks_data:
                row = [
                    stock.get("ts_code", ""),
                    stock.get("name", ""),
                    str(round(stock.get("close", 0), 2)),
                    str(round(stock.get("pct_chg", 0), 2)),
                    str(round(stock.get("pe", 0), 2)),
                    str(round(stock.get("pb", 0), 2)),
                    str(round(stock.get("roe", 0), 2)),
                    str(round(stock.get("vol", 0) / 10000, 2)),  # 万手
                    str(round(stock.get("amount", 0) / 100000000, 2)),  # 亿
                    stock.get("trend", "neutral"),
                ]
                rows.append(",".join(row))
            return header + "\n" + "\n".join(rows)
        
        else:  # deep
            # 完整字段：JSON 格式
            return json.dumps(stocks_data, ensure_ascii=False, indent=0)
    
    def estimate_tokens(self, data: str) -> int:
        """
        估算 Token 数量
        粗略估计：英文约 1 token/4 字符，中文约 1 token/1.5 字符
        """
        # 简化估算：总字符数 / 3
        return len(data) // 3
    
    def batch_split(self, stocks_data: List[Dict[str, Any]], 
                    max_tokens: int = 3000) -> List[List[Dict[str, Any]]]:
        """
        将股票列表分批，每批不超过最大 Token 数
        """
        batches = []
        current_batch = []
        current_tokens = 0
        
        for stock in stocks_data:
            # 估算单只股票 Token 数
            stock_str = self.compress_stock_data(stock)
            stock_tokens = self.estimate_tokens(stock_str)
            
            # 如果当前批次已满，开始新批次
            if current_tokens + stock_tokens > max_tokens and current_batch:
                batches.append(current_batch)
                current_batch = [stock]
                current_tokens = stock_tokens
            else:
                current_batch.append(stock)
                current_tokens += stock_tokens
        
        # 添加最后一批
        if current_batch:
            batches.append(current_batch)
        
        return batches


if __name__ == "__main__":
    optimizer = TokenOptimizer()
    
    # 测试数据
    test_data = [
        {"ts_code": "002460.SZ", "name": "赣锋锂业", "close": 69.5, "pct_chg": -0.95, "pe": 25.3, "pb": 3.2, "roe": 15.2},
        {"ts_code": "002738.SZ", "name": "中矿资源", "close": 76.65, "pct_chg": -2.16, "pe": 18.5, "pb": 2.8, "roe": 12.5},
    ]
    
    # 测试压缩
    compressed = optimizer.compress_batch(test_data)
    print("压缩后数据:")
    print(compressed)
    print(f"\n原始 Token 估算: {optimizer.estimate_tokens(str(test_data))}")
    print(f"压缩后 Token 估算: {optimizer.estimate_tokens(compressed)}")
    print(f"压缩率: {(1 - optimizer.estimate_tokens(compressed) / optimizer.estimate_tokens(str(test_data))) * 100:.1f}%")
