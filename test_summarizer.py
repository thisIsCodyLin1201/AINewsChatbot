"""
測試智能模型切換功能
"""

import os
import sys
sys.path.append('.')

from summarizer import GeminiSummarizer

def test_model_switching():
    """
    測試智能模型切換功能
    """
    print("🧪 開始測試智能模型切換功能...")
    
    try:
        # 初始化摘要器
        summarizer = GeminiSummarizer()
        
        # 顯示初始模型狀態
        status = summarizer.get_model_status()
        print(f"\n📊 初始模型狀態:")
        print(f"   - 當前模型: {status['current_model']}")
        print(f"   - 描述: {status['current_model_info']['description']}")
        print(f"   - RPM限制: {status['current_model_info']['rpm_limit']}")
        print(f"   - 失敗模型: {len(status['failed_models'])} 個")
        print(f"   - 可用模型: {len(status['available_models'])} 個")
        
        # 測試簡單摘要
        test_title = "AI 技術突破"
        test_content = """
        人工智慧技術在近期取得重大突破，新的語言模型展現出前所未有的能力。
        這項技術將會改變我們與機器互動的方式，並在各個領域帶來革命性的變化。
        專家預測，這將是科技發展史上的重要里程碑。
        """
        
        print(f"\n📝 測試摘要生成...")
        print(f"   標題: {test_title}")
        
        summary = summarizer.summarize_article(test_title, test_content)
        
        print(f"\n✅ 摘要結果:")
        print(f"   {summary}")
        
        # 測試批量摘要
        test_articles = [
            {
                'title': 'AI 晶片創新',
                'content': '新一代AI晶片採用更先進的製程技術，能效大幅提升。這將推動人工智慧應用的普及化，降低運算成本。',
                'url': 'https://example.com/1'
            },
            {
                'title': '5G 技術發展',
                'content': '5G網路基礎建設持續擴展，為物聯網和智慧城市應用提供強大支撐。超低延遲特性開啟全新應用可能。',
                'url': 'https://example.com/2'
            }
        ]
        
        print(f"\n📚 測試批量摘要生成...")
        summarized_articles = summarizer.summarize_articles(test_articles)
        
        print(f"\n✅ 批量摘要結果:")
        for i, article in enumerate(summarized_articles):
            print(f"   文章 {i+1}: {article['title']}")
            print(f"   摘要: {article['summary'][:100]}...")
        
        # 顯示最終狀態
        final_status = summarizer.get_model_status()
        print(f"\n📊 最終模型狀態:")
        print(f"   - 當前模型: {final_status['current_model']}")
        print(f"   - 失敗模型: {len(final_status['failed_models'])} 個")
        
        if final_status['failed_models']:
            print(f"   - 失敗模型列表: {final_status['failed_models']}")
        
        print("\n🎉 測試完成!")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_switching()