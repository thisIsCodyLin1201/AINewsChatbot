# Render 部署指南

## 🚀 部署步驟

### 1. 準備 GitHub Repository
```bash
# 確保所有檔案都已提交到 GitHub
git add .
git commit -m "修正 Python 版本相容性問題"
git push origin main
```

### 2. 在 Render 上建立新服務
1. 登入 [Render](https://render.com)
2. 點擊 "New" → "Web Service"
3. 連接你的 GitHub repository
4. 選擇你的 chatbot repository

### 3. 配置部署設定
- **Name**: line-techorange-newsbot
- **Environment**: Docker
- **Region**: Singapore (最近的地區)
- **Plan**: Free

### 4. 設定環境變數
在 Render 的 Environment 頁面中添加：

```
LINE_CHANNEL_ACCESS_TOKEN=你的_LINE_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_LINE_Channel_Secret  
GEMINI_API_KEY=你的_Gemini_API_Key
```

### 5. 部署
- 點擊 "Create Web Service"
- Render 將自動使用 Dockerfile 建置和部署

### 6. 取得服務 URL
部署成功後，你會得到一個類似這樣的 URL：
```
https://line-techorange-newsbot-xxxx.onrender.com
```

### 7. 更新 LINE Webhook URL
1. 登入 [LINE Developers Console](https://developers.line.biz/)
2. 選擇你的 bot
3. 到 "Messaging API" 頁面
4. 更新 "Webhook URL" 為：
   ```
   https://你的render網址.onrender.com/callback
   ```
5. 點擊 "Verify" 確認連接正常
6. 啟用 "Use webhook"

## ✅ 測試部署

### 健康檢查
訪問：`https://你的render網址.onrender.com/health`
應該返回：
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "components": {
    "line_bot": true,
    "crawler": true,
    "summarizer": true
  }
}
```

### 功能測試
1. 在 LINE 中發送「隨機」→ 應該收到 3 篇隨機文章
2. 發送「AI」→ 應該收到 AI 相關文章
3. 發送「金融」→ 應該收到金融科技相關文章

## 🔧 疑難排解

### 常見問題

#### 1. Python 版本相容性問題
**錯誤**: `lxml`、`aiohttp` 編譯錯誤
**解決方案**: 
- 使用 Python 3.11（避免 3.13 的相容性問題）
- 明確指定相容的套件版本
- 使用預編譯的二進制套件

#### 2. 部署失敗
**檢查項目**:
- 確認 Dockerfile 和 requirements.txt 正確
- 查看 Render 的 Build Logs
- 確認所有檔案都已提交到 GitHub

#### 3. 環境變數錯誤
**檢查項目**:
- 確認所有必要的環境變數都已設定
- API 金鑰格式正確
- 沒有多餘的空格或換行

#### 4. LINE Webhook 驗證失敗
**檢查項目**:
- URL 格式正確且服務正在運行
- 健康檢查端點可以正常訪問
- 防火牆設定允許 LINE 的請求

### 日誌查看
在 Render dashboard 的 "Logs" 頁面可以查看即時日誌。

## 📋 部署檔案清單

✅ **Dockerfile** - Docker 容器配置（使用 Python 3.11）
✅ **render.yaml** - Render 服務配置  
✅ **requirements.txt** - Python 依賴（已修正版本相容性）
✅ **.python-version** - Python 版本指定
✅ **runtime.txt** - Render Python 版本配置
✅ **.dockerignore** - Docker 忽略檔案
✅ **app.py** - 已更新為生產環境配置
✅ **summarizer.py** - 已更新為相容 google-generativeai==0.1.0

## 🎯 版本相容性解決方案

### Python 版本
- **使用**: Python 3.11.9
- **避免**: Python 3.13（有編譯問題）

### 關鍵套件版本
```
aiohttp==3.8.6          # 避免 3.9+ 的編譯問題
lxml==4.9.3             # 穩定版本，支援預編譯
line-bot-sdk==3.4.0     # 相容 aiohttp 3.8.x
google-generativeai==0.1.0  # 避免 aiohttp 衝突
```

### Docker 策略
- 使用 `--only-binary=all` 安裝問題套件
- 先安裝 lxml 和 aiohttp，再安裝其他依賴
- 包含所有必要的系統依賴

## 🚀 優勢

- **永久運行**: 不需要 ngrok，直接使用 Render 提供的穩定 URL
- **自動重啟**: 服務如果崩潰會自動重啟
- **HTTPS**: 自動提供 SSL 憑證
- **監控**: 內建監控和日誌功能
- **免費方案**: 免費層級即可運行基本功能
- **版本穩定**: 解決了 Python 3.13 的相容性問題
