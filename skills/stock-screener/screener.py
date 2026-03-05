"""
股票月线趋势筛选器主程序
"""
import os
import json
import pandas as pd
from datetime import datetime
from tqdm import tqdm

import config
from data_fetcher import get_stock_list, get_monthly_kline
from indicators import (
    calculate_ma, calculate_macd, calculate_kdj,
    check_macd_golden_cross, check_kdj_golden_cross,
    check_ma_alignment, check_volume_increase, get_latest_indicators
)


def screen_stock(stock_code, stock_name):
    """
    筛选单个股票，支持分级筛选
    
    Returns:
        dict or None: 符合条件的股票信息
    """
    # 获取月线数据
    data = get_monthly_kline(stock_code)
    if data is None or len(data) < 25:
        return None
    
    # 计算指标
    data = calculate_ma(data, config.MA_PERIODS)
    data = calculate_macd(data)
    data = calculate_kdj(data)
    
    # 检查筛选条件
    macd_cross = check_macd_golden_cross(data)
    kdj_cross = check_kdj_golden_cross(data)
    ma_aligned = check_ma_alignment(data)
    volume_up = check_volume_increase(data)
    
    # 分级筛选逻辑
    # A级（最佳）：MACD + KDJ 双金叉 + 均线多头排列 + 成交量放大
    if macd_cross and kdj_cross and ma_aligned and volume_up:
        indicators = get_latest_indicators(data)
        return {
            'code': stock_code,
            'name': stock_name,
            'screen_date': datetime.now().strftime('%Y-%m-%d'),
            'grade': 'A',  # 最佳
            'grade_desc': 'MACD+KDJ双金叉，均线多头排列，成交量放大',
            'position_suggestion': '首次建仓不超过30%，确认趋势后分批加仓',
            'indicators': indicators,
            'signals': {
                'macd_golden_cross': macd_cross,
                'kdj_golden_cross': kdj_cross,
                'ma_alignment': ma_aligned,
                'volume_increase': volume_up
            }
        }
    
    # B级（可接受）：MACD金叉 + 均线多头排列（KDJ可滞后）+ 成交量放大
    if macd_cross and ma_aligned and volume_up:
        indicators = get_latest_indicators(data)
        return {
            'code': stock_code,
            'name': stock_name,
            'screen_date': datetime.now().strftime('%Y-%m-%d'),
            'grade': 'B',  # 可接受
            'grade_desc': 'MACD金叉+均线多头排列，KDJ滞后',
            'position_suggestion': '首次建仓不超过20%，等待KDJ金叉确认后加仓',
            'indicators': indicators,
            'signals': {
                'macd_golden_cross': macd_cross,
                'kdj_golden_cross': kdj_cross,
                'ma_alignment': ma_aligned,
                'volume_increase': volume_up
            }
        }
    
    # C级（观察）：KDJ金叉 + 均线多头排列（MACD滞后）+ 成交量放大
    if kdj_cross and ma_aligned and volume_up:
        indicators = get_latest_indicators(data)
        return {
            'code': stock_code,
            'name': stock_name,
            'screen_date': datetime.now().strftime('%Y-%m-%d'),
            'grade': 'C',  # 观察
            'grade_desc': 'KDJ金叉+均线多头排列，MACD滞后（适合MACD不敏感场景）',
            'position_suggestion': '首次建仓不超过15%，等待MACD金叉确认后加仓，或作为观察标的',
            'indicators': indicators,
            'signals': {
                'macd_golden_cross': macd_cross,
                'kdj_golden_cross': kdj_cross,
                'ma_alignment': ma_aligned,
                'volume_increase': volume_up
            }
        }
    
    return None


def run_screening(max_stocks=None):
    """
    运行全市场筛选
    
    Args:
        max_stocks: 最大筛选股票数，None表示全部
    
    Returns:
        list: 符合条件的股票列表
    """
    print("正在获取股票列表...")
    stock_list = get_stock_list()
    
    if max_stocks:
        stock_list = stock_list.head(max_stocks)
    
    print(f"共 {len(stock_list)} 只股票，开始筛选...")
    
    results = []
    for _, row in tqdm(stock_list.iterrows(), total=len(stock_list)):
        result = screen_stock(row['code'], row['name'])
        if result:
            results.append(result)
            print(f"✓ {row['code']} {row['name']} 符合条件")
    
    return results


def save_results(results, output_dir=config.OUTPUT_DIR):
    """保存筛选结果"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # JSON格式
    json_file = os.path.join(output_dir, f'screening_{timestamp}.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # CSV格式
    if results:
        csv_data = []
        for r in results:
            row = {
                '代码': r['code'],
                '名称': r['name'],
                '评级': r.get('grade', ''),
                '评级说明': r.get('grade_desc', ''),
                '仓位建议': r.get('position_suggestion', ''),
                '筛选日期': r['screen_date'],
                '收盘价': r['indicators']['close'],
                'MA5': r['indicators']['ma5'],
                'MA10': r['indicators']['ma10'],
                'MA20': r['indicators']['ma20'],
                'MACD_DIF': r['indicators']['macd_dif'],
                'MACD_DEA': r['indicators']['macd_dea'],
                'KDJ_K': r['indicators']['kdj_k'],
                'KDJ_D': r['indicators']['kdj_d'],
                '成交量': r['indicators']['volume']
            }
            csv_data.append(row)
        
        df = pd.DataFrame(csv_data)
        csv_file = os.path.join(output_dir, f'screening_{timestamp}.csv')
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\nCSV结果已保存: {csv_file}")
    
    print(f"JSON结果已保存: {json_file}")
    return json_file


if __name__ == '__main__':
    # 运行筛选
    results = run_screening(max_stocks=config.MAX_STOCKS)
    
    print(f"\n筛选完成！共 {len(results)} 只股票符合条件")
    
    if results:
        save_results(results)
        
        print("\n符合条件的股票:")
        for r in results:
            grade = r.get('grade', 'N/A')
            if grade == 'A':
                grade_icon = "★"
            elif grade == 'B':
                grade_icon = "☆"
            else:
                grade_icon = "○"
            print(f"  {grade_icon} [{grade}] {r['code']} {r['name']} - 收盘价: {r['indicators']['close']}")
            print(f"     建议: {r.get('position_suggestion', '')}")
    else:
        print("\n当前没有符合条件的股票")