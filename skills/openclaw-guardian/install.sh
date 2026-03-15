#!/bin/bash
# OpenClaw Guardian 安装脚本
# ===========================

set -e

echo "=============================================="
echo "OpenClaw Guardian 安装程序"
echo "=============================================="
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python版本
echo "[1/6] 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}错误: 需要Python $required_version 或更高版本${NC}"
    echo "当前版本: $python_version"
    exit 1
fi

echo -e "${GREEN}✓ Python版本检查通过: $python_version${NC}"
echo

# 检查pip
echo "[2/6] 检查pip..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}错误: 未找到pip3${NC}"
    exit 1
fi

echo -e "${GREEN}✓ pip3已安装${NC}"
echo

# 安装依赖
echo "[3/6] 安装依赖..."
pip3 install -q psutil pyyaml

echo -e "${GREEN}✓ 依赖安装完成${NC}"
echo

# 创建目录结构
echo "[4/6] 创建目录结构..."
mkdir -p logs
mkdir -p reports
mkdir -p backups
mkdir -p config

echo -e "${GREEN}✓ 目录创建完成${NC}"
echo

# 复制配置文件
echo "[5/6] 设置配置文件..."
if [ ! -f "config/my_config.yaml" ]; then
    cp config/default_config.yaml config/my_config.yaml
    echo -e "${GREEN}✓ 配置文件已创建: config/my_config.yaml${NC}"
else
    echo -e "${YELLOW}⚠ 配置文件已存在，跳过${NC}"
fi
echo

# 设置权限
echo "[6/6] 设置权限..."
chmod +x main.py
chmod +x test_guardian.py

echo -e "${GREEN}✓ 权限设置完成${NC}"
echo

# 验证安装
echo "=============================================="
echo "验证安装..."
echo "=============================================="
echo

if python3 main.py --version &> /dev/null; then
    echo -e "${GREEN}✓ 安装成功！${NC}"
    echo
    echo "使用指南:"
    echo "  扫描技能包: python3 main.py scan <skill_path>"
    echo "  检查健康:   python3 main.py health"
    echo "  启动监控:   python3 main.py monitor"
    echo "  查看帮助:   python3 main.py --help"
    echo
    echo "运行测试: python3 test_guardian.py"
    echo
else
    echo -e "${RED}✗ 安装验证失败${NC}"
    exit 1
fi
