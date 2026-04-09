#!/usr/bin/env python3
"""
股票技术指标分析工具
数据来源：新浪财经 K 线 API
"""

import requests
import json
import math
from datetime import datetime


def get_kline_data(symbol: str, scale: int = 240, datalen: int = 60) -> list:
    """
    获取 K 线数据
    symbol: 股票代码，如 sz002460, sh600519
    scale: 周期，5/15/30/60 分钟，或 240 日K
    datalen: 数据条数
    """
    url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
    params = {
        "symbol": symbol,
        "scale": scale,
        "ma": "no",
        "datalen": datalen
    }
    headers = {"Referer": "https://finance.sina.com.cn/"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    text = resp.text
    # 去掉 JSONP 包装
    if "=" in text:
        text = text.split("=", 1)[1]
    data = json.loads(text)
    return data


def get_stock_quote(symbol: str) -> dict:
    """获取实时行情"""
    # 腾讯财经实时报价
    url = f"https://qt.gtimg.cn/q={symbol}"
    resp = requests.get(url, timeout=10)
    resp.encoding = "gbk"
    text = resp.text.strip()
    if not text or "none" in text:
        return {}

    parts = text.split("~")
    if len(parts) < 50:
        return {}

    fields = [
        "name", "code", "price", "yesterday_close", "open", "volume",
        "bid1_vol", "bid1_price", "bid2_vol", "bid2_price", "bid3_vol", "bid3_price",
        "bid4_vol", "bid4_price", "bid5_vol", "bid5_price",
        "ask1_vol", "ask1_price", "ask2_vol", "ask2_price", "ask3_vol", "ask3_price",
        "ask4_vol", "ask4_price", "ask5_vol", "ask5_price",
        "datetime", "change", "change_pct", "high", "low", "amplitude",
        "turnover", "pe_ttm", "total_capital", "float_capital"
    ]
    return dict(zip(fields, parts[:len(fields)]))


def calc_ma(closes: list, period: int) -> list:
    """计算移动平均线"""
    result = []
    for i in range(len(closes)):
        if i < period - 1:
            result.append(None)
        else:
            ma = sum(closes[i - period + 1:i + 1]) / period
            result.append(round(ma, 3))
    return result


def calc_ema(closes: list, period: int) -> list:
    """计算指数移动平均线"""
    k = 2 / (period + 1)
    ema = [closes[0]]
    for i in range(1, len(closes)):
        ema.append(closes[i] * k + ema[-1] * (1 - k))
    return [round(v, 3) for v in ema]


def calc_macd(closes: list, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """
    计算 MACD
    返回: (dif, dea, macd_hist)
    dif = EMA(close, 12) - EMA(close, 26)
    dea = EMA(dif, 9)
    macd_hist = 2 * (dif - dea)
    """
    ema_fast = calc_ema(closes, fast)
    ema_slow = calc_ema(closes, slow)
    dif = [ema_fast[i] - ema_slow[i] for i in range(len(closes))]
    dea = calc_ema(dif, signal)
    macd_hist = [round(2 * (dif[i] - dea[i]), 4) if i >= signal - 1 else None for i in range(len(dif))]
    return [round(v, 4) for v in dif], [round(v, 4) for v in dea], macd_hist


def calc_rsi(closes: list, period: int = 14) -> list:
    """计算 RSI 相对强弱指标"""
    if len(closes) < period + 1:
        return [None] * len(closes)

    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [c if c > 0 else 0 for c in changes]
    losses = [-c if c < 0 else 0 for c in changes]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsi = [None] * period
    if avg_loss == 0:
        rsi.append(100)
    else:
        rs = avg_gain / avg_loss
        rsi.append(round(100 - 100 / (1 + rs), 2))

    for i in range(period, len(changes)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(round(100 - 100 / (1 + rs), 2))

    return rsi


def calc_kdj(highs: list, lows: list, closes: list, n: int = 9, m1: int = 3, m2: int = 3) -> tuple:
    """
    计算 KDJ 随机指标
    """
    if len(closes) < n:
        return [None] * len(closes), [None] * len(closes), [None] * len(closes)

    k_values = []
    d_values = []

    # 第一个 K 值
    rsv_sum = 0
    for i in range(n):
        rsv = (closes[i] - min(lows[:i + 1])) / (max(highs[:i + 1]) - min(lows[:i + 1])) * 100 if max(highs[:i + 1]) != min(lows[:i + 1]) else 50
        rsv_sum += rsv
    k = rsv_sum / n
    d = k
    k_values.append(k)
    d_values.append(d)

    for i in range(n, len(closes)):
        rsv = (closes[i] - min(lows[i - n + 1:i + 1])) / (max(highs[i - n + 1:i + 1]) - min(lows[i - n + 1:i + 1])) * 100 if max(highs[i - n + 1:i + 1]) != min(lows[i - n + 1:i + 1]) else 50
        k = (k * (m1 - 1) + rsv) / m1
        d = (d * (m2 - 1) + k) / m2
        k_values.append(k)
        d_values.append(d)

    j = [None] * n + [round(3 * k_values[i] - 2 * d_values[i], 2) for i in range(len(k_values))]

    # 补齐前面的 None 使长度与 closes 一致
    k_full = [None] * n + [round(v, 2) for v in k_values]
    d_full = [None] * n + [round(v, 2) for v in d_values]
    return k_full, d_full, j


def calc_bollinger_bands(closes: list, period: int = 20, std_dev: int = 2) -> tuple:
    """
    计算布林带
    中轨 = MA
    上轨 = MA + 2 * STD
    下轨 = MA - 2 * STD
    """
    ma = calc_ma(closes, period)
    upper = []
    lower = []

    for i in range(len(closes)):
        if i < period - 1:
            upper.append(None)
            lower.append(None)
        else:
            data = closes[i - period + 1:i + 1]
            mean = ma[i]
            variance = sum((x - mean) ** 2 for x in data) / period
            std = math.sqrt(variance)
            upper.append(round(mean + std_dev * std, 3))
            lower.append(round(mean - std_dev * std, 3))

    return upper, ma, lower


def calc_vol_ma(volumes: list, period: int = 5) -> list:
    """计算成交量均线"""
    result = []
    for i in range(len(volumes)):
        if i < period - 1:
            result.append(None)
        else:
            ma = sum(volumes[i - period + 1:i + 1]) / period
            result.append(round(ma, 0))
    return result


def format_number(n: float, dec: int = 2) -> str:
    """格式化数字"""
    if n is None:
        return "N/A"
    return f"{n:.{dec}f}"


def print_analysis(symbol: str, name: str = ""):
    """打印完整技术分析"""
    print(f"\n{'=' * 60}")
    print(f"  {name} ({symbol.upper()}) 技术分析")
    print(f"{'=' * 60}")

    # 获取日 K 线（用于计算所有指标）
    print(f"\n【正在获取 K 线数据...】")
    klines = get_kline_data(symbol, scale=240, datalen=60)
    if not klines:
        print("  获取 K 线失败")
        return

    print(f"  获取到 {len(klines)} 条 K 线数据")

    closes = [float(k["close"]) for k in klines]
    opens = [float(k["open"]) for k in klines]
    highs = [float(k["high"]) for k in klines]
    lows = [float(k["low"]) for k in klines]
    volumes = [int(k["volume"]) for k in klines]
    dates = [k["day"] for k in klines]

    # 最新行情从 K 线最后一条获取
    latest = len(closes) - 1
    price = closes[latest]
    yesterday_close = closes[latest - 1] if latest > 0 else closes[0]
    change = price - yesterday_close
    change_pct = (change / yesterday_close) * 100 if yesterday_close else 0
    high = highs[latest]
    low = lows[latest]
    volume = volumes[latest]
    dt = dates[latest]

    print(f"\n【实时行情】 {dt}")
    print(f"  当前价: {price:.2f}  涨跌: {change:+.2f} ({change_pct:+.2f}%)")
    print(f"  最高: {high:.2f}  最低: {low:.2f}")
    print(f"  成交量: {volume:,} 手 ({volume * 100:,} 股)")

    # 计算各项指标
    ma5 = calc_ma(closes, 5)
    ma10 = calc_ma(closes, 10)
    ma20 = calc_ma(closes, 20)
    ma30 = calc_ma(closes, 30)

    dif, dea, macd = calc_macd(closes)
    rsi6 = calc_rsi(closes, 6)
    rsi14 = calc_rsi(closes, 14)
    rsi24 = calc_rsi(closes, 24)

    k, d, j = calc_kdj(highs, lows, closes, n=23, m1=3, m2=3)

    bb_upper, bb_mid, bb_lower = calc_bollinger_bands(closes, period=11, std_dev=3)
    vol_ma5 = calc_vol_ma(volumes, 5)

    # 打印最新数据
    latest = len(closes) - 1

    print(f"\n{'─' * 60}")
    print("【均线 MA】")
    print(f"  MA5:   {format_number(ma5[latest])}   MA10:  {format_number(ma10[latest])}   MA20:  {format_number(ma20[latest])}   MA30:  {format_number(ma30[latest])}")
    if ma5[latest] and ma10[latest] and ma20[latest]:
        if ma5[latest] > ma10[latest] > ma20[latest]:
            ma_status = "多头排列 ↑↑↑"
        elif ma5[latest] < ma10[latest] < ma20[latest]:
            ma_status = "空头排列 ↓↓↓"
        else:
            ma_status = "震荡整理"
        print(f"  均线状态: {ma_status}")

    print(f"\n【MACD】(12,26,9)")
    dif_v = dif[latest] if latest >= 25 else None
    dea_v = dea[latest] if latest >= 33 else None
    macd_v = macd[latest]
    print(f"  DIF: {format_number(dif_v)}  DEA: {format_number(dea_v)}  MACD: {format_number(macd_v)}")
    if dif_v is not None and dea_v is not None:
        if dif_v > dea_v:
            macd_status = "金叉（多头）"
        else:
            macd_status = "死叉（空头）"
        if macd_v and macd_v > 0:
            macd_status += " 红柱"
        elif macd_v and macd_v < 0:
            macd_status += " 绿柱"
        print(f"  信号: {macd_status}")

    print(f"\n【KDJ】(23,3,3)")
    k_v = k[latest]
    d_v = d[latest]
    j_v = j[latest]
    print(f"  K: {format_number(k_v)}  D: {format_number(d_v)}  J: {format_number(j_v)}")
    if k_v and d_v:
        if k_v > d_v:
            kdj_status = "金叉"
        else:
            kdj_status = "死叉"
        if j_v:
            if j_v > 80:
                kdj_status += " 超买区"
            elif j_v < 20:
                kdj_status += " 超卖区"
        print(f"  信号: {kdj_status}")

    print(f"\n【RSI】")
    print(f"  RSI6:  {format_number(rsi6[latest])}   RSI14: {format_number(rsi14[latest])}   RSI24: {format_number(rsi24[latest])}")
    if rsi14[latest]:
        v = rsi14[latest]
        if v > 70:
            rsi_status = "超买"
        elif v < 30:
            rsi_status = "超卖"
        else:
            rsi_status = "正常区间"
        print(f"  RSI14 状态: {rsi_status}")

    print(f"\n【布林带】(11,3)")
    print(f"  上轨: {format_number(bb_upper[latest])}   中轨: {format_number(bb_mid[latest])}   下轨: {format_number(bb_lower[latest])}")
    if bb_upper[latest] and price:
        position = (price - bb_lower[latest]) / (bb_upper[latest] - bb_lower[latest]) * 100 if bb_upper[latest] != bb_lower[latest] else 50
        print(f"  价格位置: {position:.1f}% (0%=下轨, 50%=中轨, 100%=上轨)")

    print(f"\n【成交量】")
    vol_ma5_v = vol_ma5[latest] if latest >= 4 else None
    vol_now = volumes[latest] if volumes else 0
    print(f"  今日成交量: {vol_now:,} 手")
    print(f"  5日均量: {format_number(vol_ma5_v, 0)} 手")
    if vol_ma5_v and vol_now:
        ratio = vol_now / vol_ma5_v
        if ratio > 2:
            vol_status = "异常放量"
        elif ratio > 1.5:
            vol_status = "温和放量"
        elif ratio < 0.5:
            vol_status = "缩量"
        else:
            vol_status = "正常"
        print(f"  量比: {ratio:.2f}x ({vol_status})")

    # 最近 5 天数据表
    print(f"\n【最近 5 日 K 线】")
    print(f"{'日期':<12} {'开盘':>8} {'最高':>8} {'最低':>8} {'收盘':>8} {'成交量':>12}")
    for i in range(latest - 4, latest + 1):
        if i >= 0:
            vol_str = f"{volumes[i]:,}" if volumes[i] else "N/A"
            print(f"{dates[i]:<12} {opens[i]:>8.2f} {highs[i]:>8.2f} {lows[i]:>8.2f} {closes[i]:>8.2f} {vol_str:>12}")

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    import sys

    # 默认分析赣锋锂业
    default = "sz002460"

    if len(sys.argv) > 1:
        code = sys.argv[1].strip()
        # 自动加前缀
        if not code.startswith("sz") and not code.startswith("sh"):
            if code.startswith("0") or code.startswith("3"):
                code = "sz" + code
            elif code.startswith("6"):
                code = "sh" + code
        symbol = code
    else:
        symbol = default

    print_analysis(symbol)
