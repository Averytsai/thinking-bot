# GitHub 倉庫設定指南

## 1. 建立GitHub倉庫

### 方法一：使用GitHub網頁界面

1. **登入GitHub**
   - 前往 https://github.com
   - 登入您的帳戶

2. **建立新倉庫**
   - 點擊右上角的 "+" 按鈕
   - 選擇 "New repository"

3. **設定倉庫資訊**
   - **Repository name**: `thinking-bot`
   - **Description**: `智能對話機器人 - 支援多通訊平台的職場思考助手`
   - **Visibility**: 選擇 Public 或 Private
   - **不要**勾選 "Add a README file"（我們已經有了）
   - **不要**勾選 "Add .gitignore"（我們已經有了）
   - **不要**勾選 "Choose a license"（稍後可以添加）

4. **點擊 "Create repository"**

### 方法二：使用GitHub CLI（推薦）

如果您想安裝GitHub CLI：

```bash
# macOS
brew install gh

# 登入GitHub
gh auth login

# 建立倉庫
gh repo create thinking-bot --public --description "智能對話機器人 - 支援多通訊平台的職場思考助手"
```

## 2. 連接本地倉庫到GitHub

建立GitHub倉庫後，執行以下命令：

```bash
# 添加遠端倉庫（替換 your-username 為您的GitHub用戶名）
git remote add origin https://github.com/your-username/thinking-bot.git

# 推送main分支
git push -u origin main

# 推送develop分支
git push -u origin develop
```

## 3. 設定倉庫保護規則

### 3.1 設定分支保護

1. 前往倉庫的 "Settings" 頁面
2. 點擊 "Branches"
3. 點擊 "Add rule"
4. 設定以下規則：

**main分支保護規則：**
- Branch name pattern: `main`
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Restrict pushes that create files larger than 100MB

**develop分支保護規則：**
- Branch name pattern: `develop`
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging

### 3.2 設定Actions

1. 前往 "Actions" 頁面
2. 點擊 "New workflow"
3. 選擇 "Simple workflow"
4. 使用以下配置：

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        # 這裡可以添加測試命令
        echo "Tests would run here"
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        echo "Deploy to production server"
        # 這裡可以添加部署命令
```

## 4. 設定環境變數

### 4.1 設定GitHub Secrets

1. 前往倉庫的 "Settings" 頁面
2. 點擊 "Secrets and variables" → "Actions"
3. 點擊 "New repository secret"
4. 添加以下secrets：

```
OPENAI_API_KEY: 您的OpenAI API密鑰
LINE_CHANNEL_ACCESS_TOKEN: 您的LINE Channel Access Token
LINE_CHANNEL_SECRET: 您的LINE Channel Secret
DB_PASSWORD: 生產環境資料庫密碼
REDIS_PASSWORD: 生產環境Redis密碼
SECRET_KEY: 生產環境密鑰
```

## 5. 設定Webhook

### 5.1 GitHub Webhook（用於CI/CD）

1. 前往倉庫的 "Settings" 頁面
2. 點擊 "Webhooks"
3. 點擊 "Add webhook"
4. 設定：
   - **Payload URL**: 您的部署服務器webhook URL
   - **Content type**: application/json
   - **Events**: 選擇 "Just the push event"

### 5.2 LINE Bot Webhook

1. 前往 LINE Developers Console
2. 選擇您的Bot
3. 在 "Messaging API" 設定中：
   - **Webhook URL**: `https://your-domain.com/api/line/webhook`
   - **Use webhook**: 啟用

## 6. 設定Issues和Projects

### 6.1 啟用Issues

1. 前往倉庫的 "Settings" 頁面
2. 在 "Features" 區域：
   - ✅ Issues
   - ✅ Projects
   - ✅ Wiki（可選）

### 6.2 建立Issue模板

在 `.github/ISSUE_TEMPLATE/` 目錄下建立模板：

```markdown
---
name: Bug Report
about: 回報bug
title: '[BUG] '
labels: bug
assignees: ''
---

## 問題描述
簡潔描述問題

## 重現步驟
1. 前往 '...'
2. 點擊 '...'
3. 滾動到 '...'
4. 看到錯誤

## 預期行為
描述您預期的行為

## 實際行為
描述實際發生的行為

## 環境資訊
- OS: [e.g. macOS, Ubuntu]
- Browser: [e.g. chrome, safari]
- Version: [e.g. 22]

## 額外資訊
添加任何其他相關資訊
```

## 7. 設定README徽章

在README.md中添加狀態徽章：

```markdown
![Build Status](https://github.com/your-username/thinking-bot/workflows/CI/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)
```

## 8. 完成設定檢查清單

- [ ] GitHub倉庫已建立
- [ ] 本地倉庫已連接到GitHub
- [ ] main和develop分支已推送
- [ ] 分支保護規則已設定
- [ ] CI/CD pipeline已配置
- [ ] 環境變數secrets已設定
- [ ] LINE Bot webhook已設定
- [ ] Issues和Projects已啟用
- [ ] Issue模板已建立
- [ ] README徽章已添加

## 9. 後續步驟

1. **測試CI/CD pipeline**
   - 推送一個小更改到develop分支
   - 確認Actions正常運行

2. **設定生產環境**
   - 按照LINODE_DEPLOYMENT.md部署到Linode
   - 測試LINE Bot功能

3. **建立Release**
   - 在GitHub上建立第一個release
   - 標記版本號（如v1.0.0）

4. **邀請協作者**
   - 如果需要，邀請其他開發者
   - 設定適當的權限
