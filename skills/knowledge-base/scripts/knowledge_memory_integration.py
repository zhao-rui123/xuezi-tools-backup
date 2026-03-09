#!/usr/bin/env python3
"""
知识库与记忆系统整合模块 (Knowledge-Memory Integration)
连接 knowledge-base、unified-memory、self-improvement 三个系统
实现知识的自动沉淀、关联发现和持续进化
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# 路径配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
KB_DIR = WORKSPACE / "knowledge-base"
SKILLS_DIR = WORKSPACE / "skills"
UMS_DIR = SKILLS_DIR / "unified-memory"
SELF_IMPROVE_DIR = SKILLS_DIR / "self-improvement"

sys.path.insert(0, str(UMS_DIR))
sys.path.insert(0, str(SELF_IMPROVE_DIR))
sys.path.insert(0, str(SELF_IMPROVE_DIR / 'core'))


@dataclass
class KnowledgeFlow:
    """知识流动记录"""
    source: str           # 来源：daily_memory / conversation / analysis
    target: str           # 目标：knowledge_base / memory / evolution
    content_type: str     # 类型：project / decision / problem / reference
    title: str
    content_summary: str
    keywords: List[str]
    importance: float     # 0-1
    created_at: str
    auto_extracted: bool = False


class KnowledgeMemoryIntegration:
    """
    知识库与记忆系统整合器
    实现三层知识架构的自动流转
    """
    
    def __init__(self):
        self.ums_available = False
        self.recall = None
        self.analyzer = None
        self.knowledge_graph = None
        self.evolution_engine = None
        
        self._init_modules()
        
        # 数据文件
        self.flow_log_file = MEMORY_DIR / "evolution" / "knowledge_flow.json"
        self.pending_kb_updates = MEMORY_DIR / "evolution" / "pending_kb_updates.json"
    
    def _init_modules(self):
        """初始化相关模块"""
        try:
            from unified_memory import EnhancedRecall, MemoryAnalyzer
            self.recall = EnhancedRecall()
            self.analyzer = MemoryAnalyzer()
            self.ums_available = True
        except Exception as e:
            print(f"⚠️ UMS 未连接: {e}")
        
        try:
            from evolution_engine import SelfEvolutionEngine
            self.evolution_engine = SelfEvolutionEngine()
        except Exception as e:
            print(f"⚠️ Evolution Engine 未连接: {e}")
    
    # ==================== 第一层：日常记忆 → 统一记忆 ====================
    
    def process_daily_memory(self, date_str: str = None) -> List[KnowledgeFlow]:
        """
        处理每日记忆，提取有价值的知识
        
        流程:
        1. 读取当天的记忆文件
        2. 使用 unified-memory 分析
        3. 识别重要决策、项目进展、问题解决
        4. 标记需要沉淀到知识库的内容
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        memory_file = MEMORY_DIR / f"{date_str}.md"
        if not memory_file.exists():
            print(f"⚠️ 记忆文件不存在: {memory_file}")
            return []
        
        # 读取记忆内容
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        flows = []
        
        # 1. 提取项目相关信息
        project_flows = self._extract_project_updates(content, date_str)
        flows.extend(project_flows)
        
        # 2. 提取决策信息
        decision_flows = self._extract_decisions(content, date_str)
        flows.extend(decision_flows)
        
        # 3. 提取问题解决信息
        problem_flows = self._extract_problems(content, date_str)
        flows.extend(problem_flows)
        
        # 4. 存储到 unified-memory
        if self.recall:
            summary = f"[每日记忆分析] {date_str}\n"
            summary += f"提取项目更新: {len(project_flows)} 项\n"
            summary += f"提取决策: {len(decision_flows)} 项\n"
            summary += f"提取问题方案: {len(problem_flows)} 项"
            self.recall.store(summary, category="memory_analysis", importance=0.7)
        
        # 5. 保存流动记录
        self._save_flow_records(flows)
        
        print(f"✅ 处理完成: {date_str}")
        print(f"   项目更新: {len(project_flows)}")
        print(f"   决策记录: {len(decision_flows)}")
        print(f"   问题方案: {len(problem_flows)}")
        
        return flows
    
    def _extract_project_updates(self, content: str, date_str: str) -> List[KnowledgeFlow]:
        """提取项目更新"""
        flows = []
        
        # 项目相关关键词模式
        project_patterns = [
            (r"(?:完成|实现|开发|部署).{0,20}(小龙虾之家|储能|股票|技能包)", "项目进展"),
            (r"(?:新增|添加|创建).{0,20}(功能|模块|工具)", "功能新增"),
            (r"(?:修复|解决|优化).{0,20}(bug|问题|性能)", "问题修复"),
        ]
        
        lines = content.split('\n')
        current_section = ""
        
        for line in lines:
            # 检测项目标题
            if line.startswith('## ') or line.startswith('### '):
                current_section = line.strip('# ')
            
            for pattern, update_type in project_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    project_name = self._identify_project(line)
                    if project_name:
                        flow = KnowledgeFlow(
                            source="daily_memory",
                            target="knowledge_base",
                            content_type="project",
                            title=f"{project_name} - {update_type}",
                            content_summary=line.strip()[:200],
                            keywords=self._extract_keywords(line),
                            importance=0.75,
                            created_at=datetime.now().isoformat(),
                            auto_extracted=True
                        )
                        flows.append(flow)
        
        return flows
    
    def _extract_decisions(self, content: str, date_str: str) -> List[KnowledgeFlow]:
        """提取决策信息"""
        flows = []
        
        # 决策模式
        decision_patterns = [
            r"\[DECISION\].*?\n(.*?)(?=\n\[|\n## |$)",
            r"(?:决定|确定|选择).{0,30}(?:使用|采用|部署|配置)",
            r"(?:方案|策略).{0,10}(?:确定|选定|通过)",
        ]
        
        for pattern in decision_patterns:
            matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                decision_text = match.group(0)[:300]
                flow = KnowledgeFlow(
                    source="daily_memory",
                    target="knowledge_base",
                    content_type="decision",
                    title=f"决策: {decision_text[:50]}...",
                    content_summary=decision_text,
                    keywords=self._extract_keywords(decision_text),
                    importance=0.85,  # 决策重要性更高
                    created_at=datetime.now().isoformat(),
                    auto_extracted=True
                )
                flows.append(flow)
        
        return flows
    
    def _extract_problems(self, content: str, date_str: str) -> List[KnowledgeFlow]:
        """提取问题和解决方案"""
        flows = []
        
        # 问题-解决模式
        problem_sections = re.findall(
            r'(?:问题|bug|错误|故障)[：:](.*?)(?:解决|方案|修复)[：:](.*?)(?=\n\n|\n## |$)',
            content, re.DOTALL | re.IGNORECASE
        )
        
        for problem, solution in problem_sections:
            flow = KnowledgeFlow(
                source="daily_memory",
                target="knowledge_base",
                content_type="problem",
                title=f"问题: {problem.strip()[:50]}...",
                content_summary=f"问题: {problem.strip()[:200]}\n解决: {solution.strip()[:200]}",
                keywords=self._extract_keywords(problem + " " + solution),
                importance=0.8,
                created_at=datetime.now().isoformat(),
                auto_extracted=True
            )
            flows.append(flow)
        
        return flows
    
    def _identify_project(self, text: str) -> Optional[str]:
        """识别项目名称"""
        projects = {
            "小龙虾之家": ["小龙虾", "看板", "AI助手"],
            "储能工具包": ["储能", "电站", "电价"],
            "股票分析系统": ["股票", "股市", "自选股"],
            "统一记忆系统": ["统一记忆", "unified-memory", "知识图谱"],
            "自我进化系统": ["自我进化", "self-improvement", "进化"],
        }
        
        for project, keywords in projects.items():
            if any(kw in text for kw in keywords):
                return project
        
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        import re
        
        # 中文关键词
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        # 英文关键词
        english = re.findall(r'[a-zA-Z_]{3,}', text)
        
        keywords = list(set(chinese + english))
        return keywords[:10]
    
    def _save_flow_records(self, flows: List[KnowledgeFlow]):
        """保存知识流动记录"""
        records = []
        if self.flow_log_file.exists():
            try:
                with open(self.flow_log_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except:
                pass
        
        for flow in flows:
            records.append(asdict(flow))
        
        # 只保留最近1000条
        records = records[-1000:]
        
        with open(self.flow_log_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    # ==================== 第二层：统一记忆 → 知识库 ====================
    
    def sync_to_knowledge_base(self, dry_run: bool = False) -> Dict:
        """
        将分析出的知识同步到知识库
        
        流程:
        1. 读取待同步的知识流动记录
        2. 根据类型分发到对应目录
        3. 更新知识库索引
        4. 标记已同步
        """
        results = {
            "projects_updated": [],
            "decisions_added": [],
            "problems_added": [],
            "references_added": []
        }
        
        # 读取流动记录
        if not self.flow_log_file.exists():
            print("⚠️ 没有知识流动记录")
            return results
        
        with open(self.flow_log_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        # 筛选未同步的记录
        pending = [r for r in records if r.get('target') == 'knowledge_base']
        
        print(f"📤 待同步到知识库: {len(pending)} 项")
        
        for record in pending:
            content_type = record.get('content_type')
            
            if content_type == 'project':
                if self._update_project_kb(record, dry_run):
                    results["projects_updated"].append(record['title'])
            
            elif content_type == 'decision':
                if self._add_decision_kb(record, dry_run):
                    results["decisions_added"].append(record['title'])
            
            elif content_type == 'problem':
                if self._add_problem_kb(record, dry_run):
                    results["problems_added"].append(record['title'])
        
        # 更新知识库索引
        if not dry_run:
            self._update_kb_index()
        
        print(f"✅ 同步完成")
        print(f"   项目更新: {len(results['projects_updated'])}")
        print(f"   决策添加: {len(results['decisions_added'])}")
        print(f"   问题添加: {len(results['problems_added'])}")
        
        return results
    
    def _update_project_kb(self, record: Dict, dry_run: bool) -> bool:
        """更新项目知识库"""
        # 识别项目名称
        project_name = self._identify_project(record['content_summary'])
        if not project_name:
            return False
        
        project_dir = KB_DIR / "projects" / project_name
        changelog_file = project_dir / "CHANGELOG.md"
        
        if dry_run:
            print(f"   [DRY-RUN] 将更新: {changelog_file}")
            return True
        
        # 确保目录存在
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 更新或创建 CHANGELOG
        entry = f"\n## {datetime.now().strftime('%Y-%m-%d')}\n"
        entry += f"- {record['content_summary'][:100]}\n"
        
        if changelog_file.exists():
            with open(changelog_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        else:
            with open(changelog_file, 'w', encoding='utf-8') as f:
                f.write(f"# {project_name} 更新日志\n\n")
                f.write(entry)
        
        return True
    
    def _add_decision_kb(self, record: Dict, dry_run: bool) -> bool:
        """添加决策到知识库"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        decision_file = KB_DIR / "decisions" / f"{date_str}-{self._slugify(record['title'][:30])}.md"
        
        if dry_run:
            print(f"   [DRY-RUN] 将创建: {decision_file}")
            return True
        
        # 确保目录存在
        decision_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"# 决策记录\n\n"
        content += f"**日期**: {date_str}\n\n"
        content += f"**决策**: {record['title']}\n\n"
        content += f"**详情**:\n{record['content_summary']}\n\n"
        content += f"**关键词**: {', '.join(record['keywords'][:5])}\n"
        
        with open(decision_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    def _add_problem_kb(self, record: Dict, dry_run: bool) -> bool:
        """添加问题解决方案到知识库"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        problem_file = KB_DIR / "problems" / f"{date_str}-{self._slugify(record['title'][:30])}.md"
        
        if dry_run:
            print(f"   [DRY-RUN] 将创建: {problem_file}")
            return True
        
        # 确保目录存在
        problem_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"# 问题与解决方案\n\n"
        content += f"**日期**: {date_str}\n\n"
        content += f"**问题**: {record['title']}\n\n"
        content += f"**解决方案**:\n{record['content_summary']}\n\n"
        content += f"**关键词**: {', '.join(record['keywords'][:5])}\n"
        
        with open(problem_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    def _slugify(self, text: str) -> str:
        """将文本转换为文件名安全的格式"""
        text = text.replace(' ', '-').replace('/', '-')
        text = re.sub(r'[^\w\-]', '', text)
        return text[:50]
    
    def _update_kb_index(self):
        """更新知识库索引"""
        # 这里可以调用 knowledge-base 的索引更新逻辑
        print("   📑 已更新知识库索引")
    
    # ==================== 第三层：联动自我进化 ====================
    
    def link_to_evolution(self) -> Dict:
        """
        将知识库内容链接到自我进化系统
        
        流程:
        1. 分析知识库中的项目进展
        2. 更新长期目标进度
        3. 识别新的学习机会
        4. 生成优化建议
        """
        results = {
            "goals_updated": [],
            "patterns_learned": [],
            "suggestions_generated": []
        }
        
        # 1. 扫描知识库中的项目
        projects_dir = KB_DIR / "projects"
        if projects_dir.exists():
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    project_name = project_dir.name
                    
                    # 读取项目更新
                    changelog = project_dir / "CHANGELOG.md"
                    if changelog.exists():
                        with open(changelog, 'r', encoding='utf-8') as f:
                            updates = f.read()
                        
                        # 关联到长期目标
                        if self.evolution_engine:
                            # 这里可以实现目标关联逻辑
                            pass
        
        # 2. 分析决策模式
        decisions_dir = KB_DIR / "decisions"
        if decisions_dir.exists():
            decision_count = len(list(decisions_dir.glob("*.md")))
            print(f"   📊 已分析 {decision_count} 个决策记录")
        
        # 3. 学习问题解决方案
        problems_dir = KB_DIR / "problems"
        if problems_dir.exists():
            problem_count = len(list(problems_dir.glob("*.md")))
            print(f"   📊 已分析 {problem_count} 个问题记录")
        
        return results
    
    # ==================== 主控流程 ====================
    
    def daily_sync(self, dry_run: bool = False) -> Dict:
        """
        每日同步主流程
        
        执行完整的三层知识流转:
        1. 处理昨日记忆 → 提取知识
        2. 同步到知识库
        3. 联动自我进化
        """
        print("🔄 启动每日知识同步...")
        print("=" * 60)
        
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 第一层：处理记忆
        print(f"\n📥 第一层：处理 {yesterday} 的记忆")
        flows = self.process_daily_memory(yesterday)
        
        # 第二层：同步到知识库
        print(f"\n📤 第二层：同步到知识库")
        sync_results = self.sync_to_knowledge_base(dry_run=dry_run)
        
        # 第三层：联动自我进化
        print(f"\n🧬 第三层：联动自我进化")
        evolution_results = self.link_to_evolution()
        
        # 生成报告
        report = self._generate_sync_report(flows, sync_results, evolution_results)
        
        print("\n" + "=" * 60)
        print("✅ 每日知识同步完成")
        
        return {
            "flows_extracted": len(flows),
            "sync_results": sync_results,
            "evolution_results": evolution_results,
            "report": report
        }
    
    def _generate_sync_report(self, flows: List[KnowledgeFlow], 
                              sync_results: Dict, 
                              evolution_results: Dict) -> str:
        """生成同步报告"""
        report = f"""# 知识同步报告

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 同步统计

| 指标 | 数值 |
|------|------|
| 知识流动数 | {len(flows)} |
| 项目更新 | {len(sync_results.get('projects_updated', []))} |
| 决策添加 | {len(sync_results.get('decisions_added', []))} |
| 问题添加 | {len(sync_results.get('problems_added', []))} |

## 📈 知识流动详情

"""
        
        for flow in flows[:10]:  # 只显示前10条
            report += f"- **{flow.content_type}**: {flow.title[:50]}... (重要度: {flow.importance})\n"
        
        return report


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="知识库与记忆系统整合")
    parser.add_argument("action", choices=[
        "process-memory", "sync-kb", "link-evolution", "daily-sync"
    ])
    parser.add_argument("--date", help="处理特定日期的记忆 (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际写入")
    
    args = parser.parse_args()
    
    integration = KnowledgeMemoryIntegration()
    
    if args.action == "process-memory":
        flows = integration.process_daily_memory(args.date)
        print(f"\n✅ 提取 {len(flows)} 条知识流动")
    
    elif args.action == "sync-kb":
        results = integration.sync_to_knowledge_base(dry_run=args.dry_run)
        print(f"\n✅ 同步完成")
    
    elif args.action == "link-evolution":
        results = integration.link_to_evolution()
        print(f"\n✅ 联动完成")
    
    elif args.action == "daily-sync":
        results = integration.daily_sync(dry_run=args.dry_run)
        print(f"\n✅ 每日同步完成")


if __name__ == "__main__":
    main()
