#!/bin/bash

# 思考機器人生產環境監控腳本
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

# 檢查服務狀態
check_services() {
    log_header "服務狀態檢查"
    
    # 檢查Docker容器
    echo "Docker容器狀態："
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    
    # 檢查服務健康狀態
    echo "服務健康檢查："
    
    # PostgreSQL
    if docker exec chatbot_postgres_prod pg_isready -U chatbot_user_prod > /dev/null 2>&1; then
        echo -e "PostgreSQL: ${GREEN}✓ 正常${NC}"
    else
        echo -e "PostgreSQL: ${RED}✗ 異常${NC}"
    fi
    
    # Redis
    if docker exec chatbot_redis_prod redis-cli ping > /dev/null 2>&1; then
        echo -e "Redis: ${GREEN}✓ 正常${NC}"
    else
        echo -e "Redis: ${RED}✗ 異常${NC}"
    fi
    
    # Web服務
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "Web服務: ${GREEN}✓ 正常${NC}"
    else
        echo -e "Web服務: ${RED}✗ 異常${NC}"
    fi
    
    # Nginx
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo -e "Nginx: ${GREEN}✓ 正常${NC}"
    else
        echo -e "Nginx: ${RED}✗ 異常${NC}"
    fi
}

# 檢查資源使用情況
check_resources() {
    log_header "資源使用情況"
    
    echo "容器資源使用："
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    echo ""
    echo "系統資源使用："
    echo "CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')%"
    echo "記憶體使用率: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
    echo "磁碟使用率: $(df -h / | awk 'NR==2{printf "%s", $5}')"
}

# 檢查日誌
check_logs() {
    log_header "最近日誌"
    
    echo "Web服務日誌 (最近20行)："
    docker-compose -f docker-compose.prod.yml logs --tail=20 web
    
    echo ""
    echo "Nginx日誌 (最近10行)："
    docker-compose -f docker-compose.prod.yml logs --tail=10 nginx
}

# 檢查資料庫狀態
check_database() {
    log_header "資料庫狀態"
    
    echo "資料庫連接數："
    docker exec chatbot_postgres_prod psql -U chatbot_user_prod -d chatbot_db_prod -c "SELECT count(*) as connections FROM pg_stat_activity;"
    
    echo ""
    echo "資料庫大小："
    docker exec chatbot_postgres_prod psql -U chatbot_user_prod -d chatbot_db_prod -c "SELECT pg_size_pretty(pg_database_size('chatbot_db_prod')) as database_size;"
    
    echo ""
    echo "表統計："
    docker exec chatbot_postgres_prod psql -U chatbot_user_prod -d chatbot_db_prod -c "
    SELECT 
        schemaname,
        tablename,
        n_tup_ins as inserts,
        n_tup_upd as updates,
        n_tup_del as deletes
    FROM pg_stat_user_tables 
    ORDER BY n_tup_ins DESC;"
}

# 檢查Redis狀態
check_redis() {
    log_header "Redis狀態"
    
    echo "Redis資訊："
    docker exec chatbot_redis_prod redis-cli info server | grep -E "(redis_version|uptime_in_seconds|connected_clients|used_memory_human)"
    
    echo ""
    echo "Redis記憶體使用："
    docker exec chatbot_redis_prod redis-cli info memory | grep -E "(used_memory_human|maxmemory_human|mem_fragmentation_ratio)"
}

# 主函數
main() {
    log_info "開始監控思考機器人生產環境..."
    
    check_services
    echo ""
    check_resources
    echo ""
    check_database
    echo ""
    check_redis
    echo ""
    check_logs
    
    log_info "監控完成"
}

# 執行主函數
main "$@"