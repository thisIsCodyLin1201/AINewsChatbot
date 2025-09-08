"""
LINE News Bot - 主程式
基於 Flask 的 LINE Bot，提供新聞摘要功能
"""
import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
from dotenv import load_dotenv
from bot.handlers import handle_message

# 載入環境變數
load_dotenv()

app = Flask(__name__)

# LINE Bot 設定
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


@app.route("/health", methods=['GET'])
def health_check():
    """健康檢查 API"""
    return {"status": "ok", "message": "LINE News Bot is running"}, 200


@app.route("/test", methods=['GET', 'POST'])
def test_endpoint():
    """測試端點"""
    return {"method": request.method, "message": "Test endpoint working"}, 200


@app.route("/callback", methods=['GET', 'POST'])
def callback():
    """LINE Bot Webhook 回調處理"""
    if request.method == 'GET':
        # LINE 的 Webhook 驗證可能會發送 GET 請求
        return {"status": "ok", "message": "LINE Bot callback endpoint"}, 200
    
    # 處理 POST 請求（實際的 Webhook）
    # 取得 X-Line-Signature 標頭值
    signature = request.headers.get('X-Line-Signature', '')

    # 取得請求主體作為文字
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 驗證請求來源
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        print(f"Error handling webhook: {e}")
        abort(500)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """處理文字訊息"""
    try:
        # 使用 handlers 模組處理訊息
        reply_text = handle_message(event)
        
        # 使用 v3 API 回覆訊息
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        
    except Exception as e:
        print(f"Error handling message: {e}")
        # 發生錯誤時的預設回覆
        error_text = "抱歉，系統發生錯誤，請稍後再試"
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=error_text)]
                    )
                )
        except:
            pass


@app.route("/", methods=['GET'])
def index():
    """首頁"""
    return """
    <h1>LINE News Bot</h1>
    <p>這是一個基於 LINE Messaging API 的新聞摘要 Bot</p>
    <h2>使用方式：</h2>
    <ul>
        <li>輸入 '/news' 取得最新 3 則新聞</li>
        <li>輸入 '/news N' 取得最新 N 則新聞（1-10 則）</li>
        <li>輸入 '新聞 N' 也可以使用中文指令</li>
    </ul>
    <h2>健康檢查：</h2>
    <p><a href="/health">/health</a></p>
    """


if __name__ == "__main__":
    # 從環境變數取得 PORT，預設為 4040
    port = int(os.environ.get('PORT', 4040))
    
    # 檢查必要的環境變數
    if not os.getenv('LINE_CHANNEL_ACCESS_TOKEN'):
        print("Warning: LINE_CHANNEL_ACCESS_TOKEN not found in environment variables")
    if not os.getenv('LINE_CHANNEL_SECRET'):
        print("Warning: LINE_CHANNEL_SECRET not found in environment variables")
    
    app.run(host='0.0.0.0', port=port, debug=True)