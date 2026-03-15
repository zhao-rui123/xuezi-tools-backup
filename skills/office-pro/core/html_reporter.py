#!/usr/bin/env python3
"""
交互式HTML报告生成器
生成可交互的HTML报告，支持图表hover、缩放、筛选等功能
"""

import os
import json
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from collections import Counter


class InteractiveHTMLReporter:
    CHART_COLORS = [
        '#4A90E2', '#E24A4A', '#2ECC71', '#F39C12', '#9B59B6',
        '#1ABC9C', '#E67E22', '#34495E', '#16A085', '#D35400'
    ]

    def __init__(self, title: str = "交互式数据报告"):
        self.title = title
        self.sections: List[Dict] = []
        self.charts: List[Dict] = []
        self.tables: List[Dict] = []
        self.styles = ""
        self.scripts = ""

    def add_header(self, level: int, text: str) -> None:
        self.sections.append({
            "type": "header",
            "level": level,
            "text": text
        })

    def add_paragraph(self, text: str, style: str = "normal") -> None:
        self.sections.append({
            "type": "paragraph",
            "text": text,
            "style": style
        })

    def add_chart(self, chart_type: str, data: Union[pd.DataFrame, Dict],
                 title: str = None, width: int = 600, height: int = 400) -> str:
        chart_id = f"chart_{len(self.charts)}"

        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient='records')

        self.charts.append({
            "id": chart_id,
            "type": chart_type,
            "title": title or "图表",
            "data": data,
            "width": width,
            "height": height
        })

        return chart_id

    def add_table(self, data: Union[pd.DataFrame, Dict, List],
                 title: str = None, max_rows: int = 100) -> str:
        table_id = f"table_{len(self.tables)}"

        if isinstance(data, pd.DataFrame):
            data = data.head(max_rows).to_dict(orient='records')
            headers = data[0].keys() if data else []
        elif isinstance(data, dict):
            headers = list(data.keys())
            data = [dict(zip(headers, row)) for row in zip(*data.values())]
        else:
            headers = data[0].keys() if data else []

        self.tables.append({
            "id": table_id,
            "title": title or "数据表",
            "headers": list(headers) if headers else [],
            "data": data[:max_rows]
        })

        return table_id

    def add_kpi_card(self, title: str, value: Union[int, float],
                     change: float = None, unit: str = "") -> str:
        card_id = f"kpi_{len([s for s in self.sections if s.get('type') == 'kpi'])}"

        self.sections.append({
            "type": "kpi",
            "id": card_id,
            "title": title,
            "value": value,
            "change": change,
            "unit": unit
        })

        return card_id

    def _generate_css(self) -> str:
        return """
        :root {
            --primary-color: #4A90E2;
            --secondary-color: #2ECC71;
            --danger-color: #E74C3C;
            --warning-color: #F39C12;
            --dark-color: #2C3E50;
            --light-color: #ECF0F1;
            --text-color: #34495E;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: #f5f6fa;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, var(--primary-color), #357ABD);
            color: white;
            padding: 40px 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .section {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .section h2 {
            color: var(--dark-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--light-color);
        }

        .section h3 {
            color: var(--dark-color);
            margin: 20px 0 15px;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .kpi-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }

        .kpi-card .title {
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 10px;
        }

        .kpi-card .value {
            font-size: 2em;
            font-weight: bold;
            color: var(--dark-color);
        }

        .kpi-card .change {
            font-size: 0.9em;
            margin-top: 10px;
        }

        .kpi-card .change.positive {
            color: var(--secondary-color);
        }

        .kpi-card .change.negative {
            color: var(--danger-color);
        }

        .chart-container {
            margin: 20px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 8px;
        }

        .chart-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: var(--dark-color);
        }

        .table-container {
            overflow-x: auto;
            margin: 20px 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }

        th {
            background: var(--primary-color);
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }

        td {
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }

        tr:hover {
            background: #f8f9fa;
        }

        .insight-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
        }

        .insight-card h4 {
            margin-bottom: 10px;
        }

        .footer {
            text-align: center;
            padding: 30px;
            color: #7f8c8d;
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8em;
            }

            .kpi-grid {
                grid-template-columns: 1fr;
            }
        }
        """

    def _generate_chart_js(self) -> str:
        return """
        function renderCharts() {
            const chartConfigs = [];

            document.querySelectorAll('.chart-container').forEach((container, index) => {
                const chartData = JSON.parse(container.dataset.chart || '[]');
                const chartType = container.dataset.type || 'bar';
                const ctx = container.querySelector('canvas');

                if (!ctx || chartData.length === 0) return;

                const config = createChartConfig(chartType, chartData, ctx);
                new Chart(ctx, config);
            });
        }

        function createChartConfig(type, data, ctx) {
            const labels = data.map(d => Object.values(d)[0]);
            const datasets = [];

            const keys = Object.keys(data[0]).slice(1);
            const colors = ['#4A90E2', '#E24A4A', '#2ECC71', '#F39C12', '#9B59B6'];

            keys.forEach((key, i) => {
                datasets.push({
                    label: key,
                    data: data.map(d => parseFloat(d[key]) || 0),
                    backgroundColor: colors[i % colors.length],
                    borderColor: colors[i % colors.length],
                    borderWidth: 2,
                    fill: type === 'area'
                });
            });

            const config = {
                type: type === 'line' ? 'line' : type,
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            };

            if (type === 'pie' || type === 'doughnut') {
                config.options.scales = {};
                config.data.datasets.forEach((dataset, i) => {
                    dataset.backgroundColor = data.map((_, j) => colors[j % colors.length]);
                });
            }

            if (type === 'line') {
                config.options.elements = {
                    line: { tension: 0.4 }
                };
            }

            return config;
        }

        document.addEventListener('DOMContentLoaded', function() {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
            script.onload = renderCharts;
            document.head.appendChild(script);
        });
        """

    def generate(self, output_path: str = None) -> str:
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>{self._generate_css()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.title}</h1>
            <div class="subtitle">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
"""

        for section in self.sections:
            if section["type"] == "header":
                html += f'<div class="section"><h{section["level"]}>{section["text"]}</h{section["level"]}></div>\n'
            elif section["type"] == "paragraph":
                style = section.get("style", "normal")
                if style == "insight":
                    html += f'<div class="insight-card"><h4>💡 洞察</h4><p>{section["text"]}</p></div>\n'
                else:
                    html += f'<div class="section"><p>{section["text"]}</p></div>\n'
            elif section["type"] == "kpi":
                change_class = ""
                change_text = ""
                if section.get("change") is not None:
                    change = section["change"]
                    change_class = "positive" if change >= 0 else "negative"
                    change_text = f'<div class="change {change_class}">{"↑" if change >= 0 else "↓"} {abs(change):.1f}% 较上期</div>'

                html += f"""
        <div class="kpi-card">
            <div class="title">{section['title']}</div>
            <div class="value">{section['value']}{section.get('unit', '')}</div>
            {change_text}
        </div>
"""

        if self.charts:
            html += '<div class="section"><h2>📊 数据可视化</h2>\n'
            for chart in self.charts:
                html += f"""
        <div class="chart-container" data-type="{chart['type']}" data-chart='{json.dumps(chart["data"], ensure_ascii=False)}'>
            <div class="chart-title">{chart['title']}</div>
            <div style="height: {chart['height']}px;">
                <canvas></canvas>
            </div>
        </div>
"""
            html += '</div>\n'

        if self.tables:
            html += '<div class="section"><h2>📋 数据详情</h2>\n'
            for table in self.tables:
                html += f'<h3>{table["title"]}</h3>\n'
                html += '<div class="table-container"><table>\n<thead><tr>\n'
                for header in table["headers"]:
                    html += f'<th>{header}</th>\n'
                html += '</tr></thead><tbody>\n'
                for row in table["data"]:
                    html += '<tr>\n'
                    for header in table["headers"]:
                        html += f'<td>{row.get(header, "")}</td>\n'
                    html += '</tr>\n'
                html += '</tbody></table></div>\n'
            html += '</div>\n'

        html += f"""
        <div class="footer">
            <p>由 Office Chart Suite AI 智能报告生成器创建</p>
        </div>
    </div>

    <script>{self._generate_chart_js()}</script>
</body>
</html>
"""

        if output_path:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"HTML报告已生成: {output_path}")

        return html


def create_interactive_report(data: Union[pd.DataFrame, Dict],
                              title: str = "数据报告",
                              charts: List[Dict] = None,
                              output_path: str = None) -> str:
    reporter = InteractiveHTMLReporter(title)

    if isinstance(data, pd.DataFrame):
        numeric_cols = data.select_dtypes(include=['number']).columns

        for col in numeric_cols[:4]:
            reporter.add_kpi_card(
                title=col,
                value=round(data[col].mean(), 2),
                change=round((data[col].iloc[-1] - data[col].iloc[0]) / data[col].iloc[0] * 100, 2) if len(data) > 1 else 0
            )

    if charts:
        for chart in charts:
            reporter.add_chart(
                chart_type=chart.get('type', 'bar'),
                data=chart.get('data', data),
                title=chart.get('title', '图表')
            )

    reporter.add_table(data, title="原始数据", max_rows=50)

    return reporter.generate(output_path)


if __name__ == "__main__":
    sample_data = {
        "月份": ["1月", "2月", "3月", "4月", "5月", "6月"],
        "销售额": [12000, 15000, 18000, 16000, 20000, 25000],
        "利润": [3000, 4500, 5500, 4800, 6500, 8000],
        "客户数": [100, 120, 150, 140, 180, 200]
    }

    df = pd.DataFrame(sample_data)

    reporter = InteractiveHTMLReporter("月度销售报告")

    reporter.add_header(1, "销售概览")

    reporter.add_kpi_card("总销售额", 106000, 108.3, "元")
    reporter.add_kpi_card("总利润", 32100, 166.7, "元")
    reporter.add_kpi_card("平均客单价", 177, 100, "元")

    reporter.add_header(2, "销售趋势分析")
    reporter.add_paragraph("从上图中可以看出，上半年销售额整体呈上升趋势。")

    reporter.add_chart("line", sample_data, title="月度销售趋势", height=350)
    reporter.add_chart("bar", sample_data, title="月度利润对比", height=350)

    reporter.add_header(2, "详细数据")
    reporter.add_table(sample_data, title="销售数据明细")

    reporter.generate("interactive_report.html")
    print("交互式报告已生成: interactive_report.html")
