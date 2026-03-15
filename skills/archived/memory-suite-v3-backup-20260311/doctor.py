#!/usr/bin/env python3
"""
Memory Suite v3.0 - 系统诊断工具
检查系统健康状态和配置
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('doctor')

# 路径配置
WORKSPACE = Path("/Users/zhaoruicn/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
CONFIG_DIR = Path(__file__).parent / "config"


class Doctor:
    """系统诊断工具"""
    
    def __init__(self):
        self.checks = []
        self.issues = []
    
    def run_check(self) -> List[Dict[str, Any]]:
        """
        运行所有检查
        
        Returns:
            检查结果列表
        """
        logger.info("运行系统诊断...")
        
        self.checks = []
        self.issues = []
        
        # 执行各项检查
        self._check_directories()
        self._check_config()
        self._check_memory_files()
        self._check_permissions()
        self._check_disk_space()
        self._check_index()
        self._check_snapshots()
        
        return self.checks
    
    def _add_check(self, name: str, ok: bool, message: str, suggestion: str = None):
        """添加检查结果"""
        result = {
            "name": name,
            "ok": ok,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if suggestion:
            result["suggestion"] = suggestion
        
        self.checks.append(result)
        
        if not ok:
            self.issues.append(result)
    
    def _check_directories(self):
        """检查必要目录"""
        required_dirs = [
            MEMORY_DIR,
            MEMORY_DIR / "snapshots",
            MEMORY_DIR / "archive",
            MEMORY_DIR / "index",
            MEMORY_DIR / "summary",
            CONFIG_DIR
        ]
        
        missing = []
        for d in required_dirs:
            if not d.exists():
                missing.append(str(d))
        
        if missing:
            self._add_check(
                "目录结构",
                False,
                f"缺少 {len(missing)} 个目录",
                f"创建缺失目录：{', '.join(missing)}"
            )
            
            # 自动创建
            for d in required_dirs:
                d.mkdir(parents=True, exist_ok=True)
        else:
            self._add_check("目录结构", True, "所有必要目录存在")
    
    def _check_config(self):
        """检查配置文件"""
        config_file = CONFIG_DIR / "config.json"
        
        if not config_file.exists():
            self._add_check(
                "配置文件",
                False,
                "配置文件不存在",
                "运行 'memory-suite config reset' 创建默认配置"
            )
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查必要字段
            required_fields = ["version", "workspace", "memory_dir"]
            missing_fields = [f for f in required_fields if f not in config]
            
            if missing_fields:
                self._add_check(
                    "配置文件",
                    False,
                    f"缺少字段：{', '.join(missing_fields)}",
                    "修复配置文件"
                )
            else:
                self._add_check(
                    "配置文件",
                    True,
                    f"配置有效 (版本：{config.get('version', 'unknown')})"
                )
                
        except json.JSONDecodeError as e:
            self._add_check(
                "配置文件",
                False,
                f"JSON 格式错误：{e}",
                "修复或重置配置文件"
            )
        except Exception as e:
            self._add_check(
                "配置文件",
                False,
                f"读取失败：{e}",
                "检查文件权限"
            )
    
    def _check_memory_files(self):
        """检查记忆文件"""
        try:
            memory_files = list(MEMORY_DIR.glob("*.md"))
            
            if len(memory_files) == 0:
                self._add_check(
                    "记忆文件",
                    False,
                    "没有记忆文件",
                    "运行 'memory-suite save' 保存会话"
                )
            else:
                # 检查最近是否有更新
                today = datetime.now().strftime("%Y-%m-%d")
                today_file = MEMORY_DIR / f"{today}.md"
                
                if today_file.exists():
                    self._add_check(
                        "记忆文件",
                        True,
                        f"有 {len(memory_files)} 个文件，今日文件已创建"
                    )
                else:
                    self._add_check(
                        "记忆文件",
                        True,
                        f"有 {len(memory_files)} 个文件，今日文件尚未创建",
                        "运行 'memory-suite save' 保存今日会话"
                    )
                    
        except Exception as e:
            self._add_check(
                "记忆文件",
                False,
                f"检查失败：{e}",
                "检查目录权限"
            )
    
    def _check_permissions(self):
        """检查文件权限"""
        try:
            # 测试写入权限
            test_file = MEMORY_DIR / ".permission_test"
            test_file.write_text("test")
            test_file.unlink()
            
            self._add_check("文件权限", True, "读写权限正常")
            
        except Exception as e:
            self._add_check(
                "文件权限",
                False,
                f"权限错误：{e}",
                "检查目录权限设置"
            )
    
    def _check_disk_space(self, min_mb: int = 100):
        """检查磁盘空间"""
        try:
            import shutil
            stat = shutil.disk_usage(WORKSPACE)
            free_mb = stat.free / (1024 * 1024)
            
            if free_mb < min_mb:
                self._add_check(
                    "磁盘空间",
                    False,
                    f"剩余空间不足：{free_mb:.1f}MB",
                    f"清理磁盘空间，至少需要 {min_mb}MB"
                )
            else:
                self._add_check(
                    "磁盘空间",
                    True,
                    f"剩余空间充足：{free_mb:.1f}MB"
                )
                
        except Exception as e:
            self._add_check(
                "磁盘空间",
                False,
                f"检查失败：{e}",
                "手动检查磁盘空间"
            )
    
    def _check_index(self):
        """检查索引"""
        index_file = MEMORY_DIR / "index" / "keywords.json"
        
        if not index_file.exists():
            self._add_check(
                "索引文件",
                False,
                "索引文件不存在",
                "运行 'memory-suite scheduler run index' 更新索引"
            )
            return
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # 检查索引是否过期
            updated_at = index_data.get("updated_at")
            if updated_at:
                update_time = datetime.fromisoformat(updated_at)
                age_hours = (datetime.now() - update_time).total_seconds() / 3600
                
                if age_hours > 24:
                    self._add_check(
                        "索引文件",
                        False,
                        f"索引过期：{age_hours:.1f}小时前更新",
                        "运行 'memory-suite scheduler run index' 更新索引"
                    )
                else:
                    self._add_check(
                        "索引文件",
                        True,
                        f"索引正常 ({len(index_data.get('keywords', {}))} 个关键词)"
                    )
            else:
                self._add_check(
                    "索引文件",
                    True,
                    "索引文件存在"
                )
                
        except Exception as e:
            self._add_check(
                "索引文件",
                False,
                f"读取失败：{e}",
                "重建索引"
            )
    
    def _check_snapshots(self):
        """检查快照"""
        snapshot_dir = MEMORY_DIR / "snapshots"
        
        if not snapshot_dir.exists():
            self._add_check(
                "会话快照",
                False,
                "快照目录不存在",
                "运行 'memory-suite save' 创建快照"
            )
            return
        
        snapshots = list(snapshot_dir.glob("session_*.json"))
        
        if len(snapshots) == 0:
            self._add_check(
                "会话快照",
                False,
                "没有快照文件",
                "运行 'memory-suite save' 创建快照"
            )
        else:
            # 检查最新快照
            latest = max(snapshots, key=lambda f: f.stat().st_mtime)
            age_hours = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).total_seconds() / 3600
            
            if age_hours > 1:
                self._add_check(
                    "会话快照",
                    False,
                    f"快照过期：{age_hours:.1f}小时前",
                    "运行 'memory-suite save' 更新快照"
                )
            else:
                self._add_check(
                    "会话快照",
                    True,
                    f"快照正常 ({len(snapshots)} 个，最新：{age_hours/60:.1f}分钟前)"
                )
    
    def get_summary(self) -> Dict[str, Any]:
        """获取诊断摘要"""
        total = len(self.checks)
        passed = sum(1 for c in self.checks if c["ok"])
        failed = total - passed
        
        return {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "health_score": (passed / total * 100) if total > 0 else 0,
            "issues": self.issues
        }
    
    def print_report(self):
        """打印诊断报告"""
        print("\n" + "=" * 60)
        print("🏥 Memory Suite v3.0 系统诊断报告")
        print("=" * 60)
        print(f"\n检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        summary = self.get_summary()
        print(f"\n总体健康度：{summary['health_score']:.1f}%")
        print(f"通过检查：{summary['passed']}/{summary['total_checks']}")
        
        print("\n" + "-" * 60)
        print("详细检查结果:")
        print("-" * 60)
        
        for check in self.checks:
            status = "✅" if check["ok"] else "❌"
            print(f"\n{status} {check['name']}")
            print(f"   {check['message']}")
            if not check["ok"] and "suggestion" in check:
                print(f"   💡 建议：{check['suggestion']}")
        
        print("\n" + "=" * 60)
        
        if summary["failed"] == 0:
            print("🎉 所有检查通过！系统运行正常")
        else:
            print(f"⚠️ 发现 {summary['failed']} 个问题，建议处理")
        
        print("=" * 60 + "\n")


def main():
    """主入口"""
    doctor = Doctor()
    results = doctor.run_check()
    doctor.print_report()
    
    # 返回退出码
    summary = doctor.get_summary()
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == '__main__':
    main()
