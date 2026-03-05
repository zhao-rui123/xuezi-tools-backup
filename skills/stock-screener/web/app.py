"""
Flask Web应用 - 股票筛选器后端
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import sys
import json
import pandas as pd
from datetime import datetime

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screener import run_screening
from full_analysis import run_full_analysis

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
CORS(app)

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
os.makedirs(DATA_DIR, exist_ok=True)


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/screen', methods=['POST'])
def api_screen():
    """运行筛选"""
    try:
        # 运行完整分析（限制股票数量以加快速度）
        results = run_full_analysis(
            max_stocks=100,  # 测试时限制数量
            analyze_fundamentals=True,
            check_sell_signals=True,
            check_cyclical=True
        )
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = os.path.join(DATA_DIR, f'screening_{timestamp}.json')
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'count': len(results),
                'results': results
            }, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
def api_history():
    """获取历史筛选记录"""
    try:
        files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json')], reverse=True)
        
        history = []
        for f in files[:10]:  # 最近10次
            with open(os.path.join(DATA_DIR, f), 'r', encoding='utf-8') as file:
                data = json.load(file)
                history.append({
                    'file': f,
                    'timestamp': data.get('timestamp'),
                    'count': data.get('count', 0)
                })
        
        return jsonify({
            'success': True,
            'history': history
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history/<filename>', methods=['GET'])
def api_history_detail(filename):
    """获取历史记录详情"""
    try:
        file_path = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/<stock_code>', methods=['GET'])
def api_stock_detail(stock_code):
    """获取单个股票详情"""
    try:
        # 从最新结果中查找
        files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json')], reverse=True)
        
        if not files:
            return jsonify({
                'success': False,
                'error': '暂无数据'
            }), 404
        
        with open(os.path.join(DATA_DIR, files[0]), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stock = next((s for s in data.get('results', []) if s['code'] == stock_code), None)
        
        if not stock:
            return jsonify({
                'success': False,
                'error': '股票未找到'
            }), 404
        
        return jsonify({
            'success': True,
            'stock': stock
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/<stock_code>/kline', methods=['GET'])
def api_stock_kline(stock_code):
    """获取股票K线数据"""
    try:
        from data_fetcher import get_monthly_kline
        from indicators import calculate_ma, calculate_macd, calculate_kdj
        
        data = get_monthly_kline(stock_code)
        if data is None or len(data) < 20:
            return jsonify({
                'success': False,
                'error': '数据不足'
            }), 404
        
        # 计算指标
        data = calculate_ma(data, [5, 10, 20])
        
        # 转换为K线数据格式
        candles = []
        ma5 = []
        ma10 = []
        ma20 = []
        
        for i, row in data.iterrows():
            timestamp = int(row['date'].timestamp())
            
            candles.append({
                'time': timestamp,
                'open': round(row['open'], 2),
                'high': round(row['high'], 2),
                'low': round(row['low'], 2),
                'close': round(row['close'], 2)
            })
            
            if not pd.isna(row.get('MA5')):
                ma5.append({'time': timestamp, 'value': round(row['MA5'], 2)})
            if not pd.isna(row.get('MA10')):
                ma10.append({'time': timestamp, 'value': round(row['MA10'], 2)})
            if not pd.isna(row.get('MA20')):
                ma20.append({'time': timestamp, 'value': round(row['MA20'], 2)})
        
        return jsonify({
            'success': True,
            'data': {
                'candles': candles,
                'ma5': ma5,
                'ma10': ma10,
                'ma20': ma20
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)