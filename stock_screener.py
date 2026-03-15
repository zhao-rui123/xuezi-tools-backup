"""
股票筛选服务
实现MACD、KDJ、均线、成交量筛选逻辑
"""
import asyncio
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from database.models import get_db, ScreenRecord, Stock, StockBasic
from config import settings


class StockScreener:
    """股票筛选器"""
    
    def __init__(self):
        self.progress = {"total": 0, "current": 0, "status": "idle"}
        self.stock_list_cache = None
        self.cache_time = None
    
    def get_progress(self) -> Dict[str, Any]:
        """获取筛选进度"""
        return self.progress
    
    async def get_all_stocks(self) -> List[Dict[str, str]]:
        """获取所有A股股票列表"""
        # 检查缓存
        if self.stock_list_cache is not None:
            cache_age = datetime.now() - self.cache_time if self.cache_time else timedelta(hours=1)
            if cache_age < timedelta(hours=1):
                print(f"使用缓存股票列表: {len(self.stock_list_cache)}只")
                return self.stock_list_cache
        
        try:
            print("正在获取A股股票列表...")
            # 使用akshare获取股票列表
            df = ak.stock_zh_a_spot_em()
            stocks = []
            for _, row in df.iterrows():
                stocks.append({
                    "code": row["代码"],
                    "name": row["名称"],
                    "industry": row.get("行业", ""),
                    "market_cap": row.get("总市值", 0)
                })
            
            print(f"获取到 {len(stocks)} 只股票")
            
            # 如果获取数量异常（少于3000只），使用备用数据源
            if len(stocks) < 3000:
                print(f"警告: 获取股票数量异常({len(stocks)}只)，尝试备用数据源")
                # 备用: 使用股票列表接口
                try:
                    df2 = ak.stock_info_a_code_name()
                    stocks = []
                    for _, row in df2.iterrows():
                        stocks.append({
                            "code": row["code"],
                            "name": row["name"],
                            "industry": "",
                            "market_cap": 0
                        })
                    print(f"备用数据源获取到 {len(stocks)} 只股票")
                except Exception as e2:
                    print(f"备用数据源也失败: {e2}")
            
            self.stock_list_cache = stocks
            self.cache_time = datetime.now()
            return stocks
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return []
    
    async def get_stock_basic(self, stock_code: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            df = ak.stock_individual_info_em(symbol=stock_code)
            if df.empty:
                return {"code": stock_code, "name": ""}
            
            info = {}
            for _, row in df.iterrows():
                info[row["item"]] = row["value"]
            
            return {
                "code": stock_code,
                "name": info.get("股票简称", ""),
                "industry": info.get("行业", ""),
                "list_date": info.get("上市时间", ""),
                "total_cap": info.get("总市值", 0),
                "float_cap": info.get("流通市值", 0)
            }
        except Exception as e:
            print(f"获取股票基本信息失败 {stock_code}: {e}")
            return {"code": stock_code, "name": ""}
    
    async def get_monthly_kline(self, stock_code: str, months: int = 24) -> pd.DataFrame:
        """获取月K线数据"""
        try:
            # 使用akshare获取月K线
            df = ak.stock_zh_a_hist(symbol=stock_code, period="monthly", 
                                    start_date="20200101", adjust="qfq")
            if df.empty:
                return pd.DataFrame()
            
            df = df.rename(columns={
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount"
            })
            
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            
            # 计算MACD
            df = self._calculate_macd(df)
            
            # 计算KDJ
            df = self._calculate_kdj(df)
            
            # 计算均线
            df = self._calculate_ma(df)
            
            return df
        except Exception as e:
            print(f"获取月K线失败 {stock_code}: {e}")
            return pd.DataFrame()
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算MACD指标"""
        exp1 = df["close"].ewm(span=settings.MACD_FAST, adjust=False).mean()
        exp2 = df["close"].ewm(span=settings.MACD_SLOW, adjust=False).mean()
        df["macd_dif"] = exp1 - exp2
        df["macd_dea"] = df["macd_dif"].ewm(span=settings.MACD_SIGNAL, adjust=False).mean()
        df["macd_bar"] = 2 * (df["macd_dif"] - df["macd_dea"])
        return df
    
    def _calculate_kdj(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算KDJ指标"""
        low_list = df["low"].rolling(window=settings.KDJ_N, min_periods=1).min()
        high_list = df["high"].rolling(window=settings.KDJ_N, min_periods=1).max()
        rsv = (df["close"] - low_list) / (high_list - low_list) * 100
        
        df["kdj_k"] = rsv.ewm(com=settings.KDJ_M1 - 1, adjust=False).mean()
        df["kdj_d"] = df["kdj_k"].ewm(com=settings.KDJ_M2 - 1, adjust=False).mean()
        df["kdj_j"] = 3 * df["kdj_k"] - 2 * df["kdj_d"]
        return df
    
    def _calculate_ma(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算均线"""
        df["ma5"] = df["close"].rolling(window=5).mean()
        df["ma10"] = df["close"].rolling(window=10).mean()
        df["ma20"] = df["close"].rolling(window=20).mean()
        df["ma60"] = df["close"].rolling(window=60).mean()
        return df
    
    def _detect_macd_golden_cross(self, df: pd.DataFrame, recent_months: int = 2) -> tuple:
        """
        检测MACD金叉（只保留0轴上金叉或0轴金叉）
        返回: (是否金叉, 金叉日期)
        """
        if len(df) < 3:
            return False, None
        
        df = df.copy()
        df["macd_golden"] = (df["macd_dif"] > df["macd_dea"]) & (df["macd_dif"].shift(1) <= df["macd_dea"].shift(1))
        
        golden_crosses = df[df["macd_golden"]]
        if golden_crosses.empty:
            return False, None
        
        # 检查最近几个月内的金叉
        for idx in range(len(golden_crosses) - 1, -1, -1):
            cross = golden_crosses.iloc[idx]
            cross_date = cross["date"]
            
            # 计算日期差
            months_diff = (datetime.now() - cross_date).days / 30
            if months_diff > recent_months:
                continue
            
            # 只保留0轴上金叉或0轴金叉
            dif_value = cross["macd_dif"]
            dea_value = cross["macd_dea"]
            
            # 0轴上金叉: DIF>0 且 DEA>0
            # 0轴金叉: 金叉时DIF或DEA在0轴附近（-0.5到0.5之间）
            if dif_value > 0 and dea_value > 0:
                # 0轴上金叉
                return True, cross_date.strftime("%Y-%m-%d")
            elif abs(dif_value) < 0.5 or abs(dea_value) < 0.5:
                # 0轴金叉（穿越0轴）
                return True, cross_date.strftime("%Y-%m-%d")
        
        return False, None
    
    def _detect_kdj_golden_cross(self, df: pd.DataFrame, recent_months: int = 2) -> tuple:
        """
        检测KDJ低位金叉（K<30, D<30）
        返回: (是否金叉, 金叉日期)
        """
        if len(df) < 3:
            return False, None
        
        df = df.copy()
        df["kdj_golden"] = (df["kdj_k"] > df["kdj_d"]) & (df["kdj_k"].shift(1) <= df["kdj_d"].shift(1))
        
        golden_crosses = df[df["kdj_golden"]]
        if golden_crosses.empty:
            return False, None
        
        # 检查最近几个月内的金叉
        for idx in range(len(golden_crosses) - 1, -1, -1):
            cross = golden_crosses.iloc[idx]
            cross_date = cross["date"]
            
            # 计算日期差
            months_diff = (datetime.now() - cross_date).days / 30
            if months_diff > recent_months:
                continue
            
            # 低位金叉: K<30 且 D<30
            k_value = cross["kdj_k"]
            d_value = cross["kdj_d"]
            
            if k_value < 30 and d_value < 30:
                return True, cross_date.strftime("%Y-%m-%d")
        
        return False, None
    
    def _check_ma_bullish(self, df: pd.DataFrame) -> bool:
        """检查均线是否多头排列"""
        if len(df) < 5:
            return False
        
        latest = df.iloc[-1]
        # 5月 > 10月 > 20月
        return latest["ma5"] > latest["ma10"] > latest["ma20"]
    
    def _check_volume_increase(self, df: pd.DataFrame) -> bool:
        """检查成交量是否放大"""
        if len(df) < 6:
            return False
        
        # 最近3个月平均成交量 > 前3个月平均成交量
        recent_volume = df["volume"].tail(3).mean()
        previous_volume = df["volume"].tail(6).head(3).mean()
        
        return recent_volume > previous_volume * 1.2  # 放大20%
    
    def _determine_grade(self, macd_cross: bool, kdj_cross: bool, 
                         ma_bullish: bool, volume_increase: bool) -> str:
        """
        确定股票等级（去掉均线多头排列要求）
        A级: MACD + KDJ 双金叉
        B级: 只有MACD金叉
        C级: 只有KDJ金叉
        """
        if macd_cross and kdj_cross:
            return "A"
        elif macd_cross:
            return "B"
        elif kdj_cross:
            return "C"
        else:
            return None
    
    async def screen_stock(self, stock_code: str, stock_name: str = "", 
                          recent_months: int = 2) -> Optional[Dict[str, Any]]:
        """筛选单只股票"""
        try:
            df = await self.get_monthly_kline(stock_code)
            if df.empty or len(df) < 20:
                return None
            
            # 检测MACD金叉
            macd_cross, macd_date = self._detect_macd_golden_cross(df, recent_months)
            
            # 检测KDJ金叉
            kdj_cross, kdj_date = self._detect_kdj_golden_cross(df, recent_months)
            
            # 检查均线多头排列（保留但不作为筛选条件）
            ma_bullish = self._check_ma_bullish(df)
            
            # 检查成交量放大（保留但不作为筛选条件）
            volume_increase = self._check_volume_increase(df)
            
            # 确定等级（去掉均线和成交量要求）
            grade = self._determine_grade(macd_cross, kdj_cross, ma_bullish, volume_increase)
            
            if grade is None:
                return None
            
            latest = df.iloc[-1]
            
            return {
                "code": stock_code,
                "name": stock_name,
                "grade": grade,
                "macd_golden_cross": macd_cross,
                "macd_golden_cross_date": macd_date,
                "kdj_golden_cross": kdj_cross,
                "kdj_golden_cross_date": kdj_date,
                "ma_bullish": ma_bullish,
                "volume_increase": volume_increase,
                "current_price": latest["close"],
                "ma5": round(latest["ma5"], 2),
                "ma10": round(latest["ma10"], 2),
                "ma20": round(latest["ma20"], 2),
                "macd_dif": round(latest["macd_dif"], 4),
                "macd_dea": round(latest["macd_dea"], 4),
                "kdj_k": round(latest["kdj_k"], 2),
                "kdj_d": round(latest["kdj_d"], 2),
                "kdj_j": round(latest["kdj_j"], 2),
                "screen_date": datetime.now().strftime("%Y-%m-%d")
            }
        except Exception as e:
            print(f"筛选股票失败 {stock_code}: {e}")
            return None
    
    async def screen_all_stocks(self, grade: Optional[str] = None,
                                check_monthly: bool = True,
                                recent_months: int = 2) -> List[Dict[str, Any]]:
        """筛选所有股票"""
        stocks = await self.get_all_stocks()
        results = []
        
        self.progress["total"] = len(stocks)
        self.progress["current"] = 0
        self.progress["status"] = "running"
        
        # 分批处理，避免内存溢出
        batch_size = 50
        for i in range(0, len(stocks), batch_size):
            batch = stocks[i:i+batch_size]
            tasks = []
            
            for stock in batch:
                task = self.screen_stock(stock["code"], stock["name"], recent_months)
                tasks.append(task)
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, dict):
                    if grade is None or result["grade"] == grade:
                        results.append(result)
            
            self.progress["current"] = min(i + batch_size, len(stocks))
            
            # 短暂休眠，避免请求过快
            await asyncio.sleep(0.5)
        
        self.progress["status"] = "completed"
        
        # 按等级排序
        grade_order = {"A": 0, "B": 1, "C": 2, "D": 3}
        results.sort(key=lambda x: grade_order.get(x["grade"], 99))
        
        # 保存筛选记录
        await self._save_screen_records(results)
        
        return results
    
    async def _save_screen_records(self, results: List[Dict[str, Any]]):
        """保存筛选记录到数据库"""
        try:
            db = next(get_db())
            screen_date = datetime.now().strftime("%Y-%m-%d")
            screen_month = datetime.now().strftime("%Y-%m")
            
            for item in results:
                record = ScreenRecord(
                    stock_code=item["code"],
                    stock_name=item["name"],
                    grade=item["grade"],
                    macd_golden_cross=item["macd_golden_cross"],
                    macd_golden_cross_date=item.get("macd_golden_cross_date"),
                    kdj_golden_cross=item["kdj_golden_cross"],
                    kdj_golden_cross_date=item.get("kdj_golden_cross_date"),
                    ma_bullish=item["ma_bullish"],
                    volume_increase=item["volume_increase"],
                    macd_data={
                        "dif": item.get("macd_dif"),
                        "dea": item.get("macd_dea")
                    },
                    kdj_data={
                        "k": item.get("kdj_k"),
                        "d": item.get("kdj_d"),
                        "j": item.get("kdj_j")
                    },
                    ma_data={
                        "ma5": item.get("ma5"),
                        "ma10": item.get("ma10"),
                        "ma20": item.get("ma20")
                    },
                    screen_date=screen_date,
                    screen_month=screen_month
                )
                db.add(record)
            
            db.commit()
        except Exception as e:
            print(f"保存筛选记录失败: {e}")
    
    async def get_screen_records(self, start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取筛选历史记录"""
        try:
            db = next(get_db())
            query = db.query(ScreenRecord)
            
            if start_date:
                query = query.filter(ScreenRecord.screen_date >= start_date)
            if end_date:
                query = query.filter(ScreenRecord.screen_date <= end_date)
            
            records = query.order_by(ScreenRecord.created_at.desc()).all()
            
            return [{
                "id": r.id,
                "code": r.stock_code,
                "name": r.stock_name,
                "grade": r.grade,
                "macd_golden_cross": r.macd_golden_cross,
                "kdj_golden_cross": r.kdj_golden_cross,
                "screen_date": r.screen_date
            } for r in records]
        except Exception as e:
            print(f"获取筛选记录失败: {e}")
            return []
    
    async def get_stock_screen_history(self, stock_code: str) -> List[Dict[str, Any]]:
        """获取某只股票的历史筛选记录"""
        try:
            db = next(get_db())
            records = db.query(ScreenRecord).filter(
                ScreenRecord.stock_code == stock_code
            ).order_by(ScreenRecord.created_at.desc()).all()
            
            return [{
                "id": r.id,
                "grade": r.grade,
                "macd_golden_cross": r.macd_golden_cross,
                "kdj_golden_cross": r.kdj_golden_cross,
                "screen_date": r.screen_date
            } for r in records]
        except Exception as e:
            print(f"获取股票历史记录失败: {e}")
            return []
    
    async def get_market_status(self) -> Dict[str, Any]:
        """获取市场状态"""
        try:
            # 获取上证指数
            sh_index = ak.stock_zh_index_spot()
            sh_data = sh_index[sh_index["代码"] == "000001"]
            
            if not sh_data.empty:
                return {
                    "market_open": True,
                    "sh_index": {
                        "price": sh_data.iloc[0]["最新价"],
                        "change": sh_data.iloc[0]["涨跌幅"]
                    }
                }
            return {"market_open": False}
        except Exception as e:
            return {"market_open": False, "error": str(e)}
    
    async def update_all_data(self):
        """更新所有数据"""
        # 更新股票列表
        await self.get_all_stocks()
        print("股票列表更新完成")
