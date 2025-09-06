# Linode 部署指南

## 1. 準備 Linode 服務器

### 1.1 創建 Linode 實例
1. 登入 Linode 控制台
2. 創建新的 Linode 實例：
   - **Distribution**: Ubuntu 22.04 LTS
   - **Region**: 選擇離用戶最近的區域
   - **Type**: 建議至少 2GB RAM (Nanode 2GB 或 Linode 2GB)
   - **Root Password**: 設定強密碼

### 1.2 基本服務器設定
```bash
# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝必要工具
sudo apt install -y curl wget git vim htop

# 設定時區
sudo timedatectl set-timezone Asia/Taipei

# 創建非root用戶
sudo adduser chatbot
sudo usermod -aG sudo chatbot
```

## 2. 安裝 Docker 和 Docker Compose

```bash
# 安裝 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 將用戶加入docker組
sudo usermod -aG docker chatbot

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登入以應用組權限
exit
# 重新SSH登入
```

## 3. 部署應用程式

### 3.1 上傳代碼
```bash
# 切換到chatbot用戶
su - chatbot

# 克隆代碼 (需要先推送到Git倉庫)
git clone https://github.com/your-username/thinking-bot.git
cd thinking-bot

# 或者使用scp上傳代碼
# scp -r /path/to/local/project chatbot@your-server-ip:/home/chatbot/
```

### 3.2 設定環境變數
```bash
# 複製環境變數範例
cp env.production.example .env.production

# 編輯環境變數
vim .env.production
```

**重要：設定以下變數**
- `DB_PASSWORD`: 強密碼
- `REDIS_PASSWORD`: 強密碼
- `OPENAI_API_KEY`: 您的OpenAI API Key
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Bot Channel Access Token
- `LINE_CHANNEL_SECRET`: LINE Bot Channel Secret
- `SECRET_KEY`: 隨機生成的密鑰

### 3.3 生成SSL證書
```bash
# 創建SSL目錄
mkdir -p nginx/ssl

# 生成自簽證書 (開發測試用)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=TW/ST=Taiwan/L=Taipei/O=Chatbot/CN=your-domain.com"

# 或者使用 Let's Encrypt (推薦生產環境)
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown chatbot:chatbot nginx/ssl/*
```

### 3.4 部署服務
```bash
# 執行部署腳本
./deploy.sh

# 或者手動部署
docker-compose -f docker-compose.prod.yml --env-file .env.production up --build -d
```

## 4. 設定防火牆

```bash
# 安裝ufw
sudo apt install ufw

# 設定防火牆規則
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 啟用防火牆
sudo ufw enable
```

## 5. 設定域名和DNS

### 5.1 購買域名
- 在域名註冊商購買域名
- 設定DNS A記錄指向Linode服務器IP

### 5.2 更新Nginx配置
```bash
# 編輯nginx配置
vim nginx/nginx.conf

# 將 server_name _; 改為您的域名
server_name your-domain.com www.your-domain.com;
```

## 6. 設定LINE Bot Webhook

1. 登入 LINE Developers Console
2. 選擇您的Bot
3. 在 Webhook URL 設定：
   ```
   https://your-domain.com/api/line/webhook
   ```
4. 啟用 Webhook

## 7. 監控和維護

### 7.1 監控服務
```bash
# 執行監控腳本
./monitor.sh

# 查看日誌
docker-compose -f docker-compose.prod.yml logs -f
```

### 7.2 備份資料庫
```bash
# 創建備份腳本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec chatbot_postgres_prod pg_dump -U chatbot_user_prod chatbot_db_prod > backup_${DATE}.sql
gzip backup_${DATE}.sql
EOF

chmod +x backup.sh

# 設定定時備份 (每天凌晨2點)
crontab -e
# 添加: 0 2 * * * /home/chatbot/thinking-bot/backup.sh
```

### 7.3 更新應用程式
```bash
# 拉取最新代碼
git pull origin main

# 重新部署
./deploy.sh
```

## 8. 安全建議

1. **定期更新系統**：
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **設定SSH密鑰認證**：
   ```bash
   # 在本地生成密鑰
   ssh-keygen -t rsa -b 4096
   
   # 上傳公鑰到服務器
   ssh-copy-id chatbot@your-server-ip
   ```

3. **禁用root登入**：
   ```bash
   sudo vim /etc/ssh/sshd_config
   # 設定: PermitRootLogin no
   sudo systemctl restart ssh
   ```

4. **設定fail2ban**：
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

## 9. 故障排除

### 9.1 服務無法啟動
```bash
# 檢查日誌
docker-compose -f docker-compose.prod.yml logs

# 檢查端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### 9.2 資料庫連接問題
```bash
# 檢查資料庫狀態
docker exec chatbot_postgres_prod pg_isready -U chatbot_user_prod

# 檢查環境變數
docker exec chatbot_web_prod env | grep DATABASE
```

### 9.3 SSL證書問題
```bash
# 檢查證書
openssl x509 -in nginx/ssl/cert.pem -text -noout

# 測試SSL
openssl s_client -connect your-domain.com:443
```

## 10. 性能優化

1. **增加服務器資源**：升級到更高配置的Linode實例
2. **設定Redis持久化**：確保數據不丟失
3. **使用CDN**：加速靜態資源載入
4. **監控性能**：使用工具如Prometheus + Grafana

## 11. 成本估算

- **Linode Nanode 2GB**: $12/月
- **域名**: $10-15/年
- **SSL證書**: 免費 (Let's Encrypt)
- **總計**: 約 $12-13/月

## 12. 支援和維護

- 定期檢查服務狀態
- 監控日誌文件
- 備份重要數據
- 及時更新安全補丁
