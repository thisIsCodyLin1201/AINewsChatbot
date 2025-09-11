#!/usr/bin/env python3
"""
部署前的完整功能測試
測試所有核心功能是否正常運作
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def test_imports():
    """測試所有必要套件的導入"""
    print("🧪 測試套件導入...")
    
    modules_to_test = [
        ('flask', 'Flask'),
        ('requests', 'requests'),
        ('aiohttp', 'aiohttp'),
        ('linebot', 'line-bot-sdk'),
        ('google.generativeai', 'google-generativeai'),
        ('bs4', 'BeautifulSoup4'),
        ('lxml', 'lxml'),
        ('feedparser', 'feedparser'),
        ('gunicorn', 'gunicorn')
    ]
    
    failed_imports = []
    
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {display_name}")
        except ImportError as e:
            print(f"  ❌ {display_name}: {e}")
            failed_imports.append(display_name)
    
    return len(failed_imports) == 0, failed_imports

def test_environment_variables():
    """測試環境變數設置"""
    print("\n🔑 測試環境變數...")
    
    required_vars = [
        'LINE_CHANNEL_ACCESS_TOKEN',
        'LINE_CHANNEL_SECRET',
        'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * 10}...{value[-4:]}")
        else:
            print(f"  ❌ {var}: 未設置")
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def test_modules():
    """測試自定義模組導入"""
    print("\n🔧 測試自定義模組...")
    
    modules = [
        'crawler',
        'summarizer', 
        'line_handler'
    ]
    
    failed_modules = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}.py")
        except ImportError as e:
            print(f"  ❌ {module}.py: {e}")
            failed_modules.append(module)
    
    return len(failed_modules) == 0, failed_modules

def test_crawler():
    """測試爬蟲功能"""
    print("\n🕷️ 測試爬蟲功能...")
    
    try:
        from crawler import TechOrangeCrawler
        crawler = TechOrangeCrawler()
        
        # 測試獲取文章列表
        articles = crawler.get_latest_articles(limit=1)
        if articles and len(articles) > 0:
            print(f"  ✅ 成功獲取 {len(articles)} 篇文章")
            article = articles[0]
            print(f"  📰 測試文章: {article.get('title', '無標題')[:50]}...")
            return True, None
        else:
            print("  ❌ 無法獲取文章")
            return False, "無法獲取文章"
            
    except Exception as e:
        print(f"  ❌ 爬蟲測試失敗: {e}")
        return False, str(e)

def test_summarizer():
    """測試摘要功能"""
    print("\n🤖 測試 Gemini 摘要功能...")
    
    try:
        from summarizer import GeminiSummarizer
        
        if not os.getenv('GEMINI_API_KEY'):
            print("  ⚠️ 跳過摘要測試 (無 API Key)")
            return True, "跳過測試"
        
        summarizer = GeminiSummarizer()
        
        # 測試摘要生成
        test_content = "這是一個測試文章。人工智能技術正在快速發展，對各行各業都產生了深遠的影響。"
        summary = summarizer.summarize_content(test_content)
        
        if summary and len(summary) > 10:
            print(f"  ✅ 摘要生成成功")
            print(f"  📝 測試摘要: {summary[:100]}...")
            return True, None
        else:
            print("  ❌ 摘要生成失敗")
            return False, "摘要內容為空或太短"
            
    except Exception as e:
        print(f"  ❌ 摘要測試失敗: {e}")
        return False, str(e)

def main():
    """主測試函數"""
    print("🚀 LINE TechOrange NewsBot 部署前測試")
    print("=" * 50)
    
    # 收集測試結果
    test_results = []
    
    # 測試套件導入
    success, details = test_imports()
    test_results.append(("套件導入", success, details))
    
    # 測試環境變數
    success, details = test_environment_variables()
    test_results.append(("環境變數", success, details))
    
    # 測試自定義模組
    success, details = test_modules()
    test_results.append(("自定義模組", success, details))
    
    # 測試爬蟲
    success, details = test_crawler()
    test_results.append(("爬蟲功能", success, details))
    
    # 測試摘要器
    success, details = test_summarizer()
    test_results.append(("摘要功能", success, details))
    
    # 總結測試結果
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, success, details in test_results:
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if not success and details:
            if isinstance(details, list):
                for detail in details:
                    print(f"    - {detail}")
            else:
                print(f"    - {details}")
        if success:
            passed += 1
    
    print(f"\n🎯 測試通過率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有測試通過！可以開始部署了。")
        return 0
    else:
        print("⚠️ 有測試失敗，請修正問題後再部署。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
