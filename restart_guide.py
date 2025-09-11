"""
快速啟動指南
"""

print("""
🚀 LINE TechOrange NewsBot 重啟指南
═══════════════════════════════════════

📋 重啟步驟 (按順序執行):

1️⃣ 啟動 Flask 應用
   方法A (推薦): 雙擊 start_bot.bat
   方法B: 在 newchatbot 資料夾中執行 python app.py

2️⃣ 啟動 ngrok 隧道  
   方法A (推薦): 雙擊 start_ngrok.bat
   方法B: 在新的命令提示字元中執行 ngrok http 5000

3️⃣ 更新 LINE Webhook (如果 ngrok URL 改變)
   - 開啟 http://127.0.0.1:4040 查看新的 HTTPS URL
   - 前往 LINE Developers Console
   - 更新 Webhook URL: https://新網址.ngrok.io/callback

🎯 簡化版本 (推薦):
═══════════════════════

1. 雙擊 start_bot.bat    (啟動 Bot)
2. 雙擊 start_ngrok.bat  (啟動隧道)
3. 檢查並更新 Webhook URL (如有需要)

⚠️ 重要提醒:
═══════════════

- 保持兩個視窗都開啟
- 不要關閉命令提示字元視窗
- 如果要關機，記得先關閉這些程式

🔍 檢查狀態:
═══════════════

- Flask 應用: http://127.0.0.1:5000/health
- ngrok 狀態: http://127.0.0.1:4040
- 測試 Bot: 在 LINE 中發送訊息

📁 檔案說明:
═══════════════

- start_bot.bat    → 啟動 LINE Bot (Flask 應用)
- start_ngrok.bat  → 啟動 ngrok 隧道
- app.py          → 主程式 (也可直接執行)
""")
