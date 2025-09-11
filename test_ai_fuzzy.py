"""
測試 Gemini AI 驅動的模糊搜尋功能
"""
import os
from dotenv import load_dotenv
from crawler import TechOrangeCrawler
import logging

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.INFO)

def test_ai_fuzzy_search():
    """測試 AI 模糊搜尋功能"""
    print("🤖 測試 Gemini AI 驅動的模糊搜尋功能...")
    
    # 檢查 API Key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ 未找到 GEMINI_API_KEY，將使用傳統模糊搜尋")
    else:
        print("✅ 找到 GEMINI_API_KEY，將使用 AI 模糊搜尋")
    
    # 初始化爬蟲
    crawler = TechOrangeCrawler()
    
    # 測試關鍵字
    test_keywords = [
        "AI",
        "永續",
        "元宇宙",
        "NFT",
        "遠距工作"
    ]
    
    for keyword in test_keywords:
        print(f"\n🔍 測試關鍵字: '{keyword}'")
        print("=" * 60)
        
        try:
            # 生成模糊關鍵字
            fuzzy_keywords = crawler._generate_fuzzy_keywords(keyword)
            print(f"📝 生成的相關關鍵字: {fuzzy_keywords}")
            
            # 模擬標題匹配測試
            test_titles = [
                f"{keyword}技術突破",
                f"企業導入{keyword}解決方案",
                "科技趨勢與創新應用",
                f"{keyword}市場分析報告"
            ]
            
            print("📊 匹配分數測試:")
            for title in test_titles:
                score = crawler._calculate_match_score(
                    title.lower(), 
                    keyword.lower(), 
                    fuzzy_keywords
                )
                print(f"   '{title}' → 分數: {score}")
                
        except Exception as e:
            print(f"❌ 測試失敗: {str(e)}")
        
        print()

def compare_search_methods():
    """比較 AI 搜尋與傳統搜尋的差異"""
    print("\n🔄 比較 AI 搜尋與傳統搜尋...")
    
    crawler = TechOrangeCrawler()
    test_keyword = "金融科技"
    
    print(f"關鍵字: {test_keyword}")
    print("-" * 40)
    
    # AI 生成關鍵字
    ai_keywords = crawler._generate_fuzzy_keywords(test_keyword)
    print(f"🤖 AI 生成: {ai_keywords}")
    
    # 傳統方法關鍵字
    traditional_keywords = crawler._generate_traditional_fuzzy_keywords(test_keyword)
    print(f"📚 傳統方法: {traditional_keywords}")
    
    # 比較覆蓋範圍
    ai_only = set(ai_keywords) - set(traditional_keywords)
    traditional_only = set(traditional_keywords) - set(ai_keywords)
    
    if ai_only:
        print(f"✨ AI 獨有關鍵字: {list(ai_only)}")
    if traditional_only:
        print(f"📖 傳統方法獨有: {list(traditional_only)}")

if __name__ == "__main__":
    test_ai_fuzzy_search()
    compare_search_methods()
