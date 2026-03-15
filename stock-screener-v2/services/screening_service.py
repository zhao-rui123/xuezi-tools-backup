"""
选股筛选服务 - 月线/周线双模式
"""
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import settings, GRADE_A, GRADE_B, GRADE_C
from services.data_service import data_service
from services.indicator_service import indicator_service
from utils.data_cache import cache
from utils.logger import logger
from utils.stock_utils import StockUtils


class StockGrade:
    """股票评级结果"""
    
    def __init__(self, code: str, name: str, grade: str, 
                 cycle: str,  # 'monthly' or 'weekly'
                 indicators: Dict = None,
                 stock_info: Dict = None):
        self.code = code
        self.name = name
        self.grade = grade
        self.cycle = cycle  # 'monthly' or 'weekly'
        self.indicators = indicators or {}
        self.stock_info = stock_info or {}
        self.screen_time = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'code': self.code,
            'name': self.name,
            'grade': self.grade,
            'cycle': self.cycle,
            'price': self.stock_info.get('price', 0),
            'change_pct': self.stock_info.get('change_pct', 0),
            'industry': self.stock_info.get('industry', ''),
            'indicators': self.indicators,
            'screen_time': self.screen_time
        }


class ScreeningService:
    """选股筛选服务"""
    
    def __init__(self):
        self.data_service = data_service
        self.indicator_service = indicator_service
    
    def analyze_stock(self, code: str, name: str = "", 
                     stock_info: Dict = None,
                     cycle: str = 'monthly') -> Optional[StockGrade]:
        """
        分析单只股票
        
        Args:
            code: 股票代码
            name: 股票名称
            stock_info: 股票基本信息
            cycle: 'monthly' or 'weekly'
        
        Returns:
            StockGrade: 评级结果
        """
        try:
            code = StockUtils.normalize_code(code)
            
            # 根据周期获取K线数据
            if cycle == 'monthly':
                kline_df = self.data_service.get_kline(code, 'monthly', 24)
            else:  # weekly
                kline_df = self.data_service.get_kline(code, 'weekly', 60)
            
            if kline_df.empty or len(kline_df) < 10:
                logger.debug(f"股票 {code} {cycle}数据不足，跳过")
                return None
            
            # 计算指标
            indicators = self.indicator_service.calculate_all_indicators(kline_df)
            
            # 判断成交量是否放大
            volume_increase = self._check_volume_increase(kline_df)
            
            # 判断评级
            grade = self._determine_grade(indicators, volume_increase)
            
            if grade is None:
                return None
            
            return StockGrade(
                code=code,
                name=name or stock_info.get('name', ''),
                grade=grade,
                cycle=cycle,
                indicators=indicators,
                stock_info=stock_info
            )
            
        except Exception as e:
            logger.error(f"分析股票 {code} 失败: {e}")
            return None
    
    def _check_volume_increase(self, df: pd.DataFrame) -> bool:
        """检测成交量是否放大"""
        if len(df) < 20:
            return False
        
        # 最近5天平均成交量
        recent_vol = df['volume'].tail(5).mean()
        # 之前20天平均成交量
        historical_vol = df['volume'].tail(20).head(15).mean()
        
        if historical_vol <= 0:
            return False
        
        # 成交量放大1.5倍以上
        return recent_vol / historical_vol >= 1.5
    
    def _determine_grade(self, indicators: Dict, volume_increase: bool) -> Optional[str]:
        """
        确定股票评级
        
        评级规则：
        - A级：MACD金叉 + KDJ金叉 + 成交量放大
        - B级：KDJ金叉 + 成交量放大（MACD未金叉）
        - C级：MACD金叉 + 成交量放大（KDJ未金叉）
        
        Args:
            indicators: 技术指标
            volume_increase: 是否成交量放大
        
        Returns:
            评级等级或None
        """
        if not volume_increase:
            return None
        
        macd_golden = indicators.get('macd_golden_cross', False)
        kdj_golden = indicators.get('kdj_golden_cross', False)
        
        # A级：MACD金叉 + KDJ金叉 + 成交量放大
        if macd_golden and kdj_golden:
            return GRADE_A
        
        # B级：KDJ金叉 + 成交量放大（MACD未金叉）
        if kdj_golden and not macd_golden:
            return GRADE_B
        
        # C级：MACD金叉 + 成交量放大（KDJ未金叉）
        if macd_golden and not kdj_golden:
            return GRADE_C
        
        return None
    
    def screen_stocks_by_cycle(self, cycle: str = 'monthly', max_stocks: int = None) -> Dict[str, List[StockGrade]]:
        """
        按周期筛选股票
        
        Args:
            cycle: 'monthly' or 'weekly'
            max_stocks: 最大筛选股票数
        
        Returns:
            按等级分类的股票列表
        """
        max_stocks = max_stocks or settings.MAX_STOCKS_PER_RUN
        
        cycle_name = '月线' if cycle == 'monthly' else '周线'
        logger.info(f"开始{cycle_name}选股，最大数量: {max_stocks}")
        
        # 获取股票列表
        stock_list = self.data_service.get_stock_list()
        if stock_list.empty:
            logger.error("获取股票列表失败")
            return {GRADE_A: [], GRADE_B: [], GRADE_C: []}
        
        # 限制数量
        stock_list = stock_list.head(max_stocks)
        
        # 筛选结果
        results = {GRADE_A: [], GRADE_B: [], GRADE_C: []}
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            
            for _, row in stock_list.iterrows():
                code = row['code']
                name = row['name']
                stock_info = row.to_dict()
                
                future = executor.submit(self.analyze_stock, code, name, stock_info, cycle)
                futures[future] = code
            
            # 收集结果
            completed = 0
            total = len(futures)
            
            for future in as_completed(futures):
                code = futures[future]
                completed += 1
                
                try:
                    result = future.result()
                    if result and result.grade:
                        results[result.grade].append(result)
                except Exception as e:
                    logger.error(f"处理股票 {code} 失败: {e}")
                
                if completed % 50 == 0:
                    logger.info(f"已处理 {completed}/{total} 只股票")
        
        logger.info(f"{cycle_name}筛选完成: A级 {len(results[GRADE_A])} 只, "
                   f"B级 {len(results[GRADE_B])} 只, C级 {len(results[GRADE_C])} 只")
        
        return results
    
    def screen_all(self, max_stocks: int = None) -> Dict[str, Dict[str, List[StockGrade]]]:
        """
        执行完整筛选（月线 + 周线）
        
        Returns:
            {'monthly': {A:[], B:[], C:[]}, 'weekly': {A:[], B:[], C:[]}}
        """
        logger.info("=" * 50)
        logger.info("开始执行完整选股筛选")
        logger.info("=" * 50)
        
        results = {
            'monthly': self.screen_stocks_by_cycle('monthly', max_stocks),
            'weekly': self.screen_stocks_by_cycle('weekly', max_stocks)
        }
        
        logger.info("=" * 50)
        logger.info("选股筛选全部完成")
        logger.info(f"月线: A级 {len(results['monthly'].get('A', []))} 只")
        logger.info(f"周线: A级 {len(results['weekly'].get('A', []))} 只")
        logger.info("=" * 50)
        
        return results
    
    def get_stock_detail(self, code: str) -> Optional[Dict]:
        """获取股票详情"""
        try:
            code = StockUtils.normalize_code(code)
            
            # 获取基本信息
            stock_info = self.data_service.get_stock_basic_info(code)
            
            # 获取各周期K线数据
            daily_df = self.data_service.get_kline(code, 'daily', 100)
            weekly_df = self.data_service.get_kline(code, 'weekly', 60)
            monthly_df = self.data_service.get_kline(code, 'monthly', 24)
            
            # 计算指标
            daily_indicators = self.indicator_service.calculate_all_indicators(daily_df) if not daily_df.empty else {}
            weekly_indicators = self.indicator_service.calculate_all_indicators(weekly_df) if not weekly_df.empty else {}
            monthly_indicators = self.indicator_service.calculate_all_indicators(monthly_df) if not monthly_df.empty else {}
            
            return {
                'code': code,
                'info': stock_info,
                'daily': daily_indicators,
                'weekly': weekly_indicators,
                'monthly': monthly_indicators
            }
            
        except Exception as e:
            logger.error(f"获取股票 {code} 详情失败: {e}")
            return None


# 全局实例
screening_service = ScreeningService()
