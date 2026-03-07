#!/usr/bin/env python3
"""
性能监控系统 - 监控和优化我的运行效率
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class PerformanceRecord:
    """性能记录"""
    timestamp: str
    session_id: str
    tokens_in: int
    tokens_out: int
    response_time_ms: int
    tools_used: int
    success: bool
    model: str

PERF_LOG = os.path.expanduser("~/.openclaw/workspace/memory/performance.json")

def record_performance(tokens_in: int, tokens_out: int, 
                      response_time_ms: int, tools_used: int, 
                      success: bool = True, model: str = "unknown"):
    """记录性能数据"""
    record = PerformanceRecord(
        timestamp=datetime.now().isoformat(),
        session_id=os.environ.get('OPENCLAW_SESSION', 'unknown'),
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        response_time_ms=response_time_ms,
        tools_used=tools_used,
        success=success,
        model=model
    )
    
    # 加载现有记录
    records = []
    if os.path.exists(PERF_LOG):
        try:
            with open(PERF_LOG, 'r') as f:
                records = json.load(f)
        except:
            pass
    
    # 添加新记录
    records.append(asdict(record))
    
    # 保留最近1000条
    records = records[-1000:]
    
    # 保存
    os.makedirs(os.path.dirname(PERF_LOG), exist_ok=True)
    with open(PERF_LOG, 'w') as f:
        json.dump(records, f, indent=2)

def analyze_performance(days: int = 7) -> Dict:
    """分析性能数据"""
    if not os.path.exists(PERF_LOG):
        return {"error": "无性能数据"}
    
    with open(PERF_LOG, 'r') as f:
        records = json.load(f)
    
    # 筛选最近N天
    cutoff = datetime.now() - timedelta(days=days)
    recent = [r for r in records 
              if datetime.fromisoformat(r['timestamp']) > cutoff]
    
    if not recent:
        return {"error": f"最近{days}天无数据"}
    
    # 计算统计
    total_tokens = sum(r['tokens_in'] + r['tokens_out'] for r in recent)
    avg_response = sum(r['response_time_ms'] for r in recent) / len(recent)
    success_rate = sum(1 for r in recent if r['success']) / len(recent) * 100
    avg_tools = sum(r['tools_used'] for r in recent) / len(recent)
    
    # 按模型分组
    models = {}
    for r in recent:
        m = r.get('model', 'unknown')
        if m not in models:
            models[m] = {'count': 0, 'tokens': 0}
        models[m]['count'] += 1
        models[m]['tokens'] += r['tokens_in'] + r['tokens_out']
    
    return {
        'period_days': days,
        'total_interactions': len(recent),
        'total_tokens': total_tokens,
        'avg_response_time_ms': round(avg_response, 2),
        'success_rate': round(success_rate, 2),
        'avg_tools_per_request': round(avg_tools, 2),
        'model_usage': models
    }

def generate_performance_report() -> str:
    """生成性能报告"""
    stats = analyze_performance(7)
    
    if 'error' in stats:
        return f"❌ {stats['error']}"
    
    lines = [
        f"\n{'='*60}",
        f"📊 性能报告 (最近{stats['period_days']}天)",
        f"{'='*60}",
        f"",
        f"总交互次数: {stats['total_interactions']}",
        f"总Token消耗: {stats['total_tokens']:,}",
        f"平均响应时间: {stats['avg_response_time_ms']}ms",
        f"成功率: {stats['success_rate']}%",
        f"平均工具调用: {stats['avg_tools_per_request']}",
        f"",
        f"模型使用分布:",
    ]
    
    for model, data in stats['model_usage'].items():
        lines.append(f"  - {model}: {data['count']}次, {data['tokens']:,}tokens")
    
    # 优化建议
    lines.extend([
        f"",
        f"💡 优化建议:",
    ])
    
    if stats['avg_response_time_ms'] > 5000:
        lines.append(f"  - 响应时间较长，考虑简化工具调用")
    
    if stats['avg_tools_per_request'] > 5:
        lines.append(f"  - 工具调用较多，考虑批量处理")
    
    if stats['success_rate'] < 95:
        lines.append(f"  - 失败率较高，检查错误日志")
    
    lines.append(f"{'='*60}")
    
    return "\n".join(lines)

def detect_anomalies():
    """检测异常模式"""
    if not os.path.exists(PERF_LOG):
        return []
    
    with open(PERF_LOG, 'r') as f:
        records = json.load(f)
    
    anomalies = []
    
    # 检测响应时间异常
    response_times = [r['response_time_ms'] for r in records[-100:]]
    if response_times:
        avg = sum(response_times) / len(response_times)
        for r in records[-10:]:
            if r['response_time_ms'] > avg * 3:
                anomalies.append({
                    'type': 'slow_response',
                    'time': r['timestamp'],
                    'value': r['response_time_ms'],
                    'threshold': avg * 2
                })
    
    # 检测失败率异常
    recent = records[-50:]
    failures = sum(1 for r in recent if not r['success'])
    if failures > 5:
        anomalies.append({
            'type': 'high_failure_rate',
            'period': '最近50次',
            'failures': failures,
            'rate': f"{failures/50*100:.1f}%"
        })
    
    return anomalies

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 performance_monitor.py report     # 生成报告")
        print("  python3 performance_monitor.py analyze    # 分析性能")
        print("  python3 performance_monitor.py anomalies  # 检测异常")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'report':
        print(generate_performance_report())
    elif cmd == 'analyze':
        stats = analyze_performance(7)
        print(json.dumps(stats, indent=2))
    elif cmd == 'anomalies':
        anomalies = detect_anomalies()
        if anomalies:
            print("⚠️ 发现异常:")
            for a in anomalies:
                print(f"  - {a}")
        else:
            print("✅ 未发现异常")
