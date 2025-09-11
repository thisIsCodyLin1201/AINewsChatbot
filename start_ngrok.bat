@echo off
echo.
echo ================================================
echo   ngrok 隧道啟動腳本
echo ================================================
echo.

echo 🌐 啟動 ngrok 隧道 (Port 5000)...
echo 注意: 請保持此視窗開啟
echo.

ngrok http 5000

echo.
echo ⚠️ ngrok 隧道已停止
pause
