# Git 分支策略

## 分支說明

### main 分支
- **用途**: 正式生產環境
- **特點**: 
  - 代碼穩定，經過充分測試
  - 直接部署到生產環境
  - 只接受來自 develop 分支的合併
  - 每次合併都會觸發生產部署

### develop 分支
- **用途**: 開發環境
- **特點**:
  - 日常開發的主要分支
  - 整合新功能和修復
  - 定期合併到 main 分支
  - 用於本地開發和測試

### feature/* 分支
- **用途**: 新功能開發
- **命名**: feature/功能名稱
- **流程**: develop → feature/* → develop

### hotfix/* 分支
- **用途**: 緊急修復
- **命名**: hotfix/修復描述
- **流程**: main → hotfix/* → main + develop

## 工作流程

### 1. 日常開發
```bash
# 切換到開發分支
git checkout develop

# 拉取最新代碼
git pull origin develop

# 創建功能分支
git checkout -b feature/new-feature

# 開發完成後合併回develop
git checkout develop
git merge feature/new-feature
git push origin develop
```

### 2. 發布到生產環境
```bash
# 從develop合併到main
git checkout main
git pull origin main
git merge develop
git push origin main

# 這會觸發生產環境部署
```

### 3. 緊急修復
```bash
# 從main創建hotfix分支
git checkout main
git checkout -b hotfix/urgent-fix

# 修復完成後合併到main和develop
git checkout main
git merge hotfix/urgent-fix
git push origin main

git checkout develop
git merge hotfix/urgent-fix
git push origin develop
```

## 部署策略

### 開發環境 (develop分支)
- 使用 `docker-compose.yml`
- 使用 `env.example` 配置
- 用於本地開發和測試

### 生產環境 (main分支)
- 使用 `docker-compose.prod.yml`
- 使用 `.env.production` 配置
- 部署到Linode服務器
- 包含Nginx反向代理和SSL

## 環境變數管理

### 開發環境
```bash
# 複製範例文件
cp env.example .env

# 編輯配置
vim .env
```

### 生產環境
```bash
# 複製範例文件
cp env.production.example .env.production

# 編輯配置
vim .env.production
```

## 部署命令

### 開發環境
```bash
# 啟動開發環境
docker-compose up --build -d

# 停止開發環境
docker-compose down
```

### 生產環境
```bash
# 自動部署
./deploy.sh

# 手動部署
docker-compose -f docker-compose.prod.yml --env-file .env.production up --build -d
```

## 監控命令

```bash
# 監控生產環境
./monitor.sh

# 查看日誌
docker-compose -f docker-compose.prod.yml logs -f
```

## 注意事項

1. **永遠不要直接在main分支開發**
2. **合併前確保代碼經過測試**
3. **生產環境變數要保密**
4. **定期備份生產數據**
5. **監控生產環境狀態**

## 版本標記

```bash
# 創建版本標記
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 查看所有標記
git tag -l
```
