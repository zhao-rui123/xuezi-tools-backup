#!/usr/bin/env python3
"""
自选股每日分析器 Pro - 新浪财经 + AkShare 组合
作者: 雪子助手
功能: 实时行情 + 大盘分析 + 板块分析 + 个股深度分析
"""

import urllib.request
import json
import re
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# 添加 akshare 支持
try:
    import akshare as ak
    import time
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

# 数据获取状态跟踪
DATA_STATUS = {
    'market_index': False,
    'stock_price': False,
    'money_flow': False,
    'market_sentiment': False,
    'north_bound': False,
    'tech_indicators': False,
    'kline': False,
    'tencent_kline': False,
}

def akshare_retry(func, max_retries=2, delay=1):
    """AkShare 调用重试机制（静默失败）"""
    for i in range(max_retries):
        try:
            return func()
        except Exception:
            if i < max_retries - 1:
                time.sleep(delay)
                continue
            return None
    return None

# 自选股列表
WATCHLIST = [
    ("002738", "中矿资源", "锂矿/资源"),
    ("002460", "赣锋锂业", "锂电池/新能源"),
    ("000792", "盐湖股份", "盐湖提锂"),
    ("002240", "盛新锂能", "锂电池材料"),
    ("000725", "京东方A", "面板/显示"),
    ("600707", "彩虹股份", "面板/显示"),
    ("688981", "中芯国际", "半导体/芯片"),
]

# 关注的板块指数
SECTOR_INDICES = {
    "锂矿": "BK0963",  # 锂矿概念
    "面板": "BK0904",  # OLED/面板概念
    "新能源": "BK0493",  # 新能源
}

# 大盘指数
MARKET_INDICES = {
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "创业板指": "sz399006",
    "科创50": "sh000688",
}

# ==================== 数据获取 ====================

def fetch_sina_data(codes: List[str]) -> Dict:
    """从新浪财经获取实时数据"""
    code_str = ",".join([
        f"sz{c}" if c.startswith(("0", "3")) else f"sh{c}"
        for c in codes
    ])
    
    url = f"https://hq.sinajs.cn/list={code_str}"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Referer', 'https://finance.sina.com.cn')
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')
        result = parse_sina_data(data)
        if result:
            DATA_STATUS['stock_price'] = True
        return result
    except Exception:
        return {}

def parse_sina_data(data: str) -> Dict:
    """解析新浪返回的数据"""
    result = {}
    
    for line in data.strip().split('\n'):
        match = re.search(r'var hq_str_(\w+)="([^"]*)"', line)
        if match:
            code_key = match.group(1)
            code = code_key[2:]
            fields = match.group(2).split(',')
            
            if len(fields) >= 33:
                result[code] = {
                    'name': fields[0],
                    'open': float(fields[1]),
                    'yesterday_close': float(fields[2]),
                    'price': float(fields[3]),
                    'high': float(fields[4]),
                    'low': float(fields[5]),
                    'volume': int(float(fields[8])),
                    'amount': float(fields[9]),
                    'bid1_price': float(fields[11]),
                    'ask1_price': float(fields[21]),
                    'date': fields[30],
                    'time': fields[31],
                }
    
    return result

def fetch_market_index(index_code: str) -> Optional[Dict]:
    """获取大盘指数数据"""
    try:
        url = f"https://hq.sinajs.cn/list={index_code}"
        req = urllib.request.Request(url)
        req.add_header('Referer', 'https://finance.sina.com.cn')
        response = urllib.request.urlopen(req, timeout=10)
        data = response.read().decode('gb2312', errors='ignore')

        match = re.search(r'var hq_str_\w+="([^"]*)"', data)
        if match:
            fields = match.group(1).split(',')
            if len(fields) >= 5:
                # 指数数据格式: 名称,当前点数,昨日收盘,今日开盘,最高,最低...
                name = fields[0]
                current = float(fields[1])  # 当前点数
                yesterday = float(fields[2])  # 昨日收盘点数
                # 涨跌点数 = 当前 - 昨日收盘
                change = current - yesterday
                # 涨跌幅百分比
                change_pct = (change / yesterday * 100) if yesterday > 0 else 0

                DATA_STATUS['market_index'] = True
                return {
                    'name': name,
                    'price': current,
                    'change': change,
                    'change_pct': change_pct,
                }
    except Exception:
        pass
    return None

def get_sector_data_with_akshare() -> Dict:
    """使用 AkShare 获取板块数据（带超时保护）"""
    if not AKSHARE_AVAILABLE:
        return {}
    
    sector_data = {}
    try:
        # 使用信号机制设置超时（仅Unix系统）
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("AkShare 请求超时")
        
        # 设置5秒超时
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)
        
        try:
            # 获取板块实时行情
            df = ak.stock_board_concept_name_em()
            if df is not None and len(df) > 0:
                for name, code in SECTOR_INDICES.items():
                    try:
                        # 查找对应板块
                        sector_row = df[df['板块名称'].str.contains(name.replace('概念', '').replace('板块', ''), na=False)]
                        if len(sector_row) > 0:
                            sector_data[name] = {
                                'change_pct': float(sector_row.iloc[0]['涨跌幅']),
                                'main_stock': sector_row.iloc[0]['领涨股票'],
                                'main_change': float(sector_row.iloc[0]['领涨股票涨跌幅']),
                            }
                    except Exception:
                        pass
        finally:
            # 恢复原来的信号处理器
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
            
    except TimeoutError:
        # 超时，返回空数据
        pass
    except Exception:
        pass
    
    return sector_data

def get_north_bound_funds() -> Optional[Dict]:
    """获取北向资金流向"""
    if not AKSHARE_AVAILABLE:
        return None
    
    try:
        df = ak.stock_hsgt_hist_em(symbol="沪港通")
        if df is not None and len(df) > 0:
            latest = df.iloc[0]
            return {
                'date': latest['日期'],
                'net_inflow': float(latest['当日资金流入']) if '当日资金流入' in latest else 0,
                'accumulated': float(latest['累计资金流入']) if '累计资金流入' in latest else 0,
            }
    except Exception:
        pass
    return None

def get_stock_news(stock_code: str) -> List[str]:
    """获取个股相关新闻"""
    if not AKSHARE_AVAILABLE:
        return []
    
    try:
        df = ak.stock_news_em(symbol=stock_code)
        if df is not None and len(df) > 0:
            # 取最近5条
            news_list = []
            for _, row in df.head(5).iterrows():
                news_list.append(f"{row['发布时间']}: {row['新闻标题']}")
            return news_list
    except Exception:
        pass
    return []

def get_tencent_kline(stock_code: str) -> Dict:
    """从腾讯财经获取K线数据并计算技术指标"""
    try:
        # 转换代码格式
        if stock_code.startswith('6'):
            tencent_code = f"sh{stock_code}"
        elif stock_code.startswith(('0', '3')):
            tencent_code = f"sz{stock_code}"
        else:
            return {}
        
        # 获取最近60天日线数据
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tencent_code},day,,,60,qfq"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        # 解析数据
        kline_key = f"{tencent_code}"
        if kline_key not in data.get('data', {}):
            return {}
        
        kline_data = data['data'][tencent_code].get('qfqday', [])
        if len(kline_data) < 20:
            return {}
        
        # 提取收盘价
        closes = [float(day[2]) for day in kline_data]  # day: [日期, 开盘, 收盘, 最低, 最高, 成交量]
        
        # 计算均线
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10
        ma20 = sum(closes[-20:]) / 20
        current_price = closes[-1]
        
        # 判断趋势
        trend = "多头" if current_price > ma5 > ma10 > ma20 else \
                "空头" if current_price < ma5 < ma10 < ma20 else "震荡"
        
        # 计算RSI (14日)
        if len(closes) >= 15:
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [d if d > 0 else 0 for d in deltas[-14:]]
            losses = [-d if d < 0 else 0 for d in deltas[-14:]]
            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14
            rs = avg_gain / avg_loss if avg_loss > 0 else 0
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50
        
        # 提取K线数据
        # day: [日期, 开盘, 收盘, 最低, 最高, 成交量]
        today = kline_data[-1]
        prev = kline_data[-2] if len(kline_data) >= 2 else today
        
        open_price = float(today[1])
        close = float(today[2])
        low = float(today[3])
        high = float(today[4])
        prev_close = float(prev[2])
        
        # 计算K线形态
        body = abs(close - open_price)
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low
        total_range = high - low
        
        is_yang = close > open_price
        
        # 判断形态
        pattern = ""
        pattern_desc = ""
        
        if total_range > 0 and body / total_range < 0.1:
            pattern = "十字星"
            pattern_desc = "多空平衡"
        elif upper_shadow > body * 2 and lower_shadow < body:
            pattern = "流星线"
            pattern_desc = "上方承压"
        elif lower_shadow > body * 2 and upper_shadow < body:
            pattern = "锤子线"
            pattern_desc = "下方支撑"
        elif body > prev_close * 0.05 and is_yang:
            pattern = "大阳线"
            pattern_desc = "强势上涨"
        elif body > prev_close * 0.05 and not is_yang:
            pattern = "大阴线"
            pattern_desc = "强势下跌"
        elif is_yang:
            pattern = "小阳线"
            pattern_desc = "温和上涨"
        else:
            pattern = "小阴线"
            pattern_desc = "温和下跌"
        
        # 5日趋势
        trend_5d = "上涨" if closes[-1] > closes[-5] else "下跌"
        change_5d = (closes[-1] - closes[-5]) / closes[-5] * 100 if closes[-5] > 0 else 0
        
        # 成交量分析
        vol_today = int(float(today[5]))
        vol_avg_5 = sum([int(float(day[5])) for day in kline_data[-5:]]) / 5
        vol_status = "放量" if vol_today > vol_avg_5 * 1.2 else "缩量" if vol_today < vol_avg_5 * 0.8 else "平量"
        
        DATA_STATUS['tencent_kline'] = True
        return {
            'ma5': round(ma5, 2),
            'ma10': round(ma10, 2),
            'ma20': round(ma20, 2),
            'trend': trend,
            'rsi': round(rsi, 1),
            'rsi_signal': '超买' if rsi > 70 else '超卖' if rsi < 30 else '正常',
            'pattern': pattern,
            'pattern_desc': pattern_desc,
            'trend_5d': trend_5d,
            'change_5d': round(change_5d, 2),
            'vol_status': vol_status,
            'source': '腾讯财经'
        }
    except Exception:
        pass
    return {}

def get_stock_tech_indicators(stock_code: str) -> Dict:
    """获取股票技术指标 - 优先腾讯财经，失败则用AkShare"""
    # 先尝试腾讯财经
    tencent_data = get_tencent_kline(stock_code)
    if tencent_data:
        DATA_STATUS['tech_indicators'] = True
        return tencent_data
    
    # 失败则用AkShare
    if not AKSHARE_AVAILABLE:
        return {}
    
    try:
        # 获取日线数据
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                start_date=(datetime.now() - timedelta(days=60)).strftime('%Y%m%d'),
                                end_date=datetime.now().strftime('%Y%m%d'),
                                adjust="qfq")
        
        if df is None or len(df) < 20:
            return {}
        
        # 计算简单技术指标
        close = df['收盘'].values
        
        # 5日、10日、20日均线
        ma5 = close[-5:].mean() if len(close) >= 5 else close.mean()
        ma10 = close[-10:].mean() if len(close) >= 10 else close.mean()
        ma20 = close[-20:].mean() if len(close) >= 20 else close.mean()
        
        current_price = close[-1]
        
        # 判断趋势
        trend = "多头" if current_price > ma5 > ma10 > ma20 else \
                "空头" if current_price < ma5 < ma10 < ma20 else "震荡"
        
        # 计算RSI (14日)
        if len(close) >= 15:
            deltas = [close[i] - close[i-1] for i in range(1, len(close))]
            gains = [d if d > 0 else 0 for d in deltas[-14:]]
            losses = [-d if d < 0 else 0 for d in deltas[-14:]]
            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14
            rs = avg_gain / avg_loss if avg_loss > 0 else 0
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50
        
        DATA_STATUS['tech_indicators'] = True
        return {
            'ma5': round(ma5, 2),
            'ma10': round(ma10, 2),
            'ma20': round(ma20, 2),
            'trend': trend,
            'rsi': round(rsi, 1),
            'rsi_signal': '超买' if rsi > 70 else '超卖' if rsi < 30 else '正常',
        }
    except Exception:
        pass
    return {}

def get_stock_money_flow(stock_code: str) -> Dict:
    """获取个股资金流向"""
    if not AKSHARE_AVAILABLE:
        return {}
    
    def fetch_flow():
        df = ak.stock_individual_fund_flow(stock=stock_code, market="sh" if stock_code.startswith('6') else "sz")
        if df is not None and len(df) > 0:
            latest = df.iloc[0]
            return {
                'main_inflow': float(latest['主力净流入-净额']) / 10000 if '主力净流入-净额' in latest else 0,  # 万元
                'main_pct': float(latest['主力净流入-净占比']) if '主力净流入-净占比' in latest else 0,
                'retail_inflow': float(latest['散户净流入-净额']) / 10000 if '散户净流入-净额' in latest else 0,
                'retail_pct': float(latest['散户净流入-净占比']) if '散户净流入-净占比' in latest else 0,
            }
        return None
    
    result = akshare_retry(fetch_flow)
    if result:
        DATA_STATUS['money_flow'] = True
    return result or {}

def get_daily_kline_analysis(stock_code: str) -> Dict:
    """获取日K线形态分析"""
    if not AKSHARE_AVAILABLE:
        return {}
    
    def fetch_kline():
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                start_date=(datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
                                end_date=datetime.now().strftime('%Y%m%d'),
                                adjust="qfq")
        
        if df is None or len(df) < 5:
            return None
        
        # 获取最近5天数据
        recent = df.tail(5)
        
        # 分析今日K线形态
        today = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else today
        
        open_price = float(today['开盘'])
        close = float(today['收盘'])
        high = float(today['最高'])
        low = float(today['最低'])
        prev_close = float(prev['收盘'])
        
        # 判断K线形态
        body = abs(close - open_price)
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low
        total_range = high - low
        
        pattern = ""
        pattern_desc = ""
        
        # 阳线/阴线
        is_yang = close > open_price
        
        if body / total_range < 0.1 if total_range > 0 else False:
            pattern = "十字星"
            pattern_desc = "多空平衡，变盘信号"
        elif upper_shadow > body * 2 and lower_shadow < body:
            pattern = "流星线"
            pattern_desc = "上方压力大，可能回调"
        elif lower_shadow > body * 2 and upper_shadow < body:
            pattern = "锤子线"
            pattern_desc = "下方支撑强，可能反弹"
        elif body > (prev_close * 0.05) and is_yang:
            pattern = "大阳线"
            pattern_desc = "强势上涨，多头主导"
        elif body > (prev_close * 0.05) and not is_yang:
            pattern = "大阴线"
            pattern_desc = "强势下跌，空头主导"
        elif is_yang:
            pattern = "小阳线"
            pattern_desc = "温和上涨"
        else:
            pattern = "小阴线"
            pattern_desc = "温和下跌"
        
        # 5日趋势
        prices = df['收盘'].tail(5).values
        trend_5d = "上涨" if prices[-1] > prices[0] else "下跌"
        change_5d = (prices[-1] - prices[0]) / prices[0] * 100 if prices[0] > 0 else 0
        
        # 成交量分析
        vol_today = int(today['成交量'])
        vol_avg_5d = int(df['成交量'].tail(5).mean())
        vol_status = "放量" if vol_today > vol_avg_5d * 1.2 else "缩量" if vol_today < vol_avg_5d * 0.8 else "平量"
        
        DATA_STATUS['kline'] = True
        return {
            'pattern': pattern,
            'pattern_desc': pattern_desc,
            'trend_5d': trend_5d,
            'change_5d': round(change_5d, 2),
            'vol_status': vol_status,
            'vol_today': vol_today,
            'vol_avg_5d': vol_avg_5d,
        }
    
    result = akshare_retry(fetch_kline)
    if result:
        DATA_STATUS['kline'] = True
    return result or {}

def get_market_sentiment() -> Dict:
    """获取市场情绪指标"""
    if not AKSHARE_AVAILABLE:
        return {}
    
    try:
        # 获取涨跌家数统计
        df = ak.stock_zt_pool_em(date=datetime.now().strftime('%Y%m%d'))
        
        # 涨停跌停统计
        zt_count = len(df) if df is not None else 0
        
        # 获取跌停
        df_dt = ak.stock_zt_pool_dtgc_em(date=datetime.now().strftime('%Y%m%d'))
        dt_count = len(df_dt) if df_dt is not None else 0
        
        DATA_STATUS['market_sentiment'] = True
        return {
            'zt_count': zt_count,
            'dt_count': dt_count,
            'sentiment': '强势' if zt_count > dt_count * 3 else 
                        '弱势' if dt_count > zt_count * 2 else '平衡'
        }
    except Exception:
        pass
    return {}

# ==================== 分析计算 ====================

def calculate_metrics(stock: Dict) -> Dict:
    """计算衍生指标"""
    price = stock['price']
    yc = stock['yesterday_close']
    
    change = price - yc
    change_pct = (change / yc) * 100 if yc > 0 else 0
    amplitude = ((stock['high'] - stock['low']) / yc) * 100 if yc > 0 else 0
    volume_wan = stock['volume'] / 10000
    amount_yi = stock['amount'] / 100000000
    
    return {
        'change': change,
        'change_pct': change_pct,
        'amplitude': amplitude,
        'volume_wan': volume_wan,
        'amount_yi': amount_yi,
    }

def analyze_stock_reason(code: str, name: str, industry: str, change_pct: float, 
                         news: List[str], tech: Dict) -> str:
    """分析个股涨跌原因"""
    reasons = []
    
    # 技术面原因
    if tech:
        if tech.get('rsi', 50) > 70:
            reasons.append("技术指标超买，短期回调压力")
        elif tech.get('rsi', 50) < 30:
            reasons.append("技术指标超卖，存在反弹机会")
        
        trend = tech.get('trend', '')
        if trend == '多头' and change_pct > 0:
            reasons.append("均线多头排列，趋势向好")
        elif trend == '空头' and change_pct < 0:
            reasons.append("均线空头排列，趋势偏弱")
    
    # 行业原因
    industry_reasons = {
        '锂矿/资源': {
            'up': ['碳酸锂价格企稳回升', '锂矿资源供应紧张', '新能源需求超预期'],
            'down': ['碳酸锂价格持续下跌', '锂矿供应过剩预期', '下游需求疲软']
        },
        '锂电池/新能源': {
            'up': ['新能源车销量超预期', '动力电池订单饱满', '储能需求爆发'],
            'down': ['产业链价格战加剧', '原材料成本压力', '下游去库存']
        },
        '盐湖提锂': {
            'up': ['成本优势明显', '产能逐步释放', '盐湖开发政策支持'],
            'down': ['锂价下跌影响盈利', '产能爬坡不及预期', '技术路线竞争']
        },
        '锂电池材料': {
            'up': ['原材料成本下降', '产能利用率提升', '新产品放量'],
            'down': ['加工费持续下滑', '下游压价', '产能过剩']
        },
        '面板/显示': {
            'up': ['面板价格上涨', '产能利用率提升', '大尺寸化趋势'],
            'down': ['需求持续疲软', '价格持续低迷', '库存压力']
        },
    }
    
    # 匹配行业原因
    for key, reasons_dict in industry_reasons.items():
        if key in industry:
            direction = 'up' if change_pct > 0 else 'down'
            if abs(change_pct) > 2:  # 涨跌幅较大时才添加行业原因
                reasons.append(reasons_dict[direction][0])
            break
    
    # 新闻原因（如果有）
    if news and abs(change_pct) > 3:
        # 提取第一条新闻作为可能原因
        first_news = news[0].split(': ', 1)[1] if ': ' in news[0] else news[0]
        if len(first_news) < 30:  # 简短新闻才添加
            reasons.append(f"相关新闻: {first_news}")
    
    return '；'.join(reasons) if reasons else '跟随板块波动'

# ==================== 报告生成 ====================

def generate_market_overview() -> str:
    """生成市场概况"""
    lines = []
    lines.append("【大盘指数】")
    
    for name, code in MARKET_INDICES.items():
        data = fetch_market_index(code)
        if data:
            # A股习惯：红涨绿跌
            emoji = "🔴" if data['change'] > 0 else "🟢"
            lines.append(f"  {emoji} {name}: {data['price']:.2f} ({data['change']:+.2f}, {data['change_pct']:+.2f}%)")
    
    # 市场情绪
    sentiment = get_market_sentiment()
    if sentiment:
        lines.append(f"\n【市场情绪】")
        lines.append(f"  涨停: {sentiment.get('zt_count', 0)}家  |  跌停: {sentiment.get('dt_count', 0)}家")
        lines.append(f"  整体氛围: {sentiment.get('sentiment', '未知')}")
    
    # 北向资金
    north = get_north_bound_funds()
    if north:
        emoji = "🟢流入" if north['net_inflow'] > 0 else "🔴流出"
        lines.append(f"\n【北向资金】")
        lines.append(f"  当日{emoji}: {north['net_inflow']:+.1f}亿元")
    
    return '\n'.join(lines)

def generate_sector_analysis() -> str:
    """生成板块分析"""
    lines = []
    lines.append("【板块表现】")
    
    # 使用 AkShare 获取板块数据
    sector_data = get_sector_data_with_akshare()
    
    if sector_data:
        for name, data in sector_data.items():
            emoji = "🟢" if data['change_pct'] > 0 else "🔴"
            lines.append(f"  {emoji} {name}: {data['change_pct']:+.2f}% (领涨: {data['main_stock']})")
    else:
        # 根据自选股计算板块表现
        sector_performance = {}
        codes = [s[0] for s in WATCHLIST]
        stock_data = fetch_sina_data(codes)
        
        for code, name, industry in WATCHLIST:
            if code in stock_data:
                ind = industry.split('/')[0]
                if ind not in sector_performance:
                    sector_performance[ind] = []
                metrics = calculate_metrics(stock_data[code])
                sector_performance[ind].append(metrics['change_pct'])
        
        for ind, changes in sector_performance.items():
            avg = sum(changes) / len(changes)
            # A股习惯：红涨绿跌
            emoji = "🔴" if avg > 0 else "🟢"
            lines.append(f"  {emoji} {ind}: 平均 {avg:+.2f}% ({len(changes)}只)")
    
    # 板块分析解读
    lines.append("\n【板块解读】")
    lines.append("  • 锂矿板块: 关注碳酸锂期货价格走势及澳洲矿山投产进度")
    lines.append("  • 面板板块: 关注面板价格能否企稳回升及下游需求恢复")
    
    return '\n'.join(lines)

def generate_stock_analysis() -> str:
    """生成个股深度分析"""
    codes = [s[0] for s in WATCHLIST]
    stock_data = fetch_sina_data(codes)
    
    if not stock_data:
        return "❌ 个股数据获取失败"
    
    # 准备数据
    stocks_with_data = []
    for code, name, industry in WATCHLIST:
        if code in stock_data:
            stock = stock_data[code]
            metrics = calculate_metrics(stock)

            # 获取技术指标
            tech = get_stock_tech_indicators(code) if AKSHARE_AVAILABLE else {}

            # 获取资金流向
            money_flow = get_stock_money_flow(code) if AKSHARE_AVAILABLE else {}

            # 获取日K线分析
            kline = get_daily_kline_analysis(code) if AKSHARE_AVAILABLE else {}

            # 获取新闻
            news = get_stock_news(code) if AKSHARE_AVAILABLE else []

            # 分析涨跌原因
            reason = analyze_stock_reason(code, name, industry,
                                         metrics['change_pct'], news, tech)

            stocks_with_data.append({
                'code': code,
                'name': name,
                'industry': industry,
                'stock': stock,
                'metrics': metrics,
                'tech': tech,
                'money_flow': money_flow,
                'kline': kline,
                'news': news,
                'reason': reason,
            })
    
    # 排序
    stocks_with_data.sort(key=lambda x: x['metrics']['change_pct'], reverse=True)
    
    lines = []
    lines.append("【个股表现】")
    lines.append("-" * 80)
    lines.append(f"{'排名':<4} {'名称':<8} {'代码':<8} {'现价':>8} {'涨跌':>8} {'涨幅':>8} {'成交额':>8}")
    lines.append("-" * 80)
    
    for i, item in enumerate(stocks_with_data, 1):
        s = item['stock']
        m = item['metrics']
        # A股习惯：红涨绿跌
        emoji = "🔴" if m['change_pct'] > 0 else "🟢" if m['change_pct'] < 0 else "⚪"
        
        lines.append(
            f"{emoji}{i:<3} {item['name']:<8} {item['code']:<8} "
            f"{s['price']:>8.2f} {m['change']:>+8.2f} {m['change_pct']:>+7.2f}% {m['amount_yi']:>7.2f}亿"
        )
    
    lines.append("-" * 80)
    
    # 详细分析
    lines.append("\n【个股深度分析】")
    
    for item in stocks_with_data:
        m = item['metrics']
        tech = item['tech']
        money = item.get('money_flow', {})

        lines.append(f"\n▶ {item['name']} ({item['code']}) - {item['industry']}")
        lines.append(f"  涨跌: {m['change']:+.2f} ({m['change_pct']:+.2f}%)  振幅: {m['amplitude']:.2f}%")

        # 资金流向
        if money:
            main_emoji = "🔴" if money.get('main_inflow', 0) > 0 else "🟢"
            lines.append(f"  资金: {main_emoji}主力 {money.get('main_inflow', 0):+.0f}万 ({money.get('main_pct', 0):+.2f}%)")

        # K线形态 & 技术指标
        if tech:
            # K线形态
            if 'pattern' in tech:
                lines.append(f"  K线: {tech.get('pattern', '未知')} ({tech.get('pattern_desc', '')})")
            
            # 5日趋势
            if 'trend_5d' in tech:
                trend_emoji = "🔴" if tech.get('change_5d', 0) > 0 else "🟢"
                lines.append(f"  趋势: 5日{trend_emoji}{tech.get('trend_5d')} {tech.get('change_5d', 0):+.2f}% | 量能: {tech.get('vol_status', '未知')}")
            
            # 技术指标
            lines.append(f"  技术: {tech.get('trend', '未知')}  RSI:{tech.get('rsi', 'N/A')}({tech.get('rsi_signal', '')})")
            lines.append(f"  均线: MA5={tech.get('ma5', 'N/A')} MA10={tech.get('ma10', 'N/A')} MA20={tech.get('ma20', 'N/A')}")

        lines.append(f"  分析: {item['reason']}")

        # 显示相关新闻（如果有重大涨跌）
        if abs(m['change_pct']) > 4 and item['news']:
            lines.append(f"  新闻: {item['news'][0].split(': ', 1)[1] if ': ' in item['news'][0] else item['news'][0]}")
    
    return '\n'.join(lines)

def generate_report() -> str:
    """生成完整分析报告"""
    report_lines = []
    
    # 标题
    report_lines.append("=" * 80)
    report_lines.append(f"📊 自选股深度分析报告 - {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # 市场概况
    report_lines.append(generate_market_overview())
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # 板块分析
    report_lines.append(generate_sector_analysis())
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # 个股分析
    report_lines.append(generate_stock_analysis())
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # 总结建议
    report_lines.append("【总结与建议】")
    report_lines.append("  1. 关注碳酸锂价格走势对锂矿股的影响")
    report_lines.append("  2. 面板板块关注价格能否企稳及需求恢复情况")
    report_lines.append("  3. 建议分散配置，控制单一板块仓位")
    report_lines.append("")
    report_lines.append("=" * 80)

    # 数据状态
    report_lines.append("【数据状态】")
    status_icons = {True: "✅", False: "❌"}
    report_lines.append(f"  实时行情: {status_icons[DATA_STATUS.get('stock_price', True)]} 新浪财经")
    report_lines.append(f"  大盘指数: {status_icons[DATA_STATUS.get('market_index', False)]} 新浪财经")
    report_lines.append(f"  资金流向: {status_icons[DATA_STATUS.get('money_flow', False)]} AkShare")
    report_lines.append(f"  市场情绪: {status_icons[DATA_STATUS.get('market_sentiment', False)]} AkShare")
    tech_source = "腾讯财经" if DATA_STATUS.get('tencent_kline') else ("AkShare" if DATA_STATUS.get('tech_indicators') else "未获取")
    report_lines.append(f"  技术指标: {status_icons[DATA_STATUS.get('tech_indicators', False) or DATA_STATUS.get('tencent_kline', False)]} {tech_source}")
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("数据来源: 新浪财经 + AkShare + 腾讯财经 | 更新时间: " + datetime.now().strftime('%H:%M:%S'))
    report_lines.append("=" * 80)
    
    return '\n'.join(report_lines)

def send_feishu_message(message: str):
    """发送飞书消息"""
    # 这里会被外部脚本调用时替换
    print(message)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--feishu":
        # 飞书模式：生成报告并通过飞书发送
        report = generate_report()
        send_feishu_message(report)
    else:
        # 普通模式：仅打印报告
        print(generate_report())
