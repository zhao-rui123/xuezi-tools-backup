"""
股票评级模块
根据技术指标进行评级分类
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

from config import config
from indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


@dataclass
class StockRating:
    """股票评级结果"""
    code: str  # 股票代码
    name: str  # 股票名称
    period: str  # 周期 (monthly/weekly)
    rating: str  # 评级 (A/B/C/D)
    rating_desc: str  # 评级描述
    macd_golden_cross: bool  # MACD金叉
    kdj_golden_cross: bool  # KDJ金叉
    volume_expanded: bool  # 成交量放大
    volume_ratio: float  # 量比
    latest_price: float  # 最新价格
    latest_date: datetime  # 最新日期
    analysis_time: datetime  # 分析时间
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "code": self.code,
            "name": self.name,
            "period": self.period,
            "rating": self.rating,
            "rating_desc": self.rating_desc,
            "macd_golden_cross": self.macd_golden_cross,
            "kdj_golden_cross": self.kdj_golden_cross,
            "volume_expanded": self.volume_expanded,
            "volume_ratio": round(self.volume_ratio, 2),
            "latest_price": round(self.latest_price, 2),
            "latest_date": self.latest_date.strftime("%Y-%m-%d"),
            "analysis_time": self.analysis_time.strftime("%Y-%m-%d %H:%M:%S")
        }


class StockRater:
    """股票评级器"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def rate_stock(
        self,
        code: str,
        name: str,
        df: pd.DataFrame,
        period: str = "monthly"
    ) -> Optional[StockRating]:
        """
        对单只股票进行评级
        
        评级标准：
        A级：MACD金叉 + KDJ金叉 + 成交量放大
        B级：KDJ金叉 + 成交量放大
        C级：MACD金叉 + 成交量放大
        D级：不符合以上条件
        
        Args:
            code: 股票代码
            name: 股票名称
            df: 股票数据DataFrame
            period: 周期 (monthly/weekly)
        
        Returns:
            StockRating对象
        """
        try:
            # 分析技术指标
            analysis = self.indicators.analyze_stock(df, period)
            
            # 判断评级
            macd_cross = analysis.get("macd_golden_cross", False)
            kdj_cross = analysis.get("kdj_golden_cross", False)
            volume_exp = analysis.get("volume_expanded", False)
            
            # 评级逻辑
            if macd_cross and kdj_cross and volume_exp:
                rating = "A"
                rating_desc = config.RATING_LEVELS["A"]
            elif kdj_cross and volume_exp:
                rating = "B"
                rating_desc = config.RATING_LEVELS["B"]
            elif macd_cross and volume_exp:
                rating = "C"
                rating_desc = config.RATING_LEVELS["C"]
            else:
                rating = "D"
                rating_desc = config.RATING_LEVELS["D"]
            
            return StockRating(
                code=code,
                name=name,
                period=period,
                rating=rating,
                rating_desc=rating_desc,
                macd_golden_cross=macd_cross,
                kdj_golden_cross=kdj_cross,
                volume_expanded=volume_exp,
                volume_ratio=analysis.get("volume_ratio", 0),
                latest_price=analysis.get("latest_close", 0),
                latest_date=analysis.get("latest_date", datetime.now()),
                analysis_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"评级股票 {code} 失败: {e}")
            return None
    
    def rate_stocks_batch(
        self,
        stock_data: Dict[str, tuple],
        period: str = "monthly"
    ) -> List[StockRating]:
        """
        批量评级股票
        
        Args:
            stock_data: 字典，key为股票代码，value为(name, df)元组
            period: 周期
        
        Returns:
            StockRating列表
        """
        results = []
        total = len(stock_data)
        
        for i, (code, (name, df)) in enumerate(stock_data.items(), 1):
            if df is None or len(df) < 26:
                logger.warning(f"股票 {code} 数据不足，跳过")
                continue
            
            rating = self.rate_stock(code, name, df, period)
            if rating:
                results.append(rating)
            
            # 每10只输出一次进度
            if i % 10 == 0 or i == total:
                logger.info(f"评级进度 ({period}): {i}/{total} ({i/total*100:.1f}%)")
        
        return results
    
    def filter_by_rating(
        self,
        ratings: List[StockRating],
        min_rating: str = "A"
    ) -> List[StockRating]:
        """
        按评级筛选股票
        
        Args:
            ratings: 评级列表
            min_rating: 最低评级 (A/B/C/D)
        
        Returns:
            筛选后的评级列表
        """
        rating_order = {"A": 4, "B": 3, "C": 2, "D": 1}
        min_level = rating_order.get(min_rating, 4)
        
        filtered = [
            r for r in ratings
            if rating_order.get(r.rating, 0) >= min_level
        ]
        
        # 按评级排序（A在前）
        filtered.sort(key=lambda x: rating_order.get(x.rating, 0), reverse=True)
        
        return filtered
    
    def get_rating_summary(self, ratings: List[StockRating]) -> dict:
        """
        获取评级汇总统计
        
        Args:
            ratings: 评级列表
        
        Returns:
            汇总统计字典
        """
        if not ratings:
            return {
                "total": 0,
                "A_count": 0,
                "B_count": 0,
                "C_count": 0,
                "D_count": 0
            }
        
        total = len(ratings)
        a_count = sum(1 for r in ratings if r.rating == "A")
        b_count = sum(1 for r in ratings if r.rating == "B")
        c_count = sum(1 for r in ratings if r.rating == "C")
        d_count = sum(1 for r in ratings if r.rating == "D")
        
        return {
            "total": total,
            "A_count": a_count,
            "B_count": b_count,
            "C_count": c_count,
            "D_count": d_count,
            "A_ratio": round(a_count / total * 100, 2),
            "B_ratio": round(b_count / total * 100, 2),
            "C_ratio": round(c_count / total * 100, 2),
            "D_ratio": round(d_count / total * 100, 2)
        }


# 全局评级器实例
rater = StockRater()


if __name__ == "__main__":
    # 测试代码
    import sys
    sys.path.insert(0, '.')
    from collector import collector
    
    # 获取股票列表（只取前5只测试）
    stocks = collector.get_stock_list()
    test_stocks = stocks.head(5)
    
    print("测试月线评级:")
    for _, row in test_stocks.iterrows():
        code = row['code']
        name = row['name']
        
        df = collector.get_monthly_data(code)
        if df is not None:
            rating = rater.rate_stock(code, name, df, "monthly")
            if rating:
                print(f"{code} {name}: {rating.rating}级 - {rating.rating_desc}")
                print(f"  MACD金叉: {rating.macd_golden_cross}, KDJ金叉: {rating.kdj_golden_cross}, 放量: {rating.volume_expanded}")
