#!/usr/bin/env python3
"""
技能包自动更新系统 - 检查、测试、更新技能包
"""

import os
import subprocess
import json
from datetime import datetime
from typing import Dict, List

def check_skill_updates() -> List[Dict]:
    """检查技能包更新（本地Git状态）"""
    skills_dir = os.path.expanduser("~/.openclaw/workspace/skills")
    updates = []
    
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_path):
            continue
        
        # 检查Git状态
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=skill_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                updates.append({
                    'name': skill_name,
                    'path': skill_path,
                    'changes': result.stdout.strip().split('\n'),
                    'has_changes': True
                })
        except:
            pass
    
    return updates

def test_skill(skill_path: str) -> bool:
    """测试技能包是否正常"""
    # 检查SKILL.md存在
    skill_md = os.path.join(skill_path, 'SKILL.md')
    if not os.path.exists(skill_md):
        return False
    
    # 尝试读取技能描述
    try:
        with open(skill_md, 'r') as f:
            content = f.read()
            return 'name:' in content and 'description:' in content
    except:
        return False

def backup_skill(skill_path: str) -> str:
    """备份技能包"""
    skill_name = os.path.basename(skill_path)
    backup_dir = os.path.expanduser(f"~/.openclaw/workspace/.skill-backups/{skill_name}")
    
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{backup_dir}/backup_{timestamp}.tar.gz"
    
    subprocess.run(
        ['tar', '-czf', backup_path, '-C', os.path.dirname(skill_path), skill_name],
        capture_output=True
    )
    
    return backup_path

def update_skill(skill_path: str) -> bool:
    """更新技能包（提交Git）"""
    try:
        # 备份
        backup_path = backup_skill(skill_path)
        print(f"  ✅ 已备份: {backup_path}")
        
        # 提交更改
        subprocess.run(['git', 'add', '.'], cwd=skill_path, check=True)
        subprocess.run(
            ['git', 'commit', '-m', f'auto-update: {datetime.now().strftime("%Y-%m-%d")}'],
            cwd=skill_path,
            capture_output=True
        )
        
        return True
    except Exception as e:
        print(f"  ❌ 更新失败: {e}")
        return False

def auto_maintain_skills():
    """自动维护所有技能包"""
    print("🔍 检查技能包状态...\n")
    
    skills_dir = os.path.expanduser("~/.openclaw/workspace/skills")
    
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_path):
            continue
        
        print(f"📦 {skill_name}")
        
        # 测试
        if test_skill(skill_path):
            print(f"  ✅ 功能正常")
        else:
            print(f"  ⚠️  缺少SKILL.md或格式错误")
        
        # 检查Git状态
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=skill_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                print(f"  📝 有未提交更改")
        except:
            print(f"  ⚠️  非Git仓库")
    
    print("\n✅ 技能包检查完成")

def generate_skill_index():
    """生成技能包索引"""
    skills_dir = os.path.expanduser("~/.openclaw/workspace/skills")
    index = []
    
    for skill_name in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_path):
            continue
        
        skill_md = os.path.join(skill_path, 'SKILL.md')
        if os.path.exists(skill_md):
            try:
                with open(skill_md, 'r') as f:
                    content = f.read()
                    # 提取描述
                    desc_match = content.split('description:')[1].split('\n')[0] if 'description:' in content else 'N/A'
                    index.append({
                        'name': skill_name,
                        'description': desc_match.strip(),
                        'path': skill_path
                    })
            except:
                pass
    
    # 保存索引
    index_path = os.path.expanduser("~/.openclaw/workspace/.skill-index.json")
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"✅ 技能包索引已生成: {len(index)}个技能包")
    return index

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 skill_auto_updater.py check      # 检查更新")
        print("  python3 skill_auto_updater.py maintain   # 自动维护")
        print("  python3 skill_auto_updater.py index      # 生成索引")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'check':
        updates = check_skill_updates()
        if updates:
            print(f"发现 {len(updates)} 个技能包有更改:")
            for u in updates:
                print(f"  - {u['name']}: {len(u['changes'])} 处更改")
        else:
            print("✅ 所有技能包已是最新")
    elif cmd == 'maintain':
        auto_maintain_skills()
    elif cmd == 'index':
        generate_skill_index()
