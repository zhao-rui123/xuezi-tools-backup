#!/usr/bin/env python3
"""
用户画像系统 (User Profile System)
第二阶段 - 智能进化

功能：
1. 分析用户提问模式
2. 记录用户偏好（模型、回复风格等）
3. 预测用户需求
4. 个性化推荐

作者: 雪子助手
版本: 1.0.0
日期: 2026-03-09
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
PROFILE_FILE = MEMORY_DIR / "user_profile.json"
INTERACTION_LOG = MEMORY_DIR / "interaction_log.json"


@dataclass
class UserProfile:
    """用户画像"""
    # 基本信息
    name: str = "雪子"
    timezone: str = "Asia/Shanghai"
    
    # 模型偏好
    preferred_model: str = "k2p5"  # 默认偏好
    model_usage_count: Dict[str, int] = None
    
    # 交互统计
    total_interactions: int = 0
    total_tokens: int = 0
    avg_session_duration: float = 0.0
    
    # 话题偏好
    topic_preferences: Dict[str, float] = None  # 话题 -> 权重
    
    # 时间模式
    active_hours: List[int] = None  # 活跃时段
    preferred_response_time: str = "immediate"  # immediate/thoughtful
    
    # 风格偏好
    response_style: str = "concise"  # concise/detailed/casual
    use_emoji: bool = True
    preferred_language: str = "zh"
    
    # 项目关注
    interested_projects: List[str] = None
    stock_watchlist: List[str] = None
    
    # 学习模式
    learning_style: str = "practical"  # practical/theoretical
    skill_level: Dict[str, str] = None  # 技能 -> 水平
    
    def __post_init__(self):
        if self.model_usage_count is None:
            self.model_usage_count = {}
        if self.topic_preferences is None:
            self.topic_preferences = {}
        if self.active_hours is None:
            self.active_hours = []
        if self.interested_projects is None:
            self.interested_projects = []
        if self.stock_watchlist is None:
            self.stock_watchlist = []
        if self.skill_level is None:
            self.skill_level = {}


class UserProfileSystem:
    """用户画像系统"""
    
    def __init__(self):
        self.profile = self._load_profile()
        self.interactions = self._load_interactions()
        self.memory_dir = MEMORY_DIR
    
    def _load_profile(self) -> UserProfile:
        """加载用户画像"""
        if PROFILE_FILE.exists():
            try:
                with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserProfile(**data)
            except Exception as e:
                print(f"  ⚠️ 加载画像失败: {str(e)}")
        
        return UserProfile()
    
    def _load_interactions(self) -> List[Dict]:
        """加载交互记录"""
        if INTERACTION_LOG.exists():
            try:
                with open(INTERACTION_LOG, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_profile(self):
        """保存用户画像"""
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.profile), f, ensure_ascii=False, indent=2)
    
    def _save_interactions(self):
        """保存交互记录"""
        # 只保留最近1000条
        recent = self.interactions[-1000:]
        with open(INTERACTION_LOG, 'w', encoding='utf-8') as f:
            json.dump(recent, f, ensure_ascii=False, indent=2)
    
    def analyze_from_memory(self):
        """从历史记忆分析用户画像"""
        print("🔍 分析历史记忆...")
        
        # 1. 分析话题偏好
        self._analyze_topics()
        
        # 2. 分析活跃时段
        self._analyze_active_hours()
        
        # 3. 分析项目关注
        self._analyze_projects()
        
        # 4. 分析股票关注
        self._analyze_stock_interest()
        
        # 保存
        self._save_profile()
        print("  ✅ 画像分析完成")
    
    def _analyze_topics(self):
        """分析话题偏好"""
        topic_keywords = {
            "储能": ["储能", "电价", "充放电", "光伏", "新能源"],
            "股票": ["股票", "股市", "行情", "分析", "K线", "涨停"],
            "开发": ["开发", "代码", "程序", "API", "部署", "网站"],
            "AI/模型": ["模型", "OpenClaw", "AI", "Agent", "k2p5", "k2.5"],
            "运维": ["备份", "配置", "服务器", "定时任务", "日志"],
            "数据分析": ["数据", "分析", "统计", "图表", "报告"],
        }
        
        topic_counts = defaultdict(int)
        
        # 扫描记忆文件
        for file_path in self.memory_dir.glob("2026-*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for topic, keywords in topic_keywords.items():
                    for keyword in keywords:
                        if keyword in content:
                            topic_counts[topic] += 1
                            break
            except:
                continue
        
        # 计算权重 (归一化)
        total = sum(topic_counts.values())
        if total > 0:
            self.profile.topic_preferences = {
                topic: round(count / total, 3)
                for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            }
    
    def _analyze_active_hours(self):
        """分析活跃时段"""
        hours = []
        
        for file_path in self.memory_dir.glob("2026-*.md"):
            # 从文件名提取日期
            match = re.search(r'(\d{4})-(\d{2})-(\d{2})', file_path.name)
            if match:
                # 从文件修改时间获取时段信息
                stat = file_path.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)
                hours.append(mtime.hour)
        
        if hours:
            # 统计最活跃的时段
            hour_counts = Counter(hours)
            # 取前3个最活跃的时段
            self.profile.active_hours = [h for h, _ in hour_counts.most_common(3)]
    
    def _analyze_projects(self):
        """分析项目关注"""
        projects = []
        
        # 扫描记忆文件
        for file_path in self.memory_dir.glob("2026-*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取项目名称
                project_matches = re.findall(r'##\s+(.*?)(?:开发|完成|项目)', content)
                projects.extend(project_matches)
                
                # 从 [PROJECT] 标签提取
                project_section = re.search(r'\[PROJECT\](.*?)(?=\n\[|\Z)', content, re.DOTALL)
                if project_section:
                    projects.append(project_section.group(1).strip()[:50])
                    
            except:
                continue
        
        # 去重并保存前10个
        unique_projects = list(set([p.strip() for p in projects if len(p.strip()) > 3]))
        self.profile.interested_projects = unique_projects[:10]
    
    def _analyze_stock_interest(self):
        """分析股票关注"""
        # 从 USER.md 或记忆中提取
        stocks = [
            "中矿资源", "赣锋锂业", "盐湖股份", "盛新锂能",
            "京东方A", "彩虹股份", "中芯国际"
        ]
        self.profile.stock_watchlist = stocks
    
    def log_interaction(self, query: str, model: str, tokens: int = 0):
        """记录交互"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:200],  # 限制长度
            "model": model,
            "tokens": tokens
        }
        
        self.interactions.append(interaction)
        self.profile.total_interactions += 1
        self.profile.total_tokens += tokens
        
        # 更新模型使用计数
        self.profile.model_usage_count[model] = self.profile.model_usage_count.get(model, 0) + 1
        
        # 更新偏好模型 (使用最多的)
        if self.profile.model_usage_count:
            self.profile.preferred_model = max(
                self.profile.model_usage_count.items(),
                key=lambda x: x[1]
            )[0]
        
        # 保存
        self._save_interactions()
        self._save_profile()
    
    def predict_need(self, context: str = "") -> Dict:
        """预测用户需求"""
        predictions = {
            "likely_topics": [],
            "suggested_model": self.profile.preferred_model,
            "response_style": self.profile.response_style,
            "confidence": 0.0
        }
        
        # 基于话题偏好预测
        if self.profile.topic_preferences:
            top_topics = sorted(
                self.profile.topic_preferences.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            predictions["likely_topics"] = [t for t, _ in top_topics]
            predictions["confidence"] = sum([s for _, s in top_topics]) / 3
        
        # 基于上下文微调
        if context:
            if any(kw in context for kw in ["股票", "股市", "行情"]):
                predictions["suggested_model"] = "k2.5"  # 需要识图
                predictions["likely_topics"].insert(0, "股票")
            elif any(kw in context for kw in ["代码", "开发", "部署", "bug"]):
                predictions["suggested_model"] = "k2p5"  # 需要推理
                predictions["likely_topics"].insert(0, "开发")
        
        return predictions
    
    def get_personalized_settings(self) -> Dict:
        """获取个性化设置"""
        return {
            "preferred_model": self.profile.preferred_model,
            "response_style": self.profile.response_style,
            "use_emoji": self.profile.use_emoji,
            "active_hours": self.profile.active_hours,
            "timezone": self.profile.timezone
        }
    
    def generate_report(self) -> Dict:
        """生成画像报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "profile": asdict(self.profile),
            "insights": {
                "most_active_hours": self.profile.active_hours,
                "top_interests": list(self.profile.topic_preferences.keys())[:3] if self.profile.topic_preferences else [],
                "favorite_model": self.profile.preferred_model,
                "total_interactions": self.profile.total_interactions
            },
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成个性化建议"""
        recommendations = []
        
        # 基于话题偏好
        if self.profile.topic_preferences:
            top_topic = max(self.profile.topic_preferences.items(), key=lambda x: x[1])[0]
            recommendations.append(f"用户对'{top_topic}'话题最感兴趣，可主动推送相关内容")
        
        # 基于活跃时段
        if self.profile.active_hours:
            recommendations.append(f"用户活跃时段: {self.profile.active_hours}点")
        
        # 基于模型偏好
        if self.profile.preferred_model:
            recommendations.append(f"用户偏好模型: {self.profile.preferred_model}")
        
        # 基于股票关注
        if self.profile.stock_watchlist:
            recommendations.append(f"关注股票: {', '.join(self.profile.stock_watchlist[:3])}...")
        
        return recommendations
    
    def run(self):
        """运行画像分析"""
        print("=" * 60)
        print("👤 用户画像系统")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 分析历史记忆
        self.analyze_from_memory()
        
        # 生成报告
        report = self.generate_report()
        
        # 打印报告
        print("\n" + "=" * 60)
        print("📊 用户画像报告")
        print("=" * 60)
        print(f"  用户名: {self.profile.name}")
        print(f"  总交互数: {self.profile.total_interactions}")
        print(f"  偏好模型: {self.profile.preferred_model}")
        print(f"  回复风格: {self.profile.response_style}")
        
        print(f"\n  🔥 话题偏好:")
        if self.profile.topic_preferences:
            for topic, weight in sorted(self.profile.topic_preferences.items(), key=lambda x: x[1], reverse=True)[:5]:
                bar = "█" * int(weight * 20)
                print(f"    {topic}: {bar} {weight:.1%}")
        
        print(f"\n  ⏰ 活跃时段: {self.profile.active_hours}")
        
        print(f"\n  📈 关注项目:")
        for project in self.profile.interested_projects[:5]:
            print(f"    - {project}")
        
        print(f"\n  💡 个性化建议:")
        for rec in report["recommendations"]:
            print(f"    • {rec}")
        
        print("\n✅ 用户画像更新完成")
        
        return report


def main():
    """主函数"""
    system = UserProfileSystem()
    report = system.run()
    
    # 保存报告
    report_file = MEMORY_DIR / "user_profile_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 报告已保存: {report_file}")


if __name__ == "__main__":
    main()
