# 思考機器人 🤖

一個支援多通訊平台的智能對話機器人，專為職場思考場景設計。

## ✨ 功能特色

### 🎯 五種思考模式
1. **任務拆解** - 使用SMART公式理清思路
2. **問題討論** - 使用RIDE模型與主管有效溝通  
3. **成果回報** - 使用PREP模型安排報告順序
4. **觀點表達** - 使用5W2H法則提升說服力
5. **總結整理** - 使用GRAI法則做出完整總結

### 🔧 技術特色
- 🚀 **多平台支援**: LINE、Telegram等通訊平台
- 🤖 **AI驅動**: 使用ChatGPT進行智能對話
- 💾 **數據持久化**: PostgreSQL + Redis
- 🐳 **容器化部署**: Docker & Docker Compose
- 🔒 **生產就緒**: Nginx反向代理 + SSL支援

## 🛠 技術棧

- **後端框架**: FastAPI (Python 3.11)
- **資料庫**: PostgreSQL 15
- **快取系統**: Redis 7
- **AI模型**: OpenAI GPT-3.5-turbo
- **通訊平台**: LINE Bot SDK
- **容器化**: Docker & Docker Compose
- **反向代理**: Nginx
- **部署平台**: Linode

## 🚀 快速開始

### 開發環境

1. **複製專案**
```bash
git clone https://github.com/your-username/thinking-bot.git
cd thinking-bot
```

2. **設定環境變數**
```bash
cp env.example .env
# 編輯 .env 文件，填入必要的API密鑰
```

3. **啟動服務**
```bash
docker-compose up --build -d
```

4. **檢查服務狀態**
```bash
curl http://localhost:8000/health
```

### 生產環境部署

請參考 [📋 Linode部署指南](LINODE_DEPLOYMENT.md) 進行生產環境部署。

## 📁 專案結構

```
thinking-bot/
├── app/                    # 應用程式主目錄
│   ├── adapters/          # 通訊平台適配器
│   │   ├── line_adapter.py    # LINE Bot適配器
│   │   └── base_adapter.py    # 基礎適配器
│   ├── api/               # API路由
│   │   └── line_webhook.py    # LINE Webhook處理
│   ├── core/              # 核心配置
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 資料庫連接
│   │   └── exceptions.py       # 異常處理
│   ├── models/            # 資料庫模型
│   │   ├── user.py             # 用戶模型
│   │   ├── conversation.py     # 對話模型
│   │   ├── message.py          # 訊息模型
│   │   └── prompt_category.py  # 提示詞分類模型
│   ├── prompts/           # 提示詞管理
│   │   ├── categories.py       # 問題分類定義
│   │   └── manager.py          # 提示詞管理器
│   └── services/          # 業務邏輯服務
│       ├── ai_service.py      # AI服務
│       ├── conversation_service.py # 對話服務
│       ├── line_service.py    # LINE服務
│       └── prompt_service.py  # 提示詞服務
├── migrations/            # 資料庫遷移腳本
├── nginx/                 # Nginx配置
├── docker-compose.yml     # 開發環境配置
├── docker-compose.prod.yml # 生產環境配置
├── deploy.sh              # 自動部署腳本
├── monitor.sh             # 監控腳本
└── LINODE_DEPLOYMENT.md   # Linode部署指南
```

## 🌿 分支策略

- **main**: 正式生產環境分支
- **develop**: 開發環境分支
- **feature/***: 新功能開發分支
- **hotfix/***: 緊急修復分支

詳細說明請參考 [📋 分支策略指南](BRANCH_STRATEGY.md)

## 🔧 環境配置

### 開發環境
```bash
# 使用開發配置
docker-compose up --build -d
```

### 生產環境
```bash
# 設定生產環境變數
cp env.production.example .env.production
vim .env.production

# 執行自動部署
./deploy.sh
```

## 📊 監控與維護

```bash
# 監控服務狀態
./monitor.sh

# 查看服務日誌
docker-compose -f docker-compose.prod.yml logs -f

# 檢查服務健康狀態
curl https://your-domain.com/health
```

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

此專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 文件

## 📞 支援

如有問題或建議，請開啟 [Issue](https://github.com/your-username/thinking-bot/issues)