# Render 部署故障排除指南

## 🔧 常見問題與解決方案

### 1. lxml/aiohttp 編譯錯誤
**錯誤訊息**: `ERROR: Failed building wheel for lxml` 或 `aiohttp compilation errors`

**解決方案**:
1. 移除 `lxml` 依賴，使用 `html5lib` 替代
2. 確保 `runtime.txt` 指定正確的 Python 版本 (3.11.5)
3. 在 render.yaml 中設定 `PYTHON_VERSION: "3.11"`

### 2. Python 版本不相容
**症狀**: 依賴包無法安裝

**解決方案**:
```
# runtime.txt
python-3.11.5

# render.yaml 環境變數
PYTHON_VERSION: "3.11"
```

### 3. 依賴安裝失敗
**解決方案**:
- 使用 `pip install --upgrade pip` 在 build 命令中
- 簡化 requirements.txt，移除非必要依賴
- 使用 `--no-cache-dir` flag

### 4. 記憶體不足
**症狀**: Build 過程中記憶體耗盡

**解決方案**:
- 升級到付費方案
- 減少並行 build 進程
- 使用預編譯的 wheels

### 5. 建議的 render.yaml 配置
```yaml
services:
  - type: web
    name: line-techorange-newsbot
    env: python
    region: singapore
    plan: free
    buildCommand: |
      pip install --upgrade pip
      pip install --no-cache-dir -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      # ... 其他環境變數
```

### 6. 最小化的 requirements.txt
```
flask==2.3.3
line-bot-sdk==3.5.0
requests==2.31.0
beautifulsoup4==4.12.2
feedparser==6.0.10
google-generativeai==0.3.2
python-dotenv==1.0.0
gunicorn==21.2.0
html5lib==1.1
```

## 🏥 健康檢查

部署後檢查以下端點：
- `/health` - 確認服務狀態
- `/` - 檢查首頁是否正常
- LINE Webhook 測試

## 📞 支援資源
- [Render Python 文件](https://render.com/docs/python)
- [Python 版本支援](https://render.com/docs/python-version)
- [Build 故障排除](https://render.com/docs/troubleshooting-deploys)
