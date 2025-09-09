#!/bin/bash

# Linode自動化部署腳本
# 使用方法: ./deploy-linode.sh

set -e  # 遇到錯誤立即退出

echo "🚀 開始Linode自動化部署..."

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數：打印帶顏色的消息
print_status() {
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

# 檢查是否為root用戶
if [ "$EUID" -ne 0 ]; then
    print_error "請使用root用戶執行此腳本"
    exit 1
fi

print_status "更新系統和安裝基礎工具..."
apt update && apt upgrade -y
apt install -y curl wget git vim htop unzip nano

print_status "設定時區為Asia/Taipei..."
timedatectl set-timezone Asia/Taipei

print_status "安裝Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl start docker
systemctl enable docker

print_status "安裝Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

print_status "創建非root用戶 'chatbot'..."
adduser --disabled-password --gecos "" chatbot
usermod -aG sudo chatbot
usermod -aG docker chatbot

print_status "設定防火牆..."
apt install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

print_status "切換到chatbot用戶並部署應用程式..."
su - chatbot -c "
    cd /home/chatbot
    git clone https://github.com/Averytsai/thinking-bot.git
    cd thinking-bot
    
    # 創建環境變數文件
    cat > .env.production << 'EOF'
# 資料庫設定
DB_HOST=postgres
DB_PORT=5432
DB_NAME=chatbot_db
DB_USER=chatbot_user
DB_PASSWORD=chatbot_password

# Redis設定
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# OpenAI API Key
OPENAI_API_KEY=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

# LINE Bot設定
LINE_CHANNEL_ACCESS_TOKEN=uHJTVf4fY6hixiqQVhSqiKN7bwcx02Qv9uLRhr7ZmOZM4dtLdy38DdgjbKqYN94p+4y+4pAPQvr9ePbwJXR9J2RJ3NRL2cyL3jj6dhAgPHg9uomCGJ5/rpb6PjxSmrN3WsR8ZdePILD2igUZWRY9QAdB04t89/1O/w1cDnyilFU=
LINE_CHANNEL_SECRET=db680d6b5849b879a1c65c596e386594

# 應用設定
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
EOF

    # 部署應用程式
    docker-compose -f docker-compose.prod.yml up --build -d
    
    # 等待服務啟動
    sleep 30
    
    # 檢查服務狀態
    docker-compose -f docker-compose.prod.yml ps
"

print_status "等待服務完全啟動..."
sleep 10

print_status "測試服務健康狀態..."
# 獲取服務器IP
SERVER_IP=$(curl -s ifconfig.me)
print_status "服務器IP: $SERVER_IP"

# 測試健康檢查
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "✅ 本地健康檢查通過"
else
    print_warning "⚠️ 本地健康檢查失敗，檢查日誌中..."
fi

if curl -f http://$SERVER_IP:8000/health > /dev/null 2>&1; then
    print_success "✅ 外部健康檢查通過"
else
    print_warning "⚠️ 外部健康檢查失敗"
fi

print_success "🎉 部署完成！"
echo ""
echo "📋 部署摘要:"
echo "   • 服務器IP: $SERVER_IP"
echo "   • 應用程式端口: 8000"
echo "   • LINE Webhook URL: http://$SERVER_IP:8000/api/line/webhook"
echo "   • 健康檢查: http://$SERVER_IP:8000/health"
echo ""
echo "🔧 管理指令:"
echo "   • 查看日誌: su - chatbot -c 'cd /home/chatbot/thinking-bot && docker-compose -f docker-compose.prod.yml logs -f'"
echo "   • 重啟服務: su - chatbot -c 'cd /home/chatbot/thinking-bot && docker-compose -f docker-compose.prod.yml restart'"
echo "   • 停止服務: su - chatbot -c 'cd /home/chatbot/thinking-bot && docker-compose -f docker-compose.prod.yml down'"
echo ""
echo "📝 下一步:"
echo "   1. 在LINE Developers Console更新Webhook URL"
echo "   2. 測試LINE Bot功能"
echo "   3. 設定域名和SSL證書 (可選)"
