#!/usr/bin/env python3
"""
记忆重要性评估系统 (Memory Importance Scorer)
第一阶段 - 基础优化

功能：
1. 自动评估记忆重要性（0-1分数）
2. 标记重要决策、关键项目
3. 低质量记忆识别
4. 为检索排序提供依据

作者: 雪子助手
版本: 1.0.0
日期: 2026-03-09
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")

# 重要性权重配置
WEIGHTS = {
    "base": 0.5,           # 基础分
    "decision": 0.25,      # 决策标记
    "project": 0.2,        # 项目标记
    "task": 0.1,           # 任务标记
    "keyword": 0.05,       # 每个关键词
    "length": 0.1,         # 长度适中
    "has_code": 0.1,       # 包含代码
    "has_url": 0.05,       # 包含URL
}

# 重要关键词列表
IMPORTANT_KEYWORDS = [
    # 决策类
    "决定", "决策", "方案", "选择", "确定", "确定", "采纳",
    "重要", "关键", "核心", "战略",
    # 项目类
    "项目", "开发", "部署", "上线", "完成", "交付",
    "系统", "工具", "平台", "产品",
    # 问题类
    "问题", "故障", "错误", "修复", "解决", "bug",
    # 成果类
    "成果", "成就", "突破", "里程碑", "成功",
    # 技术类
    "API", "配置", "数据库", "服务器", "架构", "优化",
]

# 低质量关键词
LOW_QUALITY_KEYWORDS = [
    "测试", "临时", "草稿", "待确认", "不确定",
]


@dataclass
class MemoryScore:
    """记忆评分结果"""
    file_path: Path
    importance: float
    category: str
    tags: List[str]
    reasons: List[str]
    raw_score: Dict


class MemoryImportanceScorer:
    """记忆重要性评估器"""
    
    def __init__(self):
        self.memory_dir = MEMORY_DIR
        self.results: List[MemoryScore] = []
    
    def calculate_importance(self, content: str, filename: str) -> Tuple[float, Dict]:
        """计算记忆重要性分数"""
        score = WEIGHTS["base"]  # 基础分
        details = {
            "base": WEIGHTS["base"],
            "decision": 0,
            "project": 0,
            "task": 0,
            "keywords": 0,
            "length": 0,
            "has_code": 0,
            "has_url": 0,
            "deduction": 0
        }
        
        # 1. 决策标记加分
        if re.search(r'\[DECISION\]|##.*决定|##.*决策', content, re.IGNORECASE):
            score += WEIGHTS["decision"]
            details["decision"] = WEIGHTS["decision"]
        
        # 2. 项目标记加分
        if re.search(r'\[PROJECT\]|##.*项目|项目.*完成', content, re.IGNORECASE):
            score += WEIGHTS["project"]
            details["project"] = WEIGHTS["project"]
        
        # 3. 任务标记加分
        if re.search(r'\[TODO\]|##.*任务|##.*工作', content, re.IGNORECASE):
            score += WEIGHTS["task"]
            details["task"] = WEIGHTS["task"]
        
        # 4. 关键词匹配
        keyword_count = 0
        for keyword in IMPORTANT_KEYWORDS:
            if keyword.lower() in content.lower():
                keyword_count += 1
        keyword_score = min(keyword_count * WEIGHTS["keyword"], 0.3)  # 最高0.3
        score += keyword_score
        details["keywords"] = keyword_score
        
        # 5. 内容长度（适中最好）
        content_length = len(content)
        if 500 <= content_length <= 5000:
            score += WEIGHTS["length"]
            details["length"] = WEIGHTS["length"]
        elif content_length < 100:
            score -= 0.1  # 太短扣分
            details["deduction"] += 0.1
        
        # 6. 包含代码块
        if re.search(r'```[\s\S]*?```', content):
            score += WEIGHTS["has_code"]
            details["has_code"] = WEIGHTS["has_code"]
        
        # 7. 包含URL
        if re.search(r'https?://[^\s]+', content):
            score += WEIGHTS["has_url"]
            details["has_url"] = WEIGHTS["has_url"]
        
        # 8. 低质量关键词扣分
        for keyword in LOW_QUALITY_KEYWORDS:
            if keyword in content:
                score -= 0.05
                details["deduction"] += 0.05
        
        # 确保分数在0-1之间
        score = max(0, min(1, score))
        
        return score, details
    
    def determine_category(self, content: str) -> str:
        """确定记忆类别"""
        if re.search(r'\[DECISION\]|决定|决策', content):
            return "decision"
        elif re.search(r'\[PROJECT\]|项目|开发|部署', content):
            return "project"
        elif re.search(r'\[TODO\]|任务|待办', content):
            return "task"
        elif re.search(r'bug|错误|故障|修复|问题', content, re.IGNORECASE):
            return "issue"
        elif re.search(r'股票|股市|行情|分析', content):
            return "stock"
        elif re.search(r'技能包|工具|脚本', content):
            return "skill"
        elif re.search(r'会议|讨论|沟通', content):
            return "meeting"
        elif re.search(r'学习|研究|分析', content):
            return "learning"
        else:
            return "general"
    
    def extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        tags = []
        
        # 匹配 #标签 格式
        tag_pattern = r'#([\w\u4e00-\u9fa5-]+)'
        tags = re.findall(tag_pattern, content)
        
        return tags
    
    def generate_reasons(self, score: float, details: Dict) -> List[str]:
        """生成评分理由"""
        reasons = []
        
        if details["decision"] > 0:
            reasons.append("包含重要决策")
        if details["project"] > 0:
            reasons.append("包含项目信息")
        if details["task"] > 0:
            reasons.append("包含任务记录")
        if details["keywords"] > 0.1:
            reasons.append(f"包含{int(details['keywords'] / WEIGHTS['keyword'])}个重要关键词")
        if details["has_code"] > 0:
            reasons.append("包含代码")
        if details["has_url"] > 0:
            reasons.append("包含链接")
        if details["length"] > 0:
            reasons.append("内容长度适中")
        if details["deduction"] > 0:
            reasons.append("部分内容质量较低")
        
        return reasons
    
    def score_memory_file(self, file_path: Path) -> Optional[MemoryScore]:
        """评估单个记忆文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 计算重要性
            importance, details = self.calculate_importance(content, file_path.name)
            
            # 确定类别
            category = self.determine_category(content)
            
            # 提取标签
            tags = self.extract_tags(content)
            
            # 生成理由
            reasons = self.generate_reasons(importance, details)
            
            return MemoryScore(
                file_path=file_path,
                importance=importance,
                category=category,
                tags=tags,
                reasons=reasons,
                raw_score=details
            )
            
        except Exception as e:
            print(f"  ⚠️ 评估 {file_path.name} 失败: {str(e)}")
            return None
    
    def score_all_memories(self) -> List[MemoryScore]:
        """评估所有记忆文件"""
        print("🔍 扫描记忆文件...")
        
        memory_files = []
        
        # 1. 当前目录的每日记忆
        for file_path in self.memory_dir.glob("2026-*.md"):
            memory_files.append(file_path)
        
        # 2. 归档目录的记忆
        archive_dir = self.memory_dir / "archive"
        if archive_dir.exists():
            for file_path in archive_dir.rglob("*.md"):
                memory_files.append(file_path)
        
        print(f"  找到 {len(memory_files)} 个记忆文件")
        
        # 评估每个文件
        print("\n📊 评估重要性...")
        for i, file_path in enumerate(memory_files, 1):
            print(f"  [{i}/{len(memory_files)}] {file_path.name}...", end=" ")
            
            score = self.score_memory_file(file_path)
            if score:
                self.results.append(score)
                print(f"重要性: {score.importance:.2f} [{score.category}]")
            else:
                print("跳过")
        
        return self.results
    
    def get_high_importance_memories(self, threshold: float = 0.7) -> List[MemoryScore]:
        """获取高重要性记忆"""
        return [r for r in self.results if r.importance >= threshold]
    
    def get_low_importance_memories(self, threshold: float = 0.3) -> List[MemoryScore]:
        """获取低重要性记忆"""
        return [r for r in self.results if r.importance <= threshold]
    
    def generate_report(self) -> Dict:
        """生成评估报告"""
        if not self.results:
            return {}
        
        # 统计
        high_count = len(self.get_high_importance_memories())
        low_count = len(self.get_low_importance_memories())
        medium_count = len(self.results) - high_count - low_count
        
        # 分类统计
        category_count = {}
        for r in self.results:
            category_count[r.category] = category_count.get(r.category, 0) + 1
        
        # 平均分
        avg_importance = sum(r.importance for r in self.results) / len(self.results)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_memories": len(self.results),
            "importance_distribution": {
                "high": high_count,
                "medium": medium_count,
                "low": low_count
            },
            "category_distribution": category_count,
            "average_importance": round(avg_importance, 2),
            "high_importance_memories": [
                {
                    "file": str(r.file_path.name),
                    "importance": round(r.importance, 2),
                    "category": r.category,
                    "reasons": r.reasons
                }
                for r in sorted(self.results, key=lambda x: x.importance, reverse=True)[:10]
            ]
        }
        
        return report
    
    def save_scores(self):
        """保存评分结果"""
        scores_data = {
            "timestamp": datetime.now().isoformat(),
            "scores": [
                {
                    "file": str(r.file_path.relative_to(self.memory_dir)),
                    "importance": round(r.importance, 3),
                    "category": r.category,
                    "tags": r.tags
                }
                for r in self.results
            ]
        }
        
        output_file = self.memory_dir / "memory_scores.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scores_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 评分结果已保存: {output_file}")
    
    def run(self):
        """运行评估"""
        print("=" * 60)
        print("🎯 记忆重要性评估系统")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 评估所有记忆
        self.score_all_memories()
        
        if not self.results:
            print("\n⚠️ 没有可评估的记忆文件")
            return
        
        # 生成报告
        report = self.generate_report()
        
        # 打印报告
        print("\n" + "=" * 60)
        print("📈 评估报告")
        print("=" * 60)
        print(f"  总记忆数: {report['total_memories']}")
        print(f"  平均重要性: {report['average_importance']}")
        print(f"\n  重要性分布:")
        print(f"    🔴 高 (≥0.7): {report['importance_distribution']['high']} 个")
        print(f"    🟡 中 (0.3-0.7): {report['importance_distribution']['medium']} 个")
        print(f"    🟢 低 (≤0.3): {report['importance_distribution']['low']} 个")
        print(f"\n  类别分布:")
        for cat, count in sorted(report['category_distribution'].items(), key=lambda x: x[1], reverse=True):
            print(f"    {cat}: {count} 个")
        
        print(f"\n  🔥 高重要性记忆 Top 5:")
        for i, mem in enumerate(report['high_importance_memories'][:5], 1):
            print(f"    {i}. {mem['file']} (重要性: {mem['importance']})")
            if mem['reasons']:
                print(f"       原因: {', '.join(mem['reasons'][:2])}")
        
        # 保存结果
        self.save_scores()
        
        # 保存报告
        report_file = self.memory_dir / "importance_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"📝 详细报告: {report_file}")
        
        print("\n✅ 评估完成")
        
        return report


def main():
    """主函数"""
    scorer = MemoryImportanceScorer()
    report = scorer.run()
    return report


if __name__ == "__main__":
    main()
