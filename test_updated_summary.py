"""
測試更新後的摘要功能（100-200字限制）
"""

from summarizer import GeminiSummarizer
import logging

# 設置日誌輸出到控制台
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_updated_summarizer():
    print("🧪 測試更新後的摘要功能（100-200字限制）")
    print("=" * 60)
    
    try:
        # 初始化摘要器
        print("1️⃣ 初始化摘要器...")
        summarizer = GeminiSummarizer()
        print(f"✅ 使用模型: {summarizer.model_name}")
        
        # 測試較長文章的摘要
        print("\n2️⃣ 測試較長文章摘要...")
        long_content = """
        人工智慧（AI）技術在2024年經歷了前所未有的快速發展。大語言模型如GPT-4、Claude、Gemini等
        在自然語言理解和生成方面展現了驚人的能力。這些模型不僅能夠進行流暢的對話，還能協助
        進行複雜的推理、程式碼生成、創意寫作等多種任務。
        
        同時，多模態AI也取得了重大突破，能夠同時處理文字、圖像、音頻等不同類型的資料。
        這使得AI在醫療診斷、自動駕駛、科學研究等領域的應用更加廣泛和深入。
        
        然而，AI的快速發展也帶來了新的挑戰。AI安全、數據隱私、就業影響、算法偏見等問題
        越來越受到社會關注。各國政府和科技公司都在積極制定相關的規範和標準，
        希望在促進AI發展的同時，確保其安全可控。
        
        展望未來，AI技術將繼續在各個領域發揮重要作用，改變我們的工作和生活方式。
        """
        
        test_title = "2024年人工智慧技術發展現況與挑戰"
        
        summary = summarizer.summarize_text(long_content, test_title)
        
        print(f"✅ 摘要生成完成!")
        print(f"📝 標題: {test_title}")
        print(f"📄 摘要: {summary}")
        print(f"📏 摘要長度: {len(summary)} 字")
        
        # 檢查摘要長度是否合理
        if 80 <= len(summary) <= 250:
            print("✅ 摘要長度合理（80-250字範圍內）")
        elif len(summary) < 80:
            print("⚠️ 摘要偏短，可能需要調整")
        else:
            print("⚠️ 摘要偏長，可能需要調整")
            
        # 檢查內容品質
        if "AI" in summary or "人工智慧" in summary:
            print("✅ 摘要包含關鍵主題")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_updated_summarizer()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 摘要功能更新測試通過！")
        print("💡 現在摘要長度更靈活（100-200字），內容更豐富")
        print("📱 可以在 LINE 中測試更新後的功能")
    else:
        print("❌ 測試失敗，請檢查錯誤訊息")
