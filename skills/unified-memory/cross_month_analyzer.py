#!/usr/bin/env python3
"""
跨月主题关联分析模块 (Cross-Month Theme Analyzer)
分析多个月份的主题演变趋势、长期关注点和模式转变
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any
import re

# 配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
INDEX_DIR = MEMORY_DIR / "index"
SUMMARY_DIR = MEMORY_DIR / "summary"
REPORTS_DIR = MEMORY_DIR / "reports"

# 确保目录存在
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class ThemeEvolutionTracker:
    """主题演变追踪器"""
    
    def __init__(self):
        self.themes_data = self._load_themes_data()
        self.keywords_data = self._load_keywords_data()
    
    def _load_themes_data(self) -> Dict:
        """加载主题索引数据"""
        themes_file = INDEX_DIR / "themes.json"
        if themes_file.exists():
            with open(themes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_keywords_data(self) -> Dict:
        """加载关键词索引数据"""
        kw_file = INDEX_DIR / "keywords.json"
        if kw_file.exists():
            with open(kw_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_available_months(self) -> List[str]:
        """获取可用的月份列表"""
        months = list(self.themes_data.keys())
        return sorted(months)
    
    def analyze_theme_evolution(self, months: List[str] = None) -> Dict[str, Any]:
        """
        分析主题演变趋势
        
        Args:
            months: 要分析的月份列表，如果为None则使用所有可用月份
            
        Returns:
            主题演变分析结果
        """
        if not months:
            months = self.get_available_months()
        
        if len(months) < 2:
            print(f"⚠️ 至少需要2个月的数据才能分析演变趋势 (当前: {len(months)}个月)")
            return {"error": "需要至少2个月的数据"}
        
        print(f"📊 分析 {len(months)} 个月的主题演变: {', '.join(months)}")
        
        # 收集所有主题
        all_themes = set()
        theme_timeline = defaultdict(lambda: defaultdict(int))
        
        for month in months:
            if month in self.themes_data:
                themes = self.themes_data[month].get("themes", {})
                for theme, count in themes.items():
                    all_themes.add(theme)
                    theme_timeline[theme][month] = count
        
        # 分析每个主题的演变
        evolution_analysis = {}
        
        for theme in all_themes:
            timeline = {month: theme_timeline[theme].get(month, 0) for month in months}
            values = list(timeline.values())
            
            # 计算演变指标
            non_zero_months = sum(1 for v in values if v > 0)
            first_appearance = next((m for m in months if timeline[m] > 0), None)
            last_appearance = next((m for m in reversed(months) if timeline[m] > 0), None)
            
            # 趋势分析
            trend = self._calculate_trend(values)
            
            evolution_analysis[theme] = {
                "timeline": timeline,
                "total_mentions": sum(values),
                "active_months": non_zero_months,
                "first_appearance": first_appearance,
                "last_appearance": last_appearance,
                "consistency": non_zero_months / len(months),
                "trend": trend,
                "trend_direction": trend["direction"]
            }
        
        # 按总提及次数排序
        sorted_analysis = dict(sorted(
            evolution_analysis.items(),
            key=lambda x: x[1]["total_mentions"],
            reverse=True
        ))
        
        result = {
            "months": months,
            "total_themes": len(all_themes),
            "theme_evolution": sorted_analysis,
            "generated_at": datetime.now().isoformat()
        }
        
        print(f"✅ 主题演变分析完成: 发现 {len(all_themes)} 个主题")
        return result
    
    def _calculate_trend(self, values: List[int]) -> Dict:
        """计算趋势指标"""
        if len(values) < 2:
            return {"direction": "stable", "slope": 0, "change_rate": 0}
        
        # 简单线性趋势
        n = len(values)
        x = list(range(n))
        
        # 计算斜率 (简化版)
        if values[0] == 0:
            change_rate = values[-1] if values[-1] > 0 else 0
        else:
            change_rate = (values[-1] - values[0]) / values[0] if values[0] != 0 else 0
        
        # 判断方向
        if change_rate > 0.3:
            direction = "上升"
        elif change_rate < -0.3:
            direction = "下降"
        else:
            # 检查波动
            non_zero = [v for v in values if v > 0]
            if len(non_zero) >= n * 0.7:
                direction = "稳定"
            elif len(non_zero) >= n * 0.3:
                direction = "间歇"
            else:
                direction = "偶尔"
        
        return {
            "direction": direction,
            "first_value": values[0],
            "last_value": values[-1],
            "change_rate": round(change_rate, 2),
            "peak_value": max(values),
            "avg_value": round(sum(values) / n, 2)
        }
    
    def identify_long_term_focus(self, min_months: int = 2, min_consistency: float = 0.3) -> Dict[str, Any]:
        """
        识别长期关注的重点领域
        
        Args:
            min_months: 最少活跃月数
            min_consistency: 最低一致性比例
            
        Returns:
            长期关注点分析结果
        """
        months = self.get_available_months()
        
        if len(months) < min_months:
            print(f"⚠️ 数据不足: 需要至少{min_months}个月的数据")
            return {"error": f"需要至少{min_months}个月的数据"}
        
        print(f"🔍 识别长期关注点 (数据跨度: {len(months)}个月)...")
        
        evolution = self.analyze_theme_evolution(months)
        if "error" in evolution:
            return evolution
        
        long_term_focus = {}
        emerging_themes = {}
        declining_themes = {}
        
        for theme, data in evolution["theme_evolution"].items():
            # 长期关注标准
            if (data["active_months"] >= min_months and 
                data["consistency"] >= min_consistency):
                
                long_term_focus[theme] = {
                    "total_mentions": data["total_mentions"],
                    "consistency": round(data["consistency"], 2),
                    "trend": data["trend"],
                    "first_appearance": data["first_appearance"],
                    "last_appearance": data["last_appearance"]
                }
            
            # 新兴主题 (最近出现且上升)
            if data["trend"]["direction"] == "上升" and data["active_months"] <= 2:
                emerging_themes[theme] = data
            
            # 衰退主题 (之前活跃但最近下降)
            if data["trend"]["direction"] == "下降" and data["active_months"] >= 2:
                declining_themes[theme] = data
        
        # 按重要性排序
        long_term_focus = dict(sorted(
            long_term_focus.items(),
            key=lambda x: (x[1]["consistency"], x[1]["total_mentions"]),
            reverse=True
        ))
        
        result = {
            "months_span": len(months),
            "months_range": f"{months[0]} ~ {months[-1]}",
            "long_term_focus": long_term_focus,
            "emerging_themes": emerging_themes,
            "declining_themes": declining_themes,
            "generated_at": datetime.now().isoformat()
        }
        
        print(f"✅ 长期关注点识别完成:")
        print(f"   - 长期关注: {len(long_term_focus)} 个")
        print(f"   - 新兴主题: {len(emerging_themes)} 个")
        print(f"   - 衰退主题: {len(declining_themes)} 个")
        
        return result
    
    def detect_pattern_shifts(self, window_size: int = 2) -> Dict[str, Any]:
        """
        检测工作模式的转变
        
        Args:
            window_size: 滑动窗口大小
            
        Returns:
            模式转变分析结果
        """
        months = self.get_available_months()
        
        if len(months) < window_size * 2:
            print(f"⚠️ 数据不足以检测模式转变")
            return {"error": "数据不足以检测模式转变"}
        
        print(f"🔄 检测工作模式转变 (窗口大小: {window_size}个月)...")
        
        # 分窗口分析
        early_window = months[:window_size]
        late_window = months[-window_size:]
        
        # 收集各窗口的主题分布
        early_themes = defaultdict(int)
        late_themes = defaultdict(int)
        
        for month in early_window:
            if month in self.themes_data:
                for theme, count in self.themes_data[month].get("themes", {}).items():
                    early_themes[theme] += count
        
        for month in late_window:
            if month in self.themes_data:
                for theme, count in self.themes_data[month].get("themes", {}).items():
                    late_themes[theme] += count
        
        # 分析转变
        all_themes = set(early_themes.keys()) | set(late_themes.keys())
        
        gained_focus = {}  # 新获得关注
        lost_focus = {}    # 失去关注
        intensified = {}   # 加强关注
        reduced = {}       # 减少关注
        
        for theme in all_themes:
            early_count = early_themes.get(theme, 0)
            late_count = late_themes.get(theme, 0)
            
            if early_count == 0 and late_count > 0:
                gained_focus[theme] = {"mentions": late_count}
            elif early_count > 0 and late_count == 0:
                lost_focus[theme] = {"mentions": early_count}
            elif early_count > 0 and late_count > early_count * 1.5:
                intensified[theme] = {
                    "early": early_count,
                    "late": late_count,
                    "growth": round((late_count - early_count) / early_count, 2)
                }
            elif early_count > 0 and late_count < early_count * 0.5:
                reduced[theme] = {
                    "early": early_count,
                    "late": late_count,
                    "decline": round((early_count - late_count) / early_count, 2)
                }
        
        # 分析关键词转变
        keyword_shifts = self._analyze_keyword_shifts(early_window, late_window)
        
        result = {
            "early_window": early_window,
            "late_window": late_window,
            "pattern_shifts": {
                "gained_focus": gained_focus,
                "lost_focus": lost_focus,
                "intensified": intensified,
                "reduced": reduced
            },
            "keyword_shifts": keyword_shifts,
            "generated_at": datetime.now().isoformat()
        }
        
        print(f"✅ 模式转变检测完成:")
        print(f"   - 新增关注: {len(gained_focus)} 个主题")
        print(f"   - 失去关注: {len(lost_focus)} 个主题")
        print(f"   - 关注加强: {len(intensified)} 个主题")
        print(f"   - 关注减弱: {len(reduced)} 个主题")
        
        return result
    
    def _analyze_keyword_shifts(self, early_window: List[str], late_window: List[str]) -> Dict:
        """分析关键词的转变"""
        early_keywords = defaultdict(int)
        late_keywords = defaultdict(int)
        
        for month in early_window:
            if month in self.keywords_data:
                for kw, count in self.keywords_data[month].get("keywords", []):
                    early_keywords[kw] += count
        
        for month in late_window:
            if month in self.keywords_data:
                for kw, count in self.keywords_data[month].get("keywords", []):
                    late_keywords[kw] += count
        
        # 新兴关键词
        new_keywords = []
        for kw, count in late_keywords.items():
            if kw not in early_keywords and count >= 3:
                new_keywords.append((kw, count))
        
        # 衰退关键词
        faded_keywords = []
        for kw, count in early_keywords.items():
            if kw not in late_keywords or late_keywords[kw] < count * 0.3:
                faded_keywords.append((kw, count))
        
        return {
            "new_keywords": sorted(new_keywords, key=lambda x: x[1], reverse=True)[:10],
            "faded_keywords": sorted(faded_keywords, key=lambda x: x[1], reverse=True)[:10]
        }
    
    def generate_evolution_report(self, output_format: str = "markdown") -> str:
        """
        生成主题演变可视化报告
        
        Args:
            output_format: 输出格式 (markdown/html/json)
            
        Returns:
            报告文件路径
        """
        print("📊 生成主题演变报告...")
        
        months = self.get_available_months()
        
        if not months:
            print("⚠️ 没有可用的月度数据")
            return None
        
        # 执行所有分析
        evolution = self.analyze_theme_evolution(months)
        long_term = self.identify_long_term_focus()
        shifts = self.detect_pattern_shifts() if len(months) >= 2 else {"error": "数据不足"}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == "json":
            report_file = REPORTS_DIR / f"theme_evolution_{timestamp}.json"
            report_data = {
                "evolution_analysis": evolution,
                "long_term_focus": long_term,
                "pattern_shifts": shifts,
                "generated_at": datetime.now().isoformat()
            }
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        else:  # markdown
            report_file = REPORTS_DIR / f"theme_evolution_{timestamp}.md"
            report_content = self._generate_markdown_report(evolution, long_term, shifts)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        print(f"✅ 报告已生成: {report_file}")
        return str(report_file)
    
    def _generate_markdown_report(self, evolution: Dict, long_term: Dict, shifts: Dict) -> str:
        """生成Markdown格式的报告"""
        
        content = f"""# 🧠 主题演变分析报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 数据来源: unified-memory 系统

---

## 📊 数据概览

- **分析月份**: {len(evolution.get('months', []))} 个月
- **月份范围**: {' ~ '.join(evolution.get('months', [])[:1] + evolution.get('months', [])[-1:]) if evolution.get('months') else 'N/A'}
- **主题总数**: {evolution.get('total_themes', 0)} 个

---

## 📈 主题演变趋势

### 活跃主题时间线

| 主题 | 总提及 | 活跃月数 | 首次出现 | 最后出现 | 趋势 |
|------|--------|----------|----------|----------|------|
"""
        
        for theme, data in list(evolution.get("theme_evolution", {}).items())[:15]:
            trend_icon = {
                "上升": "📈",
                "下降": "📉",
                "稳定": "➡️",
                "间歇": "〰️",
                "偶尔": "🔘"
            }.get(data["trend_direction"], "➖")
            
            content += f"| {theme} | {data['total_mentions']} | {data['active_months']} | {data['first_appearance']} | {data['last_appearance']} | {trend_icon} {data['trend_direction']} |\n"
        
        # 长期关注
        content += f"""

---

## 🎯 长期关注点

"""
        
        long_focus = long_term.get("long_term_focus", {})
        if long_focus:
            content += f"**数据跨度**: {long_term.get('months_span', 0)} 个月 ({long_term.get('months_range', 'N/A')})\n\n"
            content += "| 主题 | 总提及 | 一致性 | 趋势 | 持续时间 |\n"
            content += "|------|--------|--------|------|----------|\n"
            
            for theme, data in list(long_focus.items())[:10]:
                trend = data["trend"]["direction"]
                duration = f"{data['first_appearance']} ~ {data['last_appearance']}"
                content += f"| **{theme}** | {data['total_mentions']} | {data['consistency']*100:.0f}% | {trend} | {duration} |\n"
        else:
            content += "暂未达到长期关注标准的主题\n"
        
        # 新兴主题
        emerging = long_term.get("emerging_themes", {})
        if emerging:
            content += f"""

### 🌱 新兴主题

| 主题 | 提及次数 | 趋势 |
|------|----------|------|
"""
            for theme, data in list(emerging.items())[:5]:
                content += f"| {theme} | {data['total_mentions']} | {data['trend']['direction']} |\n"
        
        # 模式转变
        content += f"""

---

## 🔄 工作模式转变

"""
        
        if "error" not in shifts:
            pattern_shifts = shifts.get("pattern_shifts", {})
            
            gained = pattern_shifts.get("gained_focus", {})
            if gained:
                content += "### 📌 新增关注的主题\n\n"
                for theme, data in list(gained.items())[:5]:
                    content += f"- **{theme}**: {data['mentions']} 次提及\n"
                content += "\n"
            
            lost = pattern_shifts.get("lost_focus", {})
            if lost:
                content += "### 📉 失去关注的主题\n\n"
                for theme, data in list(lost.items())[:5]:
                    content += f"- **{theme}**: 之前 {data['mentions']} 次提及\n"
                content += "\n"
            
            intensified = pattern_shifts.get("intensified", {})
            if intensified:
                content += "### 🔥 关注加强的主题\n\n"
                content += "| 主题 | 前期 | 后期 | 增长率 |\n"
                content += "|------|------|------|--------|\n"
                for theme, data in list(intensified.items())[:5]:
                    content += f"| {theme} | {data['early']} | {data['late']} | +{data['growth']*100:.0f}% |\n"
                content += "\n"
            
            # 关键词转变
            kw_shifts = shifts.get("keyword_shifts", {})
            new_kw = kw_shifts.get("new_keywords", [])
            faded_kw = kw_shifts.get("faded_keywords", [])
            
            if new_kw:
                content += "### ✨ 新兴关键词\n\n"
                content += ", ".join([f"**{kw}** ({count})" for kw, count in new_kw[:8]])
                content += "\n\n"
            
            if faded_kw:
                content += "### 💤 衰退关键词\n\n"
                content += ", ".join([f"*{kw}* ({count})" for kw, count in faded_kw[:8]])
                content += "\n\n"
        else:
            content += "数据不足以分析模式转变\n"
        
        # 可视化图表 (ASCII)
        content += """

---

## 📊 主题活跃度可视化

```
"""
        
        top_themes = list(evolution.get("theme_evolution", {}).items())[:8]
        months = evolution.get("months", [])
        
        if months and top_themes:
            # 标题行
            content += "主题     "
            for m in months:
                content += f"| {m[-2:]} "  # 只显示月份
            content += "| 总计\n"
            content += "-" * (10 + len(months) * 6 + 8) + "\n"
            
            # 数据行
            for theme, data in top_themes:
                content += f"{theme[:8]:8} "
                for m in months:
                    count = data["timeline"].get(m, 0)
                    char = "█" if count >= 5 else "▓" if count >= 3 else "▒" if count >= 1 else "░"
                    content += f"|  {char} "
                content += f"| {data['total_mentions']:3}\n"
        
        content += """```

---

## 💡 洞察与建议

"""
        
        # 生成洞察
        insights = self._generate_insights(long_term, shifts)
        for i, insight in enumerate(insights, 1):
            content += f"{i}. {insight}\n"
        
        content += f"""

---

*报告由 cross_month_analyzer.py 自动生成*
*统一记忆系统 - {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        return content
    
    def _generate_insights(self, long_term: Dict, shifts: Dict) -> List[str]:
        """生成洞察建议"""
        insights = []
        
        long_focus = long_term.get("long_term_focus", {})
        if long_focus:
            top_theme = next(iter(long_focus.keys()))
            insights.append(f"**长期核心关注**: '{top_theme}' 是最持续的焦点，建议保持深入跟踪")
        
        emerging = long_term.get("emerging_themes", {})
        if emerging:
            themes = list(emerging.keys())[:2]
            insights.append(f"**新兴趋势**: {'、'.join(themes)} 是近期新出现的关注点，值得投入更多资源")
        
        if "error" not in shifts:
            gained = shifts.get("pattern_shifts", {}).get("gained_focus", {})
            if gained:
                insights.append(f"**新方向**: 开始关注 {list(gained.keys())[0]} 等新领域，可能是战略调整")
            
            intensified = shifts.get("pattern_shifts", {}).get("intensified", {})
            if intensified:
                top = list(intensified.items())[0]
                insights.append(f"**重点加强**: 对 '{top[0]}' 的关注提升了 {top[1]['growth']*100:.0f}%，进入深度阶段")
        
        if not insights:
            insights.append("数据正在积累中，建议持续记录以获得更准确的分析")
        
        return insights


# CLI 接口
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="跨月主题关联分析")
    parser.add_argument("command", choices=["evolution", "focus", "shifts", "report", "status"])
    parser.add_argument("--months", "-m", nargs="+", help="指定月份 (格式: YYYY-MM)")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown",
                       help="报告格式")
    
    args = parser.parse_args()
    
    tracker = ThemeEvolutionTracker()
    
    if args.command == "evolution":
        result = tracker.analyze_theme_evolution(args.months)
        if "error" not in result:
            print(f"\n📈 主题演变分析结果:")
            print(f"   分析月份: {', '.join(result['months'])}")
            print(f"   主题总数: {result['total_themes']}")
            for theme, data in list(result['theme_evolution'].items())[:5]:
                print(f"   - {theme}: {data['total_mentions']}次, 趋势: {data['trend_direction']}")
    
    elif args.command == "focus":
        result = tracker.identify_long_term_focus()
        if "error" not in result:
            print(f"\n🎯 长期关注点:")
            for theme, data in list(result['long_term_focus'].items())[:5]:
                print(f"   - {theme}: 一致性 {data['consistency']*100:.0f}%, 趋势: {data['trend']['direction']}")
    
    elif args.command == "shifts":
        result = tracker.detect_pattern_shifts()
        if "error" not in result:
            print(f"\n🔄 模式转变:")
            shifts = result.get('pattern_shifts', {})
            if shifts.get('gained_focus'):
                print(f"   新增: {', '.join(list(shifts['gained_focus'].keys())[:3])}")
            if shifts.get('lost_focus'):
                print(f"   失去: {', '.join(list(shifts['lost_focus'].keys())[:3])}")
    
    elif args.command == "report":
        report_path = tracker.generate_evolution_report(args.format)
        if report_path:
            print(f"\n✅ 报告已保存到: {report_path}")
    
    elif args.command == "status":
        months = tracker.get_available_months()
        print("=" * 50)
        print("🧠 跨月主题分析系统状态")
        print("=" * 50)
        print(f"\n📅 可用月份: {len(months)} 个")
        for m in months:
            themes_count = len(tracker.themes_data.get(m, {}).get('themes', {}))
            kw_count = len(tracker.keywords_data.get(m, {}).get('keywords', []))
            print(f"   - {m}: {themes_count} 主题, {kw_count} 关键词")
        print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
