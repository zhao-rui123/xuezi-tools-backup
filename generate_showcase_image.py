#!/usr/bin/env python3
"""
生成雪子助手能力展示信息图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig = plt.figure(figsize=(16, 20), facecolor='#f5f5f5')
ax = fig.add_subplot(111)
ax.set_xlim(0, 16)
ax.set_ylim(0, 20)
ax.axis('off')
ax.set_facecolor('#f5f5f5')

# 颜色方案
colors = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#C73E1D',
    'bg_light': '#E8F4F8',
    'bg_pink': '#FCE4EC',
    'bg_orange': '#FFF3E0',
    'text': '#333333'
}

# ========== 标题区域 ==========
title_box = FancyBboxPatch((0.5, 18.5), 15, 1.2, 
                           boxstyle="round,pad=0.1", 
                           facecolor=colors['primary'], 
                           edgecolor='none',
                           alpha=0.9)
ax.add_patch(title_box)

ax.text(8, 19.1, '🦞 雪子助手 - 智能工具包生态系统', 
        fontsize=28, fontweight='bold', ha='center', va='center', color='white')

ax.text(8, 18.2, '20+ 技能包 · 10,000+ 行代码 · 生产级AI助手', 
        fontsize=14, ha='center', va='center', color=colors['text'], alpha=0.8)

# ========== 核心数据卡片 ==========
card_y = 16.5
card_data = [
    ('20+', '技能包', colors['primary']),
    ('10K+', '代码行', colors['secondary']),
    ('10+', '自动化任务', colors['accent']),
    ('99.9%', '稳定性', colors['success'])
]

for i, (num, label, color) in enumerate(card_data):
    x = 1 + i * 3.8
    # 卡片背景
    card = FancyBboxPatch((x, card_y), 3.2, 1.3, 
                         boxstyle="round,pad=0.05",
                         facecolor=color, alpha=0.15,
                         edgecolor=color, linewidth=2)
    ax.add_patch(card)
    
    ax.text(x + 1.6, card_y + 0.85, num, fontsize=24, fontweight='bold', 
            ha='center', va='center', color=color)
    ax.text(x + 1.6, card_y + 0.35, label, fontsize=11, 
            ha='center', va='center', color=colors['text'])

# ========== 五大核心能力 ==========
section_y = 14.5
ax.text(8, section_y + 0.5, '🎯 五大核心能力', fontsize=18, fontweight='bold', 
        ha='center', va='center', color=colors['primary'])

abilities = [
    ('📈', '股票分析系统', '专业级·三类股票差异化分析\n新浪+雪球+腾讯K线融合', colors['bg_light']),
    ('📦', '技能包生态', '20+可复用技能包\n像搭积木一样组合', colors['bg_pink']),
    ('🔄', '自动化运维', '定时任务+3层备份\n每日自动推送报告', colors['bg_orange']),
    ('🤖', '多Agent开发', '5-Agent并行开发\n需求→开发→审查→部署', colors['bg_light']),
    ('🧠', '自我进化', '从错误中学习\n持续优化不重复犯错', colors['bg_pink']),
]

for i, (emoji, title, desc, bg_color) in enumerate(abilities):
    row = i // 2
    col = i % 2
    x = 1 + col * 7.5
    y = 11.5 - row * 2.2
    
    # 能力卡片
    card = FancyBboxPatch((x, y), 7, 1.9,
                         boxstyle="round,pad=0.08",
                         facecolor=bg_color,
                         edgecolor=colors['primary'],
                         linewidth=1.5,
                         alpha=0.8)
    ax.add_patch(card)
    
    ax.text(x + 0.5, y + 1.3, emoji, fontsize=20, ha='left', va='center')
    ax.text(x + 1.5, y + 1.3, title, fontsize=13, fontweight='bold', 
            ha='left', va='center', color=colors['primary'])
    ax.text(x + 0.5, y + 0.6, desc, fontsize=9, 
            ha='left', va='center', color=colors['text'], linespacing=1.5)

# ========== 技能包分类 ==========
skills_y = 6.5
ax.text(8, skills_y + 0.5, '📦 技能包生态系统', fontsize=18, fontweight='bold',
        ha='center', va='center', color=colors['primary'])

skill_categories = [
    ('股票分析', 'stock-analysis-pro\nstock-alert\nstock-earnings-calendar', colors['success']),
    ('搜索工具', 'web-search\nskill-finder\nsummarize', colors['secondary']),
    ('文档处理', 'office-pro\npdf-data-extractor\nnano-pdf', colors['accent']),
    ('安全防护', 'security-scanner\nsystem-guard\nsystem-backup', colors['primary']),
    ('自我进化', 'self-improvement\nperformance-monitor', colors['secondary']),
    ('系统工具', 'time-toolkit\nfile-management\ndata-processor', colors['accent']),
]

for i, (cat_name, skills, color) in enumerate(skill_categories):
    row = i // 3
    col = i % 3
    x = 0.8 + col * 5.1
    y = 4.5 - row * 2.3
    
    # 分类卡片
    card = FancyBboxPatch((x, y), 4.8, 2,
                         boxstyle="round,pad=0.06",
                         facecolor='white',
                         edgecolor=color,
                         linewidth=2,
                         alpha=0.9)
    ax.add_patch(card)
    
    # 顶部色条
    bar = Rectangle((x, y + 1.6), 4.8, 0.4, 
                    facecolor=color, alpha=0.8)
    ax.add_patch(bar)
    
    ax.text(x + 2.4, y + 1.8, cat_name, fontsize=11, fontweight='bold',
            ha='center', va='center', color='white')
    ax.text(x + 2.4, y + 0.8, skills, fontsize=8,
            ha='center', va='center', color=colors['text'], linespacing=1.4)

# ========== 自动化运维时间线 ==========
timeline_y = 1.8
ax.text(8, timeline_y + 0.5, '⏰ 自动化运维时间线', fontsize=18, fontweight='bold',
        ha='center', va='center', color=colors['primary'])

timeline_items = [
    ('00:00', '备份检查'),
    ('08:00', '健康检查'),
    ('08:30', '英语新闻'),
    ('16:30', '股票日报'),
    ('22:00', '系统备份'),
]

for i, (time, task) in enumerate(timeline_items):
    x = 1.2 + i * 3
    
    # 时间节点
    circle = Circle((x + 0.5, timeline_y - 0.3), 0.25, 
                   facecolor=colors['primary'], edgecolor='white', linewidth=2)
    ax.add_patch(circle)
    
    # 时间
    ax.text(x + 0.5, timeline_y - 0.05, time, fontsize=9, fontweight='bold',
            ha='center', va='center', color=colors['primary'])
    
    # 任务
    ax.text(x + 0.5, timeline_y - 0.75, task, fontsize=8,
            ha='center', va='center', color=colors['text'])
    
    # 连接线
    if i < len(timeline_items) - 1:
        ax.plot([x + 0.75, x + 2.75], [timeline_y - 0.3, timeline_y - 0.3], 
               color=colors['primary'], linewidth=2, alpha=0.5)

# ========== 底部标语 ==========
ax.text(8, 0.3, '🦞 不只是聊天机器人，是生产级的智能工具包生态系统',
        fontsize=11, ha='center', va='center', 
        color=colors['primary'], fontweight='bold', style='italic')

# 保存图片
plt.tight_layout()
plt.savefig('/Users/zhaoruicn/.openclaw/workspace/showcase_infographic.png', 
            dpi=150, bbox_inches='tight', facecolor='#f5f5f5')
plt.close()

print("✅ 信息图已生成: showcase_infographic.png")
