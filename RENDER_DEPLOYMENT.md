# LINE TechOrange NewsBot - Render 部署指南

## 🚀 部署到 Render 的完整步驟

### 1. 準備 GitHub Repository
1. 確保您的程式碼已推送到 GitHub repository
2. 確保包含以下檔案：
   - `app.py` (主應用程式)
   - `requirements.txt` (Python 依賴)
   - `runtime.txt` (Python 版本指定)
   - `render.yaml` (Render 配置)
   - `Procfile` (備用啟動配置)
   - `.gitignore` (忽略敏感檔案)

### 2. 在 Render 創建 Web Service
1. 登入 [Render Dashboard](https://dashboard.render.com)
2. 點擊 "New +" → "Web Service"
3. 連接您的 GitHub repository
4. 選擇包含 LINE Bot 的 repository

### 3. 配置 Render 設定
#### 基本設定：
- **Name**: `line-techorange-newsbot`
- **Environment**: `Python 3`
- **Region**: `Singapore` (對台灣較快)
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command**: `python app.py`

#### 重要：Python 版本設定
確保在 Environment Variables 中設定：
- `PYTHON_VERSION`: `3.11`

#### 環境變數設定：
在 Render 的 Environment Variables 區域新增以下變數：

**必要環境變數**：
- `LINE_CHANNEL_ACCESS_TOKEN`: 您的 LINE Channel Access Token
- `LINE_CHANNEL_SECRET`: 您的 LINE Channel Secret  
- `GEMINI_API_KEY`: 您的 Google Gemini API Key

**系統環境變數**：
- `PORT`: `10000` (Render 預設)
- `HOST`: `0.0.0.0`
- `FLASK_ENV`: `production`
- `FLASK_DEBUG`: `False`
- `MAX_ARTICLES`: `3`

### 4. 部署設定
- **Region**: 選擇離您最近的區域 (建議 Singapore 對台灣較快)
- **Plan**: Free (或根據需求選擇付費方案)
- **Auto-Deploy**: 啟用 (GitHub 推送時自動部署)

### 5. 取得 Webhook URL
部署成功後，您會得到一個 URL，格式如：
```
https://your-app-name.onrender.com
```

您的 LINE Bot Webhook URL 將是：
```
https://your-app-name.onrender.com/callback
```

### 6. 更新 LINE Bot 設定
1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 選擇您的 Channel
3. 在 "Messaging API" 頁籤中
4. 更新 "Webhook URL" 為您的 Render URL + `/callback`
5. 啟用 "Use webhook"
6. 測試 Webhook URL 連線

### 7. 測試部署
部署完成後測試以下功能：
- 健康檢查: `https://your-app-name.onrender.com/health`
- 首頁訪問: `https://your-app-name.onrender.com/`
- LINE Bot 功能測試

### 8. 監控和日誌
- 在 Render Dashboard 可查看應用程式日誌
- 監控應用程式狀態和效能
- 設定告警通知

## 🔐 安全注意事項

1. **永不在程式碼中暴露 API Keys**
2. **使用 Render 的環境變數管理敏感資料**
3. **定期更新依賴包版本**
4. **監控應用程式日誌以偵測異常**

## 📊 費用考量

### Free Plan 限制：
- 750 小時/月的運行時間
- 應用程式閒置 15 分鐘後會睡眠
- 512MB RAM
- 免費自定義網域

### 建議升級時機：
- 如需 24/7 不睡眠運行
- 需要更多 RAM 或 CPU
- 需要更快的冷啟動時間

## 🚨 常見問題

### 部署失敗？
1. 檢查 `requirements.txt` 語法
2. 確認所有依賴都已列出
3. 檢查 Python 版本相容性

### Webhook 無法連接？
1. 確認 URL 格式正確
2. 檢查 Render 應用程式是否正在運行
3. 查看 Render 日誌了解錯誤訊息

### 機器人沒有回應？
1. 檢查環境變數是否正確設定
2. 確認 LINE Channel 設定
3. 查看應用程式日誌

## 📞 支援

如遇到問題，請檢查：
1. Render 官方文件
2. LINE Bot SDK 文件
3. 應用程式日誌檔案
