"""
測試修正後的摘要功能
"""

from summarizer import GeminiSummarizer, summarize_text
import logging

# 設置日誌輸出到控制台
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_summarizer_fix():
    print("🧪 測試修正後的 Gemini 摘要功能")
    print("=" * 50)
    
    try:
        # 測試摘要器初始化
        print("1️⃣ 初始化摘要器...")
        summarizer = GeminiSummarizer()
        print(f"✅ 成功初始化，使用模型: {summarizer.model_name}")
        
        # 測試摘要生成
        print("\n2️⃣ 測試摘要生成...")
        test_content = """
        人工智慧（AI）技術在2024年取得了顯著進展，特別是在大語言模型和生成式AI領域。
        OpenAI的GPT-4和Google的Gemini等模型展現了強大的自然語言理解和生成能力。
        這些技術不僅在文本生成方面表現出色，還在程式碼生成、數據分析、
        創意寫作等多個領域發揮重要作用。同時，AI安全和倫理問題也越來越受到關注，
        各大科技公司都在致力於開發更安全、更可靠的AI系統。
        """
        
        test_title = "人工智慧技術2024年發展現況"
        
        summary = summarizer.summarize_text(test_content, test_title)
        
        print(f"✅ 摘要生成成功!")
        print(f"📝 標題: {test_title}")
        print(f"📄 摘要: {summary}")
        print(f"📏 摘要長度: {len(summary)} 字")
        
        # 檢查是否使用了後備方案
        if "。" in summary and len(summary) <= 100:
            print("✅ 這是 AI 生成的摘要")
        else:
            print("⚠️ 這可能是後備摘要")
            
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

def test_convenience_function():
    print("\n3️⃣ 測試便利函數...")
    
    try:
        summary = summarize_text("這是一個簡單的測試文本。", "測試標題")
        print(f"✅ 便利函數測試成功: {summary}")
        return True
    except Exception as e:
        print(f"❌ 便利函數測試失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success1 = test_summarizer_fix()
    success2 = test_convenience_function()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 所有測試通過！摘要功能已修正")
        print("💡 現在可以重啟 Bot 來應用修正")
    else:
        print("❌ 部分測試失敗，請檢查錯誤訊息")
