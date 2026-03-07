#!/usr/bin/env python3
"""
技能搜索助手 - 自动搜索和推荐ClawHub技能包
"""

import subprocess
import json
from typing import List, Dict

def search_clawhub(query: str, limit: int = 10) -> List[Dict]:
    """搜索ClawHub技能包"""
    try:
        result = subprocess.run(
            ['clawhub', 'search', query],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return []
        
        # 解析输出
        skills = []
        for line in result.stdout.strip().split('\n'):
            # 格式: skill-name  Description  (rating)
            parts = line.split('  ')
            if len(parts) >= 2:
                name = parts[0].strip()
                desc = parts[1].strip() if len(parts) > 1 else ''
                rating = parts[2].strip() if len(parts) > 2 else '(0.0)'
                
                skills.append({
                    'name': name,
                    'description': desc,
                    'rating': rating
                })
        
        return skills[:limit]
        
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

def get_skill_info(skill_name: str) -> Dict:
    """获取技能包详细信息"""
    try:
        result = subprocess.run(
            ['clawhub', 'info', skill_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            'name': skill_name,
            'info': result.stdout if result.returncode == 0 else result.stderr
        }
    except Exception as e:
        return {'name': skill_name, 'error': str(e)}

def recommend_skills(need: str) -> str:
    """根据需求推荐技能包"""
    # 关键词映射
    keyword_map = {
        '股票': ['stock', 'finance', 'market'],
        '天气': ['weather', 'forecast'],
        '搜索': ['search', 'tavily', 'web'],
        'GitHub': ['github', 'git'],
        '文档': ['doc', 'pdf', 'office'],
        '备份': ['backup', 'sync'],
        '提醒': ['alert', 'notify', 'remind'],
        '数据': ['data', 'csv', 'excel'],
    }
    
    # 找到匹配的关键词
    search_terms = []
    for key, terms in keyword_map.items():
        if key in need:
            search_terms.extend(terms)
    
    if not search_terms:
        search_terms = [need]
    
    # 搜索所有匹配的技能
    all_skills = []
    for term in search_terms[:3]:  # 最多搜索3个关键词
        skills = search_clawhub(term, limit=5)
        all_skills.extend(skills)
    
    # 去重并排序
    seen = set()
    unique_skills = []
    for s in all_skills:
        if s['name'] not in seen:
            seen.add(s['name'])
            unique_skills.append(s)
    
    # 格式化输出
    lines = [
        f"\n{'='*70}",
        f"🔍 技能包推荐: {need}",
        f"{'='*70}",
        f"",
    ]
    
    if not unique_skills:
        lines.append("❌ 未找到匹配的技能包")
    else:
        lines.append(f"找到 {len(unique_skills)} 个可能相关的技能包:\n")
        
        for i, s in enumerate(unique_skills[:10], 1):  # 最多显示10个
            lines.append(f"{i}. {s['name']} {s['rating']}")
            lines.append(f"   {s['description']}")
            lines.append(f"")
        
        lines.append(f"💡 安装命令示例:")
        lines.append(f"   clawhub install {unique_skills[0]['name']}")
    
    lines.append(f"{'='*70}")
    return "\n".join(lines)

def list_installed_skills() -> List[str]:
    """列出已安装的技能包"""
    try:
        result = subprocess.run(
            ['clawhub', 'list'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return []
    except:
        return []

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 skill_finder.py '股票分析'     # 搜索技能")
        print("  python3 skill_finder.py search github  # 搜索GitHub相关")
        print("  python3 skill_finder.py list           # 列出已安装")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'search' and len(sys.argv) > 2:
        query = sys.argv[2]
        skills = search_clawhub(query)
        for s in skills[:5]:
            print(f"{s['name']} - {s['description']} {s['rating']}")
    elif cmd == 'list':
        installed = list_installed_skills()
        print(f"已安装 {len(installed)} 个技能包:")
        for s in installed:
            print(f"  - {s}")
    else:
        # 推荐模式
        need = ' '.join(sys.argv[1:])
        print(recommend_skills(need))
