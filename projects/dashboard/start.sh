#!/bin/bash
# 系统监控看板启动脚本
# 一键启动所有服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
PID_DIR="${SCRIPT_DIR}/pids"
DATA_DIR="${SCRIPT_DIR}/data"
PORT=8080

# 创建必要目录
mkdir -p "${LOG_DIR}" "${PID_DIR}" "${DATA_DIR}"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 Python3，请先安装 Python 3.8+"
        exit 1
    fi
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "未找到 Node.js，请先安装 Node.js 16+"
        exit 1
    fi
    
    # 检查 nginx
    if ! command -v nginx &> /dev/null; then
        log_warning "未找到 nginx，将仅启动后端服务"
    fi
    
    log_success "依赖检查通过"
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."
    
    cd "${SCRIPT_DIR}/backend"
    
    # 检查虚拟环境
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        log_info "创建 Python 虚拟环境..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
    
    # 启动服务
    nohup python3 app.py > "${LOG_DIR}/backend.log" 2>&1 &
    echo $! > "${PID_DIR}/backend.pid"
    
    log_success "后端服务已启动 (PID: $(cat "${PID_DIR}/backend.pid"))"
    log_info "后端日志: ${LOG_DIR}/backend.log"
}

# 启动前端服务
start_frontend() {
    log_info "启动前端服务..."
    
    cd "${SCRIPT_DIR}/frontend"
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install
    fi
    
    # 构建前端
    log_info "构建前端..."
    npm run build
    
    log_success "前端构建完成"
}

# 配置 nginx
setup_nginx() {
    log_info "配置 nginx..."
    
    if ! command -v nginx &> /dev/null; then
        log_warning "nginx 未安装，跳过 nginx 配置"
        return
    fi
    
    # 检查是否有自定义 nginx 配置
    if [ -f "${SCRIPT_DIR}/nginx.conf" ]; then
        log_info "使用自定义 nginx 配置..."
        
        # 备份原配置
        if [ -f "/etc/nginx/nginx.conf" ]; then
            sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)
        fi
        
        # 复制配置（需要根据实际情况修改）
        log_warning "请手动将 nginx.conf 复制到 /etc/nginx/conf.d/ 目录"
        log_info "命令: sudo cp ${SCRIPT_DIR}/nginx.conf /etc/nginx/conf.d/dashboard.conf"
    fi
    
    # 测试 nginx 配置
    sudo nginx -t && sudo nginx -s reload || log_warning "nginx 配置测试失败"
}

# 启动服务
start_services() {
    log_info "启动系统监控看板服务..."
    
    # 检查是否已在运行
    if [ -f "${PID_DIR}/backend.pid" ]; then
        OLD_PID=$(cat "${PID_DIR}/backend.pid")
        if ps -p "${OLD_PID}" > /dev/null 2>&1; then
            log_warning "后端服务已在运行 (PID: ${OLD_PID})"
            log_info "如需重启，请先执行: ./start.sh stop"
            return
        fi
    fi
    
    check_dependencies
    start_backend
    start_frontend
    setup_nginx
    
    log_success "========================================"
    log_success "系统监控看板启动完成！"
    log_success "========================================"
    log_info "访问地址:"
    log_info "  - 本地访问: http://localhost:${PORT}"
    log_info "  - 如果有 nginx 代理: http://your-server-ip/"
    log_info ""
    log_info "管理命令:"
    log_info "  - 查看状态: ./start.sh status"
    log_info "  - 停止服务: ./start.sh stop"
    log_info "  - 重启服务: ./start.sh restart"
    log_info ""
    log_info "日志文件:"
    log_info "  - 后端日志: ${LOG_DIR}/backend.log"
}

# 停止服务
stop_services() {
    log_info "停止系统监控看板服务..."
    
    # 停止后端
    if [ -f "${PID_DIR}/backend.pid" ]; then
        PID=$(cat "${PID_DIR}/backend.pid")
        if ps -p "${PID}" > /dev/null 2>&1; then
            kill "${PID}"
            log_success "后端服务已停止 (PID: ${PID})"
        else
            log_warning "后端服务未在运行"
        fi
        rm -f "${PID_DIR}/backend.pid"
    fi
    
    log_success "所有服务已停止"
}

# 查看状态
show_status() {
    log_info "系统监控看板状态:"
    
    if [ -f "${PID_DIR}/backend.pid" ]; then
        PID=$(cat "${PID_DIR}/backend.pid")
        if ps -p "${PID}" > /dev/null 2>&1; then
            log_success "后端服务: 运行中 (PID: ${PID})"
        else
            log_error "后端服务: 未运行 (PID 文件存在但进程不存在)"
        fi
    else
        log_error "后端服务: 未运行"
    fi
    
    # 检查端口
    if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_success "端口 ${PORT}: 监听中"
    else
        log_error "端口 ${PORT}: 未监听"
    fi
}

# 显示帮助
show_help() {
    echo "系统监控看板启动脚本"
    echo ""
    echo "用法: ./start.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动所有服务 (默认)"
    echo "  stop      停止所有服务"
    echo "  restart   重启所有服务"
    echo "  status    查看服务状态"
    echo "  help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  ./start.sh           # 启动服务"
    echo "  ./start.sh start     # 启动服务"
    echo "  ./start.sh stop      # 停止服务"
    echo "  ./start.sh restart   # 重启服务"
    echo "  ./start.sh status    # 查看状态"
}

# 主函数
main() {
    case "${1:-start}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            start_services
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
