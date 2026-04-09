"""
每日更新模拟盘到Obsidian
- 持仓盈亏比和盈亏金额
- 交易记录
"""

import os
import sys
from datetime import datetime
import subprocess

SIMULATOR_DIR = os.path.dirname(os.path.abspath(__file__))
OBSIDIAN_DIR = "/BOSI/zhaorui/生活投资/模拟策略/"
WEBDAV_SH = os.path.expanduser("~/.openclaw/workspace/obsidian-webdav/webdav.sh")


def webdav_upload(remote_path: str, content: str) -> bool:
    """上传内容到WebDAV"""
    import urllib.parse
    
    tmp_file = "/tmp/obsidian_upload.md"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    # 确保目录存在 - 使用curl MKCOL
    dir_path = os.path.dirname(remote_path)
    encoded_dir = urllib.parse.quote(dir_path, safe='/')
    # 坚果云WebDAV地址
    webdav_base = "https://dav.jianguoyun.com/dav"
    full_dir_url = webdav_base + encoded_dir
    
    # 创建目录
    result = subprocess.run(
        ["curl", "-s", "-u", "1034440765@qq.com:ai7eaer5mv2gixex", "-X", "MKCOL", full_dir_url],
        capture_output=True,
        text=True
    )
    # 目录可能已存在，忽略错误
    
    # 上传文件
    encoded_path = urllib.parse.quote(remote_path, safe='/')
    full_url = webdav_base + encoded_path
    result = subprocess.run(
        ["curl", "-s", "-u", "1034440765@qq.com:ai7eaer5mv2gixex", "-X", "PUT", "-T", tmp_file, full_url],
        capture_output=True,
        text=True
    )
    return True  # PUT成功时返回空


def create_daily_note(summary: dict) -> str:
    """创建每日模拟盘笔记"""
    date = summary["date"]
    
    # 格式化日期
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    date_str = date_obj.strftime("%Y年%m月%d日")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
    
    # 计算胜率
    win_rate = summary["win_rate"] * 100 if summary["win_rate"] else 0
    
    content = f"""# 模拟盘日报 - {date_str} {weekday}

## 账户概览

| 指标 | 数值 |
|------|------|
| 日期 | {date} |
| 初始资金 | {summary['initial_cash']:,.0f} |
| 当前现金 | {summary['cash']:,.0f} |
| 总市值 | {summary['total_value']:,.0f} |
| 总盈亏 | {summary['total_profit']:+,.0f} |
| 盈亏比例 | {summary['total_profit_ratio']*100:+.2f}% |

## 持仓明细

| 股票 | 代码 | 买入价 | 现价 | 持有天数 | 盈亏金额 | 盈亏比例 | 买入日期 |
|------|------|--------|------|----------|----------|----------|----------|
"""
    
    if summary["positions"]:
        for pos in summary["positions"]:
            content += f"| {pos['name']} | {pos['code'].upper()} | {pos['buy_price']:.2f} | {pos.get('current_price', pos['buy_price']):.2f} | {pos.get('hold_days', 0)}天 | {pos.get('profit_amount', 0):+,.0f} | {pos.get('profit_ratio', 0)*100:+.1f}% | {pos['buy_date']} |\n"
    else:
        content += "| - | - | - | - | - | - | - | - |\n"
    
    content += f"""
## 交易统计

| 指标 | 数值 |
|------|------|
| 买入次数 | {summary['buy_count']} |
| 卖出次数 | {summary['sell_count']} |
| 盈利次数 | {summary['winning_count']} |
| 亏损次数 | {summary['losing_count']} |
| 胜率 | {win_rate:.1f}% |

"""
    
    # 最近交易记录
    if summary.get("trades"):
        recent_trades = summary["trades"][-10:]  # 最近10笔
        content += "## 最近交易\n\n"
        content += "| 日期 | 股票 | 操作 | 价格 | 数量 | 盈亏 | 原因 |\n"
        content += "|------|------|------|------|------|------|------|\n"
        for t in reversed(recent_trades):
            if t["action"] == "sell":
                profit_str = f"{t.get('profit_ratio', 0)*100:+.1f}%"
                reason = t.get("reason", "")
            else:
                profit_str = "-"
                reason = "-"
            content += f"| {t['date']} | {t['name']} | {'买入' if t['action']=='buy' else '卖出'} | {t['price']:.2f} | {t['shares']} | {profit_str} | {reason} |\n"
    
    content += f"""
---
_策略B v5模拟盘 | 自动更新于 {datetime.now().strftime('%H:%M')}_
"""
    return content


def create_portfolio_summary(summary: dict) -> str:
    """创建持仓汇总笔记"""
    win_rate = summary["win_rate"] * 100 if summary["win_rate"] else 0
    
    content = f"""# 策略B v5 模拟盘汇总

## 策略规则

**买入条件**：
1. MACD.DIF > 0（零轴上方）
2. MA(5) > MA(20)（均线多头）
3. CCI(14) > 0
4. 均量 <= 1.5x MA20（过热过滤）
5. boll_pos <= 2.0（不追高过滤）
6. 排除涨停开盘

**卖出条件**：
- 持有15个交易日 **或**
- 买入后从最高点回落8%止损

---

## 当前状态

| 指标 | 数值 |
|------|------|
| 更新日期 | {summary['date']} |
| 初始资金 | {summary['initial_cash']:,.0f} |
| 当前现金 | {summary['cash']:,.0f} |
| 当前总市值 | {summary['total_value']:,.0f} |
| 总盈亏 | {summary['total_profit']:+,.0f} |
| 盈亏比例 | {summary['total_profit_ratio']*100:+.2f}% |
| 当前持仓 | {len(summary['positions'])}只 |

"""
    
    if summary["positions"]:
        content += "## 持仓明细\n\n"
        content += "| 股票 | 代码 | 买入价 | 现价 | 持有天数 | 盈亏金额 | 盈亏比例 | 最高价 |\n"
        content += "|------|------|--------|------|----------|----------|----------|--------|\n"
        for pos in summary["positions"]:
            content += f"| {pos['name']} | {pos['code'].upper()} | {pos['buy_price']:.2f} | {pos.get('current_price', pos['buy_price']):.2f} | {pos.get('hold_days', 0)}天 | {pos.get('profit_amount', 0):+,.0f} | {pos.get('profit_ratio', 0)*100:+.1f}% | {pos.get('high_price', pos['buy_price']):.2f} |\n"
        content += "\n"
    
    content += f"""
## 历史表现

| 指标 | 数值 |
|------|------|
| 买入次数 | {summary['buy_count']} |
| 卖出次数 | {summary['sell_count']} |
| 盈利次数 | {summary['winning_count']} |
| 亏损次数 | {summary['losing_count']} |
| 胜率 | {win_rate:.1f}% |

"""
    
    # 最近交易记录
    if summary.get("trades"):
        recent_trades = summary["trades"][-20:]  # 最近20笔
        content += "## 最近交易\n\n"
        content += "| 日期 | 股票 | 操作 | 价格 | 数量 | 盈亏 | 原因 |\n"
        content += "|------|------|------|------|------|------|------|\n"
        for t in reversed(recent_trades):
            if t["action"] == "sell":
                profit_str = f"{t.get('profit_ratio', 0)*100:+.1f}%"
                reason = t.get("reason", "")
            else:
                profit_str = "-"
                reason = "-"
            content += f"| {t['date']} | {t['name']} | {'买入' if t['action']=='buy' else '卖出'} | {t['price']:.2f} | {t['shares']} | {profit_str} | {reason} |\n"
    
    content += f"""
---
_最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}_
"""
    return content


def main():
    sys.path.insert(0, SIMULATOR_DIR)
    from core import get_summary
    
    print("=" * 50)
    print("更新模拟盘到Obsidian")
    print("=" * 50)
    
    # 获取汇总数据
    summary = get_summary()
    print(f"\n当前状态:")
    print(f"  总市值: {summary['total_value']:,.0f}")
    print(f"  盈亏: {summary['total_profit']:+,.0f} ({summary['total_profit_ratio']*100:+.2f}%)")
    print(f"  持仓: {len(summary['positions'])}只")
    
    # 只更新汇总文件，不创建每日文件
    summary_note = create_portfolio_summary(summary)
    summary_path = f"{OBSIDIAN_DIR}模拟盘汇总.md"
    if webdav_upload(summary_path, summary_note):
        print(f"✅ 汇总已更新: 模拟盘汇总.md")
    else:
        print(f"⚠️ 汇总上传失败")


if __name__ == "__main__":
    main()
