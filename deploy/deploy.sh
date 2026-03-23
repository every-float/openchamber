#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi

    log_success "Docker environment check passed"
}

docker_compose_cmd() {
    if docker compose version &> /dev/null; then
        docker compose "$@"
    else
        docker-compose "$@"
    fi
}

create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p "${PROJECT_ROOT}/data/openchamber"
    mkdir -p "${PROJECT_ROOT}/data/opencode/share"
    mkdir -p "${PROJECT_ROOT}/data/opencode/state"
    mkdir -p "${PROJECT_ROOT}/data/opencode/config"
    mkdir -p "${PROJECT_ROOT}/data/ssh"
    mkdir -p "${PROJECT_ROOT}/workspaces"
    
    log_success "Directories created"
}

build_image() {
    log_info "Building Docker image..."
    cd "${PROJECT_ROOT}"
    docker_compose_cmd build --no-cache
    log_success "Docker image built successfully"
}

start_service() {
    log_info "Starting OpenChamber service..."
    cd "${PROJECT_ROOT}"
    docker_compose_cmd up -d
    log_success "OpenChamber service started"
}

stop_service() {
    log_info "Stopping OpenChamber service..."
    cd "${PROJECT_ROOT}"
    docker_compose_cmd down
    log_success "OpenChamber service stopped"
}

restart_service() {
    log_info "Restarting OpenChamber service..."
    stop_service
    start_service
    log_success "OpenChamber service restarted"
}

view_logs() {
    cd "${PROJECT_ROOT}"
    docker_compose_cmd logs -f
}

show_status() {
    log_info "OpenChamber service status:"
    cd "${PROJECT_ROOT}"
    docker_compose_cmd ps
}

show_help() {
    echo "OpenChamber Docker Deployment Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy    - Full deployment (build and start)"
    echo "  build     - Build Docker image"
    echo "  start     - Start service"
    echo "  stop      - Stop service"
    echo "  restart   - Restart service"
    echo "  logs      - View logs"
    echo "  status    - Show service status"
    echo "  help      - Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  UI_PASSWORD    - Set UI authentication password"
    echo "  CF_TUNNEL      - Enable Cloudflare Tunnel (true/qr/password)"
    echo "  OH_MY_OPENCODE - Enable oh-my-opencode (true)"
    echo ""
    echo "Examples:"
    echo "  $0 deploy                    # Deploy with default settings"
    echo "  UI_PASSWORD=mypassword $0 deploy  # Deploy with password protection"
}

full_deploy() {
    log_info "Starting full deployment..."
    check_docker
    create_directories
    build_image
    start_service
    
    echo ""
    log_success "=========================================="
    log_success "OpenChamber deployed successfully!"
    log_success "=========================================="
    echo ""
    log_info "Access OpenChamber at: http://localhost:59998"
    echo ""
    log_info "Useful commands:"
    echo "  View logs:     $0 logs"
    echo "  Stop service:  $0 stop"
    echo "  Restart:       $0 restart"
    echo "  Status:        $0 status"
    echo ""
}

main() {
    local command="${1:-deploy}"
    
    case "$command" in
        deploy)
            full_deploy
            ;;
        build)
            check_docker
            build_image
            ;;
        start)
            check_docker
            create_directories
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        logs)
            view_logs
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
