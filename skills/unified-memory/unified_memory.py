#!/usr/bin/env python3
"""
统一记忆系统 (Unified Memory System)
整合所有记忆相关技能包，提供一致的使用接口
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

# 配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SUMMARY_DIR = MEMORY_DIR / "summary"
PERMANENT_DIR = MEMORY_DIR / "permanent"
INDEX_DIR = MEMORY_DIR / "index"
KB_DIR = WORKSPACE / "knowledge-base"

# 确保目录存在
for d in [MEMORY_DIR, SUMMARY_DIR, PERMANENT_DIR, INDEX_DIR, KB_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 停用词
STOP_WORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'http', 'https', 'com', '文件', '可以', '使用', '进行', '需要', '已经', '完成', '添加', '通过', '如果', '然后', '今天', '现在', '开始'
])


class DailyMemory:
    """每日记忆模块"""
    
    @staticmethod
    def save(content: str = None):
        """保存每日记忆"""
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = MEMORY_DIR / f"{today}.md"
        
        if content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 每日记忆已保存: {file_path}")
        else:
            print(f"ℹ️ 记忆文件已存在: {file_path}")
        
        return file_path
    
    @staticmethod
    def get_recent(days: int = 7):
        """获取最近N天的记忆文件"""
        files = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for f in MEMORY_DIR.glob("*.md"):
            try:
                date = datetime.strptime(f.stem, "%Y-%m-%d")
                if date >= cutoff:
                    files.append(f)
            except:
                continue
        
        return sorted(files)


class MemoryAnalyzer:
    """记忆智能分析模块"""
    
    def extract_keywords(self, text: str, top_n: int = 30):
        """提取关键词"""
        words = []
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        words.extend(chinese)
        english = re.findall(r'[a-zA-Z_]{3,}', text)
        words.extend([w.lower() for w in english])
        
        filtered = [w for w in words if w not in STOP_WORDS and len(w) >= 2]
        counts = Counter(filtered)
        return counts.most_common(top_n)
    
    def extract_topics(self, keywords):
        """提取主题"""
        topics = {}
        mapping = {
            "储能项目": ["储能", "电站", "光伏", "锂电池", "PCS", "BMS"],
            "股票分析": ["股票", "股市", "K线", "均线", "RSI", "MACD"],
            "零碳园区": ["零碳", "园区", "碳中和", "多能互补", "微网"],
            "技能包开发": ["技能包", "SKILL", "OpenClaw", "API"],
            "记忆管理": ["记忆", "MEMORY", "知识库", "备份"],
            "系统运维": ["服务器", "部署", "备份", "日志", "监控"],
            "小龙虾之家": ["小龙虾", "看板", "可视化", "像素"]
        }
        
        for topic, kws in mapping.items():
            count = sum(1 for kw, _ in keywords if any(tkw in kw for tkw in kws))
            if count > 0:
                topics[topic] = count
        
        return topics
    
    def analyze_monthly(self, month_str: str = None):
        """月度分析"""
        if not month_str:
            today = datetime.now()
            month_str = today.strftime("%Y-%m") if today.day >= 5 else (today - timedelta(days=10)).strftime("%Y-%m")
        
        print(f"🧠 分析月份: {month_str}")
        
        # 获取当月文件
        files = []
        for f in MEMORY_DIR.glob("*.md"):
            if f.stem.startswith(month_str):
                files.append(f)
        
        if not files:
            print(f"⚠️ 没有找到 {month_str} 的记忆文件")
            return
        
        # 读取所有文本
        all_text = ""
        for f in files:
            with open(f, 'r', encoding='utf-8') as fp:
                all_text += fp.read() + "\n"
        
        # 分析
        keywords = self.extract_keywords(all_text)
        topics = self.extract_topics(keywords)
        
        # 生成摘要
        self._generate_summary(month_str, files, keywords, topics, len(all_text))
        
        # 更新索引
        self._update_index(month_str, keywords, topics)
        
        # 同步知识库
        self._sync_to_kb(month_str, keywords, topics)
        
        print(f"✅ 月度分析完成: {month_str}")
        return {
            "month": month_str,
            "files": len(files),
            "keywords": keywords[:10],
            "topics": topics
        }
    
    def _generate_summary(self, month_str, files, keywords, topics, total_chars):
        """生成月度摘要"""
        summary_file = SUMMARY_DIR / f"{month_str}-summary.md"
        
        content = f"""# {month_str} 月度记忆摘要

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 统计

- **文件数**: {len(files)} 个
- **字符数**: {total_chars:,} 字符
- **关键词**: {len(keywords)} 个

## 🔑 高频关键词 TOP15

"""
        for i, (word, count) in enumerate(keywords[:15], 1):
            bar = "█" * min(count, 20)
            content += f"{i}. **{word}** - {count}次 {bar}\n"
        
        content += "\n## 📁 主题分布\n\n"
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * min(count, 15)
            content += f"- **{topic}**: {count}次 {bar}\n"
        
        content += "\n---\n*由统一记忆系统自动生成*\n"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📝 月度摘要: {summary_file}")
    
    def _update_index(self, month_str, keywords, topics):
        """更新索引"""
        # 关键词索引
        kw_file = INDEX_DIR / "keywords.json"
        kw_data = json.load(open(kw_file, 'r', encoding='utf-8')) if kw_file.exists() else {}
        kw_data[month_str] = {"date": datetime.now().isoformat(), "keywords": keywords[:20]}
        with open(kw_file, 'w', encoding='utf-8') as f:
            json.dump(kw_data, f, ensure_ascii=False, indent=2)
        
        # 主题索引
        t_file = INDEX_DIR / "themes.json"
        t_data = json.load(open(t_file, 'r', encoding='utf-8')) if t_file.exists() else {}
        t_data[month_str] = {"date": datetime.now().isoformat(), "themes": topics}
        with open(t_file, 'w', encoding='utf-8') as f:
            json.dump(t_data, f, ensure_ascii=False, indent=2)
        
        print(f"📇 索引已更新")
    
    def _sync_to_kb(self, month_str, keywords, topics):
        """同步到知识库"""
        kb_index = KB_DIR / "INDEX.md"
        if not kb_index.exists():
            return
        
        with open(kb_index, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if f"{month_str}月度高频" in content:
            return
        
        top_kw = [kw for kw, _ in keywords[:5]]
        top_t = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
        
        entry = f"""\n### {month_str}月度高频主题与关键词\n\n**高频关键词**: {', '.join(top_kw)}\n\n**核心主题**:\n"""
        for t, c in top_t:
            entry += f"- {t} ({c}次)\n"
        entry += f"\n**来源**: [月度摘要](memory/summary/{month_str}-summary.md)\n\n"
        
        if "## 统计信息" in content:
            content = content.replace("## 统计信息", entry + "## 统计信息")
        
        with open(kb_index, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📚 知识库已同步")


class EnhancedRecall:
    """增强记忆模块 - 重要性分级"""
    
    def __init__(self):
        self.db_path = WORKSPACE / ".memory" / "enhanced"
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.memories_file = self.db_path / "memories.json"
        self.memories = self._load()
    
    def _load(self):
        if self.memories_file.exists():
            with open(self.memories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save(self):
        with open(self.memories_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)
    
    def store(self, text: str, category: str = "general", importance: float = 0.5, scope: str = "global"):
        """存储记忆（带重要性）"""
        memory = {
            "id": len(self.memories) + 1,
            "text": text,
            "category": category,
            "importance": importance,
            "scope": scope,
            "created": datetime.now().isoformat(),
            "access_count": 0
        }
        self.memories.append(memory)
        self._save()
        print(f"💾 记忆已存储 (重要性: {importance}): {text[:50]}...")
        return memory["id"]
    
    def search(self, query: str, top_k: int = 5, scope: str = None):
        """搜索记忆（按重要性排序）"""
        results = []
        query_lower = query.lower()
        
        for m in self.memories:
            if scope and m["scope"] != scope:
                continue
            
            # 简单匹配
            score = 0
            if query_lower in m["text"].lower():
                score += 1.0
            
            # 计算年龄衰减
            created = datetime.fromisoformat(m["created"])
            age_days = (datetime.now() - created).days
            time_decay = 0.5 + 0.5 * (2.71828 ** (-age_days / 60))
            
            # 重要性加权
            importance_weight = 0.7 + 0.3 * m["importance"]
            
            # 最终得分
            final_score = score * time_decay * importance_weight
            
            if score > 0:
                results.append({
                    "memory": m,
                    "score": final_score,
                    "time_decay": time_decay
                })
        
        # 按得分排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"🔍 找到 {len(results)} 条相关记忆 (显示前{top_k}条):")
        for i, r in enumerate(results[:top_k], 1):
            m = r["memory"]
            print(f"  {i}. [{m['importance']}] {m['text'][:60]}... (得分: {r['score']:.3f})")
        
        return results[:top_k]


class SessionPersistence:
    """会话持久化模块"""
    
    def __init__(self):
        self.state_dir = WORKSPACE / ".session-states"
        self.state_dir.mkdir(exist_ok=True)
    
    def save(self):
        """保存会话状态"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        state_file = self.state_dir / f"state_{timestamp}.json"
        
        # 获取当前信息
        state = {
            "timestamp": timestamp,
            "workdir": str(WORKSPACE),
            "memory_files": len(list(MEMORY_DIR.glob("*.md"))),
            "saved_at": datetime.now().isoformat()
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"💾 会话状态已保存: {state_file}")
        return state_file
    
    def restore(self):
        """恢复会话状态"""
        states = sorted(self.state_dir.glob("state_*.json"))
        if not states:
            print("⚠️ 没有找到会话状态文件")
            return None
        
        latest = states[-1]
        with open(latest, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        print(f"🔄 恢复会话状态 (来自: {latest.name})")
        print(f"   保存时间: {state.get('saved_at', 'unknown')}")
        print(f"   记忆文件: {state.get('memory_files', 0)} 个")
        
        return state


class PredictiveAdvisorModule:
    """预测性工作建议模块包装器"""
    
    def __init__(self):
        self.advisor = None
    
    def _load_advisor(self):
        """延迟加载预测模块"""
        if self.advisor is None:
            try:
                from predictive_advisor import PredictiveAdvisor
                self.advisor = PredictiveAdvisor()
            except ImportError as e:
                print(f"⚠️ 无法加载预测模块: {e}")
                return None
        return self.advisor
    
    def next_week_focus(self):
        """预测下周工作重点"""
        advisor = self._load_advisor()
        if advisor:
            return advisor.predict_next_week_focus()
        return {"status": "error", "message": "预测模块不可用"}
    
    def work_rhythm(self):
        """建议工作节奏"""
        advisor = self._load_advisor()
        if advisor:
            return advisor.suggest_work_rhythm()
        return {"status": "error", "message": "预测模块不可用"}
    
    def reminders(self):
        """提醒逾期事项"""
        advisor = self._load_advisor()
        if advisor:
            return advisor.remind_overdue_items()
        return {"status": "error", "message": "预测模块不可用"}
    
    def patterns(self):
        """分析工作模式"""
        advisor = self._load_advisor()
        if advisor:
            return advisor.analyze_work_patterns()
        return {"status": "error", "message": "预测模块不可用"}
    
    def briefing(self):
        """生成每日简报"""
        advisor = self._load_advisor()
        if advisor:
            return advisor.generate_daily_briefing()
        return "预测模块不可用"


class UnifiedMemorySystem:
    """统一记忆系统主类"""
    
    def __init__(self):
        self.daily = DailyMemory()
        self.analyzer = MemoryAnalyzer()
        self.recall = EnhancedRecall()
        self.session = SessionPersistence()
        self.advisor = PredictiveAdvisorModule()
    
    def get_stats(self):
        """获取系统统计"""
        stats = {
            "daily_memory": {
                "total_files": len(list(MEMORY_DIR.glob("*.md"))),
                "recent_7_days": len(self.daily.get_recent(7))
            },
            "analyzer": {
                "summaries": len(list(SUMMARY_DIR.glob("*.md"))),
                "permanent": len(list(PERMANENT_DIR.glob("*.md")))
            },
            "recall": {
                "total_memories": len(self.recall.memories)
            },
            "session": {
                "saved_states": len(list(self.session.state_dir.glob("*.json")))
            }
        }
        return stats
    
    def print_status(self):
        """打印系统状态"""
        stats = self.get_stats()
        
        print("=" * 50)
        print("🧠 统一记忆系统状态")
        print("=" * 50)
        print(f"\n📅 每日记忆:")
        print(f"   总文件数: {stats['daily_memory']['total_files']}")
        print(f"   最近7天: {stats['daily_memory']['recent_7_days']}")
        
        print(f"\n📊 智能分析:")
        print(f"   月度摘要: {stats['analyzer']['summaries']}")
        print(f"   永久记忆: {stats['analyzer']['permanent']}")
        
        print(f"\n💾 增强记忆:")
        print(f"   记忆总数: {stats['recall']['total_memories']}")
        
        print(f"\n🔄 会话持久:")
        print(f"   保存状态: {stats['session']['saved_states']}")
        
        print(f"\n🔮 预测建议:")
        print(f"   运行: ums advisor briefing")
        
        print("\n" + "=" * 50)


# CLI 入口
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="统一记忆系统")
    parser.add_argument("command", choices=["daily", "analyze", "recall", "session", "status", "advisor"])
    parser.add_argument("--action", "-a", help="具体操作")
    parser.add_argument("--month", "-m", help="指定月份")
    parser.add_argument("--text", "-t", help="记忆内容")
    parser.add_argument("--importance", "-i", type=float, default=0.5, help="重要性 0-1")
    parser.add_argument("--top", "-k", type=int, default=5, help="返回结果数量")
    
    args = parser.parse_args()
    
    ums = UnifiedMemorySystem()
    
    if args.command == "daily":
        if args.action == "save":
            ums.daily.save(args.text)
        else:
            files = ums.daily.get_recent(7)
            print(f"📅 最近7天记忆文件: {len(files)} 个")
            for f in files[-5:]:
                print(f"   - {f.name}")
    
    elif args.command == "analyze":
        result = ums.analyzer.analyze_monthly(args.month)
        if result:
            print(f"\n📊 分析结果:")
            print(f"   月份: {result['month']}")
            print(f"   文件: {result['files']} 个")
            print(f"   关键词: {len(result['keywords'])} 个")
            print(f"   主题: {len(result['topics'])} 个")
    
    elif args.command == "recall":
        if args.action == "store":
            ums.recall.store(args.text, importance=args.importance)
        else:
            if args.text:
                ums.recall.search(args.text, top_k=args.top)
            else:
                print(f"💾 存储的记忆: {len(ums.recall.memories)} 条")
    
    elif args.command == "session":
        if args.action == "save":
            ums.session.save()
        elif args.action == "restore":
            ums.session.restore()
        else:
            print("使用: ums session save|restore")
    
    elif args.command == "status":
        ums.print_status()
    
    elif args.command == "advisor":
        action = args.action or "briefing"
        
        if action == "briefing":
            print(ums.advisor.briefing())
        elif action == "focus":
            result = ums.advisor.next_week_focus()
            if result['status'] == 'success':
                print("🎯 下周工作重点预测")
                print("=" * 50)
                for area in result['focus_areas']:
                    print(f"\n{area['topic']} [{area['confidence']}]")
                    print(f"  趋势: {area['trend']}")
                    print(f"  建议: {area['suggestion']}")
            else:
                print(result['message'])
        elif action == "rhythm":
            result = ums.advisor.work_rhythm()
            if result['status'] == 'success':
                print("⏱️ 工作节奏建议")
                print("=" * 50)
                for suggestion in result['suggestions']:
                    icon = "⚠️" if suggestion['type'] == 'warning' else "💡"
                    print(f"\n{icon} {suggestion['message']}")
                    print(f"   行动: {suggestion['action']}")
            else:
                print(result['message'])
        elif action == "remind":
            result = ums.advisor.reminders()
            print("⏰ 待办事项提醒")
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
        elif action == "patterns":
            result = ums.advisor.patterns()
            if result['status'] == 'success':
                print("📈 工作模式分析")
                print("=" * 50)
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
        else:
            print("用法: ums advisor [briefing|focus|rhythm|remind|patterns]")


if __name__ == "__main__":
    main()
