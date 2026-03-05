"""
完整分析流程 - 筛选+基本面分析+卖出策略+周期股分析+完整技术指标
"""
import os
import json
from datetime import datetime
from tqdm import tqdm

import config
from screener import run_screening, save_results
from fundamentals import analyze_stock_fundamentals
from analysis_report import generate_fundamental_summary, generate_investment_recommendation
from sell_strategy import generate_sell_signals, PositionManager
from cyclical_analysis import analyze_expectation_gap
from technical_indicators import calculate_all_indicators, get_all_signals, get_latest_all_indicators
from pattern_recognition import analyze_all_patterns
from support_resistance import analyze_support_resistance


def run_full_analysis(max_stocks=None, analyze_fundamentals=True, check_sell_signals=True, check_cyclical=True):
    """
    运行完整分析流程
    
    Args:
        max_stocks: 最大筛选股票数
        analyze_fundamentals: 是否进行基本面分析
        check_sell_signals: 是否检查卖出信号
        check_cyclical: 是否进行周期股预期差分析
    
    Returns:
        list: 完整分析结果
    """
    # 第一步：技术面筛选
    print("=" * 50)
    print("第一步：技术面筛选")
    print("=" * 50)
    
    screening_results = run_screening(max_stocks=max_stocks)
    
    if not screening_results:
        print("\n没有符合技术面条件的股票")
        return []
    
    print(f"\n技术面筛选完成，{len(screening_results)} 只股票符合条件")
    
    # 第二步：基本面分析 + 卖出信号 + 周期股分析 + 完整技术指标
    full_results = []
    for result in tqdm(screening_results, desc="综合分析"):
        stock_code = result['code']
        stock_name = result['name']
        
        # 获取月线数据
        from data_fetcher import get_monthly_kline
        monthly_data = get_monthly_kline(stock_code)
        
        if monthly_data is not None and len(monthly_data) >= 25:
            # 计算所有技术指标
            monthly_data = calculate_all_indicators(monthly_data)
            
            # 获取所有指标值
            all_indicators = get_latest_all_indicators(monthly_data)
            
            # 获取所有信号
            all_signals = get_all_signals(monthly_data)
            
            # K线形态识别
            patterns = analyze_all_patterns(monthly_data)
            
            # 卖出信号分析
            sell_signals = generate_sell_signals(monthly_data)
            
            # 支撑压力位分析
            sr_analysis = analyze_support_resistance(monthly_data)
        else:
            all_indicators = result.get('indicators', {})
            all_signals = result.get('signals', {})
            patterns = []
            sell_signals = {}
            sr_analysis = {}
        
        # 基本面分析
        if analyze_fundamentals:
            fundamental_data = analyze_stock_fundamentals(stock_code)
            recommendation = generate_investment_recommendation(result, fundamental_data)
            fundamental_summary = generate_fundamental_summary(stock_code, stock_name, fundamental_data)
        else:
            fundamental_data = {}
            recommendation = {}
            fundamental_summary = ""
        
        # 周期股预期差分析
        cyclical_analysis = {}
        if check_cyclical:
            cyclical_analysis = analyze_expectation_gap(stock_code, stock_name)
        
        # 合并结果
        full_result = {
            **result,
            'all_indicators': all_indicators,
            'all_signals': all_signals,
            'patterns': patterns,
            'support_resistance': sr_analysis,
            'fundamental_analysis': fundamental_data,
            'fundamental_summary': fundamental_summary,
            'investment_recommendation': recommendation,
            'sell_signals': sell_signals,
            'cyclical_analysis': cyclical_analysis
        }
        
        full_results.append(full_result)
        
        # 打印简要信息
        print(f"\n{stock_code} {stock_name}:")
        print(f"  评级: {result.get('grade', 'N/A')} - {result.get('grade_desc', '')}")
        print(f"  仓位建议: {result.get('position_suggestion', '')}")
        if patterns:
            print(f"  识别形态: {', '.join([p['pattern'] for p in patterns])}")
        if recommendation:
            print(f"  综合评级: {recommendation.get('overall_rating', 'N/A')}")
        if cyclical_analysis:
            print(f"  周期股预期差评分: {cyclical_analysis.get('score', 0)}/100")
    
    return full_results


def save_full_results(results, output_dir=config.OUTPUT_DIR):
    """保存完整分析结果"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存完整JSON
    json_file = os.path.join(output_dir, f'full_analysis_{timestamp}.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 生成可读报告
    report_file = os.path.join(output_dir, f'report_{timestamp}.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"股票筛选分析报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"共筛选出 {len(results)} 只股票\n")
        f.write("=" * 60 + "\n\n")
        
        for i, r in enumerate(results, 1):
            f.write(f"\n{'='*60}\n")
            f.write(f"【{i}】{r['code']} {r['name']}\n")
            f.write(f"{'='*60}\n\n")
            
            # 评级和仓位
            f.write("【筛选评级】\n")
            f.write(f"评级: {r.get('grade', 'N/A')} - {r.get('grade_desc', '')}\n")
            f.write(f"仓位建议: {r.get('position_suggestion', '')}\n\n")
            
            # K线形态
            if r.get('patterns'):
                f.write("【K线形态识别】\n")
                for p in r['patterns']:
                    f.write(f"  - {p['pattern']}: {p['signal']}\n")
                    if p.get('target_price'):
                        f.write(f"    目标价: ¥{p['target_price']}\n")
                f.write("\n")
            
            # 技术面指标
            f.write("【技术面指标】\n")
            indicators = r.get('all_indicators', r.get('indicators', {}))
            f.write(f"收盘价: {indicators.get('close')}\n")
            f.write(f"MA5: {indicators.get('ma5')} | MA10: {indicators.get('ma10')} | MA20: {indicators.get('ma20')}\n")
            f.write(f"MACD DIF: {indicators.get('macd_dif')} | DEA: {indicators.get('macd_dea')}\n")
            f.write(f"KDJ K: {indicators.get('kdj_k')} | D: {indicators.get('kdj_d')} | J: {indicators.get('kdj_j')}\n")
            f.write(f"RSI14: {indicators.get('rsi14')}\n")
            f.write(f"成交量: {indicators.get('volume')}\n\n")
            
            # 投资建议
            rec = r.get('investment_recommendation', {})
            if rec:
                f.write("【投资建议】\n")
                f.write(f"技术面评分: {rec.get('technical_score')}/100\n")
                f.write(f"基本面评分: {rec.get('fundamental_score')}/100\n")
                f.write(f"综合评级: {rec.get('overall_rating')}\n")
                f.write(f"建议: {rec.get('suggestion')}\n\n")
            
            # 卖出信号
            sell = r.get('sell_signals', {})
            if sell:
                f.write("【卖出/减仓信号监控】\n")
                deviation = sell.get('deviation_from_ma5')
                if deviation:
                    f.write(f"偏离5月均线: {deviation}%\n")
                f.write(f"KDJ超买: {'是' if sell.get('kdj_overbought') else '否'}\n")
                f.write(f"KDJ死叉: {'是' if sell.get('kdj_bearish_cross') else '否'}\n")
                f.write(f"MACD死叉: {'是' if sell.get('macd_bearish_cross') else '否'}\n")
                f.write(f"跌破20月均线: {'是' if sell.get('price_below_ma20') else '否'}\n")
                
                suggestions = sell.get('suggestions', [])
                if suggestions:
                    f.write("操作建议:\n")
                    for s in suggestions:
                        f.write(f"  - [{s.get('priority')}] {s.get('type')}: {s.get('action')}\n")
                f.write("\n")
            
            # 周期股预期差
            cyclical = r.get('cyclical_analysis', {})
            if cyclical and cyclical.get('score', 0) > 0:
                f.write("【周期股预期差分析】\n")
                f.write(f"预期差评分: {cyclical.get('score')}/100\n")
                f.write(f"机会等级: {cyclical.get('opportunity_level')}\n")
                f.write(f"建议: {cyclical.get('suggestion')}\n")
                
                pe = cyclical.get('pe_analysis', {})
                if pe:
                    f.write(f"PE分析: 当前{pe.get('current_pe')} (历史分位{pe.get('pe_percentile')}%)\n")
                
                price = cyclical.get('price_analysis', {})
                if price:
                    f.write(f"价格分析: 较高点下跌{price.get('decline_pct')}%\n")
                f.write("\n")
            
            # 基本面摘要
            if 'fundamental_summary' in r and r['fundamental_summary']:
                f.write("【基本面分析】\n")
                f.write(r['fundamental_summary'])
                f.write("\n\n")
    
    print(f"\n完整分析结果已保存: {json_file}")
    print(f"可读报告已保存: {report_file}")
    
    return json_file, report_file


if __name__ == '__main__':
    # 运行完整分析
    results = run_full_analysis(max_stocks=config.MAX_STOCKS, analyze_fundamentals=True)
    
    if results:
        save_full_results(results)
        
        print("\n" + "=" * 50)
        print("分析完成！")
        print("=" * 50)
        print(f"共 {len(results)} 只股票通过筛选")
        print("\n推荐股票:")
        for r in results:
            rec = r.get('investment_recommendation', {})
            if rec.get('overall_rating') in ['强烈推荐', '推荐']:
                print(f"  ★ {r['code']} {r['name']} - {rec.get('overall_rating')}")