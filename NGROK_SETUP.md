# ngrok 設定完整指南

## 步驟 1: 下載 ngrok
1. 前往 https://ngrok.com/download
2. 選擇 "Windows (64-bit)" 版本
3. 下載 ngrok.exe 檔案

## 步驟 2: 安裝 ngrok
1. 將下載的 ngrok.exe 放到一個固定目錄（例如：C:\ngrok\）
2. 將該目錄加入系統 PATH 環境變數，或直接使用完整路徑

## 步驟 3: 註冊帳戶並取得 authtoken
1. 前往 https://dashboard.ngrok.com/signup 註冊帳戶
2. 前往 https://dashboard.ngrok.com/get-started/your-authtoken
3. 複製你的 authtoken

## 步驟 4: 設定 authtoken
在 PowerShell 中執行：
```powershell
# 如果 ngrok 在 PATH 中
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE

# 或使用完整路徑
C:\ngrok\ngrok.exe config add-authtoken YOUR_AUTHTOKEN_HERE
```

## 步驟 5: 啟動隧道
```powershell
# 確保你的 LINE Bot 正在運行在 port 5000
ngrok http 5000

# 或使用完整路徑
C:\ngrok\ngrok.exe http 5000
```

## 步驟 6: 設定 LINE Webhook
1. 複製 ngrok 顯示的 https URL（例如：https://abc123.ngrok.io）
2. 前往 LINE Developers Console
3. 在你的 Channel 設定中，將 Webhook URL 設為：
   https://abc123.ngrok.io/callback
4. 啟用 "Use webhook" 選項

## 測試指令
在 LINE 中測試：
- /news
- /news 5
- 新聞 3

## 故障排除
如果遇到問題：
1. 確認 LINE Bot 服務正在運行（python app.py）
2. 確認 ngrok 隧道已建立
3. 確認 LINE Webhook URL 設定正確
4. 檢查 ngrok 終端機的連線日誌
