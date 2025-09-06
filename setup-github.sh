#!/bin/bash

# GitHub遠端倉庫設定腳本
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

# 檢查Git狀態
check_git_status() {
    log_header "檢查Git狀態"
    
    if [ ! -d ".git" ]; then
        log_error "Git倉庫未初始化"
        exit 1
    fi
    
    if ! git diff --quiet; then
        log_error "工作目錄有未提交的更改"
        git status --short
        exit 1
    fi
    
    log_info "Git狀態正常"
}

# 獲取GitHub用戶名
get_github_username() {
    log_header "設定GitHub倉庫"
    
    echo "請輸入您的GitHub用戶名："
    read -r github_username
    
    if [ -z "$github_username" ]; then
        log_error "用戶名不能為空"
        exit 1
    fi
    
    log_info "GitHub用戶名: $github_username"
    echo "$github_username"
}

# 檢查遠端倉庫
check_remote() {
    local github_username=$1
    
    if git remote -v | grep -q "origin"; then
        log_warn "遠端倉庫已存在"
        echo "現有遠端倉庫："
        git remote -v
        
        echo ""
        echo "是否要重新設定？(y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_info "保持現有設定"
            return 0
        fi
        
        # 移除現有遠端倉庫
        git remote remove origin
        log_info "已移除現有遠端倉庫"
    fi
}

# 設定遠端倉庫
setup_remote() {
    local github_username=$1
    local repo_url="https://github.com/$github_username/thinking-bot.git"
    
    log_info "設定遠端倉庫: $repo_url"
    
    # 添加遠端倉庫
    git remote add origin "$repo_url"
    
    # 驗證設定
    log_info "遠端倉庫設定完成："
    git remote -v
}

# 推送代碼
push_code() {
    log_header "推送代碼到GitHub"
    
    log_info "推送main分支..."
    if git push -u origin main; then
        log_info "main分支推送成功"
    else
        log_error "main分支推送失敗"
        log_warn "請確認："
        log_warn "1. GitHub倉庫已建立"
        log_warn "2. 倉庫名稱是 'thinking-bot'"
        log_warn "3. 您有推送權限"
        log_warn "4. 認證資訊正確"
        exit 1
    fi
    
    log_info "推送develop分支..."
    if git push -u origin develop; then
        log_info "develop分支推送成功"
    else
        log_error "develop分支推送失敗"
        exit 1
    fi
}

# 顯示後續步驟
show_next_steps() {
    local github_username=$1
    
    log_header "設定完成！"
    
    log_info "GitHub倉庫地址: https://github.com/$github_username/thinking-bot"
    log_info "遠端倉庫設定:"
    git remote -v
    
    echo ""
    log_info "後續步驟："
    log_info "1. 前往GitHub設定分支保護規則"
    log_info "2. 設定環境變數: cp env.production.example .env.production"
    log_info "3. 編輯環境變數: vim .env.production"
    log_info "4. 執行部署檢查: ./check-deployment.sh"
    log_info "5. 開始部署: ./deploy.sh"
    
    echo ""
    log_info "參考文檔："
    log_info "- GITHUB_SETUP.md (GitHub設定指南)"
    log_info "- LINODE_DEPLOYMENT.md (Linode部署指南)"
    log_info "- BRANCH_STRATEGY.md (分支策略)"
}

# 主函數
main() {
    log_info "開始設定GitHub遠端倉庫..."
    
    # 檢查Git狀態
    check_git_status
    
    # 獲取GitHub用戶名
    github_username=$(get_github_username)
    
    # 檢查遠端倉庫
    check_remote "$github_username"
    
    # 設定遠端倉庫
    setup_remote "$github_username"
    
    # 推送代碼
    push_code
    
    # 顯示後續步驟
    show_next_steps "$github_username"
}

# 執行主函數
main "$@"
