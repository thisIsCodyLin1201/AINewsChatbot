"""
手動測試腳本 - 測試各個模組功能
"""

def test_environment():
    """測試環境設置"""
    print("=== 環境測試 ===")
    
    try:
        import sys
        print(f"Python 版本: {sys.version}")
        
        # 測試套件導入
        import requests
        print("✅ requests")
        
        import bs4
        print("✅ beautifulsoup4")
        
        import feedparser
        print("✅ feedparser")
        
        import google.generativeai
        print("✅ google-generativeai")
        
        import flask
        print("✅ flask")
        
        from linebot import LineBotApi
        print("✅ line-bot-sdk")
        
        print("\n所有套件導入成功！")
        return True
        
    except ImportError as e:
        print(f"❌ 套件導入失敗: {e}")
        return False

def test_env_file():
    """測試環境變數檔案"""
    print("\n=== 環境變數測試 ===")
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        gemini_key = os.getenv('GEMINI_API_KEY')
        line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        line_secret = os.getenv('LINE_CHANNEL_SECRET')
        
        print(f"Gemini API Key: {'✅ 已設置' if gemini_key else '❌ 未設置'}")
        print(f"LINE Token: {'✅ 已設置' if line_token and line_token != 'your_line_channel_access_token_here' else '❌ 未設置'}")
        print(f"LINE Secret: {'✅ 已設置' if line_secret and line_secret != 'your_line_channel_secret_here' else '❌ 未設置'}")
        
        return all([gemini_key, line_token, line_secret])
        
    except Exception as e:
        print(f"❌ 環境變數測試失敗: {e}")
        return False

def test_crawler():
    """測試爬蟲功能"""
    print("\n=== 爬蟲模組測試 ===")
    
    try:
        from crawler import fetch_articles
        
        print("正在測試爬取功能...")
        articles = fetch_articles("AI", 1)
        
        print(f"爬取結果: 找到 {len(articles)} 篇文章")
        
        if articles:
            article = articles[0]
            print(f"標題: {article.get('title', 'N/A')[:50]}...")
            print(f"URL: {article.get('url', 'N/A')}")
            print(f"內容預覽: {article.get('content', 'N/A')[:100]}...")
            print("✅ 爬蟲功能正常")
            return True
        else:
            print("⚠️ 未找到文章，可能是網站結構變更或網路問題")
            return False
            
    except Exception as e:
        print(f"❌ 爬蟲測試失敗: {e}")
        return False

def test_summarizer():
    """測試摘要功能"""
    print("\n=== 摘要模組測試 ===")
    
    try:
        from summarizer import summarize_text
        
        test_content = """
        人工智慧（AI）技術正在快速發展，從機器學習到深度學習，再到生成式AI，
        每一個階段都帶來了革命性的變化。目前，ChatGPT等大語言模型的出現，
        讓AI技術更貼近普通用戶的日常生活。
        """
        
        print("正在測試摘要功能...")
        summary = summarize_text(test_content, "AI 技術發展測試")
        
        print(f"摘要結果: {summary}")
        print(f"摘要長度: {len(summary)} 字")
        
        if summary and len(summary) <= 100:
            print("✅ 摘要功能正常")
            return True
        else:
            print("⚠️ 摘要功能異常")
            return False
            
    except Exception as e:
        print(f"❌ 摘要測試失敗: {e}")
        print("請檢查 Gemini API Key 是否正確")
        return False

if __name__ == "__main__":
    print("🧪 LINE TechOrange NewsBot 測試腳本")
    print("=" * 50)
    
    # 執行測試
    env_ok = test_environment()
    env_file_ok = test_env_file()
    crawler_ok = test_crawler()
    summarizer_ok = test_summarizer()
    
    # 測試結果總結
    print("\n" + "=" * 50)
    print("📋 測試結果總結:")
    print(f"環境設置: {'✅' if env_ok else '❌'}")
    print(f"環境變數: {'✅' if env_file_ok else '❌'}")
    print(f"爬蟲功能: {'✅' if crawler_ok else '❌'}")
    print(f"摘要功能: {'✅' if summarizer_ok else '❌'}")
    
    if all([env_ok, env_file_ok, crawler_ok, summarizer_ok]):
        print("\n🎉 所有測試通過！可以繼續下一步部署。")
    else:
        print("\n⚠️ 部分測試失敗，請檢查以上錯誤訊息。")
