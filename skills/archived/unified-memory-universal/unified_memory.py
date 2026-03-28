#!/usr/bin/env python3
"""
统一记忆系统 - 通用脱敏版
Unified Memory System - Universal Version

使用前请修改配置文件中的路径！
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

# ============== 配置区域 ==============
# 请修改为您的实际路径
WORKSPACE = Path(os.environ.get('UMS_WORKSPACE', os.path.expanduser('~/.ums/workspace')))
MEMORY_DIR = WORKSPACE / "memory"
SUMMARY_DIR = MEMORY_DIR / "summary"
PERMANENT_DIR = MEMORY_DIR / "permanent"
INDEX_DIR = MEMORY_DIR / "index"

# 确保目录存在
for d in [MEMORY_DIR, SUMMARY_DIR, PERMANENT_DIR, INDEX_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============== 停用词 ==============
STOP_WORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'http', 'https', 'com', '文件', '可以', '使用', '进行', '需要', '已经', '完成', '添加', '通过', '如果', '然后', '今天', '现在', '开始'
])

# ============== 核心类 ==============

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
            print(f"Saved: {file_path}")
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
        return Counter(filtered).most_common(top_n)
    
    def analyze_monthly(self, month_str: str = None):
        """月度分析"""
        if not month_str:
            today = datetime.now()
            month_str = today.strftime("%Y-%m") if today.day >= 5 else (today - timedelta(days=10)).strftime("%Y-%m")
        
        print(f"Analyzing: {month_str}")
        
        files = [f for f in MEMORY_DIR.glob("*.md") if f.stem.startswith(month_str)]
        if not files:
            print(f"No memory files found for {month_str}")
            return
        
        all_text = ""
        for f in files:
            with open(f, 'r', encoding='utf-8') as fp:
                all_text += fp.read() + "\n"
        
        keywords = self.extract_keywords(all_text)
        
        # 生成摘要
        self._generate_summary(month_str, files, keywords, len(all_text))
        self._update_index(month_str, keywords)
        
        print(f"Analysis complete: {month_str}")
        return {"month": month_str, "files": len(files), "keywords": keywords[:10]}
    
    def _generate_summary(self, month_str, files, keywords, total_chars):
        """生成月度摘要"""
        summary_file = SUMMARY_DIR / f"{month_str}-summary.md"
        
        content = f"# {month_str} Summary\n\nGenerated: {datetime.now().isoformat()}\n\n"
        content += f"Files: {len(files)}\nCharacters: {total_chars}\n\n"
        content += "## Top Keywords\n\n"
        
        for word, count in keywords[:15]:
            content += f"- {word}: {count}\n"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Summary: {summary_file}")
    
    def _update_index(self, month_str, keywords):
        """更新索引"""
        kw_file = INDEX_DIR / "keywords.json"
        kw_data = json.load(open(kw_file, 'r', encoding='utf-8')) if kw_file.exists() else {}
        kw_data[month_str] = {"date": datetime.now().isoformat(), "keywords": keywords[:20]}
        with open(kw_file, 'w', encoding='utf-8') as f:
            json.dump(kw_data, f, ensure_ascii=False, indent=2)


class EnhancedRecall:
    """增强记忆模块"""
    
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
    
    def store(self, text: str, category: str = "general", importance: float = 0.5):
        """存储记忆"""
        memory = {
            'id': len(self.memories) + 1,
            'text': text,
            'category': category,
            'importance': importance,
            'created': datetime.now().isoformat()
        }
        self.memories.append(memory)
        self._save()
        return memory
    
    def search(self, query: str, top_k: int = 5):
        """搜索记忆"""
        results = []
        query_lower = query.lower()
        
        for mem in self.memories:
            score = 0
            if query_lower in mem['text'].lower():
                score += 1.0
            
            if score > 0:
                created = datetime.fromisoformat(mem['created'])
                age_days = (datetime.now() - created).days
                time_decay = 0.5 + 0.5 * (2.71828 ** (-age_days / 60))
                importance_weight = 0.7 + 0.3 * mem['importance']
                final_score = score * time_decay * importance_weight
                
                results.append({'memory': mem, 'score': final_score})
        
        results.sort(key=lambda x: x['score'], reverse=True)
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
        
        state = {
            'timestamp': timestamp,
            'workdir': str(WORKSPACE),
            'memory_files': len(list(MEMORY_DIR.glob("*.md"))),
            'saved_at': datetime.now().isoformat()
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"Session saved: {state_file}")
        return state_file
    
    def restore(self):
        """恢复会话状态"""
        states = sorted(self.state_dir.glob("state_*.json"))
        if not states:
            print("No saved session found")
            return None
        
        latest = states[-1]
        with open(latest, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        print(f"Session restored from: {latest.name}")
        return state


# ============== CLI 入口 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Memory System")
    parser.add_argument("command", choices=["daily", "analyze", "recall", "session", "status"])
    parser.add_argument("--text", "-t", help="Memory content")
    parser.add_argument("--importance", "-i", type=float, default=0.5)
    
    args = parser.parse_args()
    
    if args.command == "daily":
        DailyMemory.save(args.text)
    elif args.command == "analyze":
        MemoryAnalyzer().analyze_monthly()
    elif args.command == "recall":
        recall = EnhancedRecall()
        if args.text:
            recall.store(args.text, importance=args.importance)
        print(f"Total memories: {len(recall.memories)}")
    elif args.command == "session":
        SessionPersistence().save()
    elif args.command == "status":
        print("Unified Memory System")
        print(f"Memory files: {len(list(MEMORY_DIR.glob('*.md')))}")

if __name__ == "__main__":
    main()
