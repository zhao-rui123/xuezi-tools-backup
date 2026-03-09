#!/usr/bin/env python3
"""
决策支持系统 (Decision Support System)
第三阶段 - 生态融合

功能：
1. 基于历史决策提供建议
2. 相似项目经验自动提示
3. 风险评估参考
4. 决策模板推荐

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
from collections import defaultdict
from dataclasses import dataclass, asdict

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
KNOWLEDGE_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/knowledge-base")
DECISION_FILE = MEMORY_DIR / "decision_history.json"


@dataclass
class Decision:
    """决策记录"""
    id: str
    title: str
    context: str
    decision: str
    reasoning: str
    outcome: str  # success, partial, failure
    date: str
    tags: List[str]
    related_projects: List[str]
    lessons: str


class DecisionSupportSystem:
    """决策支持系统"""
    
    def __init__(self):
        self.memory_dir = MEMORY_DIR
        self.knowledge_dir = KNOWLEDGE_DIR
        self.decisions: List[Decision] = []
        self._load_decisions()
    
    def _load_decisions(self):
        """加载决策历史"""
        if DECISION_FILE.exists():
            try:
                with open(DECISION_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.decisions = [Decision(**d) for d in data.get("decisions", [])]
            except:
                self.decisions = []
    
    def _save_decisions(self):
        """保存决策历史"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "decisions": [asdict(d) for d in self.decisions]
        }
        with open(DECISION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def extract_decisions_from_memory(self):
        """从记忆中提取决策"""
        print("🔍 提取历史决策...")
        
        new_decisions = 0
        
        # 扫描记忆文件
        for file_path in self.memory_dir.glob("2026-*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找 [DECISION] 区块
                decision_blocks = re.findall(
                    r'\[DECISION\]\s*(.+?)(?=\n\[|\Z)',
                    content,
                    re.DOTALL
                )
                
                for block in decision_blocks:
                    decision_text = block.strip()
                    if len(decision_text) < 10:
                        continue
                    
                    # 提取日期
                    date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', file_path.name)
                    date = date_match.group(0) if date_match else datetime.now().strftime('%Y-%m-%d')
                    
                    # 生成ID
                    decision_id = f"{date}-{hash(decision_text) % 10000:04d}"
                    
                    # 检查是否已存在
                    if any(d.id == decision_id for d in self.decisions):
                        continue
                    
                    # 解析决策
                    title = decision_text.split('\n')[0][:50]
                    reasoning = ""
                    
                    # 提取推理过程
                    if "原因" in decision_text or "理由" in decision_text:
                        reasoning_match = re.search(r'(?:原因|理由)[：:]\s*(.+?)(?=\n|$)', decision_text)
                        if reasoning_match:
                            reasoning = reasoning_match.group(1)
                    
                    # 创建决策记录
                    decision = Decision(
                        id=decision_id,
                        title=title,
                        context="",
                        decision=decision_text[:200],
                        reasoning=reasoning,
                        outcome="unknown",  # 需要后续更新
                        date=date,
                        tags=[],
                        related_projects=[],
                        lessons=""
                    )
                    
                    self.decisions.append(decision)
                    new_decisions += 1
                    
            except Exception as e:
                print(f"  ⚠️ 处理 {file_path.name} 失败: {str(e)}")
        
        if new_decisions > 0:
            self._save_decisions()
        
        print(f"  提取了 {new_decisions} 个新决策")
        return new_decisions
    
    def find_similar_decisions(self, context: str, limit: int = 3) -> List[Decision]:
        """查找相似决策"""
        if not self.decisions:
            return []
        
        # 提取关键词
        keywords = self._extract_keywords(context)
        
        # 计算相似度
        scored = []
        for decision in self.decisions:
            score = 0
            decision_text = f"{decision.title} {decision.decision} {decision.reasoning}"
            
            for keyword in keywords:
                if keyword in decision_text.lower():
                    score += 1
            
            if score > 0:
                scored.append((decision, score))
        
        # 排序并返回
        scored.sort(key=lambda x: x[1], reverse=True)
        return [d for d, _ in scored[:limit]]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 中文词汇
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
        keywords.extend(chinese)
        
        # 英文词汇
        english = re.findall(r'[A-Za-z][A-Za-z0-9_]{2,}', text)
        keywords.extend([w.lower() for w in english])
        
        return list(set(keywords))
    
    def get_decision_suggestions(self, context: str) -> List[Dict]:
        """获取决策建议"""
        suggestions = []
        
        # 1. 查找相似决策
        similar = self.find_similar_decisions(context)
        
        for decision in similar:
            # 根据结果给出建议
            if decision.outcome == "success":
                suggestion = {
                    "type": "similar_success",
                    "title": f"参考成功决策: {decision.title[:40]}",
                    "content": decision.decision[:100],
                    "reasoning": decision.reasoning,
                    "confidence": 0.8,
                    "action": "该决策在过去取得了成功，可考虑类似方案"
                }
            elif decision.outcome == "failure":
                suggestion = {
                    "type": "lesson_learned",
                    "title": f"⚠️ 曾失败的类似决策: {decision.title[:40]}",
                    "content": decision.decision[:100],
                    "reasoning": decision.reasoning,
                    "confidence": 0.9,
                    "action": "该决策曾导致失败，建议避免或改进"
                }
            else:
                suggestion = {
                    "type": "reference",
                    "title": f"相关决策: {decision.title[:40]}",
                    "content": decision.decision[:100],
                    "reasoning": decision.reasoning,
                    "confidence": 0.6,
                    "action": "可参考该决策的思路"
                }
            
            suggestions.append(suggestion)
        
        # 2. 基于常见模式给出建议
        if "模型" in context or "API" in context:
            suggestions.append({
                "type": "pattern",
                "title": "🔧 技术选型建议",
                "content": "根据历史记录，技术选型时应考虑：",
                "reasoning": "",
                "confidence": 0.7,
                "action": "1. 优先使用已验证的方案\n2. 考虑长期维护成本\n3. 测试兼容性"
            })
        
        if "项目" in context or "开发" in context:
            suggestions.append({
                "type": "pattern",
                "title": "📋 项目管理建议",
                "content": "项目启动前建议：",
                "reasoning": "",
                "confidence": 0.75,
                "action": "1. 明确需求和目标\n2. 制定详细计划\n3. 预留缓冲时间\n4. 定期回顾进度"
            })
        
        return suggestions
    
    def assess_risk(self, decision_context: str) -> Dict:
        """风险评估"""
        risk_factors = []
        risk_level = "low"
        
        # 1. 检查是否有失败先例
        similar_failures = [
            d for d in self.decisions
            if d.outcome == "failure" and any(
                kw in f"{d.title} {d.decision}" 
                for kw in self._extract_keywords(decision_context)
            )
        ]
        
        if similar_failures:
            risk_factors.append({
                "factor": "历史失败先例",
                "severity": "high",
                "description": f"发现 {len(similar_failures)} 个类似失败决策"
            })
            risk_level = "high"
        
        # 2. 检查时间因素
        if "立即" in decision_context or "马上" in decision_context:
            risk_factors.append({
                "factor": "时间压力",
                "severity": "medium",
                "description": "决策时间紧迫，可能考虑不周"
            })
            if risk_level == "low":
                risk_level = "medium"
        
        # 3. 检查复杂度
        complexity_indicators = ["系统", "架构", "重构", "迁移", "升级"]
        if any(indicator in decision_context for indicator in complexity_indicators):
            risk_factors.append({
                "factor": "系统复杂性",
                "severity": "medium",
                "description": "涉及系统级变更，风险较高"
            })
            if risk_level == "low":
                risk_level = "medium"
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "suggestions": [
                "建议制定回滚方案" if risk_level in ["high", "medium"] else "风险可控，可执行",
                "建议小范围测试" if risk_level == "high" else "",
                "建议咨询相关经验" if risk_factors else ""
            ]
        }
    
    def recommend_templates(self, decision_type: str = "") -> List[Dict]:
        """推荐决策模板"""
        templates = []
        
        # 通用决策模板
        templates.append({
            "name": "技术选型决策",
            "template": """### 技术选型决策

**问题**: [描述需要解决的问题]

**方案A**: [方案描述]
- 优点: 
- 缺点: 
- 风险: 

**方案B**: [方案描述]
- 优点: 
- 缺点: 
- 风险: 

**决定**: [选择哪个方案]

**原因**: [详细说明决策理由]
""",
            "tags": ["技术", "选型"]
        })
        
        templates.append({
            "name": "项目启动决策",
            "template": """### 项目启动决策

**项目名称**: 

**目标**: [明确的项目目标]

**范围**: [项目边界]

**资源**: [所需资源]

**时间**: [预期时间]

**风险**: [主要风险及应对措施]

**决定**: [是否启动]
""",
            "tags": ["项目", "启动"]
        })
        
        templates.append({
            "name": "快速决策",
            "template": """### 决策

**情况**: [简要描述]

**决定**: [决策内容]

**原因**: [简要理由]

**预期结果**: 
""",
            "tags": ["快速", "简单"]
        })
        
        return templates
    
    def generate_decision_report(self) -> Dict:
        """生成决策报告"""
        # 统计
        total = len(self.decisions)
        success = sum(1 for d in self.decisions if d.outcome == "success")
        failure = sum(1 for d in self.decisions if d.outcome == "failure")
        unknown = total - success - failure
        
        # 按月份统计
        monthly = defaultdict(int)
        for d in self.decisions:
            month = d.date[:7] if len(d.date) >= 7 else d.date
            monthly[month] += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_decisions": total,
                "success": success,
                "failure": failure,
                "unknown": unknown,
                "success_rate": round(success / total * 100, 1) if total > 0 else 0
            },
            "monthly_distribution": dict(monthly),
            "recent_decisions": [
                {
                    "title": d.title,
                    "date": d.date,
                    "outcome": d.outcome
                }
                for d in sorted(self.decisions, key=lambda x: x.date, reverse=True)[:5]
            ]
        }
    
    def run(self):
        """运行决策支持系统"""
        print("=" * 60)
        print("🎯 决策支持系统")
        print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 1. 提取历史决策
        new_count = self.extract_decisions_from_memory()
        
        # 2. 生成报告
        report = self.generate_decision_report()
        
        # 打印报告
        print("\n" + "=" * 60)
        print("📊 决策报告")
        print("=" * 60)
        print(f"  总决策数: {report['summary']['total_decisions']}")
        print(f"  成功: {report['summary']['success']} 次")
        print(f"  失败: {report['summary']['failure']} 次")
        print(f"  成功率: {report['summary']['success_rate']}%")
        
        if report['recent_decisions']:
            print(f"\n  📅 最近决策:")
            for i, d in enumerate(report['recent_decisions'][:3], 1):
                outcome_emoji = {"success": "✅", "failure": "❌", "unknown": "❓"}.get(d['outcome'], "❓")
                print(f"    {i}. {outcome_emoji} {d['date']} - {d['title'][:40]}")
        
        # 3. 推荐模板
        print(f"\n  📝 可用模板:")
        templates = self.recommend_templates()
        for i, t in enumerate(templates, 1):
            print(f"    {i}. {t['name']} ({', '.join(t['tags'])})")
        
        # 保存报告
        report_file = self.memory_dir / "decision_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n  📝 报告已保存: {report_file}")
        
        print("\n✅ 决策支持系统完成")
        
        return report


def main():
    """主函数"""
    system = DecisionSupportSystem()
    report = system.run()
    return report


if __name__ == "__main__":
    main()
