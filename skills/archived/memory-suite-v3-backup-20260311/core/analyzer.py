#!/usr/bin/env python3
"""
Memory Suite v3.0 - 分析引擎模块
负责记忆数据的统计分析和报告生成
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('analyzer')

# 路径配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
SUMMARY_DIR = MEMORY_DIR / "summary"
PERMANENT_DIR = MEMORY_DIR / "permanent"
KB_DIR = WORKSPACE / "knowledge-base"

# 停用词
STOP_WORDS = {
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'http', 'https', 'com', '文件', '可以', '使用', '进行', '需要', '已经', '完成', '添加', '通过', '如果', '然后', '今天', '现在', '开始'
}

# 主题映射
TOPIC_MAPPING = {
    "储能项目": ["储能", "电站", "光伏", "锂电池", "PCS", "BMS", "容量", "充放电"],
    "股票分析": ["股票", "股市", "K 线", "均线", "RSI", "MACD", "涨停", "跌停"],
    "零碳园区": ["零碳", "园区", "碳中和", "多能互补", "微网", "绿电"],
    "技能包开发": ["技能包", "SKILL", "OpenClaw", "API", "模块", "Agent"],
    "记忆管理": ["记忆", "MEMORY", "知识库", "备份", "归档", "索引"],
    "系统运维": ["服务器", "部署", "备份", "日志", "监控", "nginx"],
    "项目测算": ["测算", "财务", "IRR", "NPV", "收益", "投资"],
}


class AnalysisManager:
    """分析管理器"""
    
    def __init__(self):
        self.summary_dir = SUMMARY_DIR
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保目录存在"""
        for d in [SUMMARY_DIR, PERMANENT_DIR]:
            d.mkdir(parents=True, exist_ok=True)
    
    def extract_keywords(self, text: str, top_n: int = 30) -> List[Tuple[str, int]]:
        """提取关键词"""
        words = []
        
        # 中文词
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
        words.extend(chinese)
        
        # 英文词
        english = re.findall(r'[a-zA-Z_]{3,}', text)
        words.extend([w.lower() for w in english])
        
        # 过滤
        filtered = [w for w in words if w not in STOP_WORDS and len(w) >= 2]
        counts = Counter(filtered)
        return counts.most_common(top_n)
    
    def extract_topics(self, keywords: List[Tuple[str, int]]) -> Dict[str, int]:
        """
        从关键词提取主题
        
        Args:
            keywords: 关键词列表
        
        Returns:
            主题计数字典
        """
        topics = {}
        
        for topic, topic_keywords in TOPIC_MAPPING.items():
            count = sum(
                count for kw, count in keywords 
                if any(tk in kw for tk in topic_keywords)
            )
            if count > 0:
                topics[topic] = count
        
        return topics
    
    def analyze_period(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        分析指定时间段的记忆
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            分析结果
        """
        logger.info(f"分析时间段: {start_date.date()} ~ {end_date.date()}")
        
        # 获取时间段内的文件
        files = []
        for f in MEMORY_DIR.glob("*.md"):
            try:
                file_date = datetime.strptime(f.stem, "%Y-%m-%d")
                if start_date <= file_date <= end_date:
                    files.append(f)
            except ValueError:
                continue
        
        if not files:
            logger.warning(f"没有找到记忆文件")
            return {"error": "no_files"}
        
        # 读取所有内容
        all_text = ""
        for f in files:
            with open(f, 'r', encoding='utf-8') as fp:
                all_text += fp.read() + "\n"
        
        # 分析
        keywords = self.extract_keywords(all_text, top_n=50)
        topics = self.extract_topics(keywords)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "files": len(files),
            "total_chars": len(all_text),
            "keywords": keywords,
            "topics": topics
        }
    
    def generate_daily_report(self, date: Optional[str] = None) -> Optional[str]:
        """
        生成日报
        
        Args:
            date: 日期字符串，默认昨天
        
        Returns:
            报告文件路径
        """
        if date:
            report_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            report_date = datetime.now() - timedelta(days=1)
        
        logger.info(f"生成日报: {report_date.date()}")
        
        # 分析当天
        result = self.analyze_period(report_date, report_date)
        
        if "error" in result:
            return None
        
        # 生成报告
        report_file = self.summary_dir / f"daily_{report_date.strftime('%Y%m%d')}.md"
        
        content = self._format_daily_report(report_date, result)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"日报已生成: {report_file}")
        return str(report_file)
    
    def generate_weekly_report(self, week_start: Optional[str] = None) -> Optional[str]:
        """
        生成周报
        
        Args:
            week_start: 周开始日期，默认上周一
        
        Returns:
            报告文件路径
        """
        if week_start:
            start = datetime.strptime(week_start, "%Y-%m-%d")
        else:
            # 上周一
            today = datetime.now()
            start = today - timedelta(days=today.weekday() + 7)
        
        end = start + timedelta(days=6)
        
        logger.info(f"生成周报: {start.date()} ~ {end.date()}")
        
        result = self.analyze_period(start, end)
        
        if "error" in result:
            return None
        
        report_file = self.summary_dir / f"weekly_{start.strftime('%Y%m%d')}.md"
        content = self._format_weekly_report(start, end, result)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"周报已生成: {report_file}")
        return str(report_file)
    
    def generate_monthly_report(self, month: Optional[str] = None) -> Optional[str]:
        """
        生成月报
        
        Args:
            month: 月份字符串 (YYYY-MM)，默认上月
        
        Returns:
            报告文件路径
        """
        if month:
            year, mon = map(int, month.split('-'))
            start = datetime(year, mon, 1)
        else:
            # 上月
            today = datetime.now()
            if today.month == 1:
                start = datetime(today.year - 1, 12, 1)
            else:
                start = datetime(today.year, today.month - 1, 1)
        
        # 月末
        if start.month == 12:
            end = datetime(start.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(start.year, start.month + 1, 1) - timedelta(days=1)
        
        logger.info(f"生成月报: {start.strftime('%Y-%m')}")
        
        result = self.analyze_period(start, end)
        
        if "error" in result:
            return None
        
        report_file = self.summary_dir / f"monthly_{start.strftime('%Y%m')}.md"
        content = self._format_monthly_report(start, result)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 同步到知识库
        self._sync_to_kb(start.strftime('%Y-%m'), result)
        
        logger.info(f"月报已生成: {report_file}")
        return str(report_file)
    
    def _format_daily_report(self, date: datetime, result: Dict) -> str:
        """格式化日报"""
        keywords = result.get('keywords', [])
        topics = result.get('topics', {})
        
        content = f"""# {date.strftime('%Y-%m-%d')} 每日记忆报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 统计

- **文件数**: {result['files']} 个
- **字符数**: {result['total_chars']:,} 字符
- **关键词**: {len(keywords)} 个

## 🔑 高频关键词 TOP10

"""
        for i, (word, count) in enumerate(keywords[:10], 1):
            bar = "█" * min(count, 15)
            content += f"{i}. **{word}** - {count}次 {bar}\n"
        
        content += "\n## 📁 主题分布\n\n"
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * min(count, 10)
            content += f"- **{topic}**: {count}次 {bar}\n"
        
        if not topics:
            content += "*暂无明显主题*\n"
        
        content += "\n---\n*由 Memory Suite v3.0 自动生成*\n"
        
        return content
    
    def _format_weekly_report(self, start: datetime, end: datetime, result: Dict) -> str:
        """格式化周报"""
        keywords = result.get('keywords', [])
        topics = result.get('topics', {})
        
        content = f"""# {start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')} 周报

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 统计

- **天数**: {result['period']['days']} 天
- **文件数**: {result['files']} 个
- **字符数**: {result['total_chars']:,} 字符

## 🔑 高频关键词 TOP15

"""
        for i, (word, count) in enumerate(keywords[:15], 1):
            bar = "█" * min(count, 15)
            content += f"{i}. **{word}** - {count}次 {bar}\n"
        
        content += "\n## 📁 主题分布\n\n"
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / sum(topics.values())) * 100 if topics else 0
            bar = "█" * int(percentage / 5)
            content += f"- **{topic}**: {count}次 ({percentage:.1f}%) {bar}\n"
        
        content += "\n---\n*由 Memory Suite v3.0 自动生成*\n"
        
        return content
    
    def _format_monthly_report(self, month_start: datetime, result: Dict) -> str:
        """格式化月报"""
        keywords = result.get('keywords', [])
        topics = result.get('topics', {})
        month_str = month_start.strftime('%Y-%m')
        
        content = f"""# {month_str} 月度记忆报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 统计概览

- **天数**: {result['period']['days']} 天
- **文件数**: {result['files']} 个
- **字符数**: {result['total_chars']:,} 字符
- **关键词**: {len(keywords)} 个

## 🔑 高频关键词 TOP20

"""
        for i, (word, count) in enumerate(keywords[:20], 1):
            bar = "█" * min(count, 20)
            content += f"{i}. **{word}** - {count}次 {bar}\n"
        
        content += "\n## 📁 主题分布\n\n"
        total_topic_count = sum(topics.values()) if topics else 1
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_topic_count) * 100
            bar = "█" * int(percentage / 5)
            content += f"- **{topic}**: {count}次 ({percentage:.1f}%) {bar}\n"
        
        if not topics:
            content += "*暂无明显主题*\n"
        
        content += "\n## 📈 趋势分析\n\n"
        content += "*趋势分析需要多个月度数据对比，待实现*\n"
        
        content += "\n---\n*由 Memory Suite v3.0 自动生成*\n"
        
        return content
    
    def _sync_to_kb(self, month_str: str, result: Dict):
        """同步到知识库"""
        kb_index = KB_DIR / "INDEX.md"
        if not kb_index.exists():
            return
        
        try:
            with open(kb_index, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 避免重复
            if f"{month_str}月度高频" in content:
                return
            
            keywords = result.get('keywords', [])
            topics = result.get('topics', {})
            
            top_kw = [kw for kw, _ in keywords[:5]]
            top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
            
            entry = f"""\n### {month_str}月度高频主题与关键词\n\n**高频关键词**: {', '.join(top_kw)}\n\n**核心主题**:\n"""
            for topic, count in top_topics:
                entry += f"- {topic} ({count}次)\n"
            entry += f"\n**来源**: [月度摘要](memory/summary/monthly_{month_str.replace('-', '')}.md)\n\n"
            
            if "## 统计信息" in content:
                content = content.replace("## 统计信息", entry + "## 统计信息")
            else:
                content += "\n## 统计信息\n" + entry
            
            with open(kb_index, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"知识库已同步: {month_str}")
            
        except Exception as e:
            logger.error(f"同步知识库失败: {e}")


def main():
    """测试入口"""
    manager = AnalysisManager()
    
    print("📊 分析引擎模块测试")
    print("=" * 50)
    
    # 测试月报
    print("\n1. 生成月报...")
    report = manager.generate_monthly_report()
    if report:
        print(f"✅ 月报已生成: {report}")
    else:
        print("❌ 月报生成失败")
    
    # 测试周报
    print("\n2. 生成周报...")
    report = manager.generate_weekly_report()
    if report:
        print(f"✅ 周报已生成: {report}")
    else:
        print("❌ 周报生成失败")
    
    # 测试日报
    print("\n3. 生成日报...")
    report = manager.generate_daily_report()
    if report:
        print(f"✅ 日报已生成: {report}")
    else:
        print("❌ 日报生成失败")
    
    print("\n" + "=" * 50)


if __name__ == '__main__':
    main()
