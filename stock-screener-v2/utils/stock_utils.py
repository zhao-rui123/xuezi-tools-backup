"""
股票工具函数
"""
import re
from typing import Optional, Tuple


class StockUtils:
    """股票工具类"""
    
    @staticmethod
    def normalize_code(code: str) -> str:
        """标准化股票代码"""
        code = code.strip()
        # 去除后缀
        code = re.sub(r'\.(SH|SZ|BJ)$', '', code, flags=re.IGNORECASE)
        code = re.sub(r'\.(ss|sz)$', '', code, flags=re.IGNORECASE)
        return code.zfill(6)
    
    @staticmethod
    def get_market(code: str) -> str:
        """判断股票所属市场"""
        code = StockUtils.normalize_code(code)
        
        # 沪市
        if code.startswith('6') or code.startswith('5'):
            return 'sh'
        # 深市
        elif code.startswith('0') or code.startswith('3') or code.startswith('1') or code.startswith('2'):
            return 'sz'
        # 北交所
        elif code.startswith('8') or code.startswith('4'):
            return 'bj'
        else:
            return 'sh'
    
    @staticmethod
    def get_eastmoney_code(code: str) -> str:
        """获取东方财富格式的股票代码"""
        code = StockUtils.normalize_code(code)
        market = StockUtils.get_market(code)
        
        # 东方财富格式：市场代码.股票代码
        market_map = {
            'sh': '1',
            'sz': '0',
            'bj': '0'
        }
        return f"{market_map.get(market, '1')}.{code}"
    
    @staticmethod
    def get_akshare_code(code: str) -> str:
        """获取akshare格式的股票代码"""
        code = StockUtils.normalize_code(code)
        market = StockUtils.get_market(code)
        return f"{code}.{market.upper()}"
    
    @staticmethod
    def is_valid_code(code: str) -> bool:
        """验证股票代码是否有效"""
        code = StockUtils.normalize_code(code)
        return bool(re.match(r'^\d{6}$', code))
    
    @staticmethod
    def format_stock_name(name: str) -> str:
        """格式化股票名称"""
        if not name:
            return ""
        # 去除ST标记中的空格
        name = re.sub(r'\s*ST\s*', 'ST', name)
        return name.strip()
    
    @staticmethod
    def get_industry_display(industry: str) -> str:
        """获取行业显示名称"""
        if not industry:
            return "其他"
        return industry.strip()


# 便捷函数
def normalize_code(code: str) -> str:
    return StockUtils.normalize_code(code)


def get_market(code: str) -> str:
    return StockUtils.get_market(code)


def get_eastmoney_code(code: str) -> str:
    return StockUtils.get_eastmoney_code(code)