# 使用 Python 3.11 官方映像檔 (避免 3.13 的相容性問題)
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴和 curl (用於健康檢查)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    zlib1g-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 升級 pip 和安裝 wheel
RUN pip install --upgrade pip setuptools wheel

# 複製需求檔案
COPY requirements.txt .

# 先安裝問題套件的特定版本，避免編譯錯誤
RUN pip install --no-cache-dir --only-binary=all \
    lxml==4.9.3 \
    aiohttp==3.8.6

# 安裝其他 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 設定環境變數
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=10000

# 暴露端口
EXPOSE 10000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# 啟動指令
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
