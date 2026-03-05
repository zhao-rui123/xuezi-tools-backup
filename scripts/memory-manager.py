#!/usr/bin/env python3
"""
Memory Manager - 每日记忆自动整理脚本
方案A：程序化量化管理记忆文件
"""

import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
ARCHIVE_DIR = MEMORY_DIR / "archive"
SUMMARY_DIR = WORKSPACE / "summary" / "daily"

def ensure_dirs():
    """确保目录存在"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

def get_today_memory_file():
    """获取今日记忆文件路径"""
    today = datetime.now().strftime("%Y-%m-%d")
    return MEMORY_DIR / f"{today}.md"

def read_memory_file(filepath):
    """读取记忆文件内容"""
    if not filepath.exists():
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_key_info(content):
    """提取关键信息"""
    info = {
        'decisions': [],
        'todos': [],
        'projects': [],
        'data': [],
        'general': []
    }
    
    # 简单提取逻辑（可根据需要增强）
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 识别决策
        if any(kw in line.lower() for kw in ['决定', '确定', '采用', '选择', '方案']):
            info['decisions'].append(line)
        # 识别待办
        elif any(kw in line.lower() for kw in ['todo', '待办', '需要', '准备', '计划']):
            info['todos'].append(line)
        # 识别项目
        elif any(kw in line.lower() for kw in ['项目', '储能', '网站', '工具']):
            info['projects'].append(line)
        # 识别数据
        elif any(kw in line.lower() for kw in ['万', '%', '金额', '收益', '成本']):
            info['data'].append(line)
        else:
            info['general'].append(line)
    
    return info

def update_memory_md(info):
    """更新长期记忆文件"""
    memory_md = WORKSPACE / "MEMORY.md"
    
    # 读取现有内容
    existing_content = ""
    if memory_md.exists():
        with open(memory_md, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # 生成更新内容
    today = datetime.now().strftime("%Y-%m-%d")
    update_section = f"\n\n## 记忆更新 [{today}]\n\n"
    
    if info['decisions']:
        update_section += "### [DECISION] 重要决策\n"
        for item in info['decisions'][:5]:  # 最多5条
            update_section += f"- {item}\n"
        update_section += "\n"
    
    if info['todos']:
        update_section += "### [TODO] 待办事项\n"
        for item in info['todos'][:5]:
            update_section += f"- [ ] {item}\n"
        update_section += "\n"
    
    if info['projects']:
        update_section += "### [PROJECT] 项目进展\n"
        for item in info['projects'][:5]:
            update_section += f"- {item}\n"
        update_section += "\n"
    
    if info['data']:
        update_section += "### [DATA] 关键数据\n"
        for item in info['data'][:5]:
            update_section += f"- {item}\n"
        update_section += "\n"
    
    # 追加到文件
    with open(memory_md, 'a', encoding='utf-8') as f:
        f.write(update_section)
    
    print(f"✅ 已更新 MEMORY.md")

def generate_daily_summary(info, original_content):
    """生成每日摘要"""
    today = datetime.now().strftime("%Y-%m-%d")
    summary_file = SUMMARY_DIR / f"{today}-summary.md"
    
    summary = f"""# 每日摘要 - {today}

## 生成时间
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 今日关键信息统计
- 重要决策: {len(info['decisions'])} 条
- 待办事项: {len(info['todos'])} 条
- 项目相关: {len(info['projects'])} 条
- 关键数据: {len(info['data'])} 条

## 详细内容

### 重要决策
"""
    
    if info['decisions']:
        for item in info['decisions']:
            summary += f"- {item}\n"
    else:
        summary += "无\n"
    
    summary += "\n### 待办事项\n"
    if info['todos']:
        for item in info['todos']:
            summary += f"- [ ] {item}\n"
    else:
        summary += "无\n"
    
    summary += "\n### 原始记录\n```\n"
    summary += original_content[:2000]  # 前2000字符
    summary += "\n```\n"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✅ 已生成摘要: {summary_file}")

def archive_old_memories():
    """归档7天前的记忆文件"""
    cutoff_date = datetime.now() - timedelta(days=7)
    
    for mem_file in MEMORY_DIR.glob("*.md"):
        if mem_file.name == "archive":
            continue
        
        # 尝试解析日期
        try:
            file_date = datetime.strptime(mem_file.stem, "%Y-%m-%d")
            if file_date < cutoff_date:
                dest = ARCHIVE_DIR / mem_file.name
                shutil.move(str(mem_file), str(dest))
                print(f"📦 已归档: {mem_file.name}")
        except ValueError:
            pass  # 不是日期格式的文件跳过

def main():
    """主函数"""
    print("=" * 50)
    print("Memory Manager - 每日记忆整理")
    print("=" * 50)
    
    ensure_dirs()
    
    # 1. 读取今日记忆
    today_file = get_today_memory_file()
    content = read_memory_file(today_file)
    
    if not content:
        print(f"⚠️ 今日记忆文件不存在: {today_file}")
        return
    
    print(f"📖 读取记忆文件: {today_file}")
    
    # 2. 提取关键信息
    info = extract_key_info(content)
    print(f"📊 提取信息: {sum(len(v) for v in info.values())} 条")
    
    # 3. 更新长期记忆
    update_memory_md(info)
    
    # 4. 生成摘要
    generate_daily_summary(info, content)
    
    # 5. 归档旧记忆
    archive_old_memories()
    
    print("=" * 50)
    print("✅ 记忆整理完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
