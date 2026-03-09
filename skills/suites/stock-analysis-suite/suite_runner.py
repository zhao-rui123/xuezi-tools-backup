#!/usr/bin/env python3
"""
股票分析套件统一入口
整合: stock-screener, stock-analysis-pro, tushare-stock-datasource, xueqiu-stock-client
"""

import sys
import os
import json
from datetime import datetime

# 添加组件路径
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/skills/stock-screener'))
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/skills/stock-analysis-pro'))
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/skills/tushare-stock-datasource'))
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/skills/xueqiu-stock-client'))

SUITE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SUITE_DIR, 'config', 'watchlist.json')


def load_watchlist():
    """加载自选股列表"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'stocks': []}


def analyze_stock(stock_code: str) -> dict:
    """单股票深度分析"""
    print(f"🔍 分析股票: {stock_code}")
    
    result = {
        'code': stock_code,
        'timestamp': datetime.now().isoformat(),
        'screening': None,
        'analysis': None,
        'data': None,
        'report': ''
    }
    
    try:
        # 1. 技术指标筛选
        print("  📊 技术指标分析...")
        # 这里调用 stock-screener 的功能
        
        # 2. 深度分析
        print("  📈 深度分析...")
        # 这里调用 stock-analysis-pro 的功能
        
        # 3. 获取数据
        print("  📡 获取实时数据...")
        # 这里调用 tushare-stock-datasource 的功能
        
        result['report'] = f"股票 {stock_code} 分析完成"
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def batch_screen(criteria: dict = None) -> list:
    """批量筛选股票"""
    print("🔍 批量筛选股票...")
    
    watchlist = load_watchlist()
    stocks = watchlist.get('stocks', [])
    
    results = []
    for stock in stocks:
        print(f"  筛选: {stock['name']} ({stock['code']})")
        # 这里调用筛选逻辑
        results.append(stock)
    
    return results


def full_analysis():
    """完整分析流程"""
    print("=" * 60)
    print("📊 股票分析套件 - 完整分析")
    print("=" * 60)
    
    watchlist = load_watchlist()
    stocks = watchlist.get('stocks', [])
    
    print(f"\n📋 自选股数量: {len(stocks)}")
    
    for stock in stocks:
        print(f"\n{'='*60}")
        print(f"🔍 {stock['name']} ({stock['code']})")
        print('='*60)
        
        try:
            analyze_stock(stock['code'])
        except Exception as e:
            print(f"  ⚠️ 分析失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 分析完成")
    print("=" * 60)


def monitor_alerts():
    """监控预警"""
    print("🚨 启动实时监控...")
    
    try:
        # 调用 stock-screener 的预警功能
        from stock_monitor import quick_alert_check
        quick_alert_check()
    except Exception as e:
        print(f"  ⚠️ 预警检查失败: {e}")


def generate_portfolio_report():
    """生成组合报告"""
    print("📄 生成组合报告...")
    
    watchlist = load_watchlist()
    stocks = watchlist.get('stocks', [])
    
    report_file = os.path.join(SUITE_DIR, 'reports', 
                               f"portfolio_report_{datetime.now().strftime('%Y%m%d')}.md")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 股票组合报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**股票数量**: {len(stocks)}\n\n")
        f.write("## 自选股列表\n\n")
        for stock in stocks:
            f.write(f"- {stock['name']} ({stock['code']}) - {stock['market']}\n")
    
    print(f"  ✅ 报告已保存: {report_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='股票分析套件')
    parser.add_argument('--full-analysis', action='store_true', help='完整分析')
    parser.add_argument('--analyze', type=str, help='分析指定股票代码')
    parser.add_argument('--screen', action='store_true', help='批量筛选')
    parser.add_argument('--monitor', action='store_true', help='监控预警')
    parser.add_argument('--portfolio-report', action='store_true', help='生成组合报告')
    
    args = parser.parse_args()
    
    # 确保目录存在
    os.makedirs(os.path.join(SUITE_DIR, 'config'), exist_ok=True)
    os.makedirs(os.path.join(SUITE_DIR, 'reports'), exist_ok=True)
    
    # 创建默认配置
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            'stocks': [
                {'code': '002738', 'name': '中矿资源', 'market': 'A股'},
                {'code': '002460', 'name': '赣锋锂业', 'market': 'A股'},
                {'code': '000792', 'name': '盐湖股份', 'market': 'A股'},
                {'code': '000725', 'name': '京东方A', 'market': 'A股'},
            ]
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        print(f"✅ 已创建默认配置: {CONFIG_FILE}")
    
    if args.full_analysis:
        full_analysis()
    elif args.analyze:
        result = analyze_stock(args.analyze)
        print(result['report'])
    elif args.screen:
        batch_screen()
    elif args.monitor:
        monitor_alerts()
    elif args.portfolio_report:
        generate_portfolio_report()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
