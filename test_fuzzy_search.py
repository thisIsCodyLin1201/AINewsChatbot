"""
測試模糊搜尋功能
"""
from crawler import TechOrangeCrawler
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)

def test_fuzzy_search():
    """測試模糊搜尋功能"""
    print("🔍 測試 TechOrange 模糊搜尋功能...")
    
    # 初始化爬蟲
    crawler = TechOrangeCrawler()
    
    # 測試關鍵字
    test_cases = [
        "AI",          # 精確匹配 + 同義詞
        "區塊鏈",       # 中文詞彙 + 英文同義詞
        "新創",        # 中文詞彙
        "金融科技",     # 複合詞
        "5G"           # 英數混合
    ]
    
    for keyword in test_cases:
        print(f"\n📰 搜尋關鍵字: '{keyword}'")
        print("=" * 50)
        
        # 測試模糊關鍵字生成
        fuzzy_keywords = crawler._generate_fuzzy_keywords(keyword.lower())
        print(f"🔤 模糊關鍵字: {fuzzy_keywords}")
        
        # 測試匹配分數計算
        test_titles = [
            f"{keyword}技術發展趨勢",
            f"最新{keyword}產業動態", 
            "科技創新與未來發展",
            f"{keyword}相關新聞"
        ]
        
        print("📊 匹配分數測試:")
        for title in test_titles:
            score = crawler._calculate_match_score(title.lower(), keyword.lower(), fuzzy_keywords)
            print(f"   '{title}' → 分數: {score}")
        
        print()

if __name__ == "__main__":
    test_fuzzy_search()
