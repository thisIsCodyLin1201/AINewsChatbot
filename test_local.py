"""
本機測試 LINE Bot 功能
模擬 LINE Webhook 請求來測試所有功能
"""
import json
import requests
from datetime import datetime


def test_webhook_health():
    """測試健康檢查端點"""
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"健康檢查: {response.status_code}")
        print(f"回應: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康檢查失敗: {e}")
        return False


def test_webhook_callback():
    """測試 LINE Webhook 回調（模擬）"""
    # 模擬 LINE Webhook 請求格式
    webhook_data = {
        "destination": "your_bot_id",
        "events": [
            {
                "type": "message",
                "message": {
                    "type": "text",
                    "id": "test_message_id",
                    "text": "/news 3"
                },
                "timestamp": int(datetime.now().timestamp() * 1000),
                "source": {
                    "type": "user",
                    "userId": "test_user_id"
                },
                "replyToken": "test_reply_token",
                "mode": "active"
            }
        ]
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Line-Signature': 'test_signature'  # 這會失敗，但可以測試錯誤處理
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/callback',
            data=json.dumps(webhook_data),
            headers=headers
        )
        print(f"Webhook 測試: {response.status_code}")
        print(f"回應: {response.text}")
        return response.status_code in [200, 400]  # 400 是預期的（簽名驗證失敗）
    except Exception as e:
        print(f"Webhook 測試失敗: {e}")
        return False


def test_news_functionality():
    """測試新聞功能"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from bot.news import get_news_articles
        from bot.summarize import summarize_article
        from bot.handlers import handle_message
        
        print("=== 測試新聞抓取 ===")
        articles = get_news_articles(3)
        if articles:
            print(f"✅ 成功抓取 {len(articles)} 篇文章")
            for i, article in enumerate(articles[:2], 1):
                print(f"{i}. {article['title'][:50]}...")
        else:
            print("❌ 新聞抓取失敗")
            return False
        
        print("\n=== 測試摘要功能 ===")
        test_content = "這是第一句話。這是第二句話。這是第三句話。這是第四句話。"
        summary = summarize_article(test_content)
        print(f"✅ 摘要: {summary}")
        
        print("\n=== 測試指令處理 ===")
        class MockEvent:
            class MockMessage:
                def __init__(self, text):
                    self.text = text
            def __init__(self, text):
                self.message = self.MockMessage(text)
        
        test_commands = ['/news', '/news 5', '新聞 3', 'hello']
        for cmd in test_commands:
            try:
                event = MockEvent(cmd)
                result = handle_message(event)
                print(f"✅ '{cmd}' → {len(result)} 字回覆")
            except Exception as e:
                print(f"❌ '{cmd}' 處理失敗: {e}")
        
        return True
        
    except Exception as e:
        print(f"功能測試失敗: {e}")
        return False


def main():
    """主測試函數"""
    print("🤖 LINE News Bot 本機測試")
    print("=" * 40)
    
    print("\n1. 檢查服務狀態...")
    health_ok = test_webhook_health()
    
    print("\n2. 測試核心功能...")
    func_ok = test_news_functionality()
    
    print("\n3. 測試 Webhook 端點...")
    webhook_ok = test_webhook_callback()
    
    print("\n" + "=" * 40)
    print("📊 測試結果:")
    print(f"   健康檢查: {'✅' if health_ok else '❌'}")
    print(f"   核心功能: {'✅' if func_ok else '❌'}")
    print(f"   Webhook: {'✅' if webhook_ok else '❌'}")
    
    if all([health_ok, func_ok]):
        print("\n🎉 Bot 功能完全正常！")
        print("📝 下一步：設定公網隧道來接收 LINE Webhook")
        print("\n建議方案：")
        print("1. 註冊 ngrok 免費帳戶：https://dashboard.ngrok.com/signup")
        print("2. 或使用其他隧道服務")
        print("3. 或部署到雲端平台（Heroku、Render 等）")
    else:
        print("\n⚠️  發現問題，請檢查服務狀態")


if __name__ == "__main__":
    main()
