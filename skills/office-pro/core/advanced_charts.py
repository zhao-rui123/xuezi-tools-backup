#!/usr/bin/env python3
"""
高级图表生成模块
支持热力图、地图、甘特图、仪表盘等专业图表
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.patches import Patch
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import io
import base64


class AdvancedChartGenerator:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), '..', 'temp')
        os.makedirs(self.output_dir, exist_ok=True)
        self.charts: List[Dict] = []

    def generate_heatmap(self, data: Union[pd.DataFrame, Dict],
                        title: str = "热力图", cmap: str = "RdYlBu_r",
                        annot: bool = True, figsize: Tuple = (10, 8)) -> str:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data

        if df.empty:
            raise ValueError("Data is empty")

        fig, ax = plt.subplots(figsize=figsize)

        matrix = df.select_dtypes(include=[np.number])
        if matrix.empty:
            matrix = df

        im = ax.imshow(matrix.values, cmap=cmap, aspect='auto', interpolation='nearest')

        ax.set_xticks(np.arange(len(matrix.columns)))
        ax.set_yticks(np.arange(len(matrix)))
        ax.set_xticklabels(matrix.columns, rotation=45, ha='right')
        ax.set_yticklabels(matrix.index)

        if annot:
            for i in range(len(matrix)):
                for j in range(len(matrix.columns)):
                    val = matrix.iloc[i, j]
                    text = ax.text(j, i, f'{val:.1f}',
                                  ha="center", va="center",
                                  color="white" if abs(val) > matrix.values.mean() else "black")

        ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
        fig.colorbar(im, ax=ax, label='Value')

        plt.tight_layout()

        output_path = os.path.join(self.output_dir, f"heatmap_{len(self.charts)}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.charts.append({"type": "heatmap", "title": title, "path": output_path})
        return output_path

    def generate_gantt_chart(self, tasks: List[Dict],
                            title: str = "项目进度甘特图",
                            figsize: Tuple = (12, 6)) -> str:
        fig, ax = plt.subplots(figsize=figsize)

        for idx, task in enumerate(tasks):
            start = task.get('start')
            end = task.get('end')
            name = task.get('name', f'Task {idx+1}')
            progress = task.get('progress', 100)
            color = task.get('color', '#4A90E2')

            if isinstance(start, str):
                start = pd.to_datetime(start)
            if isinstance(end, str):
                end = pd.to_datetime(end)

            duration = (end - start).days

            ax.barh(name, duration, left=start, height=0.5, color=color, alpha=0.7)

            if progress < 100:
                completed_duration = duration * progress / 100
                ax.barh(name, completed_duration, left=start, height=0.5,
                       color=color, alpha=1.0)

            ax.text(start + timedelta(days=duration/2), idx,
                   f'{progress}%', ha='center', va='center',
                   fontsize=9, color='white', fontweight='bold')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
        ax.set_xlabel('日期', fontsize=11)
        ax.set_ylabel('任务', fontsize=11)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.xticks(rotation=45)

        ax.grid(True, axis='x', alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()

        output_path = os.path.join(self.output_dir, f"gantt_{len(self.charts)}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.charts.append({"type": "gantt", "title": title, "path": output_path})
        return output_path

    def generate_funnel_chart(self, data: Dict,
                             title: str = "漏斗图",
                             figsize: Tuple = (10, 8)) -> str:
        fig, ax = plt.subplots(figsize=figsize)

        labels = list(data.keys())
        values = list(data.values())

        max_val = max(values)
        widths = [v / max_val for v in values]

        y_positions = np.arange(len(labels))

        colors = ['#4A90E2', '#5DADE2', '#85C1E9', '#AED6F1', '#D4E6F1']

        for idx, (width, value, label) in enumerate(zip(widths, values, labels)):
            left = (1 - width) / 2
            ax.barh(y_positions[idx], width, left=left, height=0.6,
                   color=colors[idx % len(colors)], alpha=0.8,
                   edgecolor='white', linewidth=2)

            ax.text(0.5, y_positions[idx], f'{label}: {value}',
                   ha='center', va='center',
                   fontsize=11, color='white', fontweight='bold')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, len(labels) - 0.5)
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)

        plt.tight_layout()

        output_path = os.path.join(self.output_dir, f"funnel_{len(self.charts)}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.charts.append({"type": "funnel", "title": title, "path": output_path})
        return output_path

    def generate_radar_chart(self, data: Dict,
                            title: str = "雷达图",
                            figsize: Tuple = (8, 8)) -> str:
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))

        categories = list(data.keys())
        values = list(data.values())

        values += values[:1]

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
        angles += angles[:1]

        ax.plot(angles, values, 'o-', linewidth=2, color='#4A90E2')
        ax.fill(angles, values, alpha=0.25, color='#4A90E2')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        output_path = os.path.join(self.output_dir, f"radar_{len(self.charts)}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.charts.append({"type": "radar", "title": title, "path": output_path})
        return output_path

    def generate_wordcloud(self, text: str,
                          title: str = "词云图",
                          background_color: str = "white",
                          colormap: str = "viridis",
                          figsize: Tuple = (12, 8)) -> str:
        try:
            from wordcloud import WordCloud
        except ImportError:
            print("wordcloud not installed. Install with: pip install wordcloud")
            return None

        if isinstance(text, dict):
            text = ' '.join([f'{k} {v}' for k, v in text.items()])

        wordcloud = WordCloud(
            width=1200,
            height=800,
            background_color=background_color,
            colormap=colormap,
            max_words=100,
            contour_width=2,
            contour_color='steelblue'
        ).generate(text)

        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=10)

        plt.tight_layout()

        output_path = os.path.join(self.output_dir, f"wordcloud_{len(self.charts)}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.charts.append({"type": "wordcloud", "title": title, "path": output_path})
        return output_path

    def generate_waterfall_chart(self, data: Dict,
                                 title: str = "瀑布图",
                                 figsize: Tuple = (12, 6)) -> str:
        fig, ax = plt.subplots(figsize=figsize)

        categories = list(data.keys())
        values = list(data.values())

        cumulative = [0]
        for v in values[:-1]:
            cumulative.append(cumulative[-1] + v)

        blank = [cumulative[i] if values[i] >= 0 else cumulative[i] + values[i]
                for i in range(len(values))]

        colors = ['#2ECC71' if v >= 0 else '#E74C3C' for v in values]
        colors[-1] = '#3498DB'

        for i, (cat, val, cum, bl) in enumerate(zip(categories, values, cumulative, blank)):
            ax.bar(cat, abs(val), bottom=bl if val >= 0 else cum,
                  color=colors[i], alpha=0.8, width=0.6)

            label_y = bl + abs(val)/2 if val >= 0 else cum + abs(val)/2
            ax.text(i, label_y, f'{val:+d}', ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
        ax.set_ylabel('数值', fontsize=11)
        ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()

        output_path = os.path.join(self.output_dir, f"waterfall_{len(self.charts)}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.charts.append({"type": "waterfall", "title": title, "path": output_path})
        return output_path

    def generate_boxplot(self, data: Union[pd.DataFrame, Dict],
                        title: str = "箱线图",
                        figsize: Tuple = (10, 6)) -> str:
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        fig, ax = plt.subplots(figsize=figsize)

        box_data = [df[col].dropna().values for col in numeric_cols]

        bp = ax.boxplot(box_data, labels=numeric_cols, patch_artist=True)

        colors = ['#4A90E2', '#E24A4A', '#2ECC71', '#F39C12', '#9B59B6']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
        ax.set_ylabel('数值', fontsize=11)
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()

        output_path = os.path.join(self.output_dir, f"boxplot_{len(self.charts)}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.charts.append({"type": "boxplot", "title": title, "path": output_path})
        return output_path

    def generate_treemap(self, data: Dict,
                        title: str = "树图",
                        figsize: Tuple = (12, 8)) -> str:
        try:
            import squarify
        except ImportError:
            print("squarify not installed. Install with: pip install squarify")
            return None

        fig, ax = plt.subplots(figsize=figsize)

        labels = list(data.keys())
        values = list(data.values())

        colors = ['#4A90E2', '#E24A4A', '#2ECC71', '#F39C12', '#9B59B6',
                 '#1ABC9C', '#E67E22', '#34495E', '#16A085', '#D35400']

        normed = squarify.normalize_sizes(values, 100, 100)
        rects = squarify.squarify(normed, 0, 0, 100, 100)

        for rect, label, value, color in zip(rects, labels, values, colors):
            x, y, dx, dy = rect['x'], rect['y'], rect['dx'], rect['dy']
            ax.add_patch(plt.Rectangle((x, y), dx, dy, facecolor=color,
                                        alpha=0.7, edgecolor='white', linewidth=2))

            ax.text(x + dx/2, y + dy/2, f'{label}\n{value}',
                   ha='center', va='center', fontsize=10,
                   fontweight='bold', color='white')

        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=10)

        plt.tight_layout()

        output_path = os.path.join(self.output_dir, f"treemap_{len(self.charts)}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        self.charts.append({"type": "treemap", "title": title, "path": output_path})
        return output_path

    def get_chart_list(self) -> List[Dict]:
        return self.charts


def create_advanced_chart(chart_type: str, data: Union[pd.DataFrame, Dict],
                         **kwargs) -> str:
    generator = AdvancedChartGenerator()

    chart_methods = {
        'heatmap': generator.generate_heatmap,
        'gantt': generator.generate_gantt_chart,
        'funnel': generator.generate_funnel_chart,
        'radar': generator.generate_radar_chart,
        'wordcloud': generator.generate_wordcloud,
        'waterfall': generator.generate_waterfall_chart,
        'boxplot': generator.generate_boxplot,
        'treemap': generator.generate_treemap
    }

    if chart_type not in chart_methods:
        raise ValueError(f"Unsupported chart type: {chart_type}. Available: {list(chart_methods.keys())}")

    return chart_methods[chart_type](data, **kwargs)


if __name__ == "__main__":
    generator = AdvancedChartGenerator()

    heatmap_data = {
        'A': [1, 2, 3, 4],
        'B': [2, 4, 6, 8],
        'C': [3, 6, 9, 12],
        'D': [4, 8, 12, 16]
    }
    print("生成热力图...")
    heatmap_path = generator.generate_heatmap(heatmap_data, title="示例热力图")
    print(f"热力图已保存: {heatmap_path}")

    gantt_tasks = [
        {'name': '需求分析', 'start': '2024-01-01', 'end': '2024-01-10', 'progress': 100, 'color': '#2ECC71'},
        {'name': '系统设计', 'start': '2024-01-11', 'end': '2024-01-20', 'progress': 80, 'color': '#3498DB'},
        {'name': '开发', 'start': '2024-01-21', 'end': '2024-02-10', 'progress': 50, 'color': '#F39C12'},
        {'name': '测试', 'start': '2024-02-11', 'end': '2024-02-20', 'progress': 0, 'color': '#E74C3C'}
    ]
    print("生成甘特图...")
    gantt_path = generator.generate_gantt_chart(gantt_tasks, title="项目进度")
    print(f"甘特图已保存: {gantt_path}")

    funnel_data = {
        '访问量': 10000,
        '注册用户': 5000,
        '激活用户': 3000,
        '付费用户': 1000,
        '忠实用户': 500
    }
    print("生成漏斗图...")
    funnel_path = generator.generate_funnel_chart(funnel_data, title="用户转化漏斗")
    print(f"漏斗图已保存: {funnel_path}")
