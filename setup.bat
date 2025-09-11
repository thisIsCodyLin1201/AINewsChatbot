@echo off
echo 安裝 LINE TechOrange NewsBot 依賴套件...

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到 Python，請先安裝 Python 3.10+
    pause
    exit /b 1
)

REM 檢查是否有 uv
uv --version >nul 2>&1
if errorlevel 1 (
    echo 使用 pip 安裝依賴...
    pip install -r requirements.txt
) else (
    echo 使用 uv 安裝依賴...
    uv pip install -r requirements.txt
)

if errorlevel 1 (
    echo 錯誤: 安裝依賴失敗
    pause
    exit /b 1
)

echo.
echo 安裝完成！
echo.
echo 下一步:
echo 1. 複製 .env.example 為 .env
echo 2. 編輯 .env 檔案並填入你的 API Keys
echo 3. 執行 python app.py 啟動服務
echo.
pause
