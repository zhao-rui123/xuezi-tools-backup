"""
策略B v5 模拟盘 - 优化版
用新浪批量接口获取K线，高效筛选全A股
"""

import json
import os
import requests
import math
import re
from datetime import datetime
from typing import List, Dict, Optional

PORTFOLIO_FILE = os.path.join(os.path.dirname(__file__), "portfolio.json")

INITIAL_CASH = 1000000
MAX_POSITIONS = 20
HOLD_DAYS = 15
STOP_LOSS = 0.08


def get_a_stock_list(max_stocks: int = 6000) -> List[str]:
    """获取A股股票代码列表"""
    stocks = []
    page = 1
    while len(stocks) < max_stocks:
        url = 'https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'
        params = {
            'page': page,
            'num': 100,
            'sort': 'symbol',
            'asc': 1,
            'node': 'hs_a',
            'symbol': '',
            '_s_r_a': 'page'
        }
        headers = {'Referer': 'https://finance.sina.com.cn/'}
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            data = resp.json()
            if not data:
                break
            for s in data:
                symbol = s.get('symbol', '')
                # 只取沪深A股 (sh6xxxxx, sz0xxxxx, sz3xxxxx) - symbol格式如sh600519
                if re.match(r'^(sh6|sh5|sz0|sz3)\d{5}$', symbol):
                    stocks.append(symbol)
            if len(data) < 100:
                break
            page += 1
        except:
            break
    return stocks[:max_stocks]


def batch_get_kline(symbols: List[str]) -> Dict[str, dict]:
    """批量获取K线数据"""
    result = {}
    
    # 分批获取，每批20个
    for i in range(0, len(symbols), 20):
        batch = symbols[i:i+20]
        symbol_str = ','.join(batch)
        
        url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
        # 尝试批量获取，如果失败则单只获取
        for symbol in batch:
            try:
                params = {
                    "symbol": symbol,
                    "scale": 240,
                    "ma": "no",
                    "datalen": 60
                }
                headers = {"Referer": "https://finance.sina.com.cn/"}
                resp = requests.get(url, params=params, headers=headers, timeout=8)
                text = resp.text
                if "=" in text:
                    text = text.split("=", 1)[1]
                klines = json.loads(text)
                if klines and len(klines) >= 30:
                    result[symbol] = klines
            except:
                continue
    
    return result


def calc_ma(closes: list, period: int) -> Optional[float]:
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


def calc_ema(closes: list, period: int) -> Optional[float]:
    if len(closes) < period:
        return None
    k = 2 / (period + 1)
    ema = closes[0]
    for i in range(1, len(closes)):
        ema = closes[i] * k + ema * (1 - k)
    return ema


def calc_macd(closes: list) -> tuple:
    if len(closes) < 26:
        return None, None
    ema12 = calc_ema(closes[:12], 12) or closes[0]
    ema26 = calc_ema(closes[:26], 26) or closes[0]
    dif = ema12 - ema26
    # DEA用最近9天DIF计算
    dif_list = []
    for i in range(26, len(closes)):
        ef12 = closes[i] * k if (k := 2/13) else 0
        ef26 = closes[i] * (2/27) if i > 0 else 0
        dif_list.append(calc_ema(closes[max(0,i-11):i+1], 12) - calc_ema(closes[max(0,i-25):i+1], 26) if i >= 25 else 0)
    dea = sum(dif_list[-9:]) / min(9, len(dif_list)) if dif_list else 0
    return dif, dea


def calc_cci(closes: list, period: int = 14) -> Optional[float]:
    if len(closes) < period:
        return None
    typical = closes[-1]
    sma = sum(closes[-period:]) / period
    mean_dev = sum(abs(c - sma) for c in closes[-period:]) / period
    if mean_dev == 0:
        return 0
    return (typical - sma) / (0.015 * mean_dev)


def calc_boll_pos(closes: list, period: int = 20) -> Optional[float]:
    if len(closes) < period:
        return None
    vals = closes[-period:]
    mid = sum(vals) / period
    std = math.sqrt(sum((v - mid) ** 2 for v in vals) / period)
    upper = mid + 2 * std
    lower = mid - 2 * std
    if upper == lower:
        return 1
    return (closes[-1] - lower) / (upper - lower)


def calc_vol_ratio(volumes: list, period: int = 20) -> Optional[float]:
    if len(volumes) < period:
        return None
    vol_ma = sum(volumes[-period:]) / period
    return volumes[-1] / vol_ma if vol_ma > 0 else 1


def get_stock_quote(symbol: str) -> Optional[dict]:
    """获取实时行情"""
    url = f"https://qt.gtimg.cn/q={symbol}"
    try:
        resp = requests.get(url, timeout=8)
        resp.encoding = "gbk"
        text = resp.text.strip()
        if not text or "none" in text:
            return None
        parts = text.split("~")
        if len(parts) < 10:
            return None
        return {
            "name": parts[1],
            "code": parts[2],
            "price": float(parts[3]) if parts[3] else 0,
            "yesterday_close": float(parts[4]) if parts[4] else 0,
            "change_pct": float(parts[32]) if len(parts) > 32 and parts[32] else 0,
        }
    except:
        return None


def analyze_stock(klines: list, quote: dict) -> Optional[Dict]:
    """分析单只股票"""
    if not klines or len(klines) < 30:
        return None
    
    try:
        closes = [float(k['close']) for k in klines]
        volumes = [int(k['volume']) for k in klines]
        
        if not closes or closes[-1] <= 0:
            return None
        
        # 昨日数据
        yesterday_close = closes[-2] if len(closes) >= 2 else closes[-1]
        pct_chg = (closes[-1] - yesterday_close) / yesterday_close * 100 if yesterday_close > 0 else 0
        
        # 计算指标
        ma5 = calc_ma(closes, 5)
        ma20 = calc_ma(closes, 20)
        cci = calc_cci(closes)
        boll_pos = calc_boll_pos(closes)
        vol_ratio = calc_vol_ratio(volumes)
        
        # 计算DIF
        ema12 = 0
        ema26 = 0
        if len(closes) >= 12:
            ema12 = calc_ema(closes, 12) or closes[0]
        if len(closes) >= 26:
            ema26 = calc_ema(closes, 26) or closes[0]
        dif = ema12 - ema26 if ema12 and ema26 else 0
        
        return {
            "close": closes[-1],
            "dif": dif,
            "ma5": ma5,
            "ma20": ma20,
            "cci": cci,
            "boll_pos": boll_pos,
            "vol_ratio": vol_ratio,
            "pct_chg": pct_chg,
        }
    except:
        return None


def check_buy_signal(metrics: Dict) -> bool:
    """策略B v5买入信号"""
    if not metrics:
        return False
    if metrics.get("dif", 0) <= 0:
        return False
    if not (metrics.get("ma5") and metrics.get("ma20") and metrics["ma5"] > metrics["ma20"]):
        return False
    if metrics.get("cci", 0) <= 0:
        return False
    if (metrics.get("vol_ratio") or 0) > 1.5:
        return False
    if (metrics.get("boll_pos") or 0) > 2.0:
        return False
    if (metrics.get("pct_chg") or 0) >= 9.5:
        return False
    return True


def get_portfolio() -> Dict:
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "cash": INITIAL_CASH,
        "positions": [],
        "trades": [],
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "last_update": datetime.now().strftime("%Y-%m-%d"),
    }


def save_portfolio(portfolio: Dict) -> None:
    portfolio["last_update"] = datetime.now().strftime("%Y-%m-%d")
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)


def check_sell_signal(position: Dict, current_price: float) -> tuple:
    buy_date = datetime.strptime(position["buy_date"], "%Y-%m-%d")
    hold_days = (datetime.now() - buy_date).days
    high_price = position.get("high_price", position["buy_price"])
    
    if hold_days >= HOLD_DAYS:
        return True, f"持有{hold_days}天到期"
    
    drawdown = (current_price - high_price) / high_price
    if drawdown <= -STOP_LOSS:
        return True, f"回落{abs(drawdown)*100:.1f}%止损"
    
    return False, ""


def screen_a_stocks() -> List[Dict]:
    """筛选全A股"""
    print("=" * 60)
    print("策略B v5 全A股筛选")
    print("=" * 60)
    
    # 获取A股列表
    print("\n📥 获取A股股票列表...")
    stocks = get_a_stock_list(max_stocks=6000)
    print(f"   获取到 {len(stocks)} 只股票")
    
    # 批量获取K线并筛选
    print("\n🔍 批量获取K线数据并筛选...")
    buy_signals = []
    checked = 0
    
    for i in range(0, len(stocks), 50):
        batch = stocks[i:i+50]
        klines_dict = batch_get_kline(batch)
        
        for symbol, klines in klines_dict.items():
            quote = get_stock_quote(symbol)
            name = quote.get('name', '') if quote else ''
            metrics = analyze_stock(klines, quote)
            
            if check_buy_signal(metrics):
                buy_signals.append({
                    "code": symbol,
                    "name": name,
                    "price": metrics["close"],
                    "dif": metrics["dif"],
                    "ma5": metrics["ma5"],
                    "ma20": metrics["ma20"],
                    "cci": metrics["cci"],
                    "vol_ratio": metrics["vol_ratio"],
                    "boll_pos": metrics["boll_pos"],
                    "pct_chg": metrics["pct_chg"],
                })
            
            checked += 1
            if checked % 200 == 0:
                print(f"   已检查 {checked}/{len(stocks)} 只，找到 {len(buy_signals)} 个买入信号")
        
        if len(buy_signals) >= MAX_POSITIONS * 2:  # 找到足够的候选
            break
    
    print(f"\n✅ 筛选完成: 共找到 {len(buy_signals)} 个买入信号")
    return buy_signals[:MAX_POSITIONS]


def run_daily_check() -> Dict:
    """每日检查"""
    portfolio = get_portfolio()
    today = datetime.now().strftime("%Y-%m-%d")
    is_first_run = len(portfolio["positions"]) == 0
    
    results = {
        "date": today,
        "positions": [],
        "sell_signals": [],
        "buy_signals": [],
        "cash": portfolio["cash"],
        "total_value": portfolio["cash"],
        "total_profit": 0,
        "total_profit_ratio": 0,
    }
    
    # 更新持仓盈亏
    for pos in portfolio["positions"]:
        quote = get_stock_quote(pos["code"])
        if quote and quote.get("price", 0) > 0:
            current_price = float(quote["price"])
            pos["current_price"] = current_price
            pos["profit_ratio"] = (current_price - pos["buy_price"]) / pos["buy_price"]
            pos["profit_amount"] = (current_price - pos["buy_price"]) * pos["shares"]
            pos["hold_days"] = (datetime.now() - datetime.strptime(pos["buy_date"], "%Y-%m-%d")).days
            pos["high_price"] = max(pos.get("high_price", pos["buy_price"]), current_price)
            
            is_sell, reason = check_sell_signal(pos, current_price)
            if is_sell:
                results["sell_signals"].append({
                    "code": pos["code"],
                    "name": pos["name"],
                    "buy_price": pos["buy_price"],
                    "current_price": current_price,
                    "profit_ratio": pos["profit_ratio"],
                    "profit_amount": pos["profit_amount"],
                    "reason": reason,
                })
            else:
                results["positions"].append(pos)
            
            results["total_value"] += current_price * pos["shares"]
        else:
            if "current_price" in pos:
                results["total_value"] += pos["current_price"] * pos["shares"]
            results["positions"].append(pos)
    
    # 执行卖出
    for sell in results["sell_signals"]:
        for pos in portfolio["positions"][:]:
            if pos["code"] == sell["code"]:
                sell_amount = sell["current_price"] * pos["shares"]
                portfolio["cash"] += sell_amount
                portfolio["trades"].append({
                    "date": today,
                    "code": pos["code"],
                    "name": pos["name"],
                    "action": "sell",
                    "price": sell["current_price"],
                    "shares": pos["shares"],
                    "profit": sell["profit_amount"],
                    "profit_ratio": sell["profit_ratio"],
                    "reason": sell["reason"],
                })
                portfolio["positions"].remove(pos)
                print(f"📤 卖出 {pos['name']}({pos['code']}): {sell['reason']}, 盈亏{sell['profit_ratio']*100:+.1f}%")
    
    # 筛选买入
    if len(portfolio["positions"]) < MAX_POSITIONS:
        if is_first_run:
            print(f"\n🚀 首次建仓，开始全A股筛选...")
        else:
            print(f"\n📊 持仓不满，继续筛选...")
        
        signals = screen_a_stocks()
        
        # 排除已有持仓
        existing_codes = [p["code"] for p in portfolio["positions"]]
        signals = [s for s in signals if s["code"] not in existing_codes]
        results["buy_signals"] = signals
        
        # 执行买入
        slots = MAX_POSITIONS - len(portfolio["positions"])
        cash_per = portfolio["cash"] / slots if slots > 0 else 0
        
        for sig in signals[:slots]:
            if sig["price"] < 1 or sig["price"] > 10000:  # 排除价格异常
                continue
            shares = int(cash_per / sig["price"] / 100) * 100
            if shares < 100:
                continue
            
            position = {
                "code": sig["code"],
                "name": sig["name"],
                "buy_price": sig["price"],
                "shares": shares,
                "buy_date": today,
                "high_price": sig["price"],
                "current_price": sig["price"],
                "profit_ratio": 0,
                "profit_amount": 0,
                "hold_days": 0,
            }
            portfolio["positions"].append(position)
            portfolio["cash"] -= sig["price"] * shares
            portfolio["trades"].append({
                "date": today,
                "code": sig["code"],
                "name": sig["name"],
                "action": "buy",
                "price": sig["price"],
                "shares": shares,
            })
            print(f"📥 买入 {sig['name']}({sig['code']}): {sig['price']} x {shares}股 = {sig['price']*shares:,.0f}")
    
    save_portfolio(portfolio)
    
    results["total_profit"] = results["total_value"] - INITIAL_CASH
    results["total_profit_ratio"] = results["total_profit"] / INITIAL_CASH
    results["cash"] = portfolio["cash"]
    results["position_count"] = len(portfolio["positions"])
    
    return results


def get_summary() -> Dict:
    portfolio = get_portfolio()
    today = datetime.now().strftime("%Y-%m-%d")
    
    total_value = portfolio["cash"]
    positions_detail = []
    
    for pos in portfolio["positions"]:
        quote = get_stock_quote(pos["code"])
        if quote and quote.get("price", 0) > 0:
            current_price = float(quote["price"])
        else:
            current_price = pos.get("current_price", pos["buy_price"])
        
        pos["current_price"] = current_price
        pos["profit_ratio"] = (current_price - pos["buy_price"]) / pos["buy_price"]
        pos["profit_amount"] = (current_price - pos["buy_price"]) * pos["shares"]
        pos["hold_days"] = (datetime.now() - datetime.strptime(pos["buy_date"], "%Y-%m-%d")).days
        pos["high_price"] = max(pos.get("high_price", pos["buy_price"]), current_price)
        total_value += current_price * pos["shares"]
        positions_detail.append(pos)
    
    total_profit = total_value - INITIAL_CASH
    total_profit_ratio = total_profit / INITIAL_CASH
    
    sell_trades = [t for t in portfolio["trades"] if t["action"] == "sell"]
    winning_trades = [t for t in sell_trades if t.get("profit", 0) > 0]
    
    return {
        "date": today,
        "initial_cash": INITIAL_CASH,
        "cash": portfolio["cash"],
        "positions": positions_detail,
        "total_value": total_value,
        "total_profit": total_profit,
        "total_profit_ratio": total_profit_ratio,
        "buy_count": len([t for t in portfolio["trades"] if t["action"] == "buy"]),
        "sell_count": len(sell_trades),
        "winning_count": len(winning_trades),
        "losing_count": len(sell_trades) - len(winning_trades),
        "win_rate": len(winning_trades) / len(sell_trades) if sell_trades else 0,
        "trades": portfolio["trades"],
    }


if __name__ == "__main__":
    print("=" * 60)
    print("策略B v5 模拟盘 - 全A股筛选版")
    print("=" * 60)
    
    results = run_daily_check()
    print(f"\n📊 今日操作:")
    print(f"  买入: {len(results['buy_signals'])} 只")
    print(f"  卖出: {len(results['sell_signals'])} 只")
    print(f"\n💰 当前账户:")
    print(f"  现金: {results['cash']:,.0f}")
    print(f"  总市值: {results['total_value']:,.0f}")
    print(f"  盈亏: {results['total_profit']:+,.0f} ({results['total_profit_ratio']*100:+.2f}%)")
    print(f"  持仓: {results['position_count']}/{MAX_POSITIONS} 只")
