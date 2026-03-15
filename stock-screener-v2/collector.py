"""
股票数据采集模块
支持东财API和akshare
"""

import json
import time
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests
import pandas as pd
import akshare as ak

from config import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{config.LOG_DIR}/collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EastMoneyAPI:
    """东财API封装"""
    
    BASE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def _get_secid(self, stock_code: str) -> str:
        """
        获取secid参数
        沪市：1.股票代码
        深市：0.股票代码
        """
        # 根据代码规则判断市场
        if stock_code.startswith('6'):
            return f"1.{stock_code}"
        else:
            return f"0.{stock_code}"
    
    def get_kline_data(
        self,
        stock_code: str,
        period: str = "101",  # 101=日, 102=周, 103=月
        limit: int = 500
    ) -> Optional[pd.DataFrame]:
        """
        获取K线数据
        
        Args:
            stock_code: 股票代码
            period: 周期代码
            limit: 获取条数
        
        Returns:
            DataFrame包含日期、开盘、收盘、最高、最低、成交量、成交额
        """
        secid = self._get_secid(stock_code)
        
        params = {
            "secid": secid,
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": period,
            "fqt": "0",  # 不复权
            "end": "20500101",
            "lmt": str(limit),
            "cb": "jQuery"
        }
        
        try:
            for attempt in range(config.EASTMONEY_RETRY_TIMES):
                try:
                    response = self.session.get(
                        self.BASE_URL,
                        params=params,
                        timeout=config.EASTMONEY_API_TIMEOUT
                    )
                    response.raise_for_status()
                    
                    # 解析JSONP响应
                    text = response.text
                    # 提取JSON部分
                    start = text.find('(') + 1
                    end = text.rfind(')')
                    json_str = text[start:end]
                    data = json.loads(json_str)
                    
                    if data.get('data') and data['data'].get('klines'):
                        return self._parse_klines(data['data']['klines'])
                    else:
                        logger.warning(f"股票 {stock_code} 无数据返回")
                        return None
                        
                except requests.RequestException as e:
                    if attempt < config.EASTMONEY_RETRY_TIMES - 1:
                        logger.warning(f"请求失败，重试 {attempt + 1}: {e}")
                        time.sleep(1)
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"获取股票 {stock_code} K线数据失败: {e}")
            return None
    
    def _parse_klines(self, klines: List[str]) -> pd.DataFrame:
        """解析K线数据"""
        data = []
        for line in klines:
            # 格式: 日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
            parts = line.split(',')
            data.append({
                'date': parts[0],
                'open': float(parts[1]),
                'close': float(parts[2]),
                'high': float(parts[3]),
                'low': float(parts[4]),
                'volume': float(parts[5]),
                'amount': float(parts[6]),
                'amplitude': float(parts[7]) if parts[7] else 0,
                'pct_change': float(parts[8]) if parts[8] else 0,
                'change': float(parts[9]) if parts[9] else 0,
                'turnover': float(parts[10]) if len(parts) > 10 and parts[10] else 0
            })
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        return df


class StockCollector:
    """股票数据采集器"""
    
    def __init__(self):
        self.eastmoney = EastMoneyAPI()
        self._stock_list_cache: Optional[pd.DataFrame] = None
        self._cache_time: Optional[datetime] = None
    
    def get_stock_list(self, refresh: bool = False) -> pd.DataFrame:
        """
        获取A股股票列表
        
        Args:
            refresh: 是否强制刷新缓存
        
        Returns:
            DataFrame包含股票代码、名称、市场等信息
        """
        # 检查缓存
        if not refresh and self._stock_list_cache is not None:
            cache_age = (datetime.now() - self._cache_time).total_seconds()
            if cache_age < config.STOCK_LIST_CACHE_TTL:
                return self._stock_list_cache
        
        try:
            # 使用akshare获取股票列表
            logger.info("正在获取A股股票列表...")
            
            # 获取上海和深圳股票
            sh_stocks = ak.stock_sh_a_spot_em()
            sz_stocks = ak.stock_sz_a_spot_em()
            
            # 合并
            all_stocks = pd.concat([sh_stocks, sz_stocks], ignore_index=True)
            
            # 选择需要的列
            df = all_stocks[['代码', '名称', '最新价', '涨跌幅']].copy()
            df.columns = ['code', 'name', 'price', 'change_pct']
            
            # 添加市场标识
            df['market'] = df['code'].apply(
                lambda x: 'SH' if x.startswith('6') else 'SZ'
            )
            
            # 过滤掉ST、*ST、退市股票
            df = df[~df['name'].str.contains('ST|退', na=False)]
            
            # 过滤掉价格异常的股票
            df = df[df['price'] > 0]
            
            # 更新缓存
            self._stock_list_cache = df
            self._cache_time = datetime.now()
            
            logger.info(f"成功获取 {len(df)} 只股票")
            return df
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_monthly_data(self, stock_code: str) -> Optional[pd.DataFrame]:
        """
        获取月线数据
        
        Args:
            stock_code: 股票代码
        
        Returns:
            DataFrame包含月线数据
        """
        logger.debug(f"获取股票 {stock_code} 月线数据")
        return self.eastmoney.get_kline_data(
            stock_code,
            period="103",  # 月线
            limit=config.MONTHLY_DATA_MONTHS
        )
    
    def get_weekly_data(self, stock_code: str) -> Optional[pd.DataFrame]:
        """
        获取周线数据
        
        Args:
            stock_code: 股票代码
        
        Returns:
            DataFrame包含周线数据
        """
        logger.debug(f"获取股票 {stock_code} 周线数据")
        return self.eastmoney.get_kline_data(
            stock_code,
            period="102",  # 周线
            limit=config.WEEKLY_DATA_WEEKS
        )
    
    def get_daily_data(self, stock_code: str, days: int = 120) -> Optional[pd.DataFrame]:
        """
        获取日线数据
        
        Args:
            stock_code: 股票代码
            days: 获取天数
        
        Returns:
            DataFrame包含日线数据
        """
        logger.debug(f"获取股票 {stock_code} 日线数据")
        return self.eastmoney.get_kline_data(
            stock_code,
            period="101",  # 日线
            limit=days
        )
    
    def get_stock_data_batch(
        self,
        stock_codes: List[str],
        data_type: str = "monthly"
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        批量获取股票数据
        
        Args:
            stock_codes: 股票代码列表
            data_type: 数据类型 (monthly/weekly/daily)
        
        Returns:
            字典，key为股票代码，value为DataFrame
        """
        results = {}
        total = len(stock_codes)
        
        for i, code in enumerate(stock_codes, 1):
            if data_type == "monthly":
                df = self.get_monthly_data(code)
            elif data_type == "weekly":
                df = self.get_weekly_data(code)
            else:
                df = self.get_daily_data(code)
            
            results[code] = df
            
            # 每10只股票输出一次进度
            if i % 10 == 0 or i == total:
                logger.info(f"数据获取进度: {i}/{total} ({i/total*100:.1f}%)")
            
            # 添加延迟，避免请求过快
            time.sleep(0.1)
        
        return results


# 全局采集器实例
collector = StockCollector()


if __name__ == "__main__":
    # 测试代码
    collector = StockCollector()
    
    # 获取股票列表
    stocks = collector.get_stock_list()
    print(f"获取到 {len(stocks)} 只股票")
    print(stocks.head(10))
    
    # 测试获取单只股票数据
    test_code = "000001"  # 平安银行
    monthly_data = collector.get_monthly_data(test_code)
    if monthly_data is not None:
        print(f"\n{test_code} 月线数据:")
        print(monthly_data.tail())