# AI Coder Python 架构设计

> 由 Opus 4.6 设计 | 安全优先 | 防命令注入

---

## 1. 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    AI Coder (Python)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   CLI Layer  │  │  Dispatcher  │  │   Security   │  │
│  │   (click)    │  │   (Router)   │  │  (Sanitizer) │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘  │
│         │                 │                              │
│  ┌──────▼─────────────────▼──────┐  ┌──────────────┐   │
│  │      Executor Factory          │  │ Background   │   │
│  │  ┌────────────┐ ┌───────────┐ │  │ Task Manager │   │
│  │  │  LocalExec │ │ RemoteExec│ │  │ (SQLite)     │   │
│  │  │ (subprocess│ │(paramiko) │ │  └──────────────┘   │
│  │  └────────────┘ └───────────┘ │                      │
│  └───────────────────────────────┘                      │
└─────────────────────────────────────────────────────────┘
           │                 │                 │
   ┌───────▼──────┐  ┌──────▼───────┐  ┌──────▼───────┐
   │  acpx (本地)  │  │ 韩国 Codex   │  │ Skill YAML   │
   │ Claude/Opus  │  │  GPT-5.4     │  │  Registry    │
   └──────────────┘  └──────────────┘  └──────────────┘
```

---

## 2. 目录结构

```
ai_coder/
├── __init__.py
├── __main__.py                 # python -m ai_coder
├── cli.py                      # CLI 入口 (click)
├── exceptions.py               # 统一异常体系
│
├── config/
│   ├── __init__.py
│   ├── loader.py               # YAML/TOML 配置加载
│   ├── schema.py               # Pydantic 配置模型
│   └── defaults.py             # 默认值常量
│
├── security/
│   ├── __init__.py
│   ├── credentials.py          # 环境变量凭据管理
│   ├── sanitizer.py            # 输入净化（防注入）
│   └── audit.py                # 操作审计日志
│
├── core/
│   ├── __init__.py
│   ├── models.py               # Task / Result 数据模型
│   ├── dispatcher.py           # 路由调度器
│   └── lifecycle.py            # 任务生命周期管理
│
├── executors/
│   ├── __init__.py
│   ├── base.py                 # AbstractExecutor 基类
│   ├── local.py                # LocalExecutor (subprocess)
│   ├── remote.py               # RemoteExecutor (paramiko)
│   └── factory.py              # ExecutorFactory
│
├── background/
│   ├── __init__.py
│   ├── manager.py              # BackgroundTaskManager
│   ├── store.py                # 持久化任务状态 (SQLite)
│   └── watcher.py              # 后台进程看门狗
│
├── skills/
│   ├── __init__.py
│   ├── registry.py             # SkillRegistry (发现+注册)
│   ├── loader.py               # YAML skill 加载器
│   ├── runner.py               # SkillRunner (编排执行)
│   └── builtin/                # 内置 skills
│       ├── omc.py
│       └── omx.py
│
└── tests/
    ├── __init__.py
    ├── test_sanitizer.py
    ├── test_local_executor.py
    ├── test_remote_executor.py
    ├── test_dispatcher.py
    └── test_skills.py
```

---

## 3. 核心类设计

### 3.1 数据模型 — `core/models.py`

```python
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


class TaskType(Enum):
    EXEC = auto()           # 单次执行
    SESSION_NEW = auto()    # 创建 session
    SESSION_CLOSE = auto()  # 关闭 session
    STATUS = auto()         # 查询状态
    OMC = auto()            # OMC skill


class ExecutorType(Enum):
    LOCAL = "local"     # 本地 Claude Code
    REMOTE = "remote"   # 韩国 Codex


@dataclass(frozen=True)
class Task:
    """不可变的任务定义"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: TaskType = TaskType.EXEC
    executor: ExecutorType = ExecutorType.LOCAL
    
    # 任务内容
    command: Optional[str] = None      # exec 命令
    session_name: Optional[str] = None # session 名称
    skill_name: Optional[str] = None   # OMC skill 名称
    
    # 配置
    timeout: int = 300          # 超时秒数
    no_wait: bool = True        # 是否后台运行
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    output: str
    error: str
    exit_code: int
    
    # 时间戳
    started_at: str
    completed_at: str
    duration_ms: int
    
    # 执行信息
    executor_type: ExecutorType
    session_id: Optional[str] = None
    
    # 后台任务信息
    background_pid: Optional[int] = None
```

### 3.2 配置模型 — `config/schema.py`

```python
from pydantic import BaseSettings, Field, validator
from typing import Optional


class LocalConfig(BaseSettings):
    """本地 Claude Code 配置"""
    acpx_path: str = Field(default="acpx", env="AI_CODER_LOCAL_ACPX")
    workspace: str = Field(default="~/.openclaw/workspace", env="AI_CODER_WORKSPACE")
    
    class Config:
        env_prefix = "AI_CODER_LOCAL_"


class RemoteConfig(BaseSettings):
    """韩国服务器配置"""
    host: str = Field(..., env="AI_CODER_KR_HOST")
    user: str = Field(..., env="AI_CODER_KR_USER")
    ssh_key: str = Field(..., env="AI_CODER_SSH_KEY")
    acpx_path: str = Field(
        default="/home/ccuser/.nvm/versions/node/v20.20.2/bin/acpx",
        env="AI_CODER_KR_ACPX"
    )
    
    @validator('host')
    def validate_host(cls, v):
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError(f"Invalid host: {v}")
        return v
    
    @validator('user')
    def validate_user(cls, v):
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', v):
            raise ValueError(f"Invalid user: {v}")
        return v
    
    class Config:
        env_prefix = "AI_CODER_KR_"


class SecurityConfig(BaseSettings):
    """安全配置"""
    max_task_length: int = 10000
    allowed_chars_pattern: str = r'^[\w\s\-_\.\,\;\:\/\=\(\)\[\]\{\}\"\'\`\|\&\$\<\>\!\?\*\+]+$'
    enable_audit: bool = True
    audit_log_path: str = "~/.ai_coder/audit.log"
    
    class Config:
        env_prefix = "AI_CODER_SECURITY_"


class Settings(BaseSettings):
    """全局配置"""
    local: LocalConfig = LocalConfig()
    remote: RemoteConfig
    security: SecurityConfig = SecurityConfig()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### 3.3 输入净化 — `security/sanitizer.py`

```python
import re
import html
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class SanitizationResult:
    """净化结果"""
    is_valid: bool
    cleaned: str
    violations: list[str]


class InputSanitizer:
    """输入净化器 - 防止命令注入"""
    
    # 危险字符黑名单
    DANGEROUS_CHARS = [
        '\x00',  # null byte
        '\n', '\r',  # 换行
        '\x1b',  # ESC
    ]
    
    # 危险模式
    DANGEROUS_PATTERNS = [
        r'[;&|]\s*(?:rm|mv|cp|cat|sh|bash|python|curl|wget)\s',
        r'`[^`]+`',
        r'\$([^)]+)',
        r'[<>]\s*/(?:dev|proc|sys|tmp|var)',
        r'\.\./\.\.',
    ]
    
    def __init__(self, max_length: int = 10000):
        self.max_length = max_length
        self.patterns = [re.compile(p) for p in self.DANGEROUS_PATTERNS]
    
    def sanitize(self, input_str: str) -> SanitizationResult:
        """净化输入字符串"""
        violations = []
        
        # 1. 长度检查
        if len(input_str) > self.max_length:
            violations.append(f"Input exceeds max length: {len(input_str)} > {self.max_length}")
            return SanitizationResult(False, "", violations)
        
        # 2. 危险字符检查
        for char in self.DANGEROUS_CHARS:
            if char in input_str:
                violations.append(f"Dangerous character found: {repr(char)}")
        
        # 3. 危险模式检查
        for pattern in self.patterns:
            if pattern.search(input_str