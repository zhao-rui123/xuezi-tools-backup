#!/usr/bin/env python3
"""
记忆智能筛选系统
自动分析记忆文件，提取高频关键词和主题，生成永久记忆
"""

import os
import re
import json
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path

# 配置
MEMORY_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
OUTPUT_DIR = Path("/Users/zhaoruicn/.openclaw/workspace/memory")
PERMANENT_DIR = OUTPUT_DIR / "permanent"
SUMMARY_DIR = OUTPUT_DIR / "summary"
INDEX_DIR = OUTPUT_DIR / "index"

# 确保目录存在
PERMANENT_DIR.mkdir(exist_ok=True)
SUMMARY_DIR.mkdir(exist_ok=True)
INDEX_DIR.mkdir(exist_ok=True)

# 停用词列表（中文）
STOP_WORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那',
    # 英文停用词
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    # 技术词汇停用词
    'http', 'https', 'com', '文件', '可以', '使用', '进行', '需要', '已经', '完成', '添加', '通过', '如果', '然后', '今天', '现在', '开始'
])


def extract_keywords(text, top_n=20):
    """提取关键词"""
    # 简单的中文分词（基于字符和常用词）
    words = []
    
    # 匹配中文字符串（2-6个字）
    chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,6}', text)
    words.extend(chinese_words)
    
    # 匹配英文单词
    english_words = re.findall(r'[a-zA-Z_]{3,}', text)
    words.extend([w.lower() for w in english_words])
    
    # 过滤停用词和短词
    filtered_words = [w for w in words if w not in STOP_WORDS and len(w) >= 2]
    
    # 统计词频
    word_counts = Counter(filtered_words)
    
    # 返回前N个关键词
    return word_counts.most_common(top_n)


def extract_topics(text, keywords):
    """基于关键词提取主题"""
    topics = {}
    
    # 定义主题关键词映射
    topic_mapping = {
        "储能项目": ["储能", "电站", "光伏", "锂电池", "PCS", "BMS", "EMS"],
        "股票分析": ["股票", "股市", "K线", "均线", "RSI", "MACD", "估值"],
        "零碳园区": ["零碳", "园区", "碳中和", "多能互补", "微网", "碳资产"],
        "技能包开发": ["技能包", "SKILL", "OpenClaw", "API", "脚本"],
        "记忆管理": ["记忆", "MEMORY", "知识库", "备份", "存档"],
        "系统运维": ["服务器", "部署", "备份", "日志", "监控", "故障"],
        "飞书集成": ["飞书", "Feishu", "推送", "消息", "Webhook"],
        "项目测算": ["测算", "IRR", "NPV", "投资", "收益", "ROI"],
        "小龙虾之家": ["小龙虾", "看板", "可视化", "像素", "房间"],
        "战略规划": ["战略", "规划", "目标", "里程碑", "十五五", "能力建设"]
    }
    
    # 统计每个主题的出现次数
    for topic, topic_keywords in topic_mapping.items():
        count = sum(1 for kw, _ in keywords if any(tkw in kw for tkw in topic_keywords))
        if count > 0:
            topics[topic] = count
    
    return topics


def get_memory_files(days=30):
    """获取最近N天的记忆文件"""
    files = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for file_path in MEMORY_DIR.glob("*.md"):
        # 从文件名提取日期 (YYYY-MM-DD.md)
        try:
            date_str = file_path.stem
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date >= cutoff_date:
                files.append(file_path)
        except:
            continue
    
    return sorted(files)


def analyze_memory_files(files):
    """分析记忆文件"""
    all_text = ""
    file_count = len(files)
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_text += f.read() + "\n"
        except:
            continue
    
    # 提取关键词
    keywords = extract_keywords(all_text, top_n=30)
    
    # 提取主题
    topics = extract_topics(all_text, keywords)
    
    return {
        "file_count": file_count,
        "keywords": keywords,
        "topics": topics,
        "total_chars": len(all_text)
    }


def generate_summary(analysis_result, month_str):
    """生成月度记忆摘要"""
    summary_file = SUMMARY_DIR / f"{month_str}-summary.md"
    
    content = f"""# {month_str} 月度记忆摘要

> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 统计信息

- **分析文件数**: {analysis_result['file_count']} 个
- **总字符数**: {analysis_result['total_chars']:,} 字符
- **关键词数**: {len(analysis_result['keywords'])} 个

---

## 🔑 高频关键词

"""
    
    # 添加关键词列表
    for i, (word, count) in enumerate(analysis_result['keywords'][:15], 1):
        bar = "█" * min(count, 20)
        content += f"{i}. **{word}** - {count}次 {bar}\n"
    
    content += """
---

## 📁 主题分布

"""
    
    # 添加主题分布
    sorted_topics = sorted(analysis_result['topics'].items(), key=lambda x: x[1], reverse=True)
    for topic, count in sorted_topics[:10]:
        bar = "█" * min(count, 15)
        content += f"- **{topic}**: {count}次 {bar}\n"
    
    content += """
---

## 💾 永久记忆建议

基于本月高频主题，建议永久保存以下内容：

"""
    
    # 根据主题生成建议
    if sorted_topics:
        top_topic = sorted_topics[0][0]
        content += f"1. **{top_topic}** - 本月核心工作方向，建议整理成专题文档\n"
    
    if len(sorted_topics) > 1:
        content += f"2. **{sorted_topics[1][0]}** - 次要但重要的工作领域\n"
    
    content += """
3. **关键决策** - 本月做出的重要决策和方案
4. **技术突破** - 解决的关键技术问题
5. **项目里程碑** - 完成的重要项目节点

---

*本摘要由记忆智能筛选系统自动生成*
"""
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return summary_file


def update_index(analysis_result, month_str):
    """更新记忆索引"""
    # 更新关键词索引
    keywords_file = INDEX_DIR / "keywords.json"
    
    keywords_data = {}
    if keywords_file.exists():
        with open(keywords_file, 'r', encoding='utf-8') as f:
            keywords_data = json.load(f)
    
    keywords_data[month_str] = {
        "date": datetime.now().isoformat(),
        "keywords": analysis_result['keywords'][:20]
    }
    
    with open(keywords_file, 'w', encoding='utf-8') as f:
        json.dump(keywords_data, f, ensure_ascii=False, indent=2)
    
    # 更新主题索引
    themes_file = INDEX_DIR / "themes.json"
    
    themes_data = {}
    if themes_file.exists():
        with open(themes_file, 'r', encoding='utf-8') as f:
            themes_data = json.load(f)
    
    themes_data[month_str] = {
        "date": datetime.now().isoformat(),
        "themes": analysis_result['topics']
    }
    
    with open(themes_file, 'w', encoding='utf-8') as f:
        json.dump(themes_data, f, ensure_ascii=False, indent=2)


def update_knowledge_base(analysis_result, month_str):
    """更新知识库索引，添加高频关键词和主题"""
    kb_index_file = Path("/Users/zhaoruicn/.openclaw/workspace/knowledge-base/INDEX.md")
    
    if not kb_index_file.exists():
        print(f"⚠️ 知识库索引不存在，跳过更新")
        return
    
    # 读取现有内容
    with open(kb_index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 准备要添加的内容
    top_keywords = [kw for kw, _ in analysis_result['keywords'][:10]]
    top_themes = sorted(analysis_result['topics'].items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 检查是否已存在该月的记录
    if f"{month_str}月度高频" in content:
        print(f"ℹ️ 知识库已存在 {month_str} 的记录，跳过")
        return
    
    # 构建要插入的内容
    kb_entry = f"""
### {month_str}月度高频主题与关键词

**高频关键词**: {', '.join(top_keywords[:5])}

**核心主题**:
"""
    for theme, count in top_themes:
        kb_entry += f"- {theme} ({count}次)\n"
    
    kb_entry += f"\n**来源**: [月度摘要](memory/summary/{month_str}-summary.md) | [永久记忆](memory/permanent/{month_str}-permanent.md)\n"
    
    # 在## 统计信息之前插入
    if "## 统计信息" in content:
        content = content.replace("## 统计信息", kb_entry + "\n## 统计信息")
    else:
        # 在文件末尾添加
        content += "\n" + kb_entry
    
    # 写回文件
    with open(kb_index_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📚 知识库索引已更新: {kb_index_file}")


def generate_permanent_memory(analysis_result, month_str):
    """生成永久记忆"""
    # 找出最重要的3个主题
    sorted_topics = sorted(analysis_result['topics'].items(), key=lambda x: x[1], reverse=True)
    top_topics = sorted_topics[:3]
    
    if not top_topics:
        return None
    
    permanent_file = PERMANENT_DIR / f"{month_str}-permanent.md"
    
    content = f"""# {month_str} 永久记忆存档

> 从月度记忆分析中提取的核心内容

## 📌 本月核心主题

"""
    
    for i, (topic, count) in enumerate(top_topics, 1):
        content += f"""### {i}. {topic}

**出现次数**: {count} 次

**相关关键词**: 
"""
        # 找出与这个主题相关的关键词
        topic_keywords = []
        for kw, kw_count in analysis_result['keywords'][:20]:
            if any(tkw in kw for tkw in [topic]):
                topic_keywords.append(kw)
        
        if topic_keywords:
            content += ", ".join(topic_keywords[:5])
        else:
            content += "详见月度记忆摘要"
        
        content += "\n\n"
    
    content += f"""---

## 🔍 快速检索

**关键词索引**: [查看完整索引]({INDEX_DIR}/keywords.json)

**主题索引**: [查看完整索引]({INDEX_DIR}/themes.json)

**月度摘要**: [查看摘要]({SUMMARY_DIR}/{month_str}-summary.md)

---

*存档时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(permanent_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return permanent_file


def main():
    """主函数"""
    print("🧠 记忆智能筛选系统启动...")
    
    # 获取上个月的月份字符串
    today = datetime.now()
    if today.day < 5:  # 如果是月初，分析上个月
        target_month = today - timedelta(days=10)
    else:
        target_month = today
    
    month_str = target_month.strftime("%Y-%m")
    
    print(f"📅 分析月份: {month_str}")
    
    # 获取记忆文件
    files = get_memory_files(days=35)  # 获取最近35天，确保覆盖整个月
    
    if not files:
        print("⚠️ 没有找到记忆文件")
        return
    
    print(f"📁 找到 {len(files)} 个记忆文件")
    
    # 分析记忆
    analysis_result = analyze_memory_files(files)
    
    print(f"✅ 分析完成")
    print(f"   - 关键词: {len(analysis_result['keywords'])} 个")
    print(f"   - 主题: {len(analysis_result['topics'])} 个")
    
    # 生成摘要
    summary_file = generate_summary(analysis_result, month_str)
    print(f"📝 月度摘要: {summary_file}")
    
    # 更新索引
    update_index(analysis_result, month_str)
    print(f"📇 索引已更新")
    
    # 生成永久记忆
    permanent_file = generate_permanent_memory(analysis_result, month_str)
    if permanent_file:
        print(f"💾 永久记忆: {permanent_file}")
    
    # 更新知识库
    update_knowledge_base(analysis_result, month_str)
    
    print("✨ 记忆智能筛选完成!")
    
    # 输出关键信息
    print("\n📊 本月重点:")
    if analysis_result['keywords']:
        print(f"   关键词: {analysis_result['keywords'][0][0]} ({analysis_result['keywords'][0][1]}次)")
    if analysis_result['topics']:
        top_topic = max(analysis_result['topics'].items(), key=lambda x: x[1])
        print(f"   主题: {top_topic[0]} ({top_topic[1]}次)")


if __name__ == "__main__":
    main()
