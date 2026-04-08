#!/usr/bin/env python3
"""量化技术指标筛选器 - 命令行入口"""

import argparse
import json
import os
import sys
import yaml

# 添加项目根目录到路径
sys.path.insert(0, '/opt/stock-indicator-screener')

from screener import StockScreener

BASE_DIR = '/opt/stock-indicator-screener'


def load_watchlist():
    """从配置文件加载自选股"""
    config_path = os.path.join(BASE_DIR, 'config', 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return [c['ts_code'] for c in config.get('watchlist', [])]
    return []


def format_results(results_df):
    """格式化输出结果"""
    if results_df.empty:
        print("未找到符合条件的股票")
        return

    print("=" * 70)
    print("【量化技术指标筛选结果】")
    print("=" * 70)

    for idx, row in results_df.iterrows():
        print(f"\n{'─' * 70}")
        print(f"  {idx + 1}. {row['name']} ({row['code']})")
        print(f"     最新价: {row['close']}  |  信号数: {row['score']}")

        # 按买入/卖出分类显示信号
        buy_signals = [s for s in row['signals'] if s['signal'] == 1]
        sell_signals = [s for s in row['signals'] if s['signal'] == -1]

        if buy_signals:
            labels = ' '.join([s['desc'] for s in buy_signals])
            print(f"     📈 买入信号: {labels}")
        if sell_signals:
            labels = ' '.join([s['desc'] for s in sell_signals])
            print(f"     📉 卖出信号: {labels}")

    print(f"\n{'─' * 70}")
    print(f"共找到 {len(results_df)} 只股票")
    print(f"{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(
        description='股票技术指标筛选器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 run_screener.py                           # 使用配置文件中的自选股
  python3 run_screener.py --codes 002594.SZ,002460.SZ  # 指定股票代码
  python3 run_screener.py --min-signals 2          # 最少2个信号
  python3 run_screener.py --codes 002594.SZ --min-signals 1
        """
    )
    parser.add_argument(
        '--codes', type=str,
        help='股票代码，逗号分隔，如 002594.SZ,002460.SZ'
    )
    parser.add_argument(
        '--min-signals', type=int, default=1,
        help='最少信号数量（默认1）'
    )
    parser.add_argument(
        '--json', action='store_true',
        help='以JSON格式输出结果'
    )
    parser.add_argument(
        '--feishu', action='store_true',
        help='发送飞书通知'
    )

    args = parser.parse_args()

    # 确定要筛选的股票列表
    if args.codes:
        codes = [c.strip() for c in args.codes.split(',')]
    else:
        codes = load_watchlist()
        if not codes:
            print("错误: 配置文件为空，请使用 --codes 参数指定股票代码")
            sys.exit(1)

    print(f"📊 正在筛选 {len(codes)} 只股票 (最少信号数: {args.min_signals})...")
    print()

    screener = StockScreener()
    results = screener.screen(codes, args.min_signals)

    if args.json:
        # JSON格式输出
        json_results = results.to_json(orient='records', force_ascii=False, date_format='iso')
        print(json_results)
    else:
        format_results(results)

    # 发送飞书通知
    if args.feishu and results is not None and len(results) > 0:
        send_feishu_notification(results)


# 飞书通知
def send_feishu_notification(results_df):
    if results_df.empty:
        return
    try:
        from feishu_sender import FeishuSender
        sender = FeishuSender()
        sender.send_stock_report(results_df)
        print("✅ 已发送飞书通知")
    except Exception as e:
        print(f"⚠️ 飞书通知发送失败: {e}")


if __name__ == '__main__':
    main()
