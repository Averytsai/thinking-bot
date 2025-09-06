#!/bin/bash

# 部署前檢查腳本
set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# 檢查必要文件
check_required_files() {
    log_header "檢查必要文件"
    
    local files=(
        "docker-compose.prod.yml"
        "Dockerfile.prod"
        "nginx/nginx.conf"
        "deploy.sh"
        "monitor.sh"
        "env.production.example"
        "LINODE_DEPLOYMENT.md"
        "BRANCH_STRATEGY.md"
        "GITHUB_SETUP.md"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "✓ $file ${GREEN}存在${NC}"
        else
            echo -e "✗ $file ${RED}不存在${NC}"
            return 1
        fi
    done
    
    log_info "所有必要文件檢查通過"
}

# 檢查環境變數文件
check_env_files() {
    log_header "檢查環境變數文件"
    
    if [ -f ".env.production" ]; then
        log_info "生產環境變數文件存在"
        
        # 檢查必要的環境變數
        local required_vars=(
            "DB_PASSWORD"
            "REDIS_PASSWORD"
            "OPENAI_API_KEY"
            "LINE_CHANNEL_ACCESS_TOKEN"
            "LINE_CHANNEL_SECRET"
        )
        
        for var in "${required_vars[@]}"; do
            if grep -q "^${var}=" .env.production && ! grep -q "^${var}=your_" .env.production; then
                echo -e "✓ $var ${GREEN}已設定${NC}"
            else
                echo -e "✗ $var ${RED}未設定或使用預設值${NC}"
                return 1
            fi
        done
    else
        log_warn "生產環境變數文件不存在，請複製範例文件："
        log_warn "cp env.production.example .env.production"
        return 1
    fi
}

# 檢查Docker
check_docker() {
    log_header "檢查Docker環境"
    
    if command -v docker > /dev/null 2>&1; then
        echo -e "✓ Docker ${GREEN}已安裝${NC}"
        docker --version
    else
        echo -e "✗ Docker ${RED}未安裝${NC}"
        return 1
    fi
    
    if command -v docker-compose > /dev/null 2>&1; then
        echo -e "✓ Docker Compose ${GREEN}已安裝${NC}"
        docker-compose --version
    else
        echo -e "✗ Docker Compose ${RED}未安裝${NC}"
        return 1
    fi
}

# 檢查SSL證書
check_ssl_certs() {
    log_header "檢查SSL證書"
    
    if [ -f "nginx/ssl/cert.pem" ] && [ -f "nginx/ssl/key.pem" ]; then
        log_info "SSL證書存在"
        
        # 檢查證書有效期
        local expiry=$(openssl x509 -in nginx/ssl/cert.pem -noout -enddate | cut -d= -f2)
        echo "證書有效期至: $expiry"
    else
        log_warn "SSL證書不存在，部署時會自動生成自簽證書"
    fi
}

# 檢查Git狀態
check_git_status() {
    log_header "檢查Git狀態"
    
    if [ -d ".git" ]; then
        echo -e "✓ Git倉庫 ${GREEN}已初始化${NC}"
        
        # 檢查當前分支
        local current_branch=$(git branch --show-current)
        echo "當前分支: $current_branch"
        
        # 檢查是否有未提交的更改
        if git diff --quiet; then
            echo -e "✓ 工作目錄 ${GREEN}乾淨${NC}"
        else
            echo -e "✗ 工作目錄 ${RED}有未提交的更改${NC}"
            git status --short
            return 1
        fi
        
        # 檢查遠端倉庫
        if git remote -v | grep -q "origin"; then
            echo -e "✓ 遠端倉庫 ${GREEN}已設定${NC}"
            git remote -v
        else
            echo -e "✗ 遠端倉庫 ${RED}未設定${NC}"
            log_warn "請按照GITHUB_SETUP.md設定遠端倉庫"
        fi
    else
        echo -e "✗ Git倉庫 ${RED}未初始化${NC}"
        return 1
    fi
}

# 檢查端口占用
check_ports() {
    log_header "檢查端口占用"
    
    local ports=(80 443 8000 5432 6379)
    
    for port in "${ports[@]}"; do
        if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
            echo -e "✗ 端口 $port ${RED}已被占用${NC}"
            netstat -tlnp | grep ":$port "
        else
            echo -e "✓ 端口 $port ${GREEN}可用${NC}"
        fi
    done
}

# 檢查系統資源
check_system_resources() {
    log_header "檢查系統資源"
    
    # 檢查記憶體
    local total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ "$total_mem" -ge 2048 ]; then
        echo -e "✓ 記憶體 ${GREEN}充足${NC} (${total_mem}MB)"
    else
        echo -e "✗ 記憶體 ${RED}不足${NC} (${total_mem}MB，建議至少2GB)"
    fi
    
    # 檢查磁碟空間
    local disk_usage=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 80 ]; then
        echo -e "✓ 磁碟空間 ${GREEN}充足${NC} (使用率: ${disk_usage}%)"
    else
        echo -e "✗ 磁碟空間 ${RED}不足${NC} (使用率: ${disk_usage}%)"
    fi
}

# 主函數
main() {
    log_info "開始部署前檢查..."
    
    local errors=0
    
    check_required_files || ((errors++))
    echo ""
    check_env_files || ((errors++))
    echo ""
    check_docker || ((errors++))
    echo ""
    check_ssl_certs || ((errors++))
    echo ""
    check_git_status || ((errors++))
    echo ""
    check_ports || ((errors++))
    echo ""
    check_system_resources || ((errors++))
    
    echo ""
    if [ $errors -eq 0 ]; then
        log_info "✅ 所有檢查通過！可以開始部署"
        log_info "執行以下命令開始部署："
        log_info "  ./deploy.sh"
    else
        log_error "❌ 發現 $errors 個問題，請先解決這些問題再部署"
        log_info "請參考相關文檔："
        log_info "  - LINODE_DEPLOYMENT.md (部署指南)"
        log_info "  - GITHUB_SETUP.md (GitHub設定)"
        log_info "  - BRANCH_STRATEGY.md (分支策略)"
    fi
}

# 執行主函數
main "$@"
