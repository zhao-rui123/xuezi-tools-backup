"""
数据获取服务 - 东方财富API + akshare
"""
import requests
import akshare as ak
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from config import settings, PERIOD_MAP
from utils.logger import logger
from utils.stock_utils import StockUtils


class DataService:
    """数据服务"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取A股股票列表"""
        try:
            logger.info("获取A股股票列表...")
            # 使用akshare获取所有A股
            df = ak.stock_zh_a_spot_em()
            
            # 筛选需要的列
            columns = ['代码', '名称', '最新价', '涨跌幅', '成交量', '成交额', '所属行业']
            df = df[columns].copy()
            
            # 重命名列
            df.columns = ['code', 'name', 'price', 'change_pct', 'volume', 'amount', 'industry']
            
            # 过滤无效数据
            df = df[df['code'].str.match(r'^\d{6}$')]
            df = df.dropna(subset=['code', 'name'])
            
            logger.info(f"获取到 {len(df)} 只股票")
            return df
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_kline_eastmoney(self, code: str, period: str = "daily", 
                           limit: int = 100) -> pd.DataFrame:
        """
        从东方财富获取K线数据
        
        Args:
            code: 股票代码
            period: 周期 daily/weekly/monthly
            limit: 获取条数
        """
        try:
            em_code = StockUtils.get_eastmoney_code(code)
            secid = em_code.replace('.', '_')
            
            url = settings.EASTMONEY_KLINE_API
            params = {
                'secid': secid,
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': PERIOD_MAP.get(period, '101'),
                'fqt': '1',  # 前复权
                'end': datetime.now().strftime('%Y%m%d'),
                'lmt': limit
            }
            
            response = self.session.get(url, params=params, timeout=30)
            data = response.json()
            
            if 'data' not in data or not data['data'] or 'klines' not in data['data']:
                logger.warning(f"获取K线数据为空: {code} {period}")
                return pd.DataFrame()
            
            klines = data['data']['klines']
            
            # 解析K线数据
            records = []
            for line in klines:
                parts = line.split(',')
                if len(parts) >= 6:
                    records.append({
                        'date': parts[0],
                        'open': float(parts[1]),
                        'close': float(parts[2]),
                        'high': float(parts[3]),
                        'low': float(parts[4]),
                        'volume': float(parts[5]),
                        'amount': float(parts[6]) if len(parts) > 6 else 0
                    })
            
            df = pd.DataFrame(records)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"获取K线数据失败 {code} {period}: {e}")
            return pd.DataFrame()
    
    def get_kline_akshare(self, code: str, period: str = "daily",
                         start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        从akshare获取K线数据
        
        Args:
            code: 股票代码
            period: 周期 daily/weekly/monthly
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
        """
        try:
            ak_code = StockUtils.get_akshare_code(code)
            
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            # 映射周期
            period_map = {
                'daily': 'daily',
                'weekly': 'weekly', 
                'monthly': 'monthly'
            }
            ak_period = period_map.get(period, 'daily')
            
            # 获取K线数据
            df = ak.stock_zh_a_hist(
                symbol=code,
                period=ak_period,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )
            
            if df.empty:
                return df
            
            # 标准化列名
            df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 
                         'amount', 'amplitude', 'change_pct', 'change_amount', 'turnover']
            df['date'] = pd.to_datetime(df['date'])
            
            return df
            
        except Exception as e:
            logger.error(f"akshare获取K线失败 {code} {period}: {e}")
            return pd.DataFrame()
    
    def get_kline(self, code: str, period: str = "daily", 
                  limit: int = 100) -> pd.DataFrame:
        """
        获取K线数据（优先使用东方财富，失败则用akshare）
        """
        # 先尝试东方财富
        df = self.get_kline_eastmoney(code, period, limit)
        
        if df.empty or len(df) < 30:
            # 失败则使用akshare
            logger.info(f"尝试使用akshare获取 {code} {period}")
            df = self.get_kline_akshare(code, period)
        
        return df
    
    def get_stock_basic_info(self, code: str) -> Dict:
        """获取股票基本信息"""
        try:
            df = self.get_stock_list()
            stock_info = df[df['code'] == StockUtils.normalize_code(code)]
            
            if stock_info.empty:
                return {}
            
            info = stock_info.iloc[0].to_dict()
            return {
                'code': info.get('code', ''),
                'name': info.get('name', ''),
                'price': float(info.get('price', 0)) if pd.notna(info.get('price')) else 0,
                'change_pct': float(info.get('change_pct', 0)) if pd.notna(info.get('change_pct')) else 0,
                'industry': info.get('industry', '')
            }
        except Exception as e:
            logger.error(f"获取股票基本信息失败 {code}: {e}")
            return {}
    
    def get_batch_klines(self, codes: List[str], period: str = "daily") -> Dict[str, pd.DataFrame]:
        """批量获取K线数据"""
        results = {}
        total = len(codes)
        
        for i, code in enumerate(codes, 1):
            try:
                df = self.get_kline(code, period)
                if not df.empty:
                    results[code] = df
                
                if i % 50 == 0:
                    logger.info(f"已获取 {i}/{total} 只股票的 {period} K线数据")
                    
            except Exception as e:
                logger.error(f"批量获取失败 {code}: {e}")
        
        logger.info(f"成功获取 {len(results)}/{total} 只股票的 {period} K线数据")
        return results


# 全局数据服务实例
data_service = DataService()