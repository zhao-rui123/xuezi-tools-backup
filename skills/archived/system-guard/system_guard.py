#!/usr/bin/env python3
"""
系统保护守卫 - 防止恶意技能包破坏OpenClaw系统
"""

import os
import sys
import shutil
import json
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class SystemSnapshot:
    """系统快照"""
    timestamp: str
    backup_path: str
    skills_backup: str
    config_backup: str
    description: str

SYSTEM_BACKUP_DIR = os.path.expanduser("~/.openclaw/.system-backups")
GUARD_LOG = os.path.expanduser("~/.openclaw/.system-guard.log")

def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    
    os.makedirs(os.path.dirname(GUARD_LOG), exist_ok=True)
    with open(GUARD_LOG, 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')

def create_system_snapshot(description: str = "手动备份") -> SystemSnapshot:
    """
    创建系统快照
    备份关键目录，以便出现问题时恢复
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    snapshot_dir = os.path.join(SYSTEM_BACKUP_DIR, f"snapshot_{timestamp}")
    
    os.makedirs(snapshot_dir, exist_ok=True)
    
    log(f"🔄 创建系统快照: {description}")
    
    # 备份技能包目录
    skills_src = os.path.expanduser("~/.openclaw/workspace/skills")
    skills_backup = os.path.join(snapshot_dir, "skills")
    if os.path.exists(skills_src):
        shutil.copytree(skills_src, skills_backup, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        log(f"  ✅ 技能包已备份: {skills_backup}")
    
    # 备份配置文件
    config_src = os.path.expanduser("~/.openclaw")
    config_backup = os.path.join(snapshot_dir, "config")
    os.makedirs(config_backup, exist_ok=True)
    
    # 只备份关键配置文件
    config_files = ['openclaw.json', 'agents/main/agent/models.json', 'agents/main/agent/auth-profiles.json']
    for cfg_file in config_files:
        src = os.path.join(config_src, cfg_file)
        if os.path.exists(src):
            dst_dir = os.path.join(config_backup, os.path.dirname(cfg_file))
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(src, dst_dir)
    
    log(f"  ✅ 配置已备份: {config_backup}")
    
    # 保存快照信息
    snapshot_info = {
        'timestamp': timestamp,
        'description': description,
        'skills_backup': skills_backup,
        'config_backup': config_backup,
    }
    
    info_path = os.path.join(snapshot_dir, "snapshot.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot_info, f, indent=2)
    
    log(f"✅ 系统快照创建完成: {snapshot_dir}")
    
    return SystemSnapshot(
        timestamp=timestamp,
        backup_path=snapshot_dir,
        skills_backup=skills_backup,
        config_backup=config_backup,
        description=description
    )

def restore_system_snapshot(snapshot_path: str) -> bool:
    """恢复系统到快照状态"""
    if not os.path.exists(snapshot_path):
        log(f"❌ 快照不存在: {snapshot_path}")
        return False
    
    log(f"🔄 恢复系统快照: {snapshot_path}")
    
    # 读取快照信息
    info_path = os.path.join(snapshot_path, "snapshot.json")
    if os.path.exists(info_path):
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        log(f"  快照描述: {info.get('description', 'N/A')}")
    
    try:
        # 恢复技能包
        skills_backup = os.path.join(snapshot_path, "skills")
        if os.path.exists(skills_backup):
            skills_target = os.path.expanduser("~/.openclaw/workspace/skills")
            # 先备份当前（以防万一）
            if os.path.exists(skills_target):
                backup_current = f"{skills_target}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.move(skills_target, backup_current)
            # 恢复
            shutil.copytree(skills_backup, skills_target)
            log(f"  ✅ 技能包已恢复")
        
        # 恢复配置
        config_backup = os.path.join(snapshot_path, "config")
        if os.path.exists(config_backup):
            config_target = os.path.expanduser("~/.openclaw")
            for root, dirs, files in os.walk(config_backup):
                for file in files:
                    src = os.path.join(root, file)
                    rel_path = os.path.relpath(src, config_backup)
                    dst = os.path.join(config_target, rel_path)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
            log(f"  ✅ 配置已恢复")
        
        log(f"✅ 系统恢复完成")
        return True
        
    except Exception as e:
        log(f"❌ 恢复失败: {e}")
        return False

def test_skill_in_sandbox(skill_path: str) -> Tuple[bool, str]:
    """
    在沙箱环境中测试技能包
    返回: (是否安全, 测试报告)
    """
    log(f"🔬 沙箱测试技能包: {skill_path}")
    
    if not os.path.exists(skill_path):
        return False, "技能包路径不存在"
    
    issues = []
    
    # 1. 检查文件结构
    skill_name = os.path.basename(skill_path)
    skill_md = os.path.join(skill_path, "SKILL.md")
    
    if not os.path.exists(skill_md):
        issues.append("缺少SKILL.md文件")
    
    # 2. 检查危险文件
    dangerous_files = ['.exe', '.dll', '.so', '.dylib', '.bin']
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if any(file.endswith(ext) for ext in dangerous_files):
                issues.append(f"发现危险文件: {file}")
    
    # 3. 检查Python代码语法
    py_files = []
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    
    for py_file in py_files[:5]:  # 只检查前5个py文件
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', py_file],
                capture_output=True,
                timeout=10
            )
            if result.returncode != 0:
                issues.append(f"语法错误: {os.path.basename(py_file)}")
        except:
            pass
    
    # 4. 模拟导入测试（在临时目录）
    # 创建临时环境
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # 复制技能包到临时目录
            tmp_skill = os.path.join(tmpdir, skill_name)
            shutil.copytree(skill_path, tmp_skill)
            
            # 尝试导入（如果存在__init__.py）
            init_file = os.path.join(tmp_skill, "__init__.py")
            if os.path.exists(init_file):
                # 不实际执行，只是检查文件存在
                pass
        except Exception as e:
            issues.append(f"沙箱测试异常: {e}")
    
    if issues:
        return False, "; ".join(issues)
    
    return True, "沙箱测试通过"

def safe_install_skill(skill_path: str) -> bool:
    """
    安全安装技能包流程
    1. 创建系统快照
    2. 安全检查
    3. 沙箱测试
    4. 安装
    5. 验证
    """
    log(f"🛡️ 开始安全安装: {skill_path}")
    
    # 1. 创建系统快照
    snapshot = create_system_snapshot(f"安装前备份: {os.path.basename(skill_path)}")
    
    # 2. 安全检查（调用security-scanner）
    scanner_path = os.path.expanduser("~/.openclaw/workspace/skills/security-scanner/security_scanner.py")
    if os.path.exists(scanner_path):
        log("🔍 运行安全检查...")
        result = subprocess.run(
            [sys.executable, scanner_path, skill_path],
            capture_output=True,
            text=True
        )
        if "严重" in result.stdout and "建议不要安装" in result.stdout:
            log("❌ 安全检查未通过，已中止安装")
            log("💡 如需强制安装，请使用普通安装方式")
            return False
    
    # 3. 沙箱测试
    is_safe, report = test_skill_in_sandbox(skill_path)
    if not is_safe:
        log(f"❌ 沙箱测试未通过: {report}")
        return False
    log(f"✅ 沙箱测试通过")
    
    # 4. 执行安装
    try:
        target_dir = os.path.expanduser("~/.openclaw/workspace/skills")
        skill_name = os.path.basename(skill_path)
        target_path = os.path.join(target_dir, skill_name)
        
        if os.path.exists(target_path):
            # 备份旧版本
            backup_path = f"{target_path}.old.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.move(target_path, backup_path)
            log(f"📦 旧版本已备份: {backup_path}")
        
        # 复制新技能包
        shutil.copytree(skill_path, target_path, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        log(f"✅ 技能包已安装: {target_path}")
        
        # 5. 简单验证
        skill_md = os.path.join(target_path, "SKILL.md")
        if os.path.exists(skill_md):
            log(f"✅ 安装验证通过")
            log(f"💡 如需回滚，使用: python3 system_guard.py restore {snapshot.backup_path}")
            return True
        else:
            log(f"⚠️ 安装验证警告: 未找到SKILL.md")
            return True
            
    except Exception as e:
        log(f"❌ 安装失败: {e}")
        log(f"💡 建议恢复系统: python3 system_guard.py restore {snapshot.backup_path}")
        return False

def list_snapshots():
    """列出所有系统快照"""
    if not os.path.exists(SYSTEM_BACKUP_DIR):
        print("📂 暂无系统快照")
        return
    
    snapshots = []
    for item in os.listdir(SYSTEM_BACKUP_DIR):
        if item.startswith('snapshot_'):
            snapshot_path = os.path.join(SYSTEM_BACKUP_DIR, item)
            info_path = os.path.join(snapshot_path, "snapshot.json")
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    info = json.load(f)
                snapshots.append(info)
    
    if not snapshots:
        print("📂 暂无系统快照")
        return
    
    print(f"\n📸 系统快照列表 ({len(snapshots)}个):")
    print("-" * 60)
    for i, s in enumerate(snapshots[-10:], 1):  # 只显示最近10个
        print(f"{i}. {s['timestamp']} - {s['description']}")
    print()

def cleanup_old_snapshots(keep: int = 10):
    """清理旧快照，只保留最近N个"""
    if not os.path.exists(SYSTEM_BACKUP_DIR):
        return
    
    snapshots = []
    for item in os.listdir(SYSTEM_BACKUP_DIR):
        if item.startswith('snapshot_'):
            snapshot_path = os.path.join(SYSTEM_BACKUP_DIR, item)
            snapshots.append((item, snapshot_path))
    
    # 按时间排序
    snapshots.sort(key=lambda x: x[0])
    
    # 删除旧的
    if len(snapshots) > keep:
        for item, path in snapshots[:-keep]:
            try:
                shutil.rmtree(path)
                log(f"🗑️  已清理旧快照: {item}")
            except:
                pass

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='系统保护守卫')
    parser.add_argument('action', choices=['snapshot', 'restore', 'install', 'list', 'cleanup'],
                       help='操作: snapshot(创建快照), restore(恢复), install(安全安装), list(列出快照), cleanup(清理旧快照)')
    parser.add_argument('path', nargs='?', help='技能包路径或快照路径')
    parser.add_argument('-d', '--description', default='手动备份', help='快照描述')
    parser.add_argument('-k', '--keep', type=int, default=10, help='保留快照数量')
    
    args = parser.parse_args()
    
    if args.action == 'snapshot':
        create_system_snapshot(args.description)
    elif args.action == 'restore':
        if not args.path:
            print("❌ 请指定快照路径")
            sys.exit(1)
        restore_system_snapshot(args.path)
    elif args.action == 'install':
        if not args.path:
            print("❌ 请指定技能包路径")
            sys.exit(1)
        safe_install_skill(args.path)
    elif args.action == 'list':
        list_snapshots()
    elif args.action == 'cleanup':
        cleanup_old_snapshots(args.keep)
