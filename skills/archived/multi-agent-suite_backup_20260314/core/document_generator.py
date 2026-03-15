#!/usr/bin/env python3
"""
多Agent文档生成器 v2.0
自动生成PRD、架构设计、API文档、ER图等
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()
DOCS_DIR = SUITE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)


class DocType(Enum):
    """文档类型"""
    PRD = "prd"
    ARCHITECTURE = "architecture"
    ER_DIAGRAM = "er_diagram"
    API_DOC = "api_doc"
    SEQUENCE_DIAGRAM = "sequence_diagram"
    USER_MANUAL = "user_manual"
    DEPLOY_DOC = "deploy_doc"
    TEST_REPORT = "test_report"


@dataclass
class Requirement:
    """需求项"""
    id: str
    title: str
    description: str
    priority: str = "P1"  # P0/P1/P2/P3
    module: str = ""
    dependencies: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class UserStory:
    """用户故事"""
    id: str
    role: str
    action: str
    benefit: str
    priority: str = "P1"
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class APIModel:
    """API数据模型"""
    name: str
    fields: List[Dict] = field(default_factory=list)
    description: str = ""


@dataclass
class APIEndpoint:
    """API端点"""
    path: str
    method: str
    summary: str
    description: str = ""
    request_params: List[Dict] = field(default_factory=list)
    request_body: Dict = field(default_factory=dict)
    response: Dict = field(default_factory=dict)
    auth_required: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class DatabaseTable:
    """数据库表"""
    name: str
    description: str = ""
    columns: List[Dict] = field(default_factory=list)
    indexes: List[Dict] = field(default_factory=list)
    foreign_keys: List[Dict] = field(default_factory=list)


class DocumentGenerator:
    """文档生成器"""
    
    def __init__(self):
        self.templates_dir = DOCS_DIR / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_prd(self, project_name: str, description: str, 
                    requirements: List[Requirement], 
                    user_stories: List[UserStory],
                    output_path: Path = None) -> str:
        """生成PRD文档"""
        
        content = f"""# 产品需求文档 (PRD)

**项目名称**: {project_name}
**版本**: 1.0.0
**创建日期**: {datetime.now().strftime('%Y-%m-%d')}
**状态**: 草稿

---

## 1. 项目概述

### 1.1 项目背景
{description}

### 1.2 项目目标
- 目标1: 
- 目标2: 
- 目标3: 

### 1.3 目标用户
- 主要用户群体:
- 用户痛点:
- 期望功能:

---

## 2. 功能需求

### 2.1 功能清单

| 序号 | 功能名称 | 优先级 | 模块 | 描述 |
|------|----------|--------|------|------|
"""
        
        for i, req in enumerate(requirements, 1):
            content += f"| {i} | {req.title} | {req.priority} | {req.module} | {req.description} |\n"
        
        content += """
### 2.2 功能详述

"""
        
        for req in requirements:
            content += f"""
#### {req.id}. {req.title}

**优先级**: {req.priority}
**模块**: {req.module}

**描述**:
{req.description}

**验收标准**:
"""
            for criteria in req.acceptance_criteria:
                content += f"- {criteria}\n"
            
            if req.dependencies:
                content += f"\n**依赖**: {', '.join(req.dependencies)}\n"
        
        content += """
---

## 3. 用户故事

| ID | 角色 | 动作 | 价值 | 优先级 |
|----|------|------|------|--------|
"""
        
        for story in user_stories:
            content += f"| {story.id} | {story.role} | {story.action} | {story.benefit} | {story.priority} |\n"
        
        content += """
### 3.1 详述

"""
        
        for story in user_stories:
            content += f"""
##### {story.id}: {story.role}想要{story.action}以便{story.benefit}

**角色**: {story.role}
**动作**: {story.action}
**价值**: {story.benefit}
**验收标准**:
"""
            for criteria in story.acceptance_criteria:
                content += f"- {criteria}\n"
        
        content += """
---

## 4. 非功能需求

### 4.1 性能要求
- 响应时间: < 200ms
- 并发用户: > 1000
- 可用性: > 99.9%

### 4.2 安全要求
- 用户认证
- 数据加密
- 权限控制

### 4.3 兼容性
- 浏览器支持: Chrome/Firefox/Safari/Edge
- 移动端适配

---

## 5. 风险与依赖

### 5.1 风险
- 技术风险:
- 进度风险:
- 资源风险:

### 5.2 依赖
- 外部依赖:
- 内部依赖:

---

## 6. 附录

### 6.1 术语表
| 术语 | 解释 |
|------|------|
|      |      |

### 6.2 参考资料
- 

---

*本文档由 Product Agent 自动生成*
"""
        
        output_file = (output_path or DOCS_DIR) / f"{project_name}_PRD.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ PRD文档已生成: {output_file}")
        return str(output_file)
    
    def generate_architecture_doc(self, project_name: str, 
                                  modules: List[Dict],
                                  tech_stack: Dict,
                                  output_path: Path = None) -> str:
        """生成架构设计文档"""
        
        content = f"""# 系统架构设计文档

**项目名称**: {project_name}
**版本**: 1.0.0
**创建日期**: {datetime.now().strftime('%Y-%m-%d')}
**架构师**: Architect

---

## 1. 架构概述

### 1.1 设计目标
- 高可用性
- 高性能
- 可扩展性
- 安全性
- 可维护性

### 1.2 技术选型

#### 前端技术栈
"""
        
        for key, value in tech_stack.get('frontend', {}).items():
            content += f"- **{key}**: {value}\n"
        
        content += """
#### 后端技术栈
"""
        
        for key, value in tech_stack.get('backend', {}).items():
            content += f"- **{key}**: {value}\n"
        
        content += """
#### 基础设施
"""
        
        for key, value in tech_stack.get('infrastructure', {}).items():
            content += f"- **{key}**: {value}\n"
        
        content += """
---

## 2. 系统架构

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                      客户端层                               │
│   (Web浏览器 / 移动App / 小程序)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      网关层                                  │
│   (API网关 / 负载均衡 / CDN)                                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      应用服务层                              │
│   (业务微服务 / 消息队列 / 缓存服务)                         │
└──────────┬───────────────────────────────────┬──────────────┘
           │                                   │
┌──────────▼──────────┐              ┌────────▼──────────────┐
│     数据访问层      │              │      第三方服务        │
│  (数据库 / 缓存)    │              │ (支付/短信/存储等)     │
└─────────────────────┘              └───────────────────────┘
```

### 2.2 模块设计

"""
        
        for module in modules:
            content += f"""
#### {module.get('name', '模块')}

- **描述**: {module.get('description', '')}
- **职责**: {module.get('responsibility', '')}
- **技术**: {module.get('tech', '')}
- **依赖**: {', '.join(module.get('dependencies', []))}

"""
        
        content += """
---

## 3. 数据库设计

### 3.1 总体设计
- 数据库类型:
- 读写分离:
- 读写策略:

### 3.2 表结构设计
详见 ER图

---

## 4. API设计

### 4.1 接口规范
- 协议: RESTful API
- 认证方式: JWT
- 响应格式: JSON
- 错误码规范:

### 4.2 接口列表
详见 API文档

---

## 5. 安全设计

### 5.1 认证授权
- 认证方式: JWT Token
- 权限控制: RBAC

### 5.2 数据安全
- 传输加密: HTTPS
- 存储加密: AES-256

### 5.3 安全防护
- XSS防护
- CSRF防护
- SQL注入防护

---

## 6. 性能设计

### 6.1 缓存策略
- 多级缓存
- 缓存失效策略

### 6.2 异步处理
- 消息队列
- 定时任务

---

## 7. 部署架构

### 7.1 基础设施
- 云服务商:
- 区域:
- 可用区:

### 7.2 容器化
- Docker
- Kubernetes

---

*本文档由 Architect Agent 自动生成*
"""
        
        output_file = (output_path or DOCS_DIR) / f"{project_name}_架构设计.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 架构设计文档已生成: {output_file}")
        return str(output_file)
    
    def generate_er_diagram(self, project_name: str,
                            tables: List[DatabaseTable],
                            output_path: Path = None) -> str:
        """生成ER图 (Mermaid格式)"""
        
        mermaid_code = f"""# {project_name} 数据库ER图

## ER Diagram (Mermaid)

```mermaid
erDiagram
"""
        
        for table in tables:
            mermaid_code += f"    {table.name} {{\n"
            for col in table.columns:
                col_type = col.get('type', 'VARCHAR')
                col_name = col.get('name', '')
                nullable = "optional" if col.get('nullable', True) else "required"
                primary = "PK" if col.get('primary', False) else ""
                mermaid_code += f"        {col_type} {col_name} {nullable} {primary}\n"
            mermaid_code += "    }\n"
        
        mermaid_code += "\n"
        
        for table in tables:
            for fk in table.foreign_keys:
                mermaid_code += f"    {table.name} }|..|| {fk.get('references', '')} : \"{fk.get('name', '')}\"\n"
        
        content = f"""# {project_name} 数据库设计

**生成日期**: {datetime.now().strftime('%Y-%m-%d')}

---

## 数据库概览

| 表名 | 描述 |
|------|------|
"""
        
        for table in tables:
            content += f"| {table.name} | {table.description} |\n"
        
        content += """

---

## 表结构详情

"""
        
        for table in tables:
            content += f"""
### {table.name}

**描述**: {table.description}

| 字段名 | 类型 | 可空 | 主键 | 默认值 | 描述 |
|--------|------|------|------|--------|------|
"""
            for col in table.columns:
                content += f"| {col.get('name', '')} | {col.get('type', '')} | {'是' if col.get('nullable', True) else '否'} | {'是' if col.get('primary', False) else '否'} | {col.get('default', '')} | {col.get('description', '')} |\n"
            
            if table.indexes:
                content += "\n**索引**:\n"
                for idx in table.indexes:
                    content += f"- {idx.get('name', '')}: {', '.join(idx.get('columns', []))}\n"
        
        content += f"""

---

## ER图

{mermaid_code}
```

---

*本文档由 Architect Agent 自动生成*
"""
        
        output_file = (output_path or DOCS_DIR) / f"{project_name}_数据库设计.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        mermaid_file = (output_path or DOCS_DIR) / f"{project_name}_er_diagram.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)
        
        print(f"✅ 数据库设计文档已生成: {output_file}")
        print(f"✅ Mermaid ER图已生成: {mermaid_file}")
        
        return str(output_file)
    
    def generate_api_doc(self, project_name: str,
                        endpoints: List[APIEndpoint],
                        models: List[APIModel],
                        output_path: Path = None) -> str:
        """生成API文档"""
        
        content = f"""# API接口文档

**项目名称**: {project_name}
**版本**: 1.0.0
**生成日期**: {datetime.now().strftime('%Y-%m-%d')}

---

## 概述

### 认证方式
- 认证方式: Bearer Token (JWT)
- 请求头: `Authorization: Bearer <token>`

### 响应格式
```json
{{
    "code": 0,
    "message": "success",
    "data": {{}}
}}
```

### 错误码
| 错误码 | 描述 |
|--------|------|
| 0 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

## 数据模型

"""
        
        for model in models:
            content += f"""
### {model.name}

{model.description}

| 字段名 | 类型 | 描述 |
|--------|------|------|
"""
            for field in model.fields:
                content += f"| {field.get('name', '')} | {field.get('type', '')} | {field.get('description', '')} |\n"
        
        content += """

---

## 接口列表

"""
        
        methods_emoji = {
            "GET": "📥",
            "POST": "📤",
            "PUT": "📝",
            "DELETE": "🗑️",
            "PATCH": "🔧"
        }
        
        for endpoint in endpoints:
            emoji = methods_emoji.get(endpoint.method, "📄")
            content += f"""
### {emoji} {endpoint.method} {endpoint.path}

**简要**: {endpoint.summary}
**描述**: {endpoint.description}
**标签**: {', '.join(endpoint.tags)}
**认证**: {'需要' if endpoint.auth_required else '不需要'}

**请求参数**:
| 参数名 | 位置 | 类型 | 必填 | 描述 |
|--------|------|------|------|------|
"""
            for param in endpoint.request_params:
                content += f"| {param.get('name', '')} | {param.get('in', 'query')} | {param.get('type', 'string')} | {'是' if param.get('required', False) else '否'} | {param.get('description', '')} |\n"
            
            if endpoint.request_body:
                content += f"\n**请求体**:\n```json\n{json.dumps(endpoint.request_body, ensure_ascii=False, indent=2)}\n```\n"
            
            content += f"\n**响应**:\n```json\n{json.dumps(endpoint.response, ensure_ascii=False, indent=2)}\n```\n"
        
        content += """

---

*本文档由 Architect Agent 自动生成*
"""
        
        output_file = (output_path or DOCS_DIR) / f"{project_name}_API文档.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ API文档已生成: {output_file}")
        return str(output_file)
    
    def generate_user_manual(self, project_name: str,
                           features: List[Dict],
                           output_path: Path = None) -> str:
        """生成用户手册"""
        
        content = f"""# {project_name} 用户手册

**版本**: 1.0.0
**更新日期**: {datetime.now().strftime('%Y-%m-%d')}

---

## 目录

1. 产品简介
2. 快速开始
3. 功能指南
4. 常见问题
5. 联系我们

---

## 1. 产品简介

{project_name} 是一款...

## 2. 快速开始

### 2.1 账号注册
1. 访问官方网站
2. 点击注册按钮
3. 填写信息
4. 完成验证

### 2.2 首次登录
1. 输入账号密码
2. 点击登录
3. 完成初始设置

---

## 3. 功能指南

"""
        
        for feature in features:
            content += f"""
### 3.{features.index(feature) + 1} {feature.get('name', '')}

{feature.get('description', '')}

**操作步骤**:
"""
            steps = feature.get('steps', [])
            for i, step in enumerate(steps, 1):
                content += f"{i}. {step}\n"
        
        content += """

---

## 4. 常见问题

**Q: 如何重置密码?**
A: 点击登录页的"忘记密码"链接。

**Q: 如何联系客服?**
A: 发送邮件至 support@example.com

---

## 5. 联系我们

- 客服热线: 400-xxx-xxxx
- 邮箱: support@example.com
- 地址: xxx市xxx区xxx大厦

---

*本文档由 Hotel Agent 自动生成*
"""
        
        output_file = (output_path or DOCS_DIR) / f"{project_name}_用户手册.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 用户手册已生成: {output_file}")
        return str(output_file)
    
    def generate_deploy_doc(self, project_name: str,
                           server_config: Dict,
                           env_vars: Dict,
                           output_path: Path = None) -> str:
        """生成部署文档"""
        
        content = f"""# {project_name} 部署文档

**版本**: 1.0.0
**更新日期**: {datetime.now().strftime('%Y-%m-%d')}

---

## 1. 环境要求

### 1.1 硬件要求
- CPU: {server_config.get('cpu', '2核')}
- 内存: {server_config.get('memory', '4GB')}
- 磁盘: {server_config.get('disk', '50GB')}

### 1.2 软件要求
- 操作系统: {server_config.get('os', 'Ubuntu 20.04')}
- Docker: >= 20.10
- Docker Compose: >= 1.29

---

## 2. 环境变量

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
"""
        
        for key, value in env_vars.items():
            content += f"| {key} | {value.get('description', '')} | {value.get('example', '')} |\n"
        
        content += """
---

## 3. 部署步骤

### 3.1 拉取代码
```bash
git clone <repository-url>
cd project-directory
```

### 3.2 配置环境变量
```bash
cp .env.example .env
vim .env
```

### 3.3 启动服务
```bash
# Docker Compose 方式
docker-compose up -d

# 或 Kubernetes 方式
kubectl apply -f k8s/
```

### 3.4 验证部署
```bash
curl http://localhost:8080/health
```

---

## 4. 运维操作

### 4.1 查看日志
```bash
docker-compose logs -f
```

### 4.2 重启服务
```bash
docker-compose restart
```

### 4.3 备份数据
```bash
docker-compose exec db pg_dump -U user dbname > backup.sql
```

### 4.4 回滚
```bash
docker-compose down
git checkout <previous-version>
docker-compose up -d
```

---

## 5. 监控告警

### 5.1 监控指标
- CPU使用率
- 内存使用率
- 磁盘使用率
- 请求延迟

### 5.2 告警规则
- 错误率 > 5%
- 响应时间 > 500ms
- 磁盘使用率 > 80%

---

## 6. 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 服务启动失败 | 端口被占用 | 检查端口或修改配置 |
| 数据库连接失败 | 配置错误 | 检查环境变量 |
| 页面加载慢 | 网络问题 | 检查CDN配置 |

---

*本文档由 Kilo Agent 自动生成*
"""
        
        output_file = (output_path or DOCS_DIR) / f"{project_name}_部署文档.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 部署文档已生成: {output_file}")
        return str(output_file)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='文档生成器 v2.0')
    parser.add_argument('--prd', type=str, help='生成PRD文档')
    parser.add_argument('--architecture', type=str, help='生成架构文档')
    parser.add_argument('--api', type=str, help='生成API文档')
    parser.add_argument('--er', type=str, help='生成ER图')
    parser.add_argument('--manual', type=str, help='生成用户手册')
    parser.add_argument('--deploy', type=str, help='生成部署文档')
    parser.add_argument('--output', type=str, help='输出目录')
    
    args = parser.parse_args()
    
    generator = DocumentGenerator()
    output_path = Path(args.output) if args.output else None
    
    if args.prd:
        requirements = [
            Requirement("REQ-001", "用户注册", "用户可以注册账号", "P0", "用户模块"),
            Requirement("REQ-002", "用户登录", "用户可以登录系统", "P0", "用户模块"),
        ]
        user_stories = [
            UserStory("US-001", "用户", "注册账号", "使用系统功能", "P0"),
        ]
        generator.generate_prd(args.prd, "项目描述", requirements, user_stories, output_path)
    
    elif args.architecture:
        modules = [{"name": "用户模块", "description": "用户管理", "responsibility": "用户CRUD"}]
        tech_stack = {"frontend": {"Vue": "3.x"}, "backend": {"Python": "3.10"}}
        generator.generate_architecture_doc(args.architecture, modules, tech_stack, output_path)
    
    elif args.api:
        endpoints = [
            APIEndpoint("/api/users", "GET", "获取用户列表", tags=["用户"])
        ]
        models = [APIModel("User", [{"name": "id", "type": "int"}, {"name": "name", "type": "string"}])]
        generator.generate_api_doc(args.api, endpoints, models, output_path)
    
    elif args.er:
        tables = [DatabaseTable("users", "用户表", [
            {"name": "id", "type": "INT", "primary": True},
            {"name": "name", "type": "VARCHAR(100)"}
        ])]
        generator.generate_er_diagram(args.er, tables, output_path)
    
    elif args.manual:
        features = [{"name": "用户注册", "description": "注册新用户", "steps": ["填写信息", "点击注册"]}]
        generator.generate_user_manual(args.manual, features, output_path)
    
    elif args.deploy:
        server_config = {"cpu": "4核", "memory": "8GB"}
        env_vars = {"DB_HOST": {"description": "数据库地址", "example": "localhost"}}
        generator.generate_deploy_doc(args.deploy, server_config, env_vars, output_path)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
