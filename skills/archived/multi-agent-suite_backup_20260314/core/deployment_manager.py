#!/usr/bin/env python3
"""
多Agent部署管理模块 v2.0
支持部署、回滚、健康检查、监控告警
"""

import os
import json
import uuid
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod

SUITE_DIR = Path("~/.openclaw/workspace/skills/multi-agent-suite").expanduser()
DEPLOY_DIR = SUITE_DIR / "deployments"
DEPLOY_DIR.mkdir(parents=True, exist_ok=True)


class DeployStatus(Enum):
    """部署状态"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACK = "rollback"


class DeployType(Enum):
    """部署类型"""
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    SERVER = "server"
    SERVERLESS = "serverless"


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class ServerConfig:
    """服务器配置"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    host: str = ""
    port: int = 22
    user: str = "root"
    ssh_key: str = ""
    env_vars: Dict = field(default_factory=dict)
    capacity: str = ""


@dataclass
class DeploymentConfig:
    """部署配置"""
    project_name: str = ""
    version: str = "1.0.0"
    deploy_type: DeployType = DeployType.DOCKER
    image: str = ""
    container_name: str = ""
    port_mapping: Dict = field(default_factory=dict)
    volumes: List[str] = field(default_factory=list)
    environment: Dict = field(default_factory=dict)
    health_check: Dict = field(default_factory=dict)
    resources: Dict = field(default_factory=dict)


@dataclass
class Deployment:
    """部署记录"""
    id: str = field(default_factory=lambda: f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    project_name: str = ""
    version: str = "1.0.0"
    status: DeployStatus = DeployStatus.PENDING
    server_id: str = ""
    config: DeploymentConfig = field(default_factory=DeploymentConfig)
    
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration: float = 0.0
    
    logs: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    
    rollback_from: Optional[str] = None
    error_message: str = ""
    
    deployed_by: str = ""


@dataclass
class HealthCheck:
    """健康检查结果"""
    service: str = ""
    status: HealthStatus = HealthStatus.UNKNOWN
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    response_time: float = 0.0
    details: Dict = field(default_factory=dict)


class DeployStrategy(ABC):
    """部署策略基类"""
    
    @abstractmethod
    def deploy(self, deployment: Deployment, server: ServerConfig) -> bool:
        pass
    
    @abstractmethod
    def rollback(self, deployment: Deployment) -> bool:
        pass
    
    @abstractmethod
    def health_check(self, server: ServerConfig, config: DeploymentConfig) -> HealthCheck:
        pass


class DockerDeployStrategy(DeployStrategy):
    """Docker部署策略"""
    
    def deploy(self, deployment: Deployment, server: ServerConfig) -> bool:
        config = deployment.config
        
        commands = [
            f"docker pull {config.image}",
            f"docker stop {config.container_name} || true",
            f"docker rm {config.container_name} || true",
        ]
        
        port_mappings = " ".join([f"-p {host}:{container}" for host, container in config.port_mapping.items()])
        env_vars = " ".join([f"-e {k}={v}" for k, v in config.environment.items()])
        
        run_cmd = f"docker run -d {port_mappings} {env_vars} --name {config.container_name} {config.image}"
        commands.append(run_cmd)
        
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                deployment.logs.append(f"命令失败: {cmd}")
                deployment.logs.append(result.stderr)
                return False
        
        deployment.logs.extend(commands)
        return True
    
    def rollback(self, deployment: Deployment) -> bool:
        if deployment.rollback_from:
            config = deployment.config
            commands = [
                f"docker stop {config.container_name} || true",
                f"docker rm {config.container_name} || true",
                f"docker run -d {'-p 8080:8080' if config.port_mapping else ''} --name {config.container_name} {deployment.rollback_from}"
            ]
            
            for cmd in commands:
                subprocess.run(cmd, shell=True, capture_output=True)
            
            return True
        return False
    
    def health_check(self, server: ServerConfig, config: DeploymentConfig) -> HealthCheck:
        port = config.port_mapping.get(8080, 8080)
        url = f"http://{server.host}:{port}/health"
        
        import time
        start = time.time()
        
        try:
            result = subprocess.run(
                f"curl -s -o /dev/null -w '%{{http_code}}' {url}",
                shell=True, capture_output=True, text=True, timeout=5
            )
            response_time = time.time() - start
            
            http_code = result.stdout.strip()
            status = HealthStatus.HEALTHY if http_code == "200" else HealthStatus.UNHEALTHY
            
            return HealthCheck(
                service=config.project_name,
                status=status,
                response_time=response_time,
                details={"http_code": http_code, "url": url}
            )
        except Exception as e:
            return HealthCheck(
                service=config.project_name,
                status=HealthStatus.UNKNOWN,
                details={"error": str(e)}
            )


class KubernetesDeployStrategy(DeployStrategy):
    """Kubernetes部署策略"""
    
    def deploy(self, deployment: Deployment, server: ServerConfig) -> bool:
        config = deployment.config
        
        yaml_content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {config.project_name}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {config.project_name}
  template:
    metadata:
      labels:
        app: {config.project_name}
    spec:
      containers:
      - name: {config.project_name}
        image: {config.image}
        ports:
        - containerPort: 8080
        env:
"""
        for k, v in config.environment.items():
            yaml_content += f"        - name: {k}\n          value: {v}\n"
        
        yaml_content += f"""---
apiVersion: v1
kind: Service
metadata:
  name: {config.project_name}
spec:
  selector:
    app: {config.project_name}
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
"""
        
        deploy_file = DEPLOY_DIR / f"{config.project_name}-deployment.yaml"
        with open(deploy_file, 'w') as f:
            f.write(yaml_content)
        
        commands = [
            f"kubectl apply -f {deploy_file}",
            f"kubectl rollout status deployment/{config.project_name}"
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            deployment.logs.append(f"{cmd}: {result.stdout}")
            if result.returncode != 0:
                deployment.logs.append(f"错误: {result.stderr}")
                return False
        
        return True
    
    def rollback(self, deployment: Deployment) -> bool:
        config = deployment.config
        cmd = f"kubectl rollout undo deployment/{config.project_name}"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    
    def health_check(self, server: ServerConfig, config: DeploymentConfig) -> HealthCheck:
        cmd = f"kubectl get pods -l app={config.project_name} -o jsonpath='{{.items[*].status.phase}}'"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        pods_status = result.stdout.strip()
        
        status = HealthStatus.HEALTHY if "Running" in pods_status else HealthStatus.UNHEALTHY
        
        return HealthCheck(
            service=config.project_name,
            status=status,
            details={"pods": pods_status}
        )


class DeploymentManager:
    """部署管理器"""
    
    def __init__(self):
        self.deployments: Dict[str, Deployment] = {}
        self.servers: Dict[str, ServerConfig] = {}
        self.strategies: Dict[DeployType, DeployStrategy] = {
            DeployType.DOCKER: DockerDeployStrategy(),
            DeployType.KUBERNETES: KubernetesDeployStrategy()
        }
        
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        deployments_file = DEPLOY_DIR / "deployments.json"
        servers_file = DEPLOY_DIR / "servers.json"
        
        if deployments_file.exists():
            with open(deployments_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for dep_id, dep_data in data.items():
                    self.deployments[dep_id] = Deployment(**dep_data)
        
        if servers_file.exists():
            with open(servers_file, 'r', encoding='utf-8') as f:
                self.servers = {s['id']: ServerConfig(**s) for s in json.load(f)}
    
    def save_data(self):
        """保存数据"""
        deployments_file = DEPLOY_DIR / "deployments.json"
        servers_file = DEPLOY_DIR / "servers.json"
        
        with open(deployments_file, 'w', encoding='utf-8') as f:
            json.dump({k: asdict(v) for k, v in self.deployments.items()}, f, ensure_ascii=False, indent=2)
        
        with open(servers_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(s) for s in self.servers.values()], f, ensure_ascii=False, indent=2)
    
    def add_server(self, name: str, host: str, port: int = 22, 
                   user: str = "root", env_vars: Dict = None) -> str:
        """添加服务器"""
        server = ServerConfig(
            name=name,
            host=host,
            port=port,
            user=user,
            env_vars=env_vars or {}
        )
        
        self.servers[server.id] = server
        self.save_data()
        
        print(f"✅ 添加服务器: {name} ({host})")
        return server.id
    
    def list_servers(self) -> List[ServerConfig]:
        """列出服务器"""
        return list(self.servers.values())
    
    def create_deployment(self, project_name: str, version: str,
                         deploy_type: DeployType,
                         config: DeploymentConfig) -> str:
        """创建部署"""
        deployment = Deployment(
            project_name=project_name,
            version=version,
            config=config
        )
        
        self.deployments[deployment.id] = deployment
        self.save_data()
        
        print(f"✅ 创建部署: {project_name} v{version}")
        return deployment.id
    
    def execute_deploy(self, deployment_id: str, server_id: str) -> bool:
        """执行部署"""
        deployment = self.deployments.get(deployment_id)
        server = self.servers.get(server_id)
        
        if not deployment or not server:
            print("❌ 部署或服务器不存在")
            return False
        
        deployment.status = DeployStatus.DEPLOYING
        deployment.server_id = server_id
        deployment.started_at = datetime.now().isoformat()
        
        strategy = self.strategies.get(deployment.config.deploy_type)
        if not strategy:
            deployment.error_message = f"不支持的部署类型: {deployment.config.deploy_type}"
            deployment.status = DeployStatus.FAILED
            self.save_data()
            return False
        
        try:
            success = strategy.deploy(deployment, server)
            
            if success:
                deployment.status = DeployStatus.SUCCESS
                deployment.completed_at = datetime.now().isoformat()
                
                if deployment.started_at:
                    start = datetime.fromisoformat(deployment.started_at)
                    deployment.duration = (datetime.now() - start).total_seconds()
                
                print(f"✅ 部署成功: {deployment_id}")
            else:
                deployment.status = DeployStatus.FAILED
                deployment.error_message = "部署命令执行失败"
                print(f"❌ 部署失败: {deployment_id}")
            
            self.save_data()
            return success
            
        except Exception as e:
            deployment.status = DeployStatus.FAILED
            deployment.error_message = str(e)
            deployment.logs.append(f"异常: {str(e)}")
            self.save_data()
            print(f"❌ 部署异常: {e}")
            return False
    
    def rollback(self, deployment_id: str) -> bool:
        """回滚部署"""
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            print("❌ 部署不存在")
            return False
        
        if not deployment.rollback_from:
            print("❌ 没有可回滚的版本")
            return False
        
        deployment.status = DeployStatus.ROLLBACK
        
        strategy = self.strategies.get(deployment.config.deploy_type)
        if strategy:
            success = strategy.rollback(deployment)
            if success:
                deployment.status = DeployStatus.SUCCESS
                print(f"✅ 回滚成功: {deployment_id}")
            else:
                deployment.status = DeployStatus.FAILED
                print(f"❌ 回滚失败: {deployment_id}")
            
            self.save_data()
            return success
        
        return False
    
    def health_check(self, deployment_id: str) -> HealthCheck:
        """健康检查"""
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            return HealthCheck(status=HealthStatus.UNKNOWN)
        
        server = self.servers.get(deployment.server_id)
        if not server:
            return HealthCheck(status=HealthStatus.UNKNOWN)
        
        strategy = self.strategies.get(deployment.config.deploy_type)
        if strategy:
            return strategy.health_check(server, deployment.config)
        
        return HealthCheck(status=HealthStatus.UNKNOWN)
    
    def get_deployment_status(self, deployment_id: str) -> Dict:
        """获取部署状态"""
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            return {"error": "部署不存在"}
        
        health = self.health_check(deployment_id)
        
        return {
            "id": deployment.id,
            "project_name": deployment.project_name,
            "version": deployment.version,
            "status": deployment.status.value,
            "server_id": deployment.server_id,
            "started_at": deployment.started_at,
            "completed_at": deployment.completed_at,
            "duration": deployment.duration,
            "health": health.status.value,
            "error": deployment.error_message
        }
    
    def list_deployments(self, project_name: str = None) -> List[Deployment]:
        """列出部署"""
        if project_name:
            return [d for d in self.deployments.values() if d.project_name == project_name]
        return list(self.deployments.values())
    
    def generate_deploy_script(self, deployment_id: str) -> str:
        """生成部署脚本"""
        deployment = self.deployments.get(deployment_id)
        
        if not deployment:
            return ""
        
        config = deployment.config
        
        script = f"""#!/bin/bash
# {config.project_name} 部署脚本
# 版本: {config.version}
# 生成时间: {datetime.now().isoformat()}

set -e

PROJECT_NAME="{config.project_name}"
IMAGE="{config.image}"
VERSION="{config.version}"

echo "=== 开始部署 $PROJECT_NAME v$VERSION ==="

# 拉取镜像
echo "拉取镜像..."
docker pull $IMAGE

# 停止旧容器
echo "停止旧容器..."
docker stop {config.container_name} || true
docker rm {config.container_name} || true

# 启动新容器
echo "启动新容器..."
docker run -d \\
    --name {config.container_name} \\
    -p 8080:8080 \\
"""
        
        for k, v in config.environment.items():
            script += f'    -e {k}="{v}" \\\n'
        
        script += """    $IMAGE

# 健康检查
echo "执行健康检查..."
sleep 5
curl -f http://localhost:8080/health || exit 1

echo "=== 部署完成 ==="
"""
        
        script_file = DEPLOY_DIR / f"{deployment_id}_deploy.sh"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return str(script_file)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='部署管理器 v2.0')
    parser.add_argument('--deploy', action='store_true', help='执行部署')
    parser.add_argument('--rollback', type=str, help='回滚部署')
    parser.add_argument('--health', type=str, help='健康检查')
    parser.add_argument('--list', action='store_true', help='列出部署')
    parser.add_argument('--status', type=str, help='查看部署状态')
    parser.add_argument('--script', type=str, help='生成部署脚本')
    parser.add_argument('--add-server', nargs=2, help='添加服务器')
    
    args = parser.parse_args()
    
    manager = DeploymentManager()
    
    if args.add_server:
        name, host = args.add_server
        manager.add_server(name, host)
    
    elif args.list:
        deps = manager.list_deployments()
        print("\n📋 部署列表:")
        print("-" * 80)
        for d in deps:
            print(f"{d.id:<25} {d.project_name:<20} {d.version:<10} {d.status.value}")
        print("-" * 80)
    
    elif args.status:
        status = manager.get_deployment_status(args.status)
        if "error" in status:
            print(f"❌ {status['error']}")
        else:
            print(f"\n📊 部署状态:")
            for k, v in status.items():
                print(f"  {k}: {v}")
    
    elif args.health:
        health = manager.health_check(args.health)
        print(f"\n🏥 健康检查: {health.status.value}")
        print(f"  响应时间: {health.response_time}ms")
    
    elif args.script:
        script_path = manager.generate_deploy_script(args.script)
        print(f"✅ 部署脚本已生成: {script_path}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
