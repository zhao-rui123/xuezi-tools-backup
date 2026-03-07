#!/usr/bin/env python3
"""
股票类型识别与分类模块
根据行业/业务特征自动判断股票类型
"""

from typing import Dict, List, Tuple
from enum import Enum

class StockType(Enum):
    """股票类型枚举"""
    CYCLICAL = "周期股"      # 周期股
    GROWTH = "成长股"        # 成长股
    VALUE = "价值股"         # 价值股
    HYBRID = "混合型"        # 混合型（如成长价值兼具）
    UNKNOWN = "未知"         # 无法判断

# 周期股行业关键词
CYCLICAL_KEYWORDS = [
    # 锂矿/有色金属
    '锂', '钴', '镍', '铜', '铝', '锌', '铅', '锡', '稀土', '贵金属',
    # 能源
    '煤炭', '石油', '天然气', '油气', '页岩气',
    # 化工
    '化工', '化肥', '农药', '化纤', '塑料', '橡胶', '聚氨酯',
    # 钢铁/建材
    '钢铁', '铁矿石', '建材', '水泥', '玻璃', '陶瓷',
    # 航运/造船
    '航运', '港口', '造船', '船舶', '海运',
    # 工程机械
    '工程机械', '重卡', '挖掘机', '机床',
    # 其他周期
    '造纸', '林业', '养殖', '饲料',
]

# 成长股行业关键词
GROWTH_KEYWORDS = [
    # 科技
    '半导体', '芯片', '集成电路', '软件', '互联网', '人工智能', 'AI',
    '云计算', '大数据', '物联网', '5G', '通信设备', '电子元件',
    # 新能源
    '光伏', '风电', '储能', '电池', '新能源车', '电动车',
    # 医药
    '生物医药', '创新药', '医疗器械', 'CXO', 'CRO', '医疗服务',
    # 高端制造
    '机器人', '自动化', '智能制造', '航空航天', '军工',
    # 消费（部分成长）
    '新消费', '跨境电商', '直播', '免税',
]

# 价值股行业关键词
VALUE_KEYWORDS = [
    # 金融
    '银行', '保险', '证券', '信托', '金融租赁',
    # 公用事业
    '电力', '水务', '燃气', '供热', '环保', '垃圾处理',
    # 传统消费
    '白酒', '食品饮料', '家电', '零售', '超市', '百货',
    # 基础设施
    '公路', '铁路', '机场', '港口', '物流', '仓储',
    # 地产/建筑
    '房地产', '建筑', '基建', '装修', '物业',
    # 其他传统
    '纺织', '服装', '家具', '印刷', '出版',
]

# 特定公司名称映射（补充判断）
COMPANY_TYPE_MAP = {
    # 周期股
    '赣锋锂业': StockType.CYCLICAL,
    '天齐锂业': StockType.CYCLICAL,
    '中矿资源': StockType.CYCLICAL,
    '盐湖股份': StockType.CYCLICAL,
    '华友钴业': StockType.CYCLICAL,
    '北方稀土': StockType.CYCLICAL,
    # 成长股
    '宁德时代': StockType.GROWTH,
    '比亚迪': StockType.HYBRID,  # 成长+周期
    '隆基绿能': StockType.HYBRID,
    '中际旭创': StockType.GROWTH,
    '迈瑞医疗': StockType.GROWTH,
    # 价值股
    '招商银行': StockType.VALUE,
    '中国平安': StockType.VALUE,
    '贵州茅台': StockType.HYBRID,  # 成长+价值
}

def classify_stock_by_name(name: str, sector: str = "") -> StockType:
    """
    根据公司名称和行业分类股票类型
    
    Args:
        name: 公司名称
        sector: 行业分类
    
    Returns:
        StockType: 股票类型
    """
    # 1. 先查特定公司映射
    if name in COMPANY_TYPE_MAP:
        return COMPANY_TYPE_MAP[name]
    
    # 2. 根据行业关键词判断
    text = name + " " + sector
    
    # 统计各类关键词匹配数量
    cyclical_score = sum(1 for kw in CYCLICAL_KEYWORDS if kw in text)
    growth_score = sum(1 for kw in GROWTH_KEYWORDS if kw in text)
    value_score = sum(1 for kw in VALUE_KEYWORDS if kw in text)
    
    # 判断逻辑
    max_score = max(cyclical_score, growth_score, value_score)
    
    if max_score == 0:
        return StockType.UNKNOWN
    
    # 如果有多个高分，可能是混合型
    high_scores = [s for s in [cyclical_score, growth_score, value_score] if s >= max_score - 1]
    if len(high_scores) >= 2:
        return StockType.HYBRID
    
    if cyclical_score == max_score:
        return StockType.CYCLICAL
    elif growth_score == max_score:
        return StockType.GROWTH
    else:
        return StockType.VALUE

def get_stock_type_description(stock_type: StockType) -> str:
    """获取股票类型描述"""
    descriptions = {
        StockType.CYCLICAL: "周期股 - 盈利能力随经济/行业周期大幅波动",
        StockType.GROWTH: "成长股 - 处于高速成长期，盈利增速高",
        StockType.VALUE: "价值股 - 业务成熟稳定，现金流好，估值偏低",
        StockType.HYBRID: "混合型 - 兼具多种特征",
        StockType.UNKNOWN: "未知类型 - 无法自动分类",
    }
    return descriptions.get(stock_type, "未知")

def get_analysis_framework(stock_type: StockType) -> Dict:
    """
    获取对应股票类型的分析框架
    
    Returns:
        Dict: 分析框架配置
    """
    frameworks = {
        StockType.CYCLICAL: {
            "name": "周期股分析框架",
            "key_metrics": ["周期位置", "供需分析", "产品价格", "PB估值"],
            "valuation_method": "PB、EV/产能、资源量估值（不看PE）",
            "focus": "判断周期阶段，底部买入顶部卖出",
            "risk": "周期误判、价格暴跌",
        },
        StockType.GROWTH: {
            "name": "成长股分析框架",
            "key_metrics": ["成长空间", "收入增速", "渗透率", "竞争优势"],
            "valuation_method": "PEG、PS、远期PE（看增速）",
            "focus": "判断成长期，早期看空间晚期看盈利",
            "risk": "增速放缓、估值杀",
        },
        StockType.VALUE: {
            "name": "价值股分析框架",
            "key_metrics": ["ROE稳定性", "PB", "股息率", "现金流"],
            "valuation_method": "PB-ROE、股息率（不看增速）",
            "focus": "低估值买入，长期持有收息",
            "risk": "价值陷阱、增长停滞",
        },
        StockType.HYBRID: {
            "name": "混合型分析框架",
            "key_metrics": ["综合评估", "不同阶段侧重不同"],
            "valuation_method": "多种方法结合",
            "focus": "根据具体特征选择分析重点",
            "risk": "特征变化",
        },
    }
    return frameworks.get(stock_type, frameworks[StockType.UNKNOWN])

# 测试
if __name__ == "__main__":
    test_stocks = [
        ("中矿资源", "锂矿/资源"),
        ("赣锋锂业", "锂电池"),
        ("宁德时代", "新能源"),
        ("招商银行", "银行"),
        ("中际旭创", "通信设备"),
        ("贵州茅台", "白酒"),
    ]
    
    print("股票类型识别测试：")
    print("="*60)
    for name, sector in test_stocks:
        stock_type = classify_stock_by_name(name, sector)
        framework = get_analysis_framework(stock_type)
        print(f"\n{name} ({sector})")
        print(f"  类型: {stock_type.value}")
        print(f"  估值方法: {framework['valuation_method']}")
        print(f"  关键指标: {', '.join(framework['key_metrics'])}")
