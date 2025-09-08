# 測試專用的簡單腳本
"""
測試 LINE News Bot 的各項功能
"""

def test_news_fetch():
    """測試新聞抓取功能"""
    print("=== 測試新聞抓取功能 ===")
    try:
        from bot.news import get_news_articles
        articles = get_news_articles(3)
        
        if articles:
            print(f"✅ 成功抓取 {len(articles)} 則新聞")
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title'][:50]}...")
        else:
            print("❌ 無法抓取新聞")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    print()


def test_summarize():
    """測試摘要功能"""
    print("=== 測試摘要功能 ===")
    try:
        from bot.summarize import summarize_article
        
        test_content = """
        人工智慧技術正在快速發展。深度學習模型的效能不斷提升。
        這些技術正在改變各個產業的運作模式。未來將會有更多創新應用出現。
        我們需要持續關注這些技術發展趨勢。
        """
        
        summary = summarize_article(test_content, max_length=100)
        print(f"✅ 原文: {test_content.strip()}")
        print(f"✅ 摘要: {summary}")
        print(f"✅ 摘要長度: {len(summary)} 字")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    print()


def test_handlers():
    """測試指令處理功能"""
    print("=== 測試指令處理功能 ===")
    try:
        # 模擬 LINE 事件物件
        class MockEvent:
            class MockMessage:
                def __init__(self, text):
                    self.text = text
            
            def __init__(self, text):
                self.message = self.MockMessage(text)
        
        from bot.handlers import handle_message
        
        # 測試各種指令
        test_commands = ['/news', '/news 5', '新聞 3', 'hello']
        
        for cmd in test_commands:
            try:
                event = MockEvent(cmd)
                result = handle_message(event)
                print(f"✅ 指令 '{cmd}' 處理成功")
            except Exception as e:
                print(f"❌ 指令 '{cmd}' 處理失敗: {e}")
                
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    print()


def main():
    """主測試函數"""
    print("🤖 LINE News Bot 功能測試\n")
    
    test_news_fetch()
    test_summarize()
    test_handlers()
    
    print("✅ 測試完成！")


if __name__ == "__main__":
    main()
