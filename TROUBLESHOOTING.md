# Render 部署故障排除指南

## 🔧 常見問題與解決方案

### 1. aiohttp 編譯錯誤 (最新)
**錯誤訊息**: 
```
aiohttp/_websocket.c:3042:53: error: 'PyLongObject' has no member named 'ob_digit'
ERROR: Failed building wheel for aiohttp
```

**原因**: aiohttp 版本與 Python 3.11+ 不相容，內部 C 結構已改變

**解決方案**:
1. 降級 google-generativeai 版本避免 aiohttp 依賴衝突:
   ```
   google-generativeai==0.2.2
   ```
2. 或明確指定相容的 aiohttp 版本:
   ```
   aiohttp==3.8.6
   ```
3. 使用預編譯的 binary wheels:
   ```yaml
   buildCommand: |
     pip install --upgrade pip setuptools wheel &&
     pip install --no-cache-dir --prefer-binary -r requirements.txt
   ```

### 2. lxml 編譯錯誤
**錯誤訊息**: `ERROR: Failed building wheel for lxml`

**解決方案**:
1. 移除 `lxml` 依賴，使用 `html5lib` 替代
2. 確保 `runtime.txt` 指定正確的 Python 版本 (3.11.5)
3. 在 render.yaml 中設定 `PYTHON_VERSION: "3.11.5"`

### 3. Python 版本不相容
**症狀**: 依賴包無法安裝

**解決方案**:
```
# runtime.txt
python-3.11.5

# render.yaml 環境變數
PYTHON_VERSION: "3.11.5"
```

### 4. 依賴安裝失敗
**解決方案**:
- 使用 `pip install --upgrade pip` 在 build 命令中
- 簡化 requirements.txt，移除非必要依賴
- 使用 `--no-cache-dir --prefer-binary` flags

### 5. 記憶體不足
**症狀**: Build 過程中記憶體耗盡

**解決方案**:
- 升級到付費方案
- 減少並行 build 進程
- 使用預編譯的 wheels

### 6. 建議的 render.yaml 配置
```yaml
services:
  - type: web
    name: line-techorange-newsbot
    env: python
    region: singapore
    plan: free
    buildCommand: |
      pip install --upgrade pip setuptools wheel &&
      pip install --no-cache-dir --prefer-binary -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PYTHON_VERSION
        value: "3.11.5"
      - key: DISABLE_COLLECTSTATIC
        value: "1"
      # ... 其他環境變數
```

### 7. 最小化的 requirements.txt (推薦)
```
flask==2.3.3
line-bot-sdk==3.5.0
requests==2.31.0
beautifulsoup4==4.12.2
feedparser==6.0.10
google-generativeai==0.2.2
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
