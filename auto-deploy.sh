#!/bin/bash

# 完全自動化Linode部署腳本
set -e

echo "🚀 開始完全自動化部署..."

# 檢查是否為root用戶
if [ "$EUID" -ne 0 ]; then
    echo "❌ 請使用root用戶執行此腳本"
    exit 1
fi

echo "📦 更新系統和安裝基礎工具..."
apt update && apt upgrade -y
apt install -y curl wget git vim htop unzip nano

echo "🐳 安裝Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
systemctl start docker
systemctl enable docker

echo "🔧 安裝Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

echo "🌍 設定時區..."
timedatectl set-timezone Asia/Taipei

echo "👤 創建chatbot用戶..."
userdel -r chatbot 2>/dev/null || true
adduser --disabled-password --gecos "" chatbot
usermod -aG sudo chatbot
usermod -aG docker chatbot

echo "🔥 設定防火牆..."
apt install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "📥 下載並部署應用程式..."
su - chatbot -c "
    cd /home/chatbot
    
    # 下載項目代碼
    wget -q https://github.com/Averytsai/thinking-bot/archive/refs/heads/main.zip
    unzip -q main.zip
    mv thinking-bot-main thinking-bot
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

echo "⏳ 等待服務完全啟動..."
sleep 10

# 獲取服務器IP
SERVER_IP=$(curl -s ifconfig.me)
echo "🌐 服務器IP: $SERVER_IP"

# 測試健康檢查
echo "🔍 測試服務健康狀態..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 本地健康檢查通過"
else
    echo "⚠️ 本地健康檢查失敗"
fi

if curl -f http://$SERVER_IP:8000/health > /dev/null 2>&1; then
    echo "✅ 外部健康檢查通過"
else
    echo "⚠️ 外部健康檢查失敗"
fi

echo ""
echo "🎉 部署完成！"
echo "📋 部署摘要:"
echo "   • 服務器IP: $SERVER_IP"
echo "   • 應用程式端口: 8000"
echo "   • LINE Webhook URL: http://$SERVER_IP:8000/api/line/webhook"
echo "   • 健康檢查: http://$SERVER_IP:8000/health"
echo ""
echo "📝 下一步:"
echo "   1. 在LINE Developers Console更新Webhook URL"
echo "   2. 測試LINE Bot功能"
