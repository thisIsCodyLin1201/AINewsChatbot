# LINE TechOrange NewsBot

一個基於 LINE Messaging API 的 Chatbot，可以搜尋科技報橘文章並使用 Google Gemini AI 產生摘要。

## 功能特色

- 🤖 **AI 驅動智能模糊搜尋** TechOrange 最新文章
  - 使用 Gemini AI 動態生成相關關鍵字
  - 精確匹配優先顯示
  - 智能語義理解，無需預設詞庫
  - 自動適應新興科技術語
- 🎯 AI 智能摘要生成（100-200字精簡摘要）
- 📱 LINE 官方帳號整合
- ⚡ 快速回應（< 5秒）
- 🎛️ 模組化設計
- 🔄 傳統模糊搜尋備援機制

## 安裝與設定

### 1. 環境要求

- Python 3.10+
- LINE Developer Account
- Google Cloud Account (Gemini API)

### 2. 安裝依賴

```bash
# 使用 uv（推薦）
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

### 3. 環境變數設定

複製 `.env.example` 為 `.env` 並填入以下資訊：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```env
# LINE Bot Configuration
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here
LINE_CHANNEL_SECRET=your_line_channel_secret_here

# Google Gemini API Configuration  
GEMINI_API_KEY=your_gemini_api_key_here

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
MAX_ARTICLES=3
```

### 4. LINE Bot 設定

1. 到 [LINE Developers](https://developers.line.biz/) 創建 Messaging API Channel
2. 取得 Channel Access Token 和 Channel Secret
3. 設定 Webhook URL: `https://your-domain.com/callback`

### 5. Google Gemini API 設定

1. 到 [Google AI Studio](https://makersuite.google.com/app/apikey) 取得 API Key
2. 將 API Key 填入 `.env` 檔案

## 運行方式

### 本地開發

```bash
python app.py
```

伺服器將在 `http://127.0.0.1:5000` 啟動

### 使用 ngrok 進行本地測試

```bash
# 安裝 ngrok
# 在另一個終端運行
ngrok http 5000

# 將 ngrok 提供的 HTTPS URL 設定為 LINE Webhook URL
```

### 部署到雲端

推薦部署平台：
- Railway
- Render  
- Heroku
- Google Cloud Run

## 項目結構

```
newchatbot/
├── app.py              # Flask 主應用程序
├── line_handler.py     # LINE Messaging API 處理
├── crawler.py          # TechOrange 爬蟲模組
├── summarizer.py       # Gemini AI 摘要模組
├── requirements.txt    # Python 依賴
├── .env.example       # 環境變數範例
├── tests/             # 測試檔案
│   ├── test_crawler.py
│   └── test_summarizer.py
└── README.md          # 說明文件
```

## API 端點

- `POST /callback` - LINE Webhook 回調
- `GET /health` - 健康檢查
- `GET /` - 首頁
- `GET /test/<keyword>` - 測試查詢（僅開發環境）

## 使用方式

### 搜尋範例

機器人支援 **Gemini AI 驅動的智能模糊搜尋**，以下是一些使用範例：

#### 基本搜尋
```
AI
科技
新創
永續
元宇宙
```

#### AI 模糊搜尋特色
- **動態關鍵字生成**：AI 即時分析並生成最相關的搜尋詞彙
- **語義理解**：理解用戶意圖，而非僅字串匹配
- **自適應學習**：自動適應新興科技術語和趨勢

#### 搜尋範例對比

**輸入：`永續`**
- 🤖 **AI 生成可能包含**：永續發展、ESG、綠色科技、循環經濟、碳中和
- 📚 **傳統方法**：僅限預設同義詞

**輸入：`元宇宙`**
- 🤖 **AI 生成可能包含**：Metaverse、VR、AR、虛擬實境、Web3
- 📚 **傳統方法**：需手動設定詞庫

#### 搜尋優先順序
1. **精確匹配** (100分) - 標題包含完全相同的關鍵字
2. **AI 生成第一關鍵字** (95分) - AI 認為最相關的詞彙
3. **AI 生成前三關鍵字** (85分) - 高度相關詞彙
4. **其他 AI 相關詞** (70分) - 一般相關詞彙

### 操作步驟

1. 將 LINE Bot 加為好友
2. 在聊天室輸入關鍵字（例如：「AI」、「區塊鏈」）
3. Bot 會搜尋相關的 TechOrange 文章
4. 使用 Gemini AI 生成摘要
5. 回傳文章標題、摘要和連結

### 回應格式

每篇文章包含：
- 📝 **標題**：文章完整標題
- 🤖 **AI 摘要**：100-200字的重點摘要
- 🔗 **閱讀全文**：原文連結

## 測試

運行單元測試：

```bash
# 測試爬蟲模組
python -m pytest tests/test_crawler.py -v

# 測試摘要模組  
python -m pytest tests/test_summarizer.py -v

# 運行所有測試
python -m pytest tests/ -v
```

手動測試：

```bash
# 測試爬蟲功能
python crawler.py

# 測試摘要功能
python summarizer.py

# 測試 LINE Handler
python line_handler.py
```

## 開發指南

### 添加新功能

1. 在對應模組添加功能
2. 更新單元測試
3. 更新文檔

### 調試技巧

1. 檢查日誌輸出
2. 使用 `/health` 端點檢查組件狀態
3. 使用 `/test/<keyword>` 端點測試查詢

### 性能優化

- 調整 `MAX_ARTICLES` 參數
- 實施緩存機制
- 優化 Gemini API 調用頻率

## 故障排除

### 常見問題

1. **LINE Bot 沒有回應**
   - 檢查 Webhook URL 是否正確
   - 確認 Channel Access Token 和 Secret 正確

2. **爬蟲無法取得文章**
   - 檢查網路連線
   - TechOrange 網站結構可能有變更

3. **Gemini API 錯誤**
   - 確認 API Key 正確
   - 檢查 API 額度限制

### 日誌檢查

檢查應用程序日誌以瞭解詳細錯誤資訊：

```bash
tail -f app.log  # 如果有設定日誌檔案
```

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 聯絡方式

如有問題請聯絡開發團隊。
