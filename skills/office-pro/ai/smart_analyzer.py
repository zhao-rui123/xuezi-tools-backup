#!/usr/bin/env python3
"""
AI 智能分析模块
支持自然语言输入和智能数据分析
"""

import re
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from collections import Counter
import statistics


@dataclass
class AnalysisResult:
    summary: str
    insights: List[str]
    charts: List[Dict]
    anomalies: List[Dict]
    statistics: Dict


class NaturalLanguageProcessor:
    CHART_KEYWORDS = {
        "bar": ["柱状图", "柱形图", "条形图", "对比", "排名"],
        "line": ["折线图", "趋势", "走势", "变化", "增长"],
        "pie": ["饼图", "占比", "比例", "组成", "分布"],
        "area": ["面积图", "累积", "填充"],
        "scatter": ["散点图", "相关", "关系"],
        "heatmap": ["热力图", "热度", "密度"],
        "radar": ["雷达图", "多维"],
        "table": ["表格", "数据", "列表"],
        "gantt": ["甘特图", "进度", "时间线"]
    }

    ACTION_KEYWORDS = {
        "generate_report": ["生成报告", "创建报告", "输出报告"],
        "analyze": ["分析", "解析", "研究"],
        "visualize": ["可视化", "展示", "画图", "图表"],
        "compare": ["对比", "比较", "差异"],
        "summarize": ["总结", "摘要", "概括"],
        "forecast": ["预测", "预报", "预估"]
    }

    def __init__(self):
        self.context: Dict = {}

    def parse(self, text: str, data: pd.DataFrame = None) -> Dict:
        result = {
            "action": self._detect_action(text),
            "chart_type": self._detect_chart_type(text),
            "parameters": self._extract_parameters(text, data),
            "filters": self._extract_filters(text),
            "time_range": self._extract_time_range(text),
            "metrics": self._extract_metrics(text, data),
            "dimensions": self._extract_dimensions(text, data)
        }

        return result

    def _detect_action(self, text: str) -> str:
        text = text.lower()
        for action, keywords in self.ACTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return action
        return "analyze"

    def _detect_chart_type(self, text: str) -> Optional[str]:
        for chart_type, keywords in self.CHART_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return chart_type
        return None

    def _extract_parameters(self, text: str, data: pd.DataFrame = None) -> Dict:
        params = {}

        title_match = re.search(r'标题[是为：:]\s*(.+?)(?:，|$)', text)
        if title_match:
            params['title'] = title_match.group(1).strip()

        month_match = re.search(r'(\d+)\s*月', text)
        if month_match:
            params['month'] = int(month_match.group(1))

        year_match = re.search(r'(\d{4})\s*年', text)
        if year_match:
            params['year'] = int(year_match.group(1))

        return params

    def _extract_filters(self, text: str) -> Dict:
        filters = {}

        region_match = re.search(r'(华东|华南|华北|华中|西南|西北|东北)', text)
        if region_match:
            filters['region'] = region_match.group(1)

        category_match = re.search(r'(第一|第二|第三|第四)', text)
        if category_match:
            filters['quarter'] = category_match.group(1)

        return filters

    def _extract_time_range(self, text: str) -> Optional[Dict]:
        time_range = {}

        year_month_match = re.search(r'(\d{4})[年/](\d{1,2})', text)
        if year_month_match:
            time_range['year'] = int(year_month_match.group(1))
            time_range['month'] = int(year_month_match.group(2))

        quarter_match = re.search(r'(上|下)半年', text)
        if quarter_match:
            time_range['half'] = quarter_match.group(1)

        return time_range if time_range else None

    def _extract_metrics(self, text: str, data: pd.DataFrame = None) -> List[str]:
        metrics = []

        metric_keywords = ["销售额", "利润", "收入", "成本", "增长", "同比", "环比", "数量", "产量"]

        if data is not None:
            for col in data.columns:
                for keyword in metric_keywords:
                    if keyword in col:
                        metrics.append(col)

        for keyword in metric_keywords:
            if keyword in text:
                if keyword not in metrics:
                    metrics.append(keyword)

        return metrics

    def _extract_dimensions(self, text: str, data: pd.DataFrame = None) -> List[str]:
        dimensions = []

        dimension_keywords = ["地区", "省份", "城市", "产品", "类别", "部门", "人员", "月份", "季度", "年份"]

        if data is not None:
            for col in data.columns:
                for keyword in dimension_keywords:
                    if keyword in col:
                        dimensions.append(col)

        for keyword in dimension_keywords:
            if keyword in text:
                if keyword not in dimensions:
                    dimensions.append(keyword)

        return dimensions


class IntelligentDataAnalyzer:
    def __init__(self, data: Union[pd.DataFrame, Dict, str]):
        if isinstance(data, str):
            if data.endswith('.csv'):
                self.df = pd.read_csv(data)
            elif data.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(data)
            elif data.endswith('.json'):
                self.df = pd.read_json(data)
            else:
                raise ValueError(f"Unsupported file format: {data}")
        elif isinstance(data, dict):
            self.df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            self.df = data
        else:
            raise ValueError("Unsupported data format")

        self.nlp = NaturalLanguageProcessor()

    def analyze(self, question: str = None) -> AnalysisResult:
        if question:
            parsed = self.nlp.parse(question, self.df)
            action = parsed['action']

            if action == "generate_report":
                return self._generate_report(parsed)
            elif action == "visualize":
                return self._generate_visualization(parsed)
            elif action == "compare":
                return self._compare_data(parsed)
            elif action == "forecast":
                return self._forecast_data(parsed)
            else:
                return self._analyze_data(parsed)
        else:
            return self._analyze_data({})

    def _analyze_data(self, parsed: Dict) -> AnalysisResult:
        summary = self._generate_summary()
        insights = self._generate_insights()
        charts = self._recommend_charts()
        anomalies = self._detect_anomalies()
        statistics = self._calculate_statistics()

        return AnalysisResult(
            summary=summary,
            insights=insights,
            charts=charts,
            anomalies=anomalies,
            statistics=statistics
        )

    def _generate_summary(self) -> str:
        n_rows = len(self.df)
        n_cols = len(self.df.columns)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()

        summary = f"数据概览：共 {n_rows} 条记录，{n_cols} 个字段"
        if numeric_cols:
            summary += f"，其中 {len(numeric_cols)} 个数值型字段"
        summary += "。"

        if 'date' in self.df.columns or 'time' in self.df.columns or '日期' in str(self.df.columns):
            summary += f" 时间跨度从 {self.df.iloc[0].get('date', self.df.iloc[0].get('日期', 'N/A'))} 到 {self.df.iloc[-1].get('date', self.df.iloc[-1].get('日期', 'N/A'))}。"

        return summary

    def _generate_insights(self) -> List[str]:
        insights = []

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols[:5]:
            col_data = self.df[col].dropna()

            if len(col_data) > 0:
                mean_val = col_data.mean()
                std_val = col_data.std()
                max_val = col_data.max()
                min_val = col_data.min()

                if std_val > 0:
                    cv = std_val / mean_val
                    if cv > 0.5:
                        insights.append(f"{col} 波动性较大，变异系数为 {cv:.2%}，数据分布较为分散")

                if max_val > 0:
                    trend = "上升" if col_data.iloc[-1] > col_data.iloc[0] else "下降"
                    change_pct = (col_data.iloc[-1] - col_data.iloc[0]) / col_data.iloc[0] * 100
                    insights.append(f"{col} 整体呈{trend}趋势，变化幅度为 {change_pct:.1f}%")

                if mean_val > std_val * 3:
                    insights.append(f"{col} 存在异常高值，最大值为平均值的 {max_val/mean_val:.1f} 倍")

        return insights[:5]

    def _recommend_charts(self) -> List[Dict]:
        charts = []

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        category_cols = self.df.select_dtypes(include=['object', 'category']).columns
        date_cols = [col for col in self.df.columns if 'date' in col.lower() or '时间' in col]

        if len(date_cols) > 0 and len(numeric_cols) > 0:
            charts.append({
                "type": "line",
                "title": f"{numeric_cols[0]}趋势图",
                "x": date_cols[0],
                "y": numeric_cols[0],
                "reason": "检测到时间序列数据"
            })

        if len(category_cols) > 0 and len(numeric_cols) > 0:
            charts.append({
                "type": "bar",
                "title": f"{numeric_cols[0]}对比",
                "x": category_cols[0],
                "y": numeric_cols[0],
                "reason": "检测到分类数据"
            })

            if self.df[category_cols[0]].nunique() <= 8:
                charts.append({
                    "type": "pie",
                    "title": f"{numeric_cols[0]}占比",
                    "x": category_cols[0],
                    "y": numeric_cols[0],
                    "reason": "分类数量适合饼图展示"
                })

        if len(numeric_cols) >= 2:
            charts.append({
                "type": "scatter",
                "title": f"{numeric_cols[0]}与{numeric_cols[1]}相关性",
                "x": numeric_cols[0],
                "y": numeric_cols[1],
                "reason": "检测到多组数值数据"
            })

        return charts

    def _detect_anomalies(self) -> List[Dict]:
        anomalies = []

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            col_data = self.df[col].dropna()

            if len(col_data) > 3:
                mean_val = col_data.mean()
                std_val = col_data.std()

                if std_val > 0:
                    z_scores = (col_data - mean_val) / std_val
                    outlier_indices = z_scores[abs(z_scores) > 3].index.tolist()

                    for idx in outlier_indices[:5]:
                        anomalies.append({
                            "column": col,
                            "row_index": idx,
                            "value": float(self.df.loc[idx, col]),
                            "type": "statistical_outlier",
                            "description": f"{col} 在第{idx}行的值为 {self.df.loc[idx, col]:.2f}，超过3倍标准差"
                        })

        return anomalies

    def _calculate_statistics(self) -> Dict:
        stats = {}

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols[:10]:
            col_data = self.df[col].dropna()

            if len(col_data) > 0:
                stats[col] = {
                    "count": int(col_data.count()),
                    "mean": float(round(col_data.mean(), 2)),
                    "median": float(round(col_data.median(), 2)),
                    "std": float(round(col_data.std(), 2)),
                    "min": float(round(col_data.min(), 2)),
                    "max": float(round(col_data.max(), 2)),
                    "q25": float(round(col_data.quantile(0.25), 2)),
                    "q75": float(round(col_data.quantile(0.75), 2))
                }

        return stats

    def _generate_report(self, parsed: Dict) -> AnalysisResult:
        result = self._analyze_data(parsed)

        title = parsed.get('parameters', {}).get('title', '数据报告')

        result.summary = f"# {title}\n\n" + result.summary

        result.insights.insert(0, f"报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return result

    def _generate_visualization(self, parsed: Dict) -> AnalysisResult:
        result = self._analyze_data(parsed)

        requested_type = parsed.get('chart_type')

        if requested_type:
            result.charts = [{
                "type": requested_type,
                "title": f"用户请求的{requested_type}图表",
                "reason": "根据用户请求生成"
            }]

        return result

    def _compare_data(self, parsed: Dict) -> AnalysisResult:
        result = self._analyze_data(parsed)

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) >= 2:
            result.insights.append(f"关键对比：{numeric_cols[0]} 均值为 {result.statistics[numeric_cols[0]]['mean']:.2f}，{numeric_cols[1]} 均值为 {result.statistics[numeric_cols[1]]['mean']:.2f}")

        return result

    def _forecast_data(self, parsed: Dict) -> AnalysisResult:
        result = self._analyze_data(parsed)

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) > 0 and len(self.df) >= 5:
            col = numeric_cols[0]
            col_data = self.df[col].dropna()

            if len(col_data) >= 5:
                x = np.arange(len(col_data))
                y = col_data.values

                coeffs = np.polyfit(x, y, 1)
                trend = coeffs[0]

                future_x = np.array([len(col_data), len(col_data) + 1, len(col_data) + 2])
                forecast = np.polyval(coeffs, future_x)

                result.insights.append(f"趋势预测：{col} 每月平均{trend:.2f}单位，预测下期约为 {forecast[0]:.2f}")

        return result


class SmartReportGenerator:
    def __init__(self, data: Union[pd.DataFrame, Dict, str]):
        self.analyzer = IntelligentDataAnalyzer(data)

    def generate_from_natural_language(self, text: str) -> Dict:
        analysis_result = self.analyzer.analyze(text)

        report = {
            "title": "智能分析报告",
            "summary": analysis_result.summary,
            "insights": analysis_result.insights,
            "charts": analysis_result.charts,
            "anomalies": analysis_result.anomalies,
            "statistics": analysis_result.statistics,
            "recommendations": self._generate_recommendations(analysis_result)
        }

        return report

    def _generate_recommendations(self, result: AnalysisResult) -> List[str]:
        recommendations = []

        if result.anomalies:
            recommendations.append("检测到数据异常，建议进行数据清洗或异常值处理")

        if len(result.charts) < 2:
            recommendations.append("建议增加更多可视化图表以丰富报告内容")

        for insight in result.insights:
            if "波动" in insight:
                recommendations.append("数据波动较大，建议深入分析原因")
            if "趋势" in insight:
                recommendations.append("检测到明显趋势，建议关注后续变化")

        if not recommendations:
            recommendations.append("数据质量良好，建议保持现有数据收集方式")

        return recommendations[:3]


def analyze_with_ai(data, question: str = None) -> Dict:
    analyzer = IntelligentDataAnalyzer(data)
    return analyzer.analyze(question)


def generate_smart_report(data, prompt: str) -> Dict:
    generator = SmartReportGenerator(data)
    return generator.generate_from_natural_language(prompt)


if __name__ == "__main__":
    sample_data = {
        "月份": ["1月", "2月", "3月", "4月", "5月", "6月"],
        "销售额": [12000, 15000, 18000, 16000, 20000, 25000],
        "利润": [3000, 4500, 5500, 4800, 6500, 8000],
        "客户数": [100, 120, 150, 140, 180, 200]
    }

    analyzer = IntelligentDataAnalyzer(sample_data)

    result = analyzer.analyze("分析销售数据，生成趋势报告")

    print("=" * 50)
    print("分析结果")
    print("=" * 50)
    print(f"\n摘要: {result.summary}")
    print(f"\n洞察:")
    for insight in result.insights:
        print(f"  - {insight}")
    print(f"\n推荐图表:")
    for chart in result.charts:
        print(f"  - {chart['type']}: {chart['title']}")
    print(f"\n统计信息:")
    for col, stats in result.statistics.items():
        print(f"  {col}: 均值={stats['mean']}, 中位数={stats['median']}")
