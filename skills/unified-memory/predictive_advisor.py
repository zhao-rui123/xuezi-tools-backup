#!/usr/bin/env python3
"""
预测性工作建议模块 (Predictive Work Advisor)
基于历史记忆数据，预测未来工作重点，主动提醒待办事项，优化工作节奏
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional
import statistics

# 配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SUMMARY_DIR = MEMORY_DIR / "summary"
ENHANCED_MEMORY = WORKSPACE / ".memory" / "enhanced" / "memories.json"

# 主题关键词映射
TOPIC_KEYWORDS = {
    "储能项目": ["储能", "电站", "光伏", "锂电池", "PCS", "BMS", "容量", "kWh", "MWh", "收益", "IRR"],
    "股票分析": ["股票", "股市", "K线", "均线", "RSI", "MACD", "持仓", "买入", "卖出", "行情"],
    "技能包开发": ["技能包", "SKILL", "OpenClaw", "API", "开发", "Python", "代码", "模块"],
    "系统运维": ["服务器", "部署", "备份", "日志", "监控", "nginx", "SSH", "重启"],
    "记忆管理": ["记忆", "MEMORY", "知识库", "备份", "整理", "摘要"],
    "零碳园区": ["零碳", "园区", "碳中和", "多能互补", "微网", "能源管理"],
}

# 任务相关关键词
TASK_KEYWORDS = [
    "TODO", "待办", "任务", "需要完成", "计划", "安排", "准备", "开始",
    "TODO:", "【TODO】", "[TODO]", "待处理", "未完成"
]

# 截止日期模式
DEADLINE_PATTERNS = [
    r'(\d{1,2})[月/](\d{1,2})[日号]?',
    r'下周([一二三四五六日])',
    r'(明天|后天|大后天)',
    r'(\d{1,2})号',
]


class PredictiveAdvisor:
    """预测性工作建议器"""
    
    def __init__(self):
        self.memory_files = self._load_memory_files()
        self.enhanced_memories = self._load_enhanced_memories()
        self.daily_memories = self._parse_daily_memories()
        
    def _load_memory_files(self) -> List[Path]:
        """加载所有记忆文件"""
        files = []
        if MEMORY_DIR.exists():
            for f in MEMORY_DIR.glob("*.md"):
                try:
                    # 验证文件名是否为日期格式
                    datetime.strptime(f.stem.split('-')[0], "%Y")
                    files.append(f)
                except:
                    continue
        return sorted(files)
    
    def _load_enhanced_memories(self) -> List[Dict]:
        """加载增强记忆数据"""
        if ENHANCED_MEMORY.exists():
            with open(ENHANCED_MEMORY, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _parse_daily_memories(self) -> List[Dict]:
        """解析每日记忆文件内容"""
        parsed = []
        for f in self.memory_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    content = fp.read()
                
                # 尝试解析日期
                try:
                    date = datetime.strptime(f.stem[:10], "%Y-%m-%d")
                except:
                    continue
                
                parsed.append({
                    'file': f.name,
                    'date': date,
                    'content': content,
                    'length': len(content)
                })
            except Exception as e:
                continue
        return sorted(parsed, key=lambda x: x['date'])
    
    def _extract_topics(self, text: str) -> Dict[str, int]:
        """提取文本中的主题分布"""
        topics = defaultdict(int)
        for topic, keywords in TOPIC_KEYWORDS.items():
            for kw in keywords:
                count = len(re.findall(kw, text, re.IGNORECASE))
                if count > 0:
                    topics[topic] += count
        return dict(topics)
    
    def _extract_tasks(self, text: str) -> List[Dict]:
        """从文本中提取待办任务"""
        tasks = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否包含任务关键词
            is_task = any(kw in line for kw in TASK_KEYWORDS)
            
            # 检查是否为已完成（简单启发式）
            is_done = any(marker in line for marker in ['[x]', '[X]', '✓', '✅', '已完成', '已处理'])
            
            if is_task and not is_done:
                # 尝试提取截止日期
                deadline = None
                for pattern in DEADLINE_PATTERNS:
                    match = re.search(pattern, line)
                    if match:
                        deadline = match.group(0)
                        break
                
                tasks.append({
                    'text': line[:100],  # 限制长度
                    'deadline_hint': deadline,
                    'is_done': is_done
                })
        
        return tasks
    
    def predict_next_week_focus(self) -> Dict:
        """
        预测下周工作重点
        
        基于最近的工作模式，预测下周应该关注的主题
        """
        # 获取最近14天的数据
        recent_cutoff = datetime.now() - timedelta(days=14)
        recent_memories = [m for m in self.daily_memories if m['date'] >= recent_cutoff]
        
        if not recent_memories:
            return {
                'status': 'insufficient_data',
                'message': '近期数据不足，无法预测',
                'focus_areas': []
            }
        
        # 统计近期主题分布
        topic_counts = defaultdict(lambda: {'count': 0, 'last_date': None, 'days_active': set()})
        
        for mem in recent_memories:
            topics = self._extract_topics(mem['content'])
            for topic, count in topics.items():
                topic_counts[topic]['count'] += count
                topic_counts[topic]['days_active'].add(mem['date'].strftime('%Y-%m-%d'))
                if topic_counts[topic]['last_date'] is None or mem['date'] > topic_counts[topic]['last_date']:
                    topic_counts[topic]['last_date'] = mem['date']
        
        # 计算活跃度和趋势
        scored_topics = []
        today = datetime.now()
        
        for topic, data in topic_counts.items():
            days_since_last = (today - data['last_date']).days if data['last_date'] else 999
            active_days = len(data['days_active'])
            
            # 评分算法：
            # - 频次分：出现次数权重
            # - 活跃度分：活跃天数权重
            # - 时效分：越近越重要
            freq_score = min(data['count'] / 5, 3)  # 最多3分
            active_score = min(active_days / 3, 2)  # 最多2分
            recency_score = max(0, 2 - days_since_last / 7)  # 一周内2分，递减
            
            total_score = freq_score + active_score + recency_score
            
            scored_topics.append({
                'topic': topic,
                'score': round(total_score, 2),
                'frequency': data['count'],
                'active_days': active_days,
                'days_since_last': days_since_last,
                'confidence': 'high' if total_score > 4 else 'medium' if total_score > 2 else 'low'
            })
        
        # 按分数排序
        scored_topics.sort(key=lambda x: x['score'], reverse=True)
        
        # 生成预测建议
        top_topics = scored_topics[:3]
        
        predictions = []
        for t in top_topics:
            if t['days_since_last'] <= 2:
                trend = "持续进行中"
            elif t['days_since_last'] <= 7:
                trend = "近期活跃"
            else:
                trend = "需要关注"
            
            predictions.append({
                'topic': t['topic'],
                'confidence': t['confidence'],
                'trend': trend,
                'suggestion': self._generate_focus_suggestion(t['topic'], t)
            })
        
        return {
            'status': 'success',
            'prediction_date': today.strftime('%Y-%m-%d'),
            'prediction_period': '下周',
            'focus_areas': predictions,
            'all_scored': scored_topics
        }
    
    def _generate_focus_suggestion(self, topic: str, data: Dict) -> str:
        """生成针对主题的建议"""
        suggestions = {
            '储能项目': '继续推进储能项目测算，关注最新电价政策变化',
            '股票分析': '定期复盘自选股表现，关注财报季动态',
            '技能包开发': '完善现有技能包功能，考虑开发新模块',
            '系统运维': '检查服务器状态，确保备份机制正常运行',
            '记忆管理': '整理近期记忆，更新知识库索引',
            '零碳园区': '跟进园区项目进展，协调相关资源'
        }
        return suggestions.get(topic, f'继续推进{topic}相关工作')
    
    def suggest_work_rhythm(self) -> Dict:
        """
        建议工作节奏
        
        基于历史工作模式，提供工作节奏优化建议
        """
        if len(self.daily_memories) < 7:
            return {
                'status': 'insufficient_data',
                'message': '数据不足，需要至少一周的记忆数据',
                'suggestions': []
            }
        
        # 分析工作强度模式
        daily_stats = []
        for mem in self.daily_memories[-30:]:  # 最近30天
            # 计算当日工作强度（基于内容长度和主题数）
            topics = self._extract_topics(mem['content'])
            intensity = len(mem['content']) / 1000 + len(topics) * 2
            
            weekday = mem['date'].weekday()  # 0=周一
            
            daily_stats.append({
                'date': mem['date'],
                'weekday': weekday,
                'weekday_name': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][weekday],
                'intensity': intensity,
                'topics_count': len(topics),
                'content_length': len(mem['content'])
            })
        
        # 按星期几分组统计
        weekday_pattern = defaultdict(list)
        for stat in daily_stats:
            weekday_pattern[stat['weekday']].append(stat['intensity'])
        
        # 计算各天平均强度
        weekday_avg = {}
        for wd, intensities in weekday_pattern.items():
            if intensities:
                weekday_avg[wd] = {
                    'avg_intensity': statistics.mean(intensities),
                    'max_intensity': max(intensities),
                    'count': len(intensities)
                }
        
        # 识别高低强度日
        high_intensity_days = [wd for wd, data in weekday_avg.items() if data['avg_intensity'] > 5]
        low_intensity_days = [wd for wd, data in weekday_avg.items() if data['avg_intensity'] < 2]
        
        # 检测连续高强度工作模式
        consecutive_high = 0
        max_consecutive = 0
        for stat in daily_stats:
            if stat['intensity'] > 5:
                consecutive_high += 1
                max_consecutive = max(max_consecutive, consecutive_high)
            else:
                consecutive_high = 0
        
        # 生成建议
        suggestions = []
        
        # 基于强度分布的建议
        if max_consecutive >= 5:
            suggestions.append({
                'type': 'warning',
                'message': f'检测到连续{max_consecutive}天高强度工作，建议安排休息',
                'action': '本周安排至少1天轻松任务或休息'
            })
        
        # 基于工作日模式的建议
        if high_intensity_days:
            day_names = [['周一', '周二', '周三', '周四', '周五', '周六', '周日'][d] for d in sorted(high_intensity_days)]
            suggestions.append({
                'type': 'pattern',
                'message': f'通常在{", ".join(day_names)}工作强度较高',
                'action': '高强度日安排核心任务，提前准备资源'
            })
        
        # 工作多样性建议
        recent_topics = set()
        for mem in self.daily_memories[-7:]:
            topics = self._extract_topics(mem['content'])
            recent_topics.update(topics.keys())
        
        if len(recent_topics) < 2:
            suggestions.append({
                'type': 'variety',
                'message': '最近工作主题较单一，可能产生疲劳',
                'action': '安排不同类型的任务交叉进行'
            })
        
        # 一致性建议
        intensity_variance = statistics.stdev([s['intensity'] for s in daily_stats]) if len(daily_stats) > 1 else 0
        if intensity_variance > 5:
            suggestions.append({
                'type': 'balance',
                'message': '工作强度波动较大',
                'action': '尝试保持更稳定的工作节奏，避免忽忙忽闲'
            })
        
        return {
            'status': 'success',
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'work_pattern': {
                'high_intensity_days': [['周一', '周二', '周三', '周四', '周五', '周六', '周日'][d] for d in high_intensity_days],
                'low_intensity_days': [['周一', '周二', '周三', '周四', '周五', '周六', '周日'][d] for d in low_intensity_days],
                'max_consecutive_high': max_consecutive,
                'intensity_variance': round(intensity_variance, 2),
                'recent_diversity': len(recent_topics)
            },
            'suggestions': suggestions,
            'optimal_schedule': self._generate_optimal_schedule(weekday_avg)
        }
    
    def _generate_optimal_schedule(self, weekday_avg: Dict) -> List[Dict]:
        """生成最优工作日程建议"""
        schedule = []
        
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        for wd in range(7):
            if wd in weekday_avg:
                intensity = weekday_avg[wd]['avg_intensity']
                if intensity > 5:
                    task_type = '核心项目工作'
                    note = '精力充沛，处理复杂任务'
                elif intensity > 3:
                    task_type = '常规工作+学习'
                    note = '保持稳定产出'
                else:
                    task_type = '轻度任务/规划'
                    note = '适合复盘、计划、轻松任务'
            else:
                task_type = '灵活安排'
                note = '无历史数据'
            
            schedule.append({
                'day': weekday_names[wd],
                'suggested_focus': task_type,
                'note': note
            })
        
        return schedule
    
    def remind_overdue_items(self) -> Dict:
        """
        提醒逾期事项
        
        扫描记忆中的待办事项，识别可能已逾期的任务
        """
        today = datetime.now()
        overdue_items = []
        upcoming_items = []
        
        # 扫描最近30天的记忆
        recent_cutoff = today - timedelta(days=30)
        recent_memories = [m for m in self.daily_memories if m['date'] >= recent_cutoff]
        
        # 提取所有任务
        all_tasks = []
        for mem in recent_memories:
            tasks = self._extract_tasks(mem['content'])
            for task in tasks:
                task['source_date'] = mem['date']
                task['source_file'] = mem['file']
                all_tasks.append(task)
        
        # 分析任务状态
        for task in all_tasks:
            days_ago = (today - task['source_date']).days
            
            # 启发式判断逾期
            is_overdue = False
            is_upcoming = False
            
            # 如果任务提到"明天"且已过去1天以上
            if '明天' in task['text'] and days_ago >= 2:
                is_overdue = True
            
            # 如果任务提到"下周"且已过去7天以上
            if '下周' in task['text'] and days_ago >= 8:
                is_overdue = True
            
            # 如果任务已存在超过3天且没有明确完成标记
            if days_ago >= 3 and days_ago <= 7:
                is_upcoming = True
            elif days_ago > 7:
                is_overdue = True
            
            item = {
                'task': task['text'],
                'created': task['source_date'].strftime('%Y-%m-%d'),
                'days_ago': days_ago,
                'source': task['source_file']
            }
            
            if is_overdue:
                overdue_items.append(item)
            elif is_upcoming:
                upcoming_items.append(item)
        
        # 去重
        seen = set()
        overdue_items = [x for x in overdue_items if not (x['task'] in seen or seen.add(x['task']))]
        seen = set()
        upcoming_items = [x for x in upcoming_items if not (x['task'] in seen or seen.add(x['task']))]
        
        # 限制数量
        overdue_items = overdue_items[:10]
        upcoming_items = upcoming_items[:5]
        
        return {
            'status': 'success',
            'check_date': today.strftime('%Y-%m-%d'),
            'summary': {
                'total_pending': len(all_tasks),
                'overdue_count': len(overdue_items),
                'upcoming_count': len(upcoming_items)
            },
            'overdue_items': overdue_items,
            'upcoming_items': upcoming_items,
            'recommendations': self._generate_reminder_recommendations(overdue_items, upcoming_items)
        }
    
    def _generate_reminder_recommendations(self, overdue: List[Dict], upcoming: List[Dict]) -> List[str]:
        """生成提醒建议"""
        recommendations = []
        
        if overdue:
            recommendations.append(f'有 {len(overdue)} 项任务可能已逾期，建议优先处理')
            recommendations.append('逾期超过3天的任务建议重新评估优先级')
        
        if upcoming:
            recommendations.append(f'有 {len(upcoming)} 项待办任务需要跟进')
        
        if not overdue and not upcoming:
            recommendations.append('暂无逾期任务，保持良好节奏！')
        
        return recommendations
    
    def analyze_work_patterns(self) -> Dict:
        """
        分析工作模式
        
        深入分析历史工作数据，识别模式和趋势
        """
        if len(self.daily_memories) < 14:
            return {
                'status': 'insufficient_data',
                'message': '需要至少两周的数据才能进行模式分析',
                'patterns': {}
            }
        
        # 1. 主题演变分析
        topic_evolution = self._analyze_topic_evolution()
        
        # 2. 工作效率分析
        productivity_analysis = self._analyze_productivity()
        
        # 3. 工作习惯分析
        habit_analysis = self._analyze_habits()
        
        # 4. 预测未来趋势
        future_trends = self._predict_trends(topic_evolution)
        
        return {
            'status': 'success',
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'data_range': {
                'start': self.daily_memories[0]['date'].strftime('%Y-%m-%d'),
                'end': self.daily_memories[-1]['date'].strftime('%Y-%m-%d'),
                'total_days': len(self.daily_memories)
            },
            'topic_evolution': topic_evolution,
            'productivity_analysis': productivity_analysis,
            'habit_analysis': habit_analysis,
            'future_trends': future_trends,
            'insights': self._generate_insights(topic_evolution, productivity_analysis, habit_analysis)
        }
    
    def _analyze_topic_evolution(self) -> Dict:
        """分析主题演变趋势"""
        # 按周分组统计主题
        weekly_topics = defaultdict(lambda: defaultdict(int))
        
        for mem in self.daily_memories:
            week = mem['date'].strftime('%Y-W%W')
            topics = self._extract_topics(mem['content'])
            for topic, count in topics.items():
                weekly_topics[week][topic] += count
        
        # 计算各主题的兴衰趋势
        topic_trends = {}
        all_topics = set()
        for week_data in weekly_topics.values():
            all_topics.update(week_data.keys())
        
        weeks = sorted(weekly_topics.keys())
        for topic in all_topics:
            counts = [weekly_topics[week].get(topic, 0) for week in weeks]
            if len(counts) >= 2:
                # 简单线性趋势
                trend = 'stable'
                if counts[-1] > counts[0] * 1.5:
                    trend = 'rising'
                elif counts[-1] < counts[0] * 0.5:
                    trend = 'declining'
                
                topic_trends[topic] = {
                    'trend': trend,
                    'first_week': counts[0],
                    'last_week': counts[-1],
                    'peak': max(counts),
                    'total_weeks': len([c for c in counts if c > 0])
                }
        
        return {
            'weekly_distribution': dict(weekly_topics),
            'topic_trends': topic_trends,
            'dominant_topics': sorted(
                [(t, sum(weekly_topics[w].get(t, 0) for w in weeks)) for t in all_topics],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def _analyze_productivity(self) -> Dict:
        """分析工作效率模式"""
        # 计算每日产出指标
        daily_output = []
        for mem in self.daily_memories:
            topics = self._extract_topics(mem['content'])
            tasks = self._extract_tasks(mem['content'])
            
            # 综合产出分数
            output_score = (
                len(mem['content']) / 500 +  # 内容长度
                len(topics) * 3 +            # 主题数
                len(tasks) * 2               # 任务数
            )
            
            daily_output.append({
                'date': mem['date'],
                'output_score': output_score,
                'content_length': len(mem['content']),
                'topics': len(topics),
                'tasks': len(tasks)
            })
        
        # 计算统计指标
        scores = [d['output_score'] for d in daily_output]
        avg_score = statistics.mean(scores)
        
        # 识别高效日
        high_productivity_days = [d for d in daily_output if d['output_score'] > avg_score * 1.3]
        low_productivity_days = [d for d in daily_output if d['output_score'] < avg_score * 0.5]
        
        # 计算趋势
        if len(scores) >= 7:
            recent_avg = statistics.mean(scores[-7:])
            previous_avg = statistics.mean(scores[-14:-7]) if len(scores) >= 14 else avg_score
            
            if recent_avg > previous_avg * 1.1:
                trend = 'improving'
            elif recent_avg < previous_avg * 0.9:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'average_daily_score': round(avg_score, 2),
            'trend': trend,
            'high_productivity_days': len(high_productivity_days),
            'low_productivity_days': len(low_productivity_days),
            'best_day': max(daily_output, key=lambda x: x['output_score'])['date'].strftime('%Y-%m-%d') if daily_output else None,
            'recent_average': round(statistics.mean(scores[-7:]), 2) if len(scores) >= 7 else None
        }
    
    def _analyze_habits(self) -> Dict:
        """分析工作习惯"""
        # 按星期几分析
        weekday_stats = defaultdict(lambda: {'count': 0, 'total_output': 0})
        
        for mem in self.daily_memories:
            wd = mem['date'].weekday()
            topics = self._extract_topics(mem['content'])
            output = len(mem['content']) / 500 + len(topics) * 3
            
            weekday_stats[wd]['count'] += 1
            weekday_stats[wd]['total_output'] += output
        
        # 计算最活跃的工作日
        avg_by_weekday = {}
        for wd, data in weekday_stats.items():
            if data['count'] > 0:
                avg_by_weekday[wd] = data['total_output'] / data['count']
        
        most_active_day = max(avg_by_weekday.items(), key=lambda x: x[1])[0] if avg_by_weekday else None
        least_active_day = min(avg_by_weekday.items(), key=lambda x: x[1])[0] if avg_by_weekday else None
        
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        return {
            'most_active_day': weekday_names[most_active_day] if most_active_day is not None else None,
            'least_active_day': weekday_names[least_active_day] if least_active_day is not None else None,
            'weekday_distribution': {weekday_names[wd]: data['count'] for wd, data in weekday_stats.items()},
            'weekend_work_ratio': (weekday_stats.get(5, {'count': 0})['count'] + weekday_stats.get(6, {'count': 0})['count']) / len(self.daily_memories) if self.daily_memories else 0
        }
    
    def _predict_trends(self, topic_evolution: Dict) -> List[Dict]:
        """预测未来趋势"""
        predictions = []
        
        for topic, trend_data in topic_evolution.get('topic_trends', {}).items():
            if trend_data['trend'] == 'rising':
                predictions.append({
                    'topic': topic,
                    'prediction': '持续升温',
                    'confidence': 'medium',
                    'suggestion': f'{topic}投入持续增加，建议保持当前节奏'
                })
            elif trend_data['trend'] == 'declining':
                if trend_data['last_week'] == 0:
                    predictions.append({
                        'topic': topic,
                        'prediction': '可能搁置',
                        'confidence': 'medium',
                        'suggestion': f'{topic}近期未涉及，如需继续建议重新启动'
                    })
        
        return predictions
    
    def _generate_insights(self, topic_evolution: Dict, productivity: Dict, habits: Dict) -> List[str]:
        """生成洞察建议"""
        insights = []
        
        # 基于主题演变的洞察
        rising_topics = [t for t, d in topic_evolution.get('topic_trends', {}).items() if d['trend'] == 'rising']
        if rising_topics:
            insights.append(f'近期重点关注: {", ".join(rising_topics)}')
        
        # 基于效率的洞察
        if productivity.get('trend') == 'improving':
            insights.append('工作效率呈上升趋势，保持良好状态！')
        elif productivity.get('trend') == 'declining':
            insights.append('近期产出有所下降，建议调整工作节奏')
        
        # 基于习惯的洞察
        weekend_ratio = habits.get('weekend_work_ratio', 0)
        if weekend_ratio > 0.3:
            insights.append('周末工作频率较高，注意劳逸结合')
        
        if habits.get('most_active_day'):
            insights.append(f'{habits["most_active_day"]}是你最活跃的工作日')
        
        return insights
    
    def generate_daily_briefing(self) -> str:
        """生成每日简报"""
        today = datetime.now()
        
        # 获取各项分析
        focus = self.predict_next_week_focus()
        rhythm = self.suggest_work_rhythm()
        reminders = self.remind_overdue_items()
        patterns = self.analyze_work_patterns()
        
        # 生成简报文本
        briefing = f"""# 📅 每日工作简报

生成时间: {today.strftime('%Y-%m-%d %H:%M')}

---

## 🎯 今日建议重点

"""
        
        if focus['status'] == 'success' and focus['focus_areas']:
            for area in focus['focus_areas'][:3]:
                briefing += f"- **{area['topic']}** ({area['confidence']})\n"
                briefing += f"  - {area['suggestion']}\n"
        else:
            briefing += "暂无足够数据预测今日重点\n"
        
        briefing += "\n## ⏰ 待办提醒\n\n"
        
        if reminders['overdue_items']:
            briefing += f"**⚠️ 逾期任务 ({reminders['summary']['overdue_count']}项):**\n"
            for item in reminders['overdue_items'][:5]:
                briefing += f"- [ ] {item['task'][:50]}... ({item['days_ago']}天前)\n"
            briefing += "\n"
        
        if reminders['upcoming_items']:
            briefing += f"**📋 待跟进 ({reminders['summary']['upcoming_count']}项):**\n"
            for item in reminders['upcoming_items'][:3]:
                briefing += f"- [ ] {item['task'][:50]}...\n"
        
        if not reminders['overdue_items'] and not reminders['upcoming_items']:
            briefing += "✅ 暂无紧急待办任务\n"
        
        briefing += "\n## 📊 工作节奏建议\n\n"
        
        if rhythm['status'] == 'success':
            for suggestion in rhythm['suggestions'][:3]:
                icon = '⚠️' if suggestion['type'] == 'warning' else '💡'
                briefing += f"{icon} {suggestion['message']}\n"
                briefing += f"   → {suggestion['action']}\n\n"
        
        briefing += "\n---\n*由预测性工作建议模块生成*\n"
        
        return briefing


# CLI 入口
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="预测性工作建议模块")
    parser.add_argument("command", 
                       choices=["focus", "rhythm", "remind", "patterns", "briefing", "all"],
                       help="执行的命令")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text",
                       help="输出格式")
    
    args = parser.parse_args()
    
    advisor = PredictiveAdvisor()
    
    if args.command == "focus" or args.command == "all":
        result = advisor.predict_next_week_focus()
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("\n🎯 下周工作重点预测")
            print("=" * 50)
            if result['status'] == 'success':
                for area in result['focus_areas']:
                    print(f"\n{area['topic']} [{area['confidence']}]")
                    print(f"  趋势: {area['trend']}")
                    print(f"  建议: {area['suggestion']}")
            else:
                print(result['message'])
    
    if args.command == "rhythm" or args.command == "all":
        result = advisor.suggest_work_rhythm()
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("\n\n⏱️ 工作节奏建议")
            print("=" * 50)
            if result['status'] == 'success':
                for suggestion in result['suggestions']:
                    icon = "⚠️" if suggestion['type'] == 'warning' else "💡"
                    print(f"\n{icon} {suggestion['message']}")
                    print(f"   行动: {suggestion['action']}")
            else:
                print(result['message'])
    
    if args.command == "remind" or args.command == "all":
        result = advisor.remind_overdue_items()
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("\n\n⏰ 待办事项提醒")
            print("=" * 50)
            if result['overdue_items']:
                print(f"\n⚠️ 逾期任务 ({len(result['overdue_items'])}项):")
                for item in result['overdue_items']:
                    print(f"  - {item['task'][:60]} ({item['days_ago']}天前)")
            if result['upcoming_items']:
                print(f"\n📋 待跟进 ({len(result['upcoming_items'])}项):")
                for item in result['upcoming_items']:
                    print(f"  - {item['task'][:60]}")
            if not result['overdue_items'] and not result['upcoming_items']:
                print("\n✅ 暂无紧急待办")
    
    if args.command == "patterns" or args.command == "all":
        result = advisor.analyze_work_patterns()
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("\n\n📈 工作模式分析")
            print("=" * 50)
            if result['status'] == 'success':
                print(f"\n数据范围: {result['data_range']['start']} ~ {result['data_range']['end']}")
                print(f"总天数: {result['data_range']['total_days']}")
                print(f"\n效率趋势: {result['productivity_analysis']['trend']}")
                print(f"平均日产出: {result['productivity_analysis']['average_daily_score']}")
                
                print("\n主要工作主题:")
                for topic, count in result['topic_evolution']['dominant_topics'][:5]:
                    print(f"  - {topic}: {count}次")
                
                print("\n洞察:")
                for insight in result['insights']:
                    print(f"  💡 {insight}")
            else:
                print(result['message'])
    
    if args.command == "briefing":
        print(advisor.generate_daily_briefing())


if __name__ == "__main__":
    main()
