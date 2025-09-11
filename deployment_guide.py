"""
部署檢查清單和設定指南
"""

print("""
🚀 LINE TechOrange NewsBot 部署指南

📋 部署前檢查清單:
═══════════════════════════════════════

1. ✅ Python 環境 (Python 3.10+)
2. ✅ 依賴套件安裝
3. ❓ LINE Bot 設定
4. ✅ Gemini API Key
5. ❓ .env 檔案設定
6. ❓ 本地測試
7. ❓ ngrok 設定
8. ❓ LINE Webhook 設定

📝 需要提供的資訊:
═════════════════════════

🔹 LINE Bot 資訊 (必須取得):
   📍 如何取得 LINE Bot 資訊:
   
   1. 前往 https://developers.line.biz/
   2. 使用您的 LINE 帳號登入
   3. 點擊 "Create a new provider"（如果是首次使用）
   4. 輸入 Provider 名稱（例如：TechOrange Bot）
   5. 點擊 "Create"
   6. 在 Provider 頁面點擊 "Create a Messaging API channel"
   7. 填寫 Channel 資訊：
      - Channel name: TechOrange NewsBot
      - Channel description: AI新聞摘要機器人
      - Category: News
      - Subcategory: IT/Technology
   8. 同意條款並創建
   
   🔑 取得必要金鑰:
   
   A. Channel Secret:
      - 在 Channel 設定頁面
      - "Basic settings" 標籤
      - 找到 "Channel secret" 並複製
   
   B. Channel Access Token:
      - 點擊 "Messaging API" 標籤
      - 在 "Channel access token" 區域
      - 點擊 "Issue" 按鈕生成 token
      - 複製生成的 token

🔹 其他設定:
   ✅ Gemini API Key: 已提供
   ❓ ngrok 帳號: 用於本地測試（可選）

🛠️ 設定步驟:
═══════════════

步驟 1: 編輯 .env 檔案
   - 開啟 .env 檔案
   - 將取得的 LINE 資訊填入：
     LINE_CHANNEL_ACCESS_TOKEN=你的_channel_access_token
     LINE_CHANNEL_SECRET=你的_channel_secret

步驟 2: 測試基本功能
   - 執行: python test_setup.py

步驟 3: 啟動本地伺服器
   - 執行: python app.py

步驟 4: 設定 ngrok（本地測試）
   - 下載 ngrok: https://ngrok.com/
   - 執行: ngrok http 5000
   - 複製 https URL

步驟 5: 設定 LINE Webhook
   - 回到 LINE Developers Console
   - "Messaging API" 標籤
   - 在 "Webhook settings" 設定：
     Webhook URL: https://你的ngrok網址.ngrok.io/callback
   - 啟用 "Use webhook"

步驟 6: 測試 Bot
   - 掃描 QR Code 加 Bot 為好友
   - 發送訊息測試

🌐 部署選項:
═══════════════

本地開發:
- ✅ ngrok + 本地 Python
- 優點: 免費、快速測試
- 缺點: 需要電腦持續運行

雲端部署:
- 🚀 Railway (推薦): https://railway.app/
- 🚀 Render: https://render.com/
- 🚀 Heroku: https://heroku.com/
- 🚀 Google Cloud Run

⚠️ 常見問題:
═══════════════

1. LINE Bot 沒反應:
   - 檢查 Webhook URL 是否正確
   - 確認 Channel Access Token 有效
   - 檢查伺服器是否運行

2. 爬蟲沒有結果:
   - 網路連線問題
   - TechOrange 網站結構變更
   - 關鍵字沒有相關文章

3. Gemini API 錯誤:
   - API Key 錯誤或過期
   - API 額度限制
   - 網路連線問題

📞 取得協助:
═══════════════

如果遇到問題，請提供：
1. 錯誤訊息截圖
2. test_setup.py 執行結果
3. LINE Bot 設定截圖（遮蔽敏感資訊）
""")
