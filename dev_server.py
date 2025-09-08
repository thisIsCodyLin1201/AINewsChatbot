"""
開發模式啟動腳本
在沒有 LINE Channel 設定的情況下也能啟動基本服務
"""
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = Flask(__name__)


@app.route("/health", methods=['GET'])
def health_check():
    """健康檢查 API"""
    return {
        "status": "ok", 
        "message": "LINE News Bot is running",
        "has_line_config": bool(os.getenv('LINE_CHANNEL_ACCESS_TOKEN') and os.getenv('LINE_CHANNEL_SECRET'))
    }, 200


@app.route("/test-news", methods=['GET'])
def test_news():
    """測試新聞抓取功能"""
    try:
        from bot.news import get_news_articles
        articles = get_news_articles(3)
        
        if articles:
            return {
                "status": "success",
                "count": len(articles),
                "articles": [
                    {
                        "title": article['title'],
                        "summary": article['summary'][:100] + "..." if len(article['summary']) > 100 else article['summary'],
                        "link": article['link']
                    }
                    for article in articles
                ]
            }
        else:
            return {"status": "error", "message": "無法抓取新聞"}, 500
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


@app.route("/test-summary", methods=['POST'])
def test_summary():
    """測試摘要功能"""
    try:
        from bot.summarize import summarize_article
        
        data = request.get_json()
        if not data or 'content' not in data:
            return {"status": "error", "message": "請提供 content 欄位"}, 400
        
        content = data['content']
        max_length = data.get('max_length', 280)
        
        summary = summarize_article(content, max_length)
        
        return {
            "status": "success",
            "original_length": len(content),
            "summary_length": len(summary),
            "summary": summary
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


@app.route("/", methods=['GET'])
def index():
    """首頁"""
    has_line_config = bool(os.getenv('LINE_CHANNEL_ACCESS_TOKEN') and os.getenv('LINE_CHANNEL_SECRET'))
    
    return f"""
    <h1>LINE News Bot - 開發模式</h1>
    <p>這是一個基於 LINE Messaging API 的新聞摘要 Bot</p>
    
    <h2>狀態</h2>
    <p>LINE 設定: {'✅ 已配置' if has_line_config else '❌ 未配置'}</p>
    
    <h2>測試 API</h2>
    <ul>
        <li><a href="/health">健康檢查</a></li>
        <li><a href="/test-news">測試新聞抓取</a></li>
        <li>測試摘要功能 (POST /test-summary)</li>
    </ul>
    
    <h2>LINE Bot 使用方式：</h2>
    <ul>
        <li>輸入 '/news' 取得最新 3 則新聞</li>
        <li>輸入 '/news N' 取得最新 N 則新聞（1-10 則）</li>
        <li>輸入 '新聞 N' 也可以使用中文指令</li>
    </ul>
    
    <h2>設定指南</h2>
    <p>1. 複製 .env.example 為 .env</p>
    <p>2. 在 <a href="https://developers.line.biz/console/">LINE Developers Console</a> 取得 Channel Secret 和 Access Token</p>
    <p>3. 填入 .env 檔案並重新啟動</p>
    """


if __name__ == "__main__":
    # 從環境變數取得 PORT，預設為 5000
    port = int(os.environ.get('PORT', 5000))
    
    # 檢查必要的環境變數
    if not os.getenv('LINE_CHANNEL_ACCESS_TOKEN'):
        print("Warning: LINE_CHANNEL_ACCESS_TOKEN not found - running in development mode")
    if not os.getenv('LINE_CHANNEL_SECRET'):
        print("Warning: LINE_CHANNEL_SECRET not found - running in development mode")
    
    print(f"🤖 LINE News Bot starting on port {port}")
    print(f"📱 健康檢查: http://localhost:{port}/health")
    print(f"🧪 測試新聞: http://localhost:{port}/test-news")
    
    app.run(host='0.0.0.0', port=port, debug=True)
