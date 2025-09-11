@echo off
echo.
echo ================================================
echo   LINE TechOrange NewsBot 啟動腳本
echo ================================================
echo.

cd /d "c:\Users\cody9\OneDrive\桌面\newchatbot"

echo 🔍 檢查當前目錄...
echo 當前目錄: %cd%
echo.

echo 🔍 檢查必要檔案...
if not exist "app.py" (
    echo ❌ 找不到 app.py 檔案
    pause
    exit /b 1
)

if not exist ".env" (
    echo ❌ 找不到 .env 檔案
    pause
    exit /b 1
)

echo ✅ 檔案檢查完成
echo.

echo 🚀 啟動 Flask 應用...
echo 注意: 請保持此視窗開啟
echo.

python app.py

echo.
echo ⚠️ Flask 應用已停止
pause
