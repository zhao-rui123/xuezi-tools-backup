#!/usr/bin/env python3
"""
长期规划联动模块 - 实现中长期目标的自我进化
与 unified-memory 深度联动，实现目标分解、进度跟踪、自动调整
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict

# 添加 unified-memory 路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'unified-memory'))

try:
    from unified_memory import EnhancedRecall, MemoryAnalyzer, DailyMemory
    UMS_AVAILABLE = True
except ImportError:
    UMS_AVAILABLE = False
    print("⚠️ unified-memory 不可用，使用本地存储")

# 配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
GOALS_FILE = WORKSPACE / "memory" / "long_term_goals.json"
MILESTONES_FILE = WORKSPACE / "memory" / "milestones.json"
PLAN_HISTORY_FILE = WORKSPACE / "memory" / "plan_history.json"
REPORTS_DIR = WORKSPACE / "memory" / "reports"

# 确保目录存在
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class LongTermGoal:
    """长期目标"""
    id: str
    title: str
    description: str
    category: str
    start_date: str
    target_date: str
    status: str = "active"  # active, completed, paused, abandoned
    progress: float = 0.0  # 0-100
    priority: int = 3  # 1-5, 5最高
    keywords: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    milestones: List[Dict] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)


@dataclass
class ShortTermTask:
    """短期任务"""
    id: str
    goal_id: str
    title: str
    description: str
    due_date: str
    status: str = "pending"  # pending, in_progress, completed, blocked
    priority: int = 3
    estimated_hours: float = 0
    actual_hours: float = 0
    completed_at: Optional[str] = None
    related_memories: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Milestone:
    """里程碑"""
    id: str
    goal_id: str
    title: str
    description: str
    target_date: str
    completed: bool = False
    completed_at: Optional[str] = None
    completion_notes: str = ""


class LongTermPlanner:
    """长期规划管理器"""
    
    def __init__(self):
        self.goals: Dict[str, LongTermGoal] = {}
        self.tasks: Dict[str, ShortTermTask] = {}
        self.milestones: Dict[str, Milestone] = {}
        self.plan_history: List[Dict] = []
        self.recall = self._get_recall()
        self._load_data()
    
    def _get_recall(self) -> Optional[EnhancedRecall]:
        """获取增强记忆实例"""
        if UMS_AVAILABLE:
            return EnhancedRecall()
        return None
    
    def _load_data(self):
        """加载所有数据"""
        # 加载目标
        if GOALS_FILE.exists():
            with open(GOALS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for g in data.get('goals', []):
                    self.goals[g['id']] = LongTermGoal(**g)
                for t in data.get('tasks', []):
                    self.tasks[t['id']] = ShortTermTask(**t)
        
        # 加载里程碑
        if MILESTONES_FILE.exists():
            with open(MILESTONES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for m in data.get('milestones', []):
                    self.milestones[m['id']] = Milestone(**m)
        
        # 加载计划历史
        if PLAN_HISTORY_FILE.exists():
            with open(PLAN_HISTORY_FILE, 'r', encoding='utf-8') as f:
                self.plan_history = json.load(f).get('history', [])
    
    def _save_data(self):
        """保存所有数据"""
        # 保存目标
        goals_data = {
            'goals': [asdict(g) for g in self.goals.values()],
            'tasks': [asdict(t) for t in self.tasks.values()],
            'updated_at': datetime.now().isoformat()
        }
        with open(GOALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(goals_data, f, ensure_ascii=False, indent=2)
        
        # 保存里程碑
        milestones_data = {
            'milestones': [asdict(m) for m in self.milestones.values()],
            'updated_at': datetime.now().isoformat()
        }
        with open(MILESTONES_FILE, 'w', encoding='utf-8') as f:
            json.dump(milestones_data, f, ensure_ascii=False, indent=2)
        
        # 保存计划历史
        with open(PLAN_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({'history': self.plan_history}, f, ensure_ascii=False, indent=2)
    
    def set_long_term_goal(self, goal: str, timeline: str, 
                          description: str = "", category: str = "general",
                          priority: int = 3) -> str:
        """
        设置长期目标
        
        Args:
            goal: 目标标题
            timeline: 时间线 (如 "6个月", "2025-12-31", "Q4 2025")
            description: 目标描述
            category: 目标类别
            priority: 优先级 1-5
            
        Returns:
            goal_id: 目标ID
        """
        goal_id = f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(2).hex()}"
        
        # 解析时间线
        target_date = self._parse_timeline(timeline)
        
        # 提取关键词
        keywords = self._extract_keywords(goal + " " + description)
        
        # 创建目标
        new_goal = LongTermGoal(
            id=goal_id,
            title=goal,
            description=description,
            category=category,
            start_date=datetime.now().strftime('%Y-%m-%d'),
            target_date=target_date,
            priority=priority,
            keywords=keywords
        )
        
        self.goals[goal_id] = new_goal
        self._save_data()
        
        # 同步到 unified-memory
        if self.recall:
            memory_text = f"[长期目标] {goal}\n描述: {description}\n时间线: {timeline}\n类别: {category}"
            self.recall.store(memory_text, category="long_term_goal", importance=0.85)
        
        print(f"✅ 长期目标已设置: {goal}")
        print(f"   ID: {goal_id}")
        print(f"   目标日期: {target_date}")
        print(f"   关键词: {', '.join(keywords[:5])}")
        
        return goal_id
    
    def _parse_timeline(self, timeline: str) -> str:
        """解析时间线为具体日期"""
        today = datetime.now()
        
        # 尝试解析具体日期
        try:
            if re.match(r'\d{4}-\d{2}-\d{2}', timeline):
                return timeline
        except:
            pass
        
        # 解析相对时间
        if '月' in timeline:
            months = int(re.search(r'(\d+)', timeline).group(1))
            target = today + timedelta(days=30*months)
            return target.strftime('%Y-%m-%d')
        
        if '周' in timeline:
            weeks = int(re.search(r'(\d+)', timeline).group(1))
            target = today + timedelta(weeks=weeks)
            return target.strftime('%Y-%m-%d')
        
        if '季度' in timeline or 'Q' in timeline.upper():
            quarter_match = re.search(r'Q(\d)', timeline.upper())
            year_match = re.search(r'(\d{4})', timeline)
            if quarter_match and year_match:
                quarter = int(quarter_match.group(1))
                year = int(year_match.group(1))
                month = quarter * 3
                return f"{year}-{month:02d}-01"
        
        # 默认6个月
        target = today + timedelta(days=180)
        return target.strftime('%Y-%m-%d')
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 中文关键词
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        # 英文关键词
        english = re.findall(r'[a-zA-Z_]{3,}', text)
        
        keywords = list(set(chinese + english))
        return keywords[:10]  # 最多10个
    
    def decompose_to_tasks(self, goal_id: str, task_specs: List[Dict] = None) -> List[str]:
        """
        将长期目标分解为短期任务
        
        Args:
            goal_id: 目标ID
            task_specs: 任务规格列表，如果不提供则自动分解
            
        Returns:
            List[str]: 任务ID列表
        """
        if goal_id not in self.goals:
            print(f"❌ 目标不存在: {goal_id}")
            return []
        
        goal = self.goals[goal_id]
        
        if task_specs is None:
            # 自动分解
            task_specs = self._auto_decompose(goal)
        
        task_ids = []
        for i, spec in enumerate(task_specs):
            task_id = f"task_{goal_id}_{i+1}"
            
            task = ShortTermTask(
                id=task_id,
                goal_id=goal_id,
                title=spec.get('title', f'任务 {i+1}'),
                description=spec.get('description', ''),
                due_date=spec.get('due_date', goal.target_date),
                priority=spec.get('priority', goal.priority),
                estimated_hours=spec.get('estimated_hours', 0)
            )
            
            self.tasks[task_id] = task
            task_ids.append(task_id)
        
        # 更新目标的里程碑
        goal.milestones = [
            {"task_id": tid, "title": self.tasks[tid].title}
            for tid in task_ids
        ]
        goal.updated_at = datetime.now().isoformat()
        
        self._save_data()
        
        print(f"✅ 目标已分解为 {len(task_ids)} 个任务")
        for tid in task_ids:
            print(f"   • {self.tasks[tid].title}")
        
        return task_ids
    
    def _auto_decompose(self, goal: LongTermGoal) -> List[Dict]:
        """根据目标自动分解任务"""
        tasks = []
        
        # 解析目标日期
        try:
            target = datetime.strptime(goal.target_date, '%Y-%m-%d')
            start = datetime.strptime(goal.start_date, '%Y-%m-%d')
            total_days = (target - start).days
        except:
            total_days = 180
        
        # 根据类别生成不同的分解策略
        category_patterns = {
            "知识图谱": [
                {"title": "需求分析与架构设计", "estimated_hours": 16},
                {"title": "核心模块开发", "estimated_hours": 40},
                {"title": "数据模型设计", "estimated_hours": 24},
                {"title": "功能测试与优化", "estimated_hours": 16}
            ],
            "多模态记忆": [
                {"title": "技术调研与方案选型", "estimated_hours": 12},
                {"title": "图像处理模块开发", "estimated_hours": 32},
                {"title": "音频处理模块开发", "estimated_hours": 32},
                {"title": "跨模态关联实现", "estimated_hours": 24}
            ],
            "个性化模型": [
                {"title": "偏好收集机制设计", "estimated_hours": 16},
                {"title": "行为分析模块开发", "estimated_hours": 32},
                {"title": "推荐算法实现", "estimated_hours": 24},
                {"title": "模型训练与调优", "estimated_hours": 24}
            ],
            "技能包": [
                {"title": "功能设计与API定义", "estimated_hours": 8},
                {"title": "核心功能实现", "estimated_hours": 24},
                {"title": "错误处理与边界情况", "estimated_hours": 12},
                {"title": "文档编写与测试", "estimated_hours": 8}
            ],
            "股票分析": [
                {"title": "数据获取模块开发", "estimated_hours": 16},
                {"title": "技术指标计算", "estimated_hours": 24},
                {"title": "可视化图表生成", "estimated_hours": 16},
                {"title": "策略回测框架", "estimated_hours": 32}
            ]
        }
        
        # 查找匹配的模式
        matched_pattern = None
        for cat, pattern in category_patterns.items():
            if cat in goal.title or cat in goal.description or cat in goal.category:
                matched_pattern = pattern
                break
        
        if matched_pattern is None:
            # 通用分解
            matched_pattern = [
                {"title": f"阶段一：需求分析与规划", "estimated_hours": 16},
                {"title": f"阶段二：核心功能开发", "estimated_hours": 48},
                {"title": f"阶段三：测试与优化", "estimated_hours": 24},
                {"title": f"阶段四：文档与交付", "estimated_hours": 12}
            ]
        
        # 分配日期
        task_count = len(matched_pattern)
        days_per_task = max(total_days // task_count, 7)
        
        for i, pattern in enumerate(matched_pattern):
            due = (start + timedelta(days=days_per_task * (i + 1))).strftime('%Y-%m-%d')
            tasks.append({
                "title": pattern["title"],
                "description": f"为达成'{goal.title}'的子任务",
                "due_date": due,
                "estimated_hours": pattern["estimated_hours"],
                "priority": goal.priority
            })
        
        return tasks
    
    def track_progress(self, goal_id: str = None) -> Dict:
        """
        跟踪目标进度
        
        Args:
            goal_id: 目标ID，如果不提供则跟踪所有活跃目标
            
        Returns:
            进度统计信息
        """
        results = {}
        
        goals_to_track = [self.goals[goal_id]] if goal_id else \
                        [g for g in self.goals.values() if g.status == "active"]
        
        for goal in goals_to_track:
            # 获取该目标的所有任务
            goal_tasks = [t for t in self.tasks.values() if t.goal_id == goal.id]
            
            if not goal_tasks:
                continue
            
            total_tasks = len(goal_tasks)
            completed = len([t for t in goal_tasks if t.status == "completed"])
            in_progress = len([t for t in goal_tasks if t.status == "in_progress"])
            blocked = len([t for t in goal_tasks if t.status == "blocked"])
            
            # 计算进度百分比
            progress = (completed / total_tasks * 100) if total_tasks > 0 else 0
            
            # 考虑进行中的任务
            progress += (in_progress / total_tasks * 100 * 0.5) if total_tasks > 0 else 0
            
            # 更新目标进度
            goal.progress = min(progress, 100)
            goal.updated_at = datetime.now().isoformat()
            
            # 检查是否完成
            if progress >= 100:
                goal.status = "completed"
                goal.progress = 100
            
            # 从 unified-memory 获取相关记忆
            related_memories = self._find_related_memories(goal)
            goal.related_memories = [m['memory']['id'] for m in related_memories]
            
            results[goal.id] = {
                "title": goal.title,
                "progress": goal.progress,
                "total_tasks": total_tasks,
                "completed": completed,
                "in_progress": in_progress,
                "blocked": blocked,
                "target_date": goal.target_date,
                "days_remaining": (datetime.strptime(goal.target_date, '%Y-%m-%d') - datetime.now()).days,
                "related_memories_count": len(related_memories)
            }
        
        self._save_data()
        
        # 输出结果
        print("📊 目标进度跟踪")
        print("=" * 60)
        for gid, stats in results.items():
            bar_length = 20
            filled = int(stats["progress"] / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"\n{stats['title']}")
            print(f"   进度: [{bar}] {stats['progress']:.1f}%")
            print(f"   任务: {stats['completed']}/{stats['total_tasks']} 完成, {stats['in_progress']} 进行中")
            print(f"   剩余: {stats['days_remaining']} 天")
        
        return results
    
    def _find_related_memories(self, goal: LongTermGoal, top_k: int = 5) -> List[Dict]:
        """从 unified-memory 查找相关记忆"""
        if not self.recall:
            return []
        
        related = []
        
        # 用关键词搜索
        for keyword in goal.keywords[:3]:
            results = self.recall.search(keyword, top_k=top_k)
            related.extend(results)
        
        # 用目标标题搜索
        results = self.recall.search(goal.title, top_k=top_k)
        related.extend(results)
        
        # 去重并排序
        seen = set()
        unique = []
        for r in related:
            mid = r['memory']['id']
            if mid not in seen:
                seen.add(mid)
                unique.append(r)
        
        unique.sort(key=lambda x: x['score'], reverse=True)
        return unique[:top_k]
    
    def check_milestones(self) -> List[Dict]:
        """
        检查里程碑完成情况
        
        Returns:
            里程碑状态列表
        """
        today = datetime.now()
        updates = []
        
        print("🎯 里程碑检查")
        print("=" * 60)
        
        for milestone in self.milestones.values():
            target = datetime.strptime(milestone.target_date, '%Y-%m-%d')
            days_until = (target - today).days
            
            status_info = {
                "milestone_id": milestone.id,
                "title": milestone.title,
                "target_date": milestone.target_date,
                "days_until": days_until,
                "completed": milestone.completed
            }
            
            if milestone.completed:
                print(f"   ✅ {milestone.title} - 已完成")
            elif days_until < 0:
                print(f"   ⚠️ {milestone.title} - 逾期 {abs(days_until)} 天")
                status_info["alert"] = "overdue"
            elif days_until <= 7:
                print(f"   📅 {milestone.title} - 即将到期 ({days_until} 天)")
                status_info["alert"] = "upcoming"
            else:
                print(f"   ⏳ {milestone.title} - 剩余 {days_until} 天")
            
            updates.append(status_info)
        
        # 同时检查任务作为里程碑
        for task in self.tasks.values():
            if task.status == "completed":
                continue
                
            target = datetime.strptime(task.due_date, '%Y-%m-%d')
            days_until = (target - today).days
            
            if days_until < 0:
                print(f"   ⚠️ 任务逾期: {task.title} ({abs(days_until)} 天)")
            elif days_until <= 3:
                print(f"   📌 近期任务: {task.title} ({days_until} 天)")
        
        return updates
    
    def adjust_plan_based_on_data(self) -> List[Dict]:
        """
        基于实际数据调整计划
        
        Returns:
            调整建议列表
        """
        adjustments = []
        
        print("🔄 计划自动调整分析")
        print("=" * 60)
        
        # 1. 分析完成速度
        completed_tasks = [t for t in self.tasks.values() if t.status == "completed" and t.completed_at]
        
        if completed_tasks:
            # 计算平均完成时间
            total_hours = sum(t.actual_hours for t in completed_tasks if t.actual_hours > 0)
            count = len([t for t in completed_tasks if t.actual_hours > 0])
            avg_completion_time = total_hours / count if count > 0 else 0
            
            print(f"\n📈 完成统计:")
            print(f"   已完成任务: {len(completed_tasks)}")
            print(f"   平均耗时: {avg_completion_time:.1f} 小时/任务")
        
        # 2. 识别延期风险
        for goal in self.goals.values():
            if goal.status != "active":
                continue
            
            goal_tasks = [t for t in self.tasks.values() if t.goal_id == goal.id]
            pending = [t for t in goal_tasks if t.status == "pending"]
            
            if not pending:
                continue
            
            # 计算剩余时间
            try:
                target = datetime.strptime(goal.target_date, '%Y-%m-%d')
                days_remaining = (target - datetime.now()).days
            except:
                continue
            
            # 估算所需时间
            estimated_hours_needed = sum(t.estimated_hours for t in pending)
            estimated_days_needed = estimated_hours_needed / 4  # 假设每天4小时有效工作时间
            
            if estimated_days_needed > days_remaining:
                risk_ratio = estimated_days_needed / days_remaining if days_remaining > 0 else float('inf')
                
                suggestion = {
                    "goal_id": goal.id,
                    "goal_title": goal.title,
                    "risk": "high" if risk_ratio > 1.5 else "medium",
                    "days_remaining": days_remaining,
                    "estimated_days_needed": estimated_days_needed,
                    "suggestions": []
                }
                
                if risk_ratio > 1.5:
                    suggestion["suggestions"].append("目标进度严重滞后，建议延长截止日期或削减范围")
                else:
                    suggestion["suggestions"].append("目标进度有延期风险，建议加快执行")
                
                # 建议优先级调整
                high_priority_pending = [t for t in pending if t.priority >= 4]
                if len(high_priority_pending) < len(pending) / 2:
                    suggestion["suggestions"].append("建议重新评估任务优先级，集中资源在高优先级任务上")
                
                adjustments.append(suggestion)
                
                print(f"\n⚠️ {goal.title}")
                print(f"   风险等级: {suggestion['risk']}")
                print(f"   建议: {'; '.join(suggestion['suggestions'])}")
        
        # 3. 基于 unified-memory 的工作记录调整
        work_patterns = self._analyze_work_patterns()
        if work_patterns:
            print(f"\n📊 工作模式分析:")
            print(f"   高频主题: {', '.join(work_patterns.get('top_topics', [])[:3])}")
            print(f"   活跃时段: {work_patterns.get('active_hours', '未知')}")
        
        # 4. 保存调整历史
        if adjustments:
            self.plan_history.append({
                "timestamp": datetime.now().isoformat(),
                "adjustments": adjustments,
                "trigger": "periodic_review"
            })
            self._save_data()
        
        return adjustments
    
    def _analyze_work_patterns(self) -> Dict:
        """分析工作模式"""
        patterns = {
            "top_topics": [],
            "active_hours": "",
            "productivity_trend": ""
        }
        
        # 从 daily memory 文件分析
        recent_files = sorted(MEMORY_DIR.glob("*.md"))[-14:]  # 最近两周
        
        all_text = ""
        for f in recent_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    all_text += fp.read() + "\n"
            except:
                continue
        
        if all_text and UMS_AVAILABLE:
            analyzer = MemoryAnalyzer()
            keywords = analyzer.extract_keywords(all_text, top_n=10)
            patterns["top_topics"] = [k for k, _ in keywords]
            
            topics = analyzer.extract_topics(keywords)
            patterns["topic_distribution"] = topics
        
        return patterns
    
    def generate_progress_report(self, period: str = "weekly") -> str:
        """
        生成进度报告
        
        Args:
            period: 报告周期 (daily, weekly, monthly)
            
        Returns:
            报告文件路径
        """
        now = datetime.now()
        
        # 确定报告时间范围
        if period == "daily":
            since = now - timedelta(days=1)
            title = f"{now.strftime('%Y-%m-%d')} 每日进度报告"
        elif period == "weekly":
            since = now - timedelta(days=7)
            title = f"第{now.isocalendar()[1]}周 进度报告"
        elif period == "monthly":
            since = now - timedelta(days=30)
            title = f"{now.strftime('%Y年%m月')} 月度进度报告"
        else:
            since = now - timedelta(days=7)
            title = "进度报告"
        
        # 统计信息
        active_goals = [g for g in self.goals.values() if g.status == "active"]
        completed_goals = [g for g in self.goals.values() if g.status == "completed"]
        
        # 任务统计
        all_tasks = list(self.tasks.values())
        completed_tasks = [t for t in all_tasks if t.status == "completed"]
        in_progress_tasks = [t for t in all_tasks if t.status == "in_progress"]
        
        # 近期完成的任务
        recently_completed = []
        for t in completed_tasks:
            if t.completed_at:
                try:
                    completed_date = datetime.fromisoformat(t.completed_at)
                    if completed_date >= since:
                        recently_completed.append(t)
                except:
                    pass
        
        # 生成报告内容
        report = f"""# {title}

> 生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}

## 📊 总体概览

| 指标 | 数值 |
|------|------|
| 活跃目标 | {len(active_goals)} 个 |
| 已完成目标 | {len(completed_goals)} 个 |
| 总任务数 | {len(all_tasks)} 个 |
| 已完成任务 | {len(completed_tasks)} 个 |
| 进行中任务 | {len(in_progress_tasks)} 个 |
| 本周期完成 | {len(recently_completed)} 个 |

## 🎯 目标进度详情

"""
        
        for goal in active_goals:
            progress_bar = self._make_progress_bar(goal.progress, 20)
            report += f"""### {goal.title}

- **进度**: [{progress_bar}] {goal.progress:.1f}%
- **目标日期**: {goal.target_date}
- **类别**: {goal.category}
- **优先级**: {'⭐' * goal.priority}

"""
            
            # 添加相关任务
            goal_tasks = [t for t in all_tasks if t.goal_id == goal.id]
            if goal_tasks:
                report += "**任务列表**:\n"
                for t in goal_tasks:
                    status_icon = {
                        "completed": "✅",
                        "in_progress": "🔄",
                        "pending": "⏳",
                        "blocked": "🚫"
                    }.get(t.status, "⏳")
                    report += f"- {status_icon} {t.title}\n"
                report += "\n"
        
        # 本周期完成的工作
        if recently_completed:
            report += """## ✅ 本周期完成

"""
            for t in recently_completed:
                goal = self.goals.get(t.goal_id)
                goal_title = goal.title if goal else "未知目标"
                report += f"- **{t.title}** (属于: {goal_title})\n"
                if t.description:
                    report += f"  - {t.description}\n"
            report += "\n"
        
        # 风险提醒
        report += """## ⚠️ 风险与建议

"""
        
        risks_found = False
        for goal in active_goals:
            try:
                target = datetime.strptime(goal.target_date, '%Y-%m-%d')
                days_remaining = (target - now).days
                
                if days_remaining < 7 and goal.progress < 80:
                    report += f"- **{goal.title}**: 即将到期但进度仅 {goal.progress:.1f}%，建议加速推进\n"
                    risks_found = True
                elif days_remaining < 0:
                    report += f"- **{goal.title}**: 已逾期 {abs(days_remaining)} 天，建议重新评估计划\n"
                    risks_found = True
            except:
                pass
        
        if not risks_found:
            report += "- 暂无重大风险\n"
        
        report += """
## 📈 下一步计划

"""
        
        # 添加即将到期的任务
        upcoming = []
        for t in all_tasks:
            if t.status in ["pending", "in_progress"]:
                try:
                    due = datetime.strptime(t.due_date, '%Y-%m-%d')
                    days_until = (due - now).days
                    if 0 <= days_until <= 7:
                        upcoming.append((t, days_until))
                except:
                    pass
        
        upcoming.sort(key=lambda x: x[1])
        
        if upcoming:
            report += "**即将到期的任务**:\n"
            for t, days in upcoming[:5]:
                report += f"- {t.title} (还剩 {days} 天)\n"
        else:
            report += "- 无紧急任务\n"
        
        report += f"""

---
*由长期规划系统自动生成*
"""
        
        # 保存报告
        report_filename = f"{period}_report_{now.strftime('%Y%m%d_%H%M%S')}.md"
        report_path = REPORTS_DIR / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 报告已生成: {report_path}")
        
        return str(report_path)
    
    def _make_progress_bar(self, progress: float, length: int = 20) -> str:
        """生成进度条"""
        filled = int(progress / 100 * length)
        return "█" * filled + "░" * (length - filled)
    
    def update_task_status(self, task_id: str, status: str, actual_hours: float = None, notes: str = ""):
        """更新任务状态"""
        if task_id not in self.tasks:
            print(f"❌ 任务不存在: {task_id}")
            return False
        
        task = self.tasks[task_id]
        task.status = status
        
        if actual_hours is not None:
            task.actual_hours = actual_hours
        
        if status == "completed":
            task.completed_at = datetime.now().isoformat()
            
            # 同步到 unified-memory
            if self.recall:
                goal = self.goals.get(task.goal_id)
                goal_title = goal.title if goal else "未知目标"
                memory_text = f"[任务完成] {task.title}\n属于目标: {goal_title}\n耗时: {task.actual_hours} 小时"
                self.recall.store(memory_text, category="task_completed", importance=0.7)
        
        self._save_data()
        
        # 更新父目标进度
        self.track_progress(task.goal_id)
        
        print(f"✅ 任务状态已更新: {task.title} → {status}")
        return True
    
    def link_memory_to_goal(self, goal_id: str, memory_id: str):
        """将记忆关联到目标"""
        if goal_id in self.goals:
            if memory_id not in self.goals[goal_id].related_memories:
                self.goals[goal_id].related_memories.append(memory_id)
                self._save_data()
                print(f"✅ 记忆已关联到目标: {self.goals[goal_id].title}")
                return True
        return False
    
    def list_goals(self, status: str = None) -> List[Dict]:
        """列出所有目标"""
        goals = self.goals.values()
        if status:
            goals = [g for g in goals if g.status == status]
        
        return [{
            "id": g.id,
            "title": g.title,
            "progress": g.progress,
            "status": g.status,
            "target_date": g.target_date,
            "priority": g.priority
        } for g in sorted(goals, key=lambda x: x.priority, reverse=True)]
    
    def get_goal_details(self, goal_id: str) -> Optional[Dict]:
        """获取目标详情"""
        if goal_id not in self.goals:
            return None
        
        goal = self.goals[goal_id]
        tasks = [t for t in self.tasks.values() if t.goal_id == goal_id]
        
        return {
            "goal": asdict(goal),
            "tasks": [asdict(t) for t in tasks],
            "milestones": [asdict(m) for m in self.milestones.values() if m.goal_id == goal_id]
        }
    
    def auto_discover_from_memory(self, days: int = 7) -> List[Dict]:
        """
        自动从记忆中发现潜在目标
        
        Args:
            days: 检查最近几天的记忆
            
        Returns:
            潜在目标建议列表
        """
        suggestions = []
        
        if not UMS_AVAILABLE:
            print("⚠️ unified-memory 不可用，无法自动发现")
            return suggestions
        
        # 获取最近记忆
        recent_files = sorted(MEMORY_DIR.glob("*.md"))[-days:]
        
        all_text = ""
        for f in recent_files:
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    all_text += fp.read() + "\n"
            except:
                continue
        
        if not all_text:
            return suggestions
        
        # 分析关键词
        analyzer = MemoryAnalyzer()
        keywords = analyzer.extract_keywords(all_text, top_n=20)
        
        # 识别潜在目标模式
        goal_patterns = [
            ("知识图谱.*开发", "知识图谱", "知识图谱系统开发与优化"),
            ("多模态.*记忆", "多模态记忆", "多模态记忆系统实现"),
            ("个性化.*模型", "个性化模型", "用户偏好学习与个性化模型"),
            ("技能包.*开发", "技能包", "新技能包开发"),
            ("股票.*分析", "股票分析", "股票分析工具改进"),
            ("储能.*测算", "储能测算", "储能项目测算系统优化"),
        ]
        
        for pattern, category, suggestion_title in goal_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                # 检查是否已有类似目标
                existing = any(category in g.category or pattern.replace(".*", "") in g.title 
                              for g in self.goals.values() if g.status == "active")
                
                if not existing:
                    suggestions.append({
                        "title": suggestion_title,
                        "category": category,
                        "confidence": "medium",
                        "source": "memory_analysis"
                    })
        
        if suggestions:
            print("\n💡 从记忆中发现的潜在目标:")
            for s in suggestions:
                print(f"   • {s['title']} ({s['category']})")
        
        return suggestions


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="长期规划联动模块")
    parser.add_argument("command", choices=[
        "set-goal", "decompose", "track", "check-milestones",
        "adjust", "report", "update-task", "list", "details",
        "discover", "link-memory"
    ])
    parser.add_argument("--goal", "-g", help="目标ID")
    parser.add_argument("--title", "-t", help="目标/任务标题")
    parser.add_argument("--desc", "-d", help="描述")
    parser.add_argument("--timeline", "-l", help="时间线 (如: 3个月, 2025-12-31)")
    parser.add_argument("--category", "-c", default="general", help="类别")
    parser.add_argument("--priority", "-p", type=int, default=3, help="优先级 1-5")
    parser.add_argument("--task-id", help="任务ID")
    parser.add_argument("--status", "-s", help="任务状态")
    parser.add_argument("--hours", type=float, help="实际工时")
    parser.add_argument("--period", default="weekly", help="报告周期")
    parser.add_argument("--memory-id", help="记忆ID")
    
    args = parser.parse_args()
    
    planner = LongTermPlanner()
    
    if args.command == "set-goal":
        if not args.title or not args.timeline:
            print("❌ 请提供 --title 和 --timeline")
            return
        planner.set_long_term_goal(
            goal=args.title,
            timeline=args.timeline,
            description=args.desc or "",
            category=args.category,
            priority=args.priority
        )
    
    elif args.command == "decompose":
        if not args.goal:
            print("❌ 请提供 --goal")
            return
        planner.decompose_to_tasks(args.goal)
    
    elif args.command == "track":
        planner.track_progress(args.goal)
    
    elif args.command == "check-milestones":
        planner.check_milestones()
    
    elif args.command == "adjust":
        planner.adjust_plan_based_on_data()
    
    elif args.command == "report":
        planner.generate_progress_report(args.period)
    
    elif args.command == "update-task":
        if not args.task_id or not args.status:
            print("❌ 请提供 --task-id 和 --status")
            return
        planner.update_task_status(args.task_id, args.status, args.hours)
    
    elif args.command == "list":
        goals = planner.list_goals(args.status)
        print("\n📋 目标列表")
        print("=" * 60)
        for g in goals:
            bar = planner._make_progress_bar(g['progress'], 15)
            print(f"\n{g['title']}")
            print(f"   ID: {g['id']}")
            print(f"   进度: [{bar}] {g['progress']:.1f}%")
            print(f"   状态: {g['status']} | 优先级: {'⭐' * g['priority']}")
            print(f"   目标日期: {g['target_date']}")
    
    elif args.command == "details":
        if not args.goal:
            print("❌ 请提供 --goal")
            return
        details = planner.get_goal_details(args.goal)
        if details:
            import json
            print(json.dumps(details, ensure_ascii=False, indent=2))
        else:
            print("❌ 目标不存在")
    
    elif args.command == "discover":
        planner.auto_discover_from_memory()
    
    elif args.command == "link-memory":
        if not args.goal or not args.memory_id:
            print("❌ 请提供 --goal 和 --memory-id")
            return
        planner.link_memory_to_goal(args.goal, args.memory_id)
    
    else:
        print("请指定命令")


if __name__ == "__main__":
    main()
