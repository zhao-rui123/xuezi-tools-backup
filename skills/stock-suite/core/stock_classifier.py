"""
股票分类器 - 周期股/成长股/价值股识别
"""

from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class StockTypeResult:
    """股票类型分析结果"""
    stock_type: str
    keywords: list
    analysis_framework: str
    valuation_method: str
    description: str

CYCLICAL_KEYWORDS = [
    '锂', '钴', '铜', '铝', '锌', '铅', '镍', '钢铁', '煤炭', '化工',
    '航运', '航空', '油气', '石油', '地产', '工程机械', '水泥', '玻璃',
    '造纸', '纺织', '化工', '氟化工', '磷化工', '电解液', '正极', '负极',
]

GROWTH_KEYWORDS = [
    '半导体', '芯片', '集成电路', '软件', '云计算', '大数据', '人工智能',
    '新能源', '光伏', '风电', '储能', '电池', '电动车', '自动驾驶',
    '生物医药', '医疗器械', '疫苗', '创新药', 'CRO', 'CMO',
    '消费电子', '5G', '通信', '物联网', '智能制造', '机器人',
]

VALUE_KEYWORDS = [
    '银行', '保险', '证券', '公用事业', '电力', '燃气', '水务',
    '白酒', '家电', '食品', '饮料', '医药商业', '高速公路', '机场',
    '港口', '铁路', '公交', '地产', '建筑', '建材',
]

CYCLICAL_INDUSTRIES = [
    '有色金属', '钢铁', '煤炭', '化工', '交通运输', '房地产',
    '工程机械', '建筑材料', '造纸印刷', '纺织服装',
]

GROWTH_INDUSTRIES = [
    '电子', '计算机', '通信', '医药生物', '电气设备', '国防军工',
    '汽车', '机械设备', '轻工制造',
]

VALUE_INDUSTRIES = [
    '银行', '非银金融', '公用事业', '交通运输', '房地产', '建筑装饰',
    '食品饮料', '家用电器', '医药商业',
]

def classify_stock(stock_code: str, stock_name: str = "", industry: str = "") -> StockTypeResult:
    """
    识别股票类型
    
    Args:
        stock_code: 股票代码
        stock_name: 股票名称
        industry: 所属行业
    
    Returns:
        StockTypeResult对象
    """
    name = stock_name.upper()
    industry_upper = industry.upper() if industry else ""
    
    for kw in CYCLICAL_KEYWORDS:
        if kw in name:
            return StockTypeResult(
                stock_type="周期股",
                keywords=[kw],
                analysis_framework="周期位置+供需分析",
                valuation_method="PB分位、EV/产能",
                description=f"识别到周期股特征关键词: {kw}"
            )
    
    for kw in GROWTH_KEYWORDS:
        if kw in name:
            return StockTypeResult(
                stock_type="成长股",
                keywords=[kw],
                analysis_framework="成长空间+PEG",
                valuation_method="PEG、PS、市值空间",
                description=f"识别到成长股特征关键词: {kw}"
            )
    
    for kw in VALUE_KEYWORDS:
        if kw in name:
            return StockTypeResult(
                stock_type="价值股",
                keywords=[kw],
                analysis_framework="ROE稳定性+股息率",
                valuation_method="PB-ROE、股息率",
                description=f"识别到价值股特征关键词: {kw}"
            )
    
    if industry_upper:
        for ind in CYCLICAL_INDUSTRIES:
            if ind in industry_upper:
                return StockTypeResult(
                    stock_type="周期股",
                    keywords=[],
                    analysis_framework="周期位置+供需分析",
                    valuation_method="PB分位、EV/产能",
                    description=f"根据行业分类为周期股: {industry}"
                )
        
        for ind in GROWTH_INDUSTRIES:
            if ind in industry_upper:
                return StockTypeResult(
                    stock_type="成长股",
                    keywords=[],
                    analysis_framework="成长空间+PEG",
                    valuation_method="PEG、PS、市值空间",
                    description=f"根据行业分类为成长股: {industry}"
                )
        
        for ind in VALUE_INDUSTRIES:
            if ind in industry_upper:
                return StockTypeResult(
                    stock_type="价值股",
                    keywords=[],
                    analysis_framework="ROE稳定性+股息率",
                    valuation_method="PB-ROE、股息率",
                    description=f"根据行业分类为价值股: {industry}"
                )
    
    return StockTypeResult(
        stock_type="成长股",
        keywords=[],
        analysis_framework="综合分析",
        valuation_method="PE/PB/PEG",
        description="未识别到明显特征，默认按成长股分析"
    )

def get_valuation_method(stock_type: str) -> str:
    """获取估值方法"""
    methods = {
        "周期股": "PB分位、资源量估值、重置成本",
        "成长股": "PEG、PS、市值空间、渗透率",
        "价值股": "PB-ROE、股息率、PE分位",
    }
    return methods.get(stock_type, "综合估值")

def get_analysis_framework(stock_type: str) -> str:
    """获取分析框架"""
    frameworks = {
        "周期股": "周期位置判断、供需分析、产能利用率、行业景气度",
        "成长股": "成长空间、渗透率、TAM、竞争优势、技术壁垒",
        "价值股": "ROE质量、PB分位、股息稳定性、安全边际",
    }
    return frameworks.get(stock_type, "综合分析")
