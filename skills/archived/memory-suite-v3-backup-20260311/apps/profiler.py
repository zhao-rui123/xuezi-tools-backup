#!/usr/bin/env python3
"""
Memory Suite v3.0 - 用户画像模块 (Profiler)

功能：
1. 分析用户偏好和习惯
2. 构建用户兴趣模型
3. 生成用户画像报告
4. 预测用户需求

作者: Memory Suite Team
版本: 3.0.0
日期: 2026-03-11
"""

import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set

# 导入核心层工具
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import (
    setup_logger, expand_path, load_json, save_json,
    format_datetime, get_date_string, ConfigManager,
    MemorySuiteError, safe_execute, truncate_text
)


# ============================================================================
# 数据类定义
# ============================================================================

@dataclass
class UserProfile:
    """用户画像数据类"""
    
    # 基本信息
    name: str = "用户"
    timezone: str = "Asia/Shanghai"
    language: str = "zh"
    
    # 模型偏好
    preferred_model: str = "kimi-k2.5"
    model_usage_count: Dict[str, int] = field(default_factory=dict)
    
    # 交互统计
    total_interactions: int = 0
    total_tokens: int = 0
    avg_session_duration_minutes: float = 0.0
    last_interaction: Optional[str] = None
    
    # 话题偏好 (话题 -> 权重 0-1)
    topic_preferences: Dict[str, float] = field(default_factory=dict)
    
    # 时间模式
    active_hours: List[int] = field(default_factory=list)  # 活跃时段 (0-23)
    active_days: List[int] = field(default_factory=list)   # 活跃星期 (0-6, 0=周一)
    preferred_response_time: str = "immediate"  # immediate/thoughtful
    
    # 风格偏好
    response_style: str = "concise"  # concise/detailed/casual/formal
    use_emoji: bool = True
    use_markdown: bool = True
    preferred_language: str = "zh"
    
    # 项目关注
    interested_projects: List[str] = field(default_factory=list)
    project_activity: Dict[str, int] = field(default_factory=dict)  # 项目 -> 提及次数
    
    # 股票关注
    stock_watchlist: List[str] = field(default_factory=list)
    stock_mentions: Dict[str, int] = field(default_factory=dict)
    
    # 技能使用
    skill_usage: Dict[str, int] = field(default_factory=dict)  # 技能 -> 使用次数
    skill_level: Dict[str, str] = field(default_factory=dict)  # 技能 -> 水平
    
    # 学习模式
    learning_style: str = "practical"  # practical/theoretical/balanced
    
    # 分析元数据
    last_analyzed: Optional[str] = None
    analysis_version: str = "3.0.0"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        """从字典创建"""
        return cls(**data)


# ============================================================================
# 用户画像系统主类
# ============================================================================

class Profiler:
    """
    用户画像系统
    
    分析用户行为、偏好、习惯，构建个性化用户画像。
    """
    
    # 预定义话题分类
    TOPIC_CATEGORIES = {
        '储能': ['储能', '电价', '充放电', '光伏', '新能源', '电池', '容量', '功率'],
        '股票': ['股票', '股市', '行情', '分析', 'K 线', '涨停', '跌停', '板块', '龙头'],
        '开发': ['开发', '代码', '程序', 'API', '部署', '网站', '前端', '后端', '数据库'],
        'AI/模型': ['模型', 'OpenClaw', 'AI', 'Agent', 'k2p5', 'k2.5', 'kimi', '智能'],
        '运维': ['备份', '配置', '服务器', '定时任务', '日志', '监控', '维护'],
        '数据分析': ['数据', '分析', '统计', '图表', '报告', '可视化', 'Excel'],
        '项目管理': ['项目', '计划', '进度', '任务', '需求', '文档', '测试'],
        '技能包': ['技能', 'skill', '工具', '功能', '模块', '插件'],
    }
    
    # 股票代码映射
    STOCK_CODES = {
        '中矿资源': '002738',
        '赣锋锂业': '002460/01772',
        '盐湖股份': '000792',
        '盛新锂能': '002240',
        '京东方 A': '000725',
        '彩虹股份': '600707',
        '中芯国际': '00981',
        '宁德时代': '300750',
        '比亚迪': '002594',
        '天赐材料': '002709',
    }
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化用户画像系统
        
        Args:
            config: 配置字典，None 则自动加载
        """
        self.logger = setup_logger("memory_suite.profiler")
        self.logger.info("初始化用户画像系统...")
        
        # 加载配置
        if config is None:
            config_manager = ConfigManager()
            config = config_manager.load_config() or {}
        self.config = config
        
        # 路径设置
        self.workspace = expand_path(config.get('workspace', '~/.openclaw/workspace'))
        self.memory_dir = expand_path(config.get('memory_dir', '~/.openclaw/workspace/memory'))
        
        # 文件路径
        self.profile_file = self.memory_dir / 'user_profile.json'
        self.interaction_log = self.memory_dir / 'interaction_log.json'
        
        # 内部状态
        self._profile: Optional[UserProfile] = None
        self._interactions: List[Dict] = []
        
        self.logger.info("用户画像系统初始化完成")
    
    # ========================================================================
    # 数据加载与保存
    # ========================================================================
    
    def _load_profile(self) -> UserProfile:
        """加载用户画像"""
        if self._profile is not None:
            return self._profile
        
        if self.profile_file.exists():
            try:
                data = load_json(self.profile_file)
                if data:
                    self._profile = UserProfile.from_dict(data)
                    self.logger.debug(f"用户画像加载成功：{self.profile_file}")
                    return self._profile
            except Exception as e:
                self.logger.warning(f"加载用户画像失败：{e}")
        
        # 创建默认画像
        self._profile = UserProfile()
        self.logger.info("创建默认用户画像")
        return self._profile
    
    def _save_profile(self) -> bool:
        """保存用户画像"""
        if self._profile is None:
            self.logger.warning("没有可保存的用户画像")
            return False
        
        try:
            self.profile_file.parent.mkdir(parents=True, exist_ok=True)
            data = self._profile.to_dict()
            if save_json(data, self.profile_file):
                self.logger.info(f"用户画像已保存：{self.profile_file}")
                return True
            else:
                self.logger.error("保存用户画像失败")
                return False
        except Exception as e:
            self.logger.error(f"保存用户画像异常：{e}")
            return False
    
    def _load_interactions(self) -> List[Dict]:
        """加载交互记录"""
        if self._interactions:
            return self._interactions
        
        if self.interaction_log.exists():
            try:
                self._interactions = load_json(self.interaction_log) or []
                self.logger.debug(f"交互记录加载成功：{len(self._interactions)} 条")
            except Exception as e:
                self.logger.warning(f"加载交互记录失败：{e}")
                self._interactions = []
        else:
            self._interactions = []
        
        return self._interactions
    
    def _save_interactions(self) -> bool:
        """保存交互记录（只保留最近 1000 条）"""
        try:
            recent = self._interactions[-1000:]
            if save_json(recent, self.interaction_log):
                self.logger.debug(f"交互记录已保存：{len(recent)} 条")
                return True
            return False
        except Exception as e:
            self.logger.error(f"保存交互记录异常：{e}")
            return False
    
    # ========================================================================
    # 核心分析方法
    # ========================================================================
    
    def analyze_all(self) -> UserProfile:
        """
        执行完整分析
        
        Returns:
            更新后的用户画像
        """
        self.logger.info("=" * 60)
        self.logger.info("开始完整用户画像分析")
        self.logger.info("=" * 60)
        
        # 加载数据
        profile = self._load_profile()
        interactions = self._load_interactions()
        
        # 执行各项分析
        self._analyze_topics()
        self._analyze_active_hours()
        self._analyze_projects()
        self._analyze_stock_interest()
        self._analyze_model_preference()
        self._analyze_response_style()
        
        # 更新元数据
        profile = self._profile
        profile.last_analyzed = format_datetime()
        profile.analysis_version = "3.0.0"
        
        # 保存
        self._save_profile()
        
        self.logger.info("用户画像分析完成")
        return profile
    
    def _analyze_topics(self):
        """分析话题偏好"""
        self.logger.info("  分析话题偏好...")
        
        topic_counts = defaultdict(int)
        total_mentions = 0
        
        # 扫描记忆文件
        memory_files = list(self.memory_dir.glob("2026-*.md"))
        memory_files.extend(self.memory_dir.glob("2025-*.md"))
        
        for file_path in memory_files[:60]:  # 限制文件数量
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 统计每个话题的提及次数
                for topic, keywords in self.TOPIC_CATEGORIES.items():
                    for keyword in keywords:
                        if keyword.lower() in content.lower():
                            topic_counts[topic] += 1
                            total_mentions += 1
                            break  # 每个话题在每个文件中只计一次
            except Exception as e:
                self.logger.warning(f"读取文件失败 {file_path}: {e}")
        
        # 计算权重（归一化）
        if total_mentions > 0:
            topic_weights = {
                topic: round(count / total_mentions, 3)
                for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
                if count > 0
            }
            self._profile.topic_preferences = topic_weights
            self.logger.debug(f"  识别 {len(topic_weights)} 个话题偏好")
        else:
            self.logger.warning("  未找到足够的话题数据")
    
    def _analyze_active_hours(self):
        """分析活跃时段"""
        self.logger.info("  分析活跃时段...")
        
        hours = []
        days = []
        
        # 从记忆文件修改时间分析
        memory_files = list(self.memory_dir.glob("2026-*.md"))
        memory_files.extend(self.memory_dir.glob("2025-*.md"))
        
        for file_path in memory_files[:90]:  # 限制文件数量
            try:
                stat = file_path.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)
                hours.append(mtime.hour)
                days.append(mtime.weekday())  # 0=周一
            except Exception:
                continue
        
        if hours:
            # 统计最活跃的时段（Top 5）
            hour_counts = Counter(hours)
            self._profile.active_hours = [h for h, _ in hour_counts.most_common(5)]
            
            # 统计最活跃的天（Top 3）
            day_counts = Counter(days)
            self._profile.active_days = [d for d, _ in day_counts.most_common(3)]
            
            self.logger.debug(f"  活跃时段：{self._profile.active_hours}")
        else:
            self.logger.warning("  无法分析活跃时段")
    
    def _analyze_projects(self):
        """分析项目关注"""
        self.logger.info("  分析项目关注...")
        
        projects = []
        project_counts = defaultdict(int)
        
        # 扫描记忆文件
        memory_files = list(self.memory_dir.glob("2026-*.md"))
        
        for file_path in memory_files[:30]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 从 [PROJECT] 标记提取
                project_section = re.search(
                    r'\[PROJECT\]\s*(.+?)(?=\n\[|\Z)',
                    content, re.DOTALL | re.IGNORECASE
                )
                if project_section:
                    project_name = project_section.group(1).strip()[:50]
                    if len(project_name) > 3:
                        projects.append(project_name)
                        project_counts[project_name] += 1
                
                # 从标题提取
                headers = re.findall(r'^##\s+(.+?)(?:开发 | 完成 | 项目 | 系统)?$', 
                                   content, re.MULTILINE | re.IGNORECASE)
                for header in headers:
                    header = header.strip()
                    if 3 < len(header) < 60:
                        projects.append(header)
                        project_counts[header] += 1
                        
            except Exception as e:
                self.logger.warning(f"分析项目失败 {file_path}: {e}")
        
        # 去重并保存
        unique_projects = list(set(projects))
        self._profile.interested_projects = unique_projects[:15]
        self._profile.project_activity = dict(project_counts)
        
        self.logger.debug(f"  识别 {len(unique_projects)} 个项目")
    
    def _analyze_stock_interest(self):
        """分析股票关注"""
        self.logger.info("  分析股票关注...")
        
        stock_counts = defaultdict(int)
        
        # 扫描记忆文件
        memory_files = list(self.memory_dir.glob("2026-*.md"))
        
        for file_path in memory_files[:30]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找股票代码和名称
                for stock_name, stock_code in self.STOCK_CODES.items():
                    if stock_name in content or stock_code in content:
                        stock_counts[stock_name] += 1
                        
            except Exception as e:
                self.logger.warning(f"分析股票失败 {file_path}: {e}")
        
        # 更新关注列表
        if stock_counts:
            sorted_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)
            self._profile.stock_watchlist = [name for name, _ in sorted_stocks[:10]]
            self._profile.stock_mentions = dict(sorted_stocks)
            self.logger.debug(f"  识别 {len(sorted_stocks)} 只关注股票")
        else:
            # 使用默认列表
            self._profile.stock_watchlist = list(self.STOCK_CODES.keys())[:7]
    
    def _analyze_model_preference(self):
        """分析模型偏好"""
        self.logger.info("  分析模型偏好...")
        
        interactions = self._load_interactions()
        
        if interactions:
            model_counts = defaultdict(int)
            total_tokens = 0
            
            for interaction in interactions:
                model = interaction.get('model', 'unknown')
                model_counts[model] += 1
                total_tokens += interaction.get('tokens', 0)
            
            self._profile.model_usage_count = dict(model_counts)
            self._profile.total_tokens = total_tokens
            
            # 确定偏好模型
            if model_counts:
                preferred = max(model_counts.items(), key=lambda x: x[1])[0]
                self._profile.preferred_model = preferred
            
            self.logger.debug(f"  模型使用：{dict(model_counts)}")
        else:
            self.logger.warning("  无交互记录")
    
    def _analyze_response_style(self):
        """分析回复风格偏好"""
        self.logger.info("  分析回复风格...")
        
        # 从配置或默认值推断
        # 这里可以扩展为分析用户反馈
        
        # 检查 USER.md
        user_file = self.workspace / 'USER.md'
        if user_file.exists():
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 简单推断
                if '简洁' in content or 'concise' in content.lower():
                    self._profile.response_style = 'concise'
                elif '详细' in content or 'detailed' in content.lower():
                    self._profile.response_style = 'detailed'
                    
            except Exception:
                pass
        
        self.logger.debug(f"  回复风格：{self._profile.response_style}")
    
    # ========================================================================
    # 交互记录
    # ========================================================================
    
    def log_interaction(self, query: str, model: str, tokens: int = 0,
                       duration_minutes: float = 0.0) -> bool:
        """
        记录一次交互
        
        Args:
            query: 用户查询
            model: 使用的模型
            tokens: 消耗的 token 数
            duration_minutes: 会话时长（分钟）
            
        Returns:
            是否记录成功
        """
        try:
            interaction = {
                'timestamp': format_datetime(),
                'query': truncate_text(query, 200),
                'model': model,
                'tokens': tokens,
                'duration_minutes': duration_minutes
            }
            
            self._interactions.append(interaction)
            
            # 更新统计
            self._profile.total_interactions += 1
            self._profile.total_tokens += tokens
            self._profile.last_interaction = interaction['timestamp']
            
            # 更新模型计数
            self._profile.model_usage_count[model] = \
                self._profile.model_usage_count.get(model, 0) + 1
            
            # 更新偏好模型
            if self._profile.model_usage_count:
                self._profile.preferred_model = max(
                    self._profile.model_usage_count.items(),
                    key=lambda x: x[1]
                )[0]
            
            # 保存
            self._save_interactions()
            self._save_profile()
            
            self.logger.debug(f"交互记录成功：{model}, {tokens} tokens")
            return True
            
        except Exception as e:
            self.logger.error(f"记录交互失败：{e}")
            return False
    
    # ========================================================================
    # 预测与建议
    # ========================================================================
    
    def predict_need(self, context: str = "") -> Dict[str, Any]:
        """
        预测用户需求
        
        Args:
            context: 当前上下文
            
        Returns:
            预测结果字典
        """
        profile = self._load_profile()
        
        predictions = {
            'likely_topics': [],
            'suggested_model': profile.preferred_model,
            'response_style': profile.response_style,
            'confidence': 0.0,
            'active_now': False
        }
        
        # 基于话题偏好预测
        if profile.topic_preferences:
            top_topics = sorted(
                profile.topic_preferences.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            predictions['likely_topics'] = [t for t, _ in top_topics]
            predictions['confidence'] = sum([s for _, s in top_topics]) / 3
        
        # 基于上下文微调
        if context:
            context_lower = context.lower()
            
            # 股票相关 -> 需要识图/分析能力
            if any(kw in context_lower for kw in ['股票', '行情', 'k 线', '分析']):
                predictions['suggested_model'] = 'kimi-k2.5'
                if '股票' not in predictions['likely_topics']:
                    predictions['likely_topics'].insert(0, '股票')
            
            # 代码/开发相关 -> 需要推理能力
            if any(kw in context_lower for kw in ['代码', '开发', 'bug', '部署', 'api']):
                predictions['suggested_model'] = 'kimi-k2.5'
                if '开发' not in predictions['likely_topics']:
                    predictions['likely_topics'].insert(0, '开发')
        
        # 检查是否活跃时段
        current_hour = datetime.now().hour
        if current_hour in profile.active_hours:
            predictions['active_now'] = True
        
        return predictions
    
    def get_personalized_settings(self) -> Dict[str, Any]:
        """
        获取个性化设置
        
        Returns:
            个性化设置字典
        """
        profile = self._load_profile()
        
        return {
            'preferred_model': profile.preferred_model,
            'response_style': profile.response_style,
            'use_emoji': profile.use_emoji,
            'use_markdown': profile.use_markdown,
            'active_hours': profile.active_hours,
            'timezone': profile.timezone,
            'language': profile.language
        }
    
    # ========================================================================
    # 报告生成
    # ========================================================================
    
    def generate_report(self) -> Dict[str, Any]:
        """
        生成用户画像报告
        
        Returns:
            报告字典
        """
        profile = self._load_profile()
        
        report = {
            'timestamp': format_datetime(),
            'profile': profile.to_dict(),
            'insights': self._generate_insights(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_insights(self) -> Dict[str, Any]:
        """生成洞察分析"""
        profile = self._profile
        
        insights = {
            'most_active_hours': profile.active_hours,
            'most_active_days': profile.active_days,
            'top_interests': list(profile.topic_preferences.keys())[:3] if profile.topic_preferences else [],
            'favorite_model': profile.preferred_model,
            'total_interactions': profile.total_interactions,
            'total_tokens': profile.total_tokens,
            'projects_count': len(profile.interested_projects),
            'stocks_watched': len(profile.stock_watchlist)
        }
        
        # 添加深度分析
        if profile.topic_preferences:
            primary_interest = max(profile.topic_preferences.items(), key=lambda x: x[1])
            insights['primary_focus'] = {
                'topic': primary_interest[0],
                'weight': primary_interest[1]
            }
        
        return insights
    
    def _generate_recommendations(self) -> List[str]:
        """生成个性化建议"""
        profile = self._profile
        recommendations = []
        
        # 基于话题偏好
        if profile.topic_preferences:
            top_topic = max(profile.topic_preferences.items(), key=lambda x: x[1])[0]
            recommendations.append(
                f"用户对'{top_topic}'话题最感兴趣，可主动推送相关内容"
            )
        
        # 基于活跃时段
        if profile.active_hours:
            hour_str = ', '.join([f"{h}点" for h in profile.active_hours[:3]])
            recommendations.append(f"用户活跃时段：{hour_str}")
        
        # 基于模型偏好
        if profile.preferred_model:
            recommendations.append(f"用户偏好模型：{profile.preferred_model}")
        
        # 基于股票关注
        if profile.stock_watchlist:
            stocks_str = ', '.join(profile.stock_watchlist[:3])
            recommendations.append(f"关注股票：{stocks_str}...")
        
        # 基于项目
        if profile.interested_projects:
            recommendations.append(
                f"当前关注 {len(profile.interested_projects)} 个项目"
            )
        
        return recommendations
    
    def save_report(self, report: Optional[Dict] = None,
                   filename: Optional[str] = None) -> Path:
        """
        保存画像报告
        
        Args:
            report: 报告字典，None 则自动生成
            filename: 文件名，None 则使用默认名称
            
        Returns:
            保存的文件路径
        """
        if report is None:
            report = self.generate_report()
        
        if filename is None:
            filename = f"user_profile_report_{get_date_string()}.json"
        
        report_path = self.memory_dir / 'reports' / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        if save_json(report, report_path):
            self.logger.info(f"画像报告已保存：{report_path}")
        else:
            self.logger.error(f"保存画像报告失败：{report_path}")
        
        return report_path
    
    # ========================================================================
    # CLI 接口
    # ========================================================================
    
    def run(self, save: bool = True) -> Dict[str, Any]:
        """
        运行用户画像分析（完整流程）
        
        Args:
            save: 是否保存报告
            
        Returns:
            画像报告
        """
        self.logger.info("=" * 60)
        self.logger.info("开始运行用户画像分析")
        self.logger.info("=" * 60)
        
        # 执行分析
        profile = self.analyze_all()
        
        # 生成报告
        report = self.generate_report()
        
        # 打印摘要
        self._print_summary(report)
        
        # 保存报告
        if save:
            self.save_report(report)
        
        self.logger.info("用户画像分析完成")
        return report
    
    def _print_summary(self, report: Dict):
        """打印画像摘要"""
        profile = self._profile
        
        print("\n" + "=" * 60)
        print("👤 用户画像报告")
        print("=" * 60)
        print(f"  用户名：{profile.name}")
        print(f"  时区：{profile.timezone}")
        print(f"  总交互数：{profile.total_interactions}")
        print(f"  总 Token 数：{profile.total_tokens:,}")
        print(f"  偏好模型：{profile.preferred_model}")
        print(f"  回复风格：{profile.response_style}")
        
        # 话题偏好
        if profile.topic_preferences:
            print(f"\n  🔥 话题偏好:")
            for topic, weight in sorted(profile.topic_preferences.items(), 
                                       key=lambda x: x[1], reverse=True)[:5]:
                bar = "█" * int(weight * 20)
                print(f"    {topic}: {bar} {weight:.1%}")
        
        # 活跃时段
        if profile.active_hours:
            hour_str = ', '.join([f"{h}点" for h in profile.active_hours])
            print(f"\n  ⏰ 活跃时段：{hour_str}")
        
        # 关注项目
        if profile.interested_projects:
            print(f"\n  📈 关注项目:")
            for project in profile.interested_projects[:5]:
                print(f"    - {truncate_text(project, 40)}")
        
        # 关注股票
        if profile.stock_watchlist:
            print(f"\n  💹 关注股票:")
            for stock in profile.stock_watchlist[:5]:
                count = profile.stock_mentions.get(stock, 0)
                print(f"    - {stock} ({count}次提及)")
        
        # 个性化建议
        if report.get('recommendations'):
            print(f"\n  💡 个性化建议:")
            for rec in report['recommendations'][:5]:
                print(f"    • {rec}")
        
        print("\n" + "=" * 60)


# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """主函数 - CLI 入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Memory Suite 用户画像系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python profiler.py                    # 执行完整分析
  python profiler.py --log "查询内容"    # 记录交互
  python profiler.py --predict "上下文"  # 预测需求
  python profiler.py --save false       # 不保存报告
        """
    )
    
    parser.add_argument('--log', '-l', type=str,
                       help='记录一次交互（查询内容）')
    parser.add_argument('--model', '-m', type=str, default='kimi-k2.5',
                       help='使用的模型名称')
    parser.add_argument('--tokens', '-t', type=int, default=0,
                       help='消耗的 token 数')
    parser.add_argument('--predict', '-p', type=str,
                       help='预测需求（提供上下文）')
    parser.add_argument('--save', '-s', type=lambda x: x.lower() == 'true',
                       default=True,
                       help='是否保存报告 (true/false)')
    parser.add_argument('--config', type=str,
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config:
        config = load_json(args.config)
    
    # 初始化画像系统
    profiler = Profiler(config)
    
    # 根据参数执行操作
    if args.log:
        # 记录交互
        profiler.log_interaction(args.log, args.model, args.tokens)
        print(f"✅ 交互记录成功：{args.model}, {args.tokens} tokens")
    elif args.predict:
        # 预测需求
        prediction = profiler.predict_need(args.predict)
        print("\n🔮 需求预测:")
        print(f"  可能话题：{', '.join(prediction['likely_topics'])}")
        print(f"  建议模型：{prediction['suggested_model']}")
        print(f"  置信度：{prediction['confidence']:.1%}")
        print(f"  当前活跃：{'是' if prediction['active_now'] else '否'}")
    else:
        # 执行完整分析
        report = profiler.run(save=args.save)


if __name__ == "__main__":
    main()
