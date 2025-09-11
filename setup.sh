#!/bin/bash

echo "安裝 LINE TechOrange NewsBot 依賴套件..."

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 未找到 Python3，請先安裝 Python 3.10+"
    exit 1
fi

# 檢查是否有 uv
if command -v uv &> /dev/null; then
    echo "使用 uv 安裝依賴..."
    uv pip install -r requirements.txt
else
    echo "使用 pip 安裝依賴..."
    pip3 install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    echo "錯誤: 安裝依賴失敗"
    exit 1
fi

echo ""
echo "安裝完成！"
echo ""
echo "下一步:"
echo "1. 複製 .env.example 為 .env"
echo "2. 編輯 .env 檔案並填入你的 API Keys"
echo "3. 執行 python3 app.py 啟動服務"
echo ""
