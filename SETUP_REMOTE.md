# 設定GitHub遠端倉庫

## 步驟1：建立GitHub倉庫

請按照以下步驟在GitHub上建立倉庫：

1. **前往GitHub**
   - 打開瀏覽器，前往 https://github.com
   - 登入您的帳戶

2. **建立新倉庫**
   - 點擊右上角的 "+" 按鈕
   - 選擇 "New repository"

3. **設定倉庫資訊**
   - **Repository name**: `thinking-bot`
   - **Description**: `智能對話機器人 - 支援多通訊平台的職場思考助手`
   - **Visibility**: 選擇 Public 或 Private
   - **不要**勾選任何初始化選項（我們已經有了代碼）

4. **點擊 "Create repository"**

## 步驟2：獲取倉庫URL

建立倉庫後，GitHub會顯示倉庫URL，類似：
```
https://github.com/your-username/thinking-bot.git
```

請記住這個URL，稍後會用到。

## 步驟3：連接本地倉庫

在終端中執行以下命令（替換 `your-username` 為您的GitHub用戶名）：

```bash
# 添加遠端倉庫
git remote add origin https://github.com/your-username/thinking-bot.git

# 驗證遠端倉庫設定
git remote -v

# 推送main分支
git push -u origin main

# 推送develop分支
git push -u origin develop
```

## 步驟4：驗證設定

執行以下命令確認設定成功：

```bash
# 檢查遠端倉庫
git remote -v

# 檢查分支狀態
git branch -a

# 檢查最後一次提交
git log --oneline -5
```

## 如果遇到問題

### 問題1：認證失敗
如果推送時遇到認證問題，請：

1. **使用Personal Access Token**
   - 前往 GitHub Settings → Developer settings → Personal access tokens
   - 生成新的token
   - 使用token作為密碼

2. **或者使用SSH**
   ```bash
   # 生成SSH密鑰
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
   
   # 添加SSH密鑰到GitHub
   # 然後使用SSH URL
   git remote set-url origin git@github.com:your-username/thinking-bot.git
   ```

### 問題2：倉庫已存在
如果倉庫名稱已被使用，請：

1. 選擇不同的倉庫名稱
2. 或者使用您的組織帳戶

### 問題3：權限問題
如果沒有推送權限，請：

1. 確認您是倉庫的所有者
2. 檢查倉庫的權限設定

## 完成後的下一步

設定遠端倉庫後，您可以：

1. **重新執行檢查腳本**
   ```bash
   ./check-deployment.sh
   ```

2. **設定生產環境變數**
   ```bash
   cp env.production.example .env.production
   vim .env.production
   ```

3. **開始部署到Linode**
   ```bash
   ./deploy.sh
   ```

## 重要提醒

- 確保您的GitHub用戶名正確
- 倉庫名稱必須是 `thinking-bot`
- 如果使用HTTPS，需要Personal Access Token
- 如果使用SSH，需要設定SSH密鑰
