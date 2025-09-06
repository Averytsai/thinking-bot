# 思考機器人 (Thinking Bot)

一個支援多通訊平台的對話機器人，初期支援LINE，未來可擴展至其他平台。

## 架構特色

- **模組化設計**: 通訊適配器與AI模型獨立運作
- **容器化部署**: 使用Docker管理多版本和持續更新
- **會話管理**: 支援30分鐘無活動自動分段
- **成本追蹤**: 記錄token使用量用於成本計算

## 技術棧

- **後端**: FastAPI (Python)
- **資料庫**: PostgreSQL + Redis
- **容器化**: Docker + Docker Compose
- **AI模型**: ChatGPT (初期)

## 專案結構

```
思考機器人/
├── app/                    # 應用程式主目錄
│   ├── api/               # API路由
│   ├── core/              # 核心配置
│   ├── models/            # 資料庫模型
│   ├── services/          # 業務邏輯服務
│   └── adapters/          # 通訊適配器
├── migrations/            # 資料庫遷移腳本
├── docker/               # Docker相關檔案
├── tests/                 # 測試檔案
├── docker-compose.yml     # Docker Compose配置
├── Dockerfile            # Docker映像檔
└── requirements.txt      # Python依賴
```

## 快速開始

1. 複製環境變數檔案
```bash
cp .env.example .env
```

2. 啟動服務
```bash
docker-compose up -d
```

3. 執行資料庫遷移
```bash
docker-compose exec web python -m alembic upgrade head
```

## 開發模式

開發環境會自動重載，修改程式碼後無需重啟容器。

## 版本管理

- **主版本**: 穩定發布版本
- **分支版本**: 開發和測試版本

每次開發開始時會說明當前版本和上次開發記錄。
