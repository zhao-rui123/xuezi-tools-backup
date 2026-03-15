#!/usr/bin/env python3
"""
Unified CLI Service - Script Management Module
统一命令行入口服务 - 脚本管理模块

提供统一的 CLI 入口：oc-cli memory/knowledge/action/skill/backup/status
支持脚本分类管理和命令注册分发

Author: Golf Agent (Builder)
Version: 1.0.0
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


# ============================================================================
# Constants & Configuration
# ============================================================================

WORKSPACE_ROOT = Path.home() / ".openclaw" / "workspace"
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"
SKILLS_DIR = WORKSPACE_ROOT / "skills"
MEMORY_DIR = WORKSPACE_ROOT / "memory"
KNOWLEDGE_BASE_DIR = WORKSPACE_ROOT / "knowledge-base"
BACKUP_DIR = WORKSPACE_ROOT / "backups"

CONFIG_FILE = WORKSPACE_ROOT / "config" / "cli_config.json"


# ============================================================================
# Enums & Data Classes
# ============================================================================

class ScriptCategory(Enum):
    """脚本分类枚举"""
    MEMORY = "memory"           # 记忆管理
    KNOWLEDGE = "knowledge"     # 知识库管理
    ACTION = "action"           # 动作执行
    SKILL = "skill"             # 技能包管理
    BACKUP = "backup"           # 备份管理
    STATUS = "status"           # 状态检查
    SYSTEM = "system"           # 系统管理
    UTILITY = "utility"         # 工具脚本


@dataclass
class CommandInfo:
    """命令信息数据类"""
    name: str
    category: ScriptCategory
    description: str
    script_path: Optional[Path] = None
    handler: Optional[Callable] = None
    aliases: List[str] = field(default_factory=list)
    args: List[str] = field(default_factory=list)
    requires_confirm: bool = False


@dataclass
class ScriptMetadata:
    """脚本元数据"""
    name: str
    category: ScriptCategory
    description: str
    version: str = "1.0.0"
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


# ============================================================================
# Script Registry - 命令注册表
# ============================================================================

class ScriptRegistry:
    """
    脚本注册表 - 管理所有 CLI 命令
    支持命令注册、查找、分类管理
    """
    
    def __init__(self):
        self._commands: Dict[str, CommandInfo] = {}
        self._category_map: Dict[ScriptCategory, List[str]] = {
            cat: [] for cat in ScriptCategory
        }
        self._aliases: Dict[str, str] = {}  # alias -> command_name
    
    def register(
        self,
        name: str,
        category: ScriptCategory,
        description: str,
        script_path: Optional[Path] = None,
        handler: Optional[Callable] = None,
        aliases: Optional[List[str]] = None,
        requires_confirm: bool = False
    ) -> CommandInfo:
        """
        注册一个新命令
        
        Args:
            name: 命令名称
            category: 命令分类
            description: 命令描述
            script_path: 脚本文件路径（可选）
            handler: 处理函数（可选）
            aliases: 命令别名列表
            requires_confirm: 是否需要确认
        
        Returns:
            CommandInfo: 注册的命令信息
        """
        if name in self._commands:
            raise ValueError(f"Command '{name}' already registered")
        
        cmd_info = CommandInfo(
            name=name,
            category=category,
            description=description,
            script_path=script_path,
            handler=handler,
            aliases=aliases or [],
            requires_confirm=requires_confirm
        )
        
        self._commands[name] = cmd_info
        self._category_map[category].append(name)
        
        # 注册别名
        for alias in (aliases or []):
            if alias in self._aliases:
                raise ValueError(f"Alias '{alias}' already used by command '{self._aliases[alias]}'")
            self._aliases[alias] = name
        
        return cmd_info
    
    def get(self, name: str) -> Optional[CommandInfo]:
        """获取命令信息（支持别名解析）"""
        # 首先检查是否是别名
        if name in self._aliases:
            name = self._aliases[name]
        return self._commands.get(name)
    
    def get_by_category(self, category: ScriptCategory) -> List[CommandInfo]:
        """获取指定分类的所有命令"""
        return [self._commands[name] for name in self._category_map.get(category, [])]
    
    def list_all(self) -> Dict[str, CommandInfo]:
        """列出所有注册的命令"""
        return self._commands.copy()
    
    def list_categories(self) -> List[ScriptCategory]:
        """列出所有分类"""
        return list(ScriptCategory)
    
    def unregister(self, name: str) -> bool:
        """注销命令"""
        if name not in self._commands:
            return False
        
        cmd = self._commands[name]
        
        # 从分类映射中移除
        if name in self._category_map[cmd.category]:
            self._category_map[cmd.category].remove(name)
        
        # 移除别名
        for alias in cmd.aliases:
            self._aliases.pop(alias, None)
        
        # 移除命令
        del self._commands[name]
        return True


# ============================================================================
# Command Dispatcher - 命令分发器
# ============================================================================

class CommandDispatcher:
    """
    命令分发器 - 执行 CLI 命令
    支持脚本执行和函数调用
    """
    
    def __init__(self, registry: ScriptRegistry):
        self.registry = registry
        self._pre_hooks: List[Callable] = []
        self._post_hooks: List[Callable] = []
    
    def add_pre_hook(self, hook: Callable):
        """添加前置钩子"""
        self._pre_hooks.append(hook)
    
    def add_post_hook(self, hook: Callable):
        """添加后置钩子"""
        self._post_hooks.append(hook)
    
    def dispatch(self, command_name: str, args: List[str]) -> int:
        """
        分发并执行命令
        
        Args:
            command_name: 命令名称
            args: 命令参数
        
        Returns:
            int: 退出码 (0 = 成功)
        """
        cmd = self.registry.get(command_name)
        
        if not cmd:
            print(f"Error: Unknown command '{command_name}'")
            print(f"Run 'oc-cli --help' to see available commands.")
            return 1
        
        # 执行前置钩子
        for hook in self._pre_hooks:
            try:
                hook(cmd, args)
            except Exception as e:
                print(f"Pre-hook error: {e}")
        
        # 需要确认
        if cmd.requires_confirm:
            confirm = input(f"Confirm execution of '{command_name}'? [y/N]: ")
            if confirm.lower() not in ('y', 'yes'):
                print("Cancelled.")
                return 0
        
        # 执行命令
        try:
            if cmd.handler:
                # 调用处理函数
                result = cmd.handler(args)
                exit_code = result if isinstance(result, int) else 0
            elif cmd.script_path:
                # 执行脚本文件
                exit_code = self._execute_script(cmd.script_path, args)
            else:
                print(f"Error: Command '{command_name}' has no handler or script")
                return 1
        except Exception as e:
            print(f"Error executing command: {e}")
            exit_code = 1
        
        # 执行后置钩子
        for hook in self._post_hooks:
            try:
                hook(cmd, args, exit_code)
            except Exception as e:
                print(f"Post-hook error: {e}")
        
        return exit_code
    
    def _execute_script(self, script_path: Path, args: List[str]) -> int:
        """执行外部脚本"""
        if not script_path.exists():
            print(f"Error: Script not found: {script_path}")
            return 1
        
        cmd = [str(script_path)] + args
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode


# ============================================================================
# Built-in Command Handlers - 内置命令处理函数
# ============================================================================

def handle_memory(args: List[str]) -> int:
    """处理 memory 命令"""
    parser = argparse.ArgumentParser(description="Memory management commands")
    parser.add_argument("action", choices=["list", "read", "write", "search", "compress"],
                       help="Memory action to perform")
    parser.add_argument("--date", help="Date for memory (YYYY-MM-DD)")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--content", help="Content to write")
    
    try:
        parsed = parser.parse_args(args)
    except SystemExit:
        return 1
    
    if parsed.action == "list":
        return _memory_list()
    elif parsed.action == "read":
        return _memory_read(parsed.date)
    elif parsed.action == "write":
        return _memory_write(parsed.date, parsed.content)
    elif parsed.action == "search":
        return _memory_search(parsed.query)
    elif parsed.action == "compress":
        return _memory_compress()
    
    return 0


def _memory_list() -> int:
    """列出记忆文件"""
    memory_path = Path(MEMORY_DIR)
    if not memory_path.exists():
        print("No memory directory found.")
        return 1
    
    files = sorted([f for f in memory_path.glob("*.md")])
    if not files:
        print("No memory files found.")
        return 0
    
    print("Memory files:")
    for f in files[-20:]:  # 显示最近20个
        print(f"  {f.stem}")
    return 0


def _memory_read(date: Optional[str]) -> int:
    """读取记忆"""
    if not date:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
    
    memory_file = Path(MEMORY_DIR) / f"{date}.md"
    if not memory_file.exists():
        print(f"No memory file for {date}")
        return 1
    
    print(memory_file.read_text())
    return 0


def _memory_write(date: Optional[str], content: Optional[str]) -> int:
    """写入记忆"""
    if not date:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
    
    memory_file = Path(MEMORY_DIR) / f"{date}.md"
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    
    if content:
        with open(memory_file, "a") as f:
            f.write(f"\n{content}\n")
        print(f"Appended to {memory_file}")
    else:
        print(f"Memory file: {memory_file}")
        print("Use --content to add content")
    return 0


def _memory_search(query: Optional[str]) -> int:
    """搜索记忆"""
    if not query:
        print("Please provide a search query with --query")
        return 1
    
    import subprocess
    try:
        result = subprocess.run(
            ["grep", "-r", "-i", query, str(MEMORY_DIR)],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        else:
            print(f"No results found for '{query}'")
    except Exception as e:
        print(f"Search error: {e}")
    return 0


def _memory_compress() -> int:
    """压缩记忆"""
    compressor_script = SCRIPTS_DIR / "session-compressor.py"
    if compressor_script.exists():
        subprocess.run(["python3", str(compressor_script)])
    else:
        print("Compressor script not found")
    return 0


def handle_knowledge(args: List[str]) -> int:
    """处理 knowledge 命令"""
    parser = argparse.ArgumentParser(description="Knowledge base management")
    parser.add_argument("action", choices=["list", "read", "search", "index"],
                       help="Knowledge action to perform")
    parser.add_argument("--topic", help="Topic to read")
    parser.add_argument("--query", help="Search query")
    
    try:
        parsed = parser.parse_args(args)
    except SystemExit:
        return 1
    
    kb_path = Path(KNOWLEDGE_BASE_DIR)
    
    if parsed.action == "list":
        if kb_path.exists():
            files = list(kb_path.glob("*.md"))
            print("Knowledge base topics:")
            for f in sorted(files):
                print(f"  {f.stem}")
        return 0
    
    elif parsed.action == "read" and parsed.topic:
        topic_file = kb_path / f"{parsed.topic}.md"
        if topic_file.exists():
            print(topic_file.read_text())
        else:
            print(f"Topic '{parsed.topic}' not found")
        return 0
    
    elif parsed.action == "search" and parsed.query:
        try:
            result = subprocess.run(
                ["grep", "-r", "-i", parsed.query, str(kb_path)],
                capture_output=True,
                text=True
            )
            print(result.stdout or f"No results for '{parsed.query}'")
        except Exception as e:
            print(f"Search error: {e}")
    
    return 0


def handle_action(args: List[str]) -> int:
    """处理 action 命令"""
    parser = argparse.ArgumentParser(description="Execute actions")
    parser.add_argument("name", help="Action name")
    parser.add_argument("--params", help="Action parameters (JSON)")
    
    try:
        parsed = parser.parse_args(args)
    except SystemExit:
        return 1
    
    print(f"Executing action: {parsed.name}")
    if parsed.params:
        params = json.loads(parsed.params)
        print(f"Parameters: {params}")
    
    # Action execution logic would go here
    return 0


def handle_skill(args: List[str]) -> int:
    """处理 skill 命令"""
    parser = argparse.ArgumentParser(description="Skill package management")
    parser.add_argument("action", choices=["list", "info", "run", "install"],
                       help="Skill action")
    parser.add_argument("--name", help="Skill name")
    
    try:
        parsed = parser.parse_args(args)
    except SystemExit:
        return 1
    
    skills_path = Path(SKILLS_DIR)
    
    if parsed.action == "list":
        if skills_path.exists():
            skills = [d.name for d in skills_path.iterdir() if d.is_dir()]
            print("Installed skills:")
            for skill in sorted(skills):
                print(f"  {skill}")
        return 0
    
    elif parsed.action == "info" and parsed.name:
        skill_dir = skills_path / parsed.name
        if skill_dir.exists():
            readme = skill_dir / "README.md"
            if readme.exists():
                print(readme.read_text())
            else:
                print(f"Skill '{parsed.name}' (no README)")
        else:
            print(f"Skill '{parsed.name}' not found")
    
    return 0


def handle_backup(args: List[str]) -> int:
    """处理 backup 命令"""
    parser = argparse.ArgumentParser(description="Backup management")
    parser.add_argument("action", choices=["create", "list", "restore", "clean"],
                       help="Backup action")
    parser.add_argument("--name", help="Backup name")
    
    try:
        parsed = parser.parse_args(args)
    except SystemExit:
        return 1
    
    backup_script = SCRIPTS_DIR / "backup-manager.py"
    
    if parsed.action == "create":
        if backup_script.exists():
            subprocess.run(["python3", str(backup_script), "backup"])
        else:
            print("Backup script not found")
    
    elif parsed.action == "list":
        backup_path = Path(BACKUP_DIR)
        if backup_path.exists():
            backups = sorted([d.name for d in backup_path.iterdir() if d.is_dir()])
            print("Available backups:")
            for b in backups:
                print(f"  {b}")
    
    return 0


def handle_status(args: List[str]) -> int:
    """处理 status 命令"""
    print("=" * 50)
    print("OpenClaw Workspace Status")
    print("=" * 50)
    
    # Workspace info
    print(f"\nWorkspace: {WORKSPACE_ROOT}")
    print(f"Exists: {WORKSPACE_ROOT.exists()}")
    
    # Directory status
    dirs = {
        "Scripts": SCRIPTS_DIR,
        "Skills": SKILLS_DIR,
        "Memory": MEMORY_DIR,
        "Knowledge Base": KNOWLEDGE_BASE_DIR,
        "Backups": BACKUP_DIR,
    }
    
    print("\nDirectories:")
    for name, path in dirs.items():
        status = "✓" if path.exists() else "✗"
        count = len(list(path.iterdir())) if path.exists() else 0
        print(f"  [{status}] {name}: {path.name} ({count} items)")
    
    # System info
    print("\nSystem:")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Platform: {sys.platform}")
    
    return 0


# ============================================================================
# CLI Builder - 构建完整的 CLI
# ============================================================================

class UnifiedCLI:
    """
    统一 CLI 入口类
    整合所有命令并提供统一的命令行接口
    """
    
    def __init__(self):
        self.registry = ScriptRegistry()
        self.dispatcher = CommandDispatcher(self.registry)
        self._setup_logging()
        self._register_builtin_commands()
    
    def _setup_logging(self):
        """设置日志"""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger("oc-cli")
    
    def _register_builtin_commands(self):
        """注册内置命令"""
        # Memory commands
        self.registry.register(
            name="memory",
            category=ScriptCategory.MEMORY,
            description="Memory management (list, read, write, search, compress)",
            handler=handle_memory,
            aliases=["mem", "m"]
        )
        
        # Knowledge commands
        self.registry.register(
            name="knowledge",
            category=ScriptCategory.KNOWLEDGE,
            description="Knowledge base management (list, read, search)",
            handler=handle_knowledge,
            aliases=["know", "k", "kb"]
        )
        
        # Action commands
        self.registry.register(
            name="action",
            category=ScriptCategory.ACTION,
            description="Execute actions with parameters",
            handler=handle_action,
            aliases=["act", "a"]
        )
        
        # Skill commands
        self.registry.register(
            name="skill",
            category=ScriptCategory.SKILL,
            description="Skill package management (list, info, run)",
            handler=handle_skill,
            aliases=["sk", "s"]
        )
        
        # Backup commands
        self.registry.register(
            name="backup",
            category=ScriptCategory.BACKUP,
            description="Backup management (create, list, restore)",
            handler=handle_backup,
            aliases=["bak", "b"],
            requires_confirm=True
        )
        
        # Status commands
        self.registry.register(
            name="status",
            category=ScriptCategory.STATUS,
            description="Show workspace status",
            handler=handle_status,
            aliases=["st", "stat"]
        )
    
    def register_custom_command(
        self,
        name: str,
        category: ScriptCategory,
        description: str,
        handler: Optional[Callable] = None,
        script_path: Optional[Path] = None,
        aliases: Optional[List[str]] = None
    ):
        """注册自定义命令"""
        return self.registry.register(
            name=name,
            category=category,
            description=description,
            handler=handler,
            script_path=script_path,
            aliases=aliases
        )
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        运行 CLI
        
        Args:
            args: 命令行参数，默认为 sys.argv[1:]
        
        Returns:
            int: 退出码
        """
        if args is None:
            args = sys.argv[1:]
        
        # 创建主解析器
        parser = argparse.ArgumentParser(
            prog="oc-cli",
            description="OpenClaw Unified CLI - 统一命令行入口",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  oc-cli memory list              # 列出记忆文件
  oc-cli knowledge search --query "topic"  # 搜索知识库
  oc-cli skill list               # 列出技能包
  oc-cli backup create            # 创建备份
  oc-cli status                   # 查看状态

Categories:
  memory    - 记忆管理
  knowledge - 知识库管理
  action    - 动作执行
  skill     - 技能包管理
  backup    - 备份管理
  status    - 状态检查
            """
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s 1.0.0"
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )
        
        # 子命令解析器
        subparsers = parser.add_subparsers(
            dest="command",
            help="Available commands",
            metavar="COMMAND"
        )
        
        # 为每个注册的命令创建子解析器
        for cmd_name, cmd_info in self.registry.list_all().items():
            cmd_parser = subparsers.add_parser(
                cmd_name,
                help=cmd_info.description,
                aliases=cmd_info.aliases
            )
            cmd_parser.add_argument(
                "args",
                nargs=argparse.REMAINDER,
                help="Command arguments"
            )
        
        # 解析参数
        parsed = parser.parse_args(args)
        
        if not parsed.command:
            parser.print_help()
            return 0
        
        # 分发命令
        remaining_args = parsed.args if hasattr(parsed, 'args') else []
        return self.dispatcher.dispatch(parsed.command, remaining_args)
    
    def get_help_text(self) -> str:
        """获取帮助文本"""
        lines = ["OpenClaw Unified CLI", "=" * 40, ""]
        
        for category in ScriptCategory:
            cmds = self.registry.get_by_category(category)
            if cmds:
                lines.append(f"\n[{category.value.upper()}]")
                for cmd in cmds:
                    alias_str = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
                    lines.append(f"  {cmd.name}{alias_str}")
                    lines.append(f"    {cmd.description}")
        
        return "\n".join(lines)


# ============================================================================
# Script Manager - 脚本管理器
# ============================================================================

class ScriptManager:
    """
    脚本管理器
    管理脚本的发现、加载和元数据
    """
    
    def __init__(self, scripts_dir: Path = SCRIPTS_DIR):
        self.scripts_dir = scripts_dir
        self._scripts: Dict[str, ScriptMetadata] = {}
    
    def discover_scripts(self) -> List[ScriptMetadata]:
        """发现所有脚本"""
        if not self.scripts_dir.exists():
            return []
        
        scripts = []
        for file_path in self.scripts_dir.iterdir():
            if file_path.suffix in ('.py', '.sh', '.js'):
                metadata = self._extract_metadata(file_path)
                scripts.append(metadata)
                self._scripts[metadata.name] = metadata
        
        return scripts
    
    def _extract_metadata(self, file_path: Path) -> ScriptMetadata:
        """从脚本文件中提取元数据"""
        content = file_path.read_text() if file_path.exists() else ""
        
        # 简单的元数据提取（从注释中）
        name = file_path.stem
        category = ScriptCategory.UTILITY
        description = ""
        version = "1.0.0"
        
        # 解析文件头部的注释
        for line in content.split('\n')[:20]:
            if 'Category:' in line:
                cat_str = line.split(':', 1)[1].strip().lower()
                try:
                    category = ScriptCategory(cat_str)
                except ValueError:
                    pass
            elif 'Description:' in line:
                description = line.split(':', 1)[1].strip()
            elif 'Version:' in line:
                version = line.split(':', 1)[1].strip()
        
        return ScriptMetadata(
            name=name,
            category=category,
            description=description,
            version=version
        )
    
    def get_script(self, name: str) -> Optional[ScriptMetadata]:
        """获取脚本元数据"""
        return self._scripts.get(name)
    
    def list_by_category(self, category: ScriptCategory) -> List[ScriptMetadata]:
        """按分类列出脚本"""
        return [s for s in self._scripts.values() if s.category == category]


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """主入口函数"""
    cli = UnifiedCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
