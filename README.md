# LINE News Bot

一個基於 LINE Messaging API 的新聞摘要 Chatbot，提供 TechOrange 最新科技新聞。

## 功能特色

- `/news` 或 `/news N` 指令取得最新新聞（1-10 篇）
- 支援中文指令「新聞 N」
- 自動摘要生成（Lead-3 演算法）
- 健康檢查 API
- 完整錯誤處理機制

## 專案結構

```
line-news-bot/
├── app.py              # Flask 主程式 + LINE Webhook
├── bot/
│   ├── __init__.py     # Bot 套件初始化
│   ├── handlers.py     # 指令分派處理
│   ├── news.py         # TechOrange RSS 抓取
│   └── summarize.py    # Lead-3 摘要生成
├── .env.example        # 環境變數範本
├── pyproject.toml      # uv 依賴管理
├── uv.lock            # 依賴鎖定檔
└── README.md          # 專案說明
```

## 安裝與設定

### 1. 安裝依賴
```bash
# 使用 uv 安裝依賴
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 2. 設定環境變數
```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，填入你的 LINE Channel 資訊
```

`.env` 檔案內容：
```
LINE_CHANNEL_SECRET=your_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
```

### 3. 取得 LINE Channel 資訊
1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 創建 Provider 和 Channel（Messaging API）
3. 取得 Channel Secret 和 Channel Access Token
4. 設定 Webhook URL：`https://your-domain.com/callback`

## 本地開發

### 啟動服務
```bash
# 使用 uv
uv run python app.py

# 或直接執行
python app.py
```

### 使用 ngrok 建立公網 URL
```bash
# 安裝 ngrok
# 啟動 ngrok
ngrok http 5000

# 將產生的 https URL 設定為 LINE Webhook URL
# 例如：https://abc123.ngrok.io/callback
```

## 測試功能

### 測試新聞抓取
```bash
# 測試 RSS 抓取功能
uv run python -m bot.news

# 測試摘要功能
uv run python -m bot.summarize
```

### 健康檢查
```bash
curl http://localhost:5000/health
```

### LINE Bot 指令
在 LINE 中傳送以下訊息：
- `/news` - 取得最新 3 則新聞
- `/news 5` - 取得最新 5 則新聞
- `新聞 3` - 中文指令取得 3 則新聞

## 部署到雲端

### Render 部署
1. 推送程式碼到 GitHub
2. 連接 Render 到你的 repository
3. 設定環境變數
4. 部署服務

### Heroku 部署
```bash
# 創建 Procfile
echo "web: python app.py" > Procfile

# 推送到 Heroku
heroku create your-app-name
git push heroku main
heroku config:set LINE_CHANNEL_SECRET=your_secret
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_token
```

## API 文檔

### Webhook 端點
- `POST /callback` - LINE Bot webhook 回調
- `GET /health` - 健康檢查
- `GET /` - 服務首頁

### 回覆格式
```
📰 最新新聞摘要

1. 新聞標題
簡短摘要內容...
🔗 https://article-link.com

2. 第二則新聞標題
第二則新聞摘要...
🔗 https://article-link2.com
```

## 開發指南

### 新增新聞來源
在 `bot/news.py` 中新增新的 RSS 來源：
```python
def get_inside_articles(count=3):
    # 實作 Inside 新聞抓取
    pass
```

### 改進摘要演算法
在 `bot/summarize.py` 中實作更進階的摘要方法：
```python
def ai_summarize(content):
    # 整合 OpenAI 或其他 AI 服務
    pass
```

## 故障排除

### 常見錯誤
1. **Invalid signature** - 檢查 Channel Secret 是否正確
2. **抓不到新聞** - 檢查網路連線和 RSS URL
3. **Import 錯誤** - 確認已安裝所有依賴套件

### 除錯模式
```bash
# 啟用 Flask debug 模式
export FLASK_DEBUG=True
python app.py
```

## 授權

MIT License

## 聯絡資訊

如有問題請開 Issue 或聯絡維護者。
