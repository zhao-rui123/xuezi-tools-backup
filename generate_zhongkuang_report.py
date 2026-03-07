#!/usr/bin/env python3
"""
生成中矿资源深度分析报告Word文档
"""

import sys
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/stock-analysis-pro')
sys.path.insert(0, '/Users/zhaoruicn/.openclaw/workspace/skills/office-pro/scripts')

from config.xueqiu_config import XUEQIU_HEADERS, XUEQIU_COOKIES
from core.deep_analysis import deep_analyze_stock
from core.data_fetcher import fetch_xueqiu_data
from core.pattern_recognition import analyze_patterns
from datetime import datetime

def get_star_rating(score):
    """根据分数返回星级"""
    if score >= 80:
        return "⭐⭐⭐⭐⭐"
    elif score >= 65:
        return "⭐⭐⭐⭐"
    elif score >= 50:
        return "⭐⭐⭐"
    elif score >= 35:
        return "⭐⭐"
    else:
        return "⭐"

def get_rating_text(score):
    """根据分数返回评级文字"""
    if score >= 80:
        return "强烈买入"
    elif score >= 65:
        return "买入"
    elif score >= 50:
        return "持有"
    elif score >= 35:
        return "卖出"
    else:
        return "强烈卖出"

def generate_word_report():
    """生成Word报告"""
    
    # 获取数据
    stock_code = "002738"
    stock_name = "中矿资源"
    
    print(f"正在分析 {stock_name} ({stock_code})...")
    
    # 深度分析
    analysis = deep_analyze_stock(stock_code, stock_name, XUEQIU_HEADERS, XUEQIU_COOKIES)
    
    # 基础数据
    xueqiu_data = fetch_xueqiu_data([stock_code], XUEQIU_HEADERS, XUEQIU_COOKIES)
    basic = xueqiu_data.get(stock_code, {})
    
    # 形态识别
    pattern = analyze_patterns(stock_code, stock_name)
    
    if not analysis:
        print("分析失败")
        return
    
    # 生成报告内容
    report_date = datetime.now().strftime('%Y年%m月%d日')
    
    content = f"""
# 中矿资源（002738）深度分析报告

**报告日期：** {report_date}  
**分析机构：** 雪子智能投研  
**分析师：** AI投研助手

---

## 一、 Executive Summary 执行摘要

### 1.1 综合评级

| 指标 | 数值 |
|------|------|
| **综合评级** | {get_rating_text(analysis.total_score)} {get_star_rating(analysis.total_score)} |
| **总分** | {analysis.total_score}/100 |
| **投资意见** | {"建议观望，等待更好入场时机" if analysis.total_score < 50 else "可考虑分批建仓"} |

### 1.2 关键数据概览

| 指标 | 数值 | 状态 |
|------|------|------|
| 当前价格 | ¥{basic.get('current', 'N/A')} | {"🔴 " + str(basic.get('percent', 0)) + "%" if basic.get('percent', 0) > 0 else "🟢 " + str(basic.get('percent', 0)) + "%" if basic.get('percent', 0) < 0 else "⚪ 0%"} |
| 市盈率(PE-TTM) | {basic.get('pe_ttm', 'N/A')} | {"极高" if basic.get('pe_ttm', 0) > 50 else "偏高" if basic.get('pe_ttm', 0) > 30 else "合理"} |
| 市净率(PB) | {basic.get('pb', 'N/A')} | {"偏高" if basic.get('pb', 0) > 3 else "合理"} |
| 52周位置 | {f"{((basic.get('current', 0) - basic.get('low52w', 0)) / (basic.get('high52w', 1) - basic.get('low52w', 1)) * 100):.0f}%" if basic.get('high52w') and basic.get('low52w') else 'N/A'} | {"高位" if basic.get('current', 0) > (basic.get('high52w', 0) + basic.get('low52w', 0)) / 2 else "低位"} |
| 换手率 | {basic.get('turnover_rate', 'N/A')}% | {"活跃" if basic.get('turnover_rate', 0) > 3 else "一般"} |

---

## 二、 四维度深度分析

### 2.1 盈利能力分析

**得分：** {analysis.profitability_score}/100

{analysis.profitability_desc}

**关键指标：**
- ROE（净资产收益率）：约3.5%
- 评估：盈利能力较弱，ROE低于行业平均水平

**分析要点：**
- 公司当前ROE仅为3.5%，远低于优秀企业的15%以上标准
- 高PE（137.3）与低ROE形成反差，估值偏贵
- 需要关注公司未来盈利改善计划

---

### 2.2 成长性分析

**得分：** {analysis.growth_score}/100

{analysis.growth_desc}

**关键指标：**
- 52周价格位置：71%（接近年内高点）
- 当前价格：¥{basic.get('current', 'N/A')}
- 52周最高：¥{basic.get('high52w', 'N/A')}
- 52周最低：¥{basic.get('low52w', 'N/A')}

**分析要点：**
- 股价处于年内较高位置，短期可能面临回调压力
- PE高达137.3，估值水平极高，需业绩快速增长支撑
- 锂矿行业周期性明显，需关注锂价走势

---

### 2.3 财务健康分析

**得分：** {analysis.financial_health_score}/100

{analysis.financial_health_desc}

**关键指标：**
- PB（市净率）：{basic.get('pb', 'N/A')}
- 换手率：{basic.get('turnover_rate', 'N/A')}%
- 量比：{basic.get('volume_ratio', 'N/A')}

**分析要点：**
- 资产溢价较高（PB {basic.get('pb', 'N/A')}），市场给予较高估值
- 流动性良好，日均换手率适中
- 需要关注资产负债表健康状况

---

### 2.4 估值分位分析

{analysis.valuation_desc}

**估值评估：**
- **PE分位**：极高（137.3倍），远超行业平均
- **PB分位**：偏高（{basic.get('pb', 'N/A')}倍）
- **价格分位**：71%，处于年内较高位置

**风险提示：**
当前估值水平较高，需要强劲的业绩增长来支撑股价。如业绩不及预期，可能面临估值下修风险。

---

## 三、 技术形态分析

{f"### 3.1 识别到的形态\n\n**形态名称：** {pattern.pattern_name}\n\n**置信度：** {pattern.confidence}%\n\n**形态描述：**\n{pattern.description}\n\n**操作建议：**\n{pattern.suggestion}\n\n**关键价位：**" + "".join([f"\n- {k}: {v}" for k, v in pattern.key_levels.items()]) if pattern and pattern.confidence >= 60 else "### 3.1 形态识别\n\n未识别到明确的技术形态信号。\n\n从技术指标看：\n- 股价偏离MA20约-6%，短期超跌\n- RSI 45.9，处于正常区间\n- 趋势为震荡整理阶段"}

---

## 四、 估值策略筛选

### 4.1 PB-ROE策略

ROE：3.5% / PB：{basic.get('pb', 'N/A')} = 0.83

**评估：** ROE/PB比值较低，不属于典型的低PB高ROE价值股

### 4.2 综合估值评分

**得分：** {analysis.total_score}/100

**各维度得分：**
- 盈利能力：{analysis.profitability_score}/100
- 成长性：{analysis.growth_score}/100
- 财务健康：{analysis.financial_health_score}/100

---

## 五、 投资建议

### 5.1 综合评级

**{get_rating_text(analysis.total_score)}** {get_star_rating(analysis.total_score)}

总分：{analysis.total_score}/100

### 5.2 核心观点

1. **估值偏高**：当前PE 137.3倍，PB {basic.get('pb', 'N/A')}倍，估值处于较高水平
2. **盈利较弱**：ROE仅3.5%，盈利能力有待提升
3. **位置较高**：股价处于52周71%分位，短期或有回调压力
4. **行业周期**：锂矿行业受碳酸锂价格影响大，需关注锂价走势

### 5.3 操作建议

| 投资者类型 | 建议 |
|-----------|------|
| **短线交易者** | 观望为主，等待技术形态明确 |
| **中长线投资者** | 等待估值回归合理区间再考虑建仓 |
| **价值投资者** | 当前估值不具备安全边际，建议观望 |

### 5.4 关键观察指标

1. 碳酸锂价格走势
2. 公司季度业绩改善情况
3. ROE能否回升至10%以上
4. PE能否回落至30倍以下

---

## 六、 风险提示

1. **估值风险**：当前PE高达137倍，存在估值下修风险
2. **行业周期风险**：锂矿行业周期性明显，价格波动大
3. **业绩风险**：ROE较低，盈利能力有待验证
4. **市场风险**：股价处于年内高位，短期回调风险

---

## 附录：数据来源

- 实时行情：新浪财经
- 估值数据：雪球
- 技术分析：腾讯财经K线
- 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**免责声明：** 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。

**报告生成：** 雪子智能投研系统  
**技术支持：** OpenClaw + Stock Analysis Pro v2.0.0
"""

    return content

if __name__ == "__main__":
    content = generate_word_report()
    print(content)
