"""
測試多來源爬蟲功能
"""
from crawler import MultiSourceTechCrawler
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)

def test_multisource_crawler():
    """測試多來源爬蟲"""
    print("🔍 測試多來源科技新聞爬蟲...")
    
    # 初始化爬蟲
    crawler = MultiSourceTechCrawler()
    
    # 測試關鍵字
    test_keywords = ["AI", "5G", "區塊鏈"]
    
    for keyword in test_keywords:
        print(f"\n📰 搜尋關鍵字: {keyword}")
        print("=" * 50)
        
        articles = crawler.fetch_articles(keyword, 2)
        
        if articles:
            print(f"✅ 找到 {len(articles)} 篇文章:")
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. 標題: {article.get('title', '無標題')}")
                print(f"   來源: {article.get('source', '未知來源')}")
                print(f"   網址: {article.get('url', '無網址')}")
                print(f"   內容預覽: {article.get('content', '無內容')[:100]}...")
        else:
            print(f"❌ 沒有找到與 '{keyword}' 相關的文章")
        
        print()

if __name__ == "__main__":
    test_multisource_crawler()
