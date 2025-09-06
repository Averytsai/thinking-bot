#!/bin/bash

# 思考機器人生產環境部署腳本
set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 檢查環境變數文件
check_env_file() {
    if [ ! -f ".env.production" ]; then
        log_error "生產環境變數文件 .env.production 不存在"
        log_info "請複製 env.production.example 並設定正確的值："
        log_info "cp env.production.example .env.production"
        exit 1
    fi
    log_info "環境變數文件檢查通過"
}

# 檢查SSL證書
check_ssl_certs() {
    if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
        log_warn "SSL證書不存在，將使用自簽證書"
        generate_self_signed_cert
    else
        log_info "SSL證書檢查通過"
    fi
}

# 生成自簽SSL證書
generate_self_signed_cert() {
    log_info "生成自簽SSL證書..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=TW/ST=Taiwan/L=Taipei/O=Chatbot/CN=localhost"
    log_info "自簽SSL證書生成完成"
}

# 停止現有服務
stop_services() {
    log_info "停止現有服務..."
    docker-compose -f docker-compose.prod.yml down || true
    log_info "服務已停止"
}

# 構建和啟動服務
start_services() {
    log_info "構建和啟動服務..."
    docker-compose -f docker-compose.prod.yml --env-file .env.production up --build -d
    log_info "服務啟動完成"
}

# 等待服務就緒
wait_for_services() {
    log_info "等待服務就緒..."
    sleep 10
    
    # 檢查PostgreSQL
    for i in {1..30}; do
        if docker exec chatbot_postgres_prod pg_isready -U chatbot_user_prod > /dev/null 2>&1; then
            log_info "PostgreSQL 已就緒"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "PostgreSQL 啟動超時"
            exit 1
        fi
        sleep 2
    done
    
    # 檢查Redis
    for i in {1..30}; do
        if docker exec chatbot_redis_prod redis-cli ping > /dev/null 2>&1; then
            log_info "Redis 已就緒"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "Redis 啟動超時"
            exit 1
        fi
        sleep 2
    done
    
    # 檢查Web服務
    for i in {1..30}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_info "Web服務 已就緒"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "Web服務 啟動超時"
            exit 1
        fi
        sleep 2
    done
}

# 顯示服務狀態
show_status() {
    log_info "服務狀態："
    docker-compose -f docker-compose.prod.yml ps
    
    log_info "服務日誌："
    docker-compose -f docker-compose.prod.yml logs --tail=20
}

# 主函數
main() {
    log_info "開始部署思考機器人到生產環境..."
    
    check_env_file
    check_ssl_certs
    stop_services
    start_services
    wait_for_services
    show_status
    
    log_info "部署完成！"
    log_info "服務訪問地址："
    log_info "  HTTP:  http://localhost"
    log_info "  HTTPS: https://localhost"
    log_info "  健康檢查: https://localhost/health"
}

# 執行主函數
main "$@"