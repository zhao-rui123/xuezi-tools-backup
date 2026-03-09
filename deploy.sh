#!/bin/bash
#
# 一键部署脚本 - OpenClaw 智能助手系统
# 自动安装依赖、配置定时任务、创建必要目录
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    local missing_deps=()
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # 检查 pip
    if ! command -v pip3 &> /dev/null; then
        missing_deps+=("pip3")
    fi
    
    # 检查 OpenClaw
    if ! command -v openclaw &> /dev/null; then
        print_warning "OpenClaw 命令未找到，请确保已安装"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "缺少依赖: ${missing_deps[*]}"
        print_info "请安装: brew install python3"
        exit 1
    fi
    
    print_success "依赖检查通过"
}

# 安装 Python 依赖
install_python_deps() {
    print_info "安装 Python 依赖..."
    
    local deps=(
        "requests"
        "pandas"
        "openpyxl"
        "python-docx"
    )
    
    for dep in "${deps[@]}"; do
        pip3 install --user "$dep" -q 2>/dev/null || true
    done
    
    print_success "Python 依赖安装完成"
}

# 创建目录结构
create_directories() {
    print_info "创建目录结构..."
    
    local dirs=(
        "$HOME/.openclaw/workspace/memory/archive"
        "$HOME/.openclaw/workspace/memory/permanent"
        "$HOME/.openclaw/workspace/memory/index"
        "$HOME/.openclaw/workspace/memory/knowledge_graph"
        "$HOME/.openclaw/workspace/memory/evolution"
        "$HOME/.openclaw/workspace/knowledge-base/projects"
        "$HOME/.openclaw/workspace/knowledge-base/decisions"
        "$HOME/.openclaw/workspace/knowledge-base/references"
        "$HOME/.openclaw/workspace/logs"
        "$HOME/.openclaw/workspace/dashboard"
        "$HOME/.openclaw/workspace/tmp/screenshots"
        "$HOME/.openclaw/workspace/tmp/downloads"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
    done
    
    print_success "目录结构创建完成"
}

# 设置权限
set_permissions() {
    print_info "设置权限..."
    
    # 设置脚本权限
    find "$HOME/.openclaw/workspace/skills" -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
    find "$HOME/.openclaw/workspace/skills" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    
    print_success "权限设置完成"
}

# 配置定时任务
setup_cron() {
    print_info "配置定时任务..."
    
    # 创建临时 crontab 文件
    local temp_cron=$(mktemp)
    
    # 获取当前 crontab
    crontab -l > "$temp_cron" 2>/dev/null || echo "# 新的 crontab" > "$temp_cron"
    
    # 检查是否已有我们的任务
    if grep -q "OpenClaw Automation" "$temp_cron"; then
        print_warning "定时任务已存在，跳过"
        rm "$temp_cron"
        return
    fi
    
    # 添加定时任务
    cat >> "$temp_cron" << 'EOF'

# OpenClaw Automation - 智能助手系统定时任务
# 统一记忆系统 (每天 01:00)
0 1 * * * $HOME/.openclaw/workspace/skills/unified-memory/cron_tasks.sh >> /tmp/unified-memory-cron.log 2>&1

# 每日健康检查 (每天 09:00)
0 9 * * * $HOME/.openclaw/workspace/skills/system-maintenance/daily-health-check.sh >> /tmp/daily-health.log 2>&1

# 系统维护 (每周日 02:00)
0 2 * * 0 $HOME/.openclaw/workspace/skills/system-maintenance/system-maintenance.sh >> /tmp/system-maintenance.log 2>&1

# 监控告警 (每 6 小时)
0 */6 * * * $HOME/.openclaw/workspace/skills/monitoring-alert/alert_system.py --run >> /tmp/alert-system.log 2>&1

# 文档自动化 (每周一 03:00)
0 3 * * 1 $HOME/.openclaw/workspace/skills/doc-automation/doc_automation.py >> /tmp/doc-automation.log 2>&1

# OpenClaw Automation END
EOF
    
    # 应用 crontab
    crontab "$temp_cron"
    rm "$temp_cron"
    
    print_success "定时任务配置完成"
}

# 验证安装
verify_installation() {
    print_info "验证安装..."
    
    local errors=()
    
    # 检查关键技能包
    local required_skills=(
        "unified-memory"
        "self-improvement"
        "cron-manager"
        "monitoring-alert"
        "dashboard"
    )
    
    for skill in "${required_skills[@]}"; do
        if [ ! -d "$HOME/.openclaw/workspace/skills/$skill" ]; then
            errors+=("缺少技能包: $skill")
        fi
    done
    
    # 检查关键脚本
    if [ ! -f "$HOME/.openclaw/workspace/skills/unified-memory/cron_tasks.sh" ]; then
        errors+=("缺少统一记忆系统定时任务脚本")
    fi
    
    if [ ${#errors[@]} -eq 0 ]; then
        print_success "验证通过"
        return 0
    else
        print_error "验证失败:"
        for error in "${errors[@]}"; do
            echo "  - $error"
        done
        return 1
    fi
}

# 生成配置模板
generate_config_template() {
    print_info "生成配置模板..."
    
    local config_file="$HOME/.openclaw/workspace/config.json"
    
    if [ -f "$config_file" ]; then
        print_warning "配置文件已存在，跳过"
        return
    fi
    
    cat > "$config_file" << 'EOF'
{
  "user": {
    "name": "[你的名称]",
    "timezone": "Asia/Shanghai"
  },
  "server": {
    "ip": "[你的服务器IP]",
    "user": "root",
    "website_dir": "/usr/share/nginx/html"
  },
  "feishu": {
    "user_id": "[你的飞书用户ID]"
  },
  "stocks": {
    "watchlist": [
      {"code": "000001", "name": "平安银行", "market": "A股"}
    ]
  }
}
EOF
    
    print_success "配置模板已生成: $config_file"
    print_warning "请编辑配置文件，替换占位符"
}

# 主函数
main() {
    echo "========================================"
    echo "🚀 OpenClaw 智能助手系统 - 一键部署"
    echo "========================================"
    echo ""
    
    # 确认
    read -p "是否开始部署? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 0
    fi
    
    # 执行步骤
    check_dependencies
    install_python_deps
    create_directories
    set_permissions
    setup_cron
    generate_config_template
    
    # 验证
    if verify_installation; then
        echo ""
        echo "========================================"
        echo "✅ 部署成功!"
        echo "========================================"
        echo ""
        echo "下一步:"
        echo "1. 编辑配置文件: ~/.openclaw/workspace/config.json"
        echo "2. 运行数据看板: python3 ~/.openclaw/workspace/skills/dashboard/dashboard.py"
        echo "3. 查看定时任务: crontab -l"
        echo ""
        echo "系统将在每天 01:00 自动运行"
    else
        echo ""
        echo "========================================"
        echo "⚠️  部署完成但有警告"
        echo "========================================"
        echo ""
        echo "请检查上述错误"
    fi
}

# 运行主函数
main
