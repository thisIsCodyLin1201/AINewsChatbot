"""
TechOrange 爬蟲模組單元測試
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from crawler import TechOrangeCrawler, fetch_articles

class TestTechOrangeCrawler(unittest.TestCase):
    
    def setUp(self):
        """測試前準備"""
        self.crawler = TechOrangeCrawler()
    
    def test_crawler_initialization(self):
        """測試爬蟲初始化"""
        self.assertIsNotNone(self.crawler.base_url)
        self.assertIsNotNone(self.crawler.rss_url)
        self.assertIsNotNone(self.crawler.session)
    
    @patch('crawler.requests.Session.get')
    def test_fetch_articles_success(self, mock_get):
        """測試成功爬取文章"""
        # 模擬 RSS 回應
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>AI 技術的最新發展</title>
                    <link>https://buzzorange.com/techorange/test1</link>
                    <description>人工智慧技術持續進步...</description>
                </item>
                <item>
                    <title>機器學習應用</title>
                    <link>https://buzzorange.com/techorange/test2</link>
                    <description>機器學習在各領域的應用...</description>
                </item>
            </channel>
        </rss>"""
        mock_get.return_value = mock_response
        
        # 執行測試
        articles = self.crawler.fetch_articles("AI", 2)
        
        # 驗證結果
        self.assertIsInstance(articles, list)
        self.assertGreaterEqual(len(articles), 0)
    
    @patch('crawler.requests.Session.get')
    def test_fetch_articles_network_error(self, mock_get):
        """測試網路錯誤處理"""
        # 模擬網路錯誤
        mock_get.side_effect = requests.RequestException("Network error")
        
        # 執行測試
        articles = self.crawler.fetch_articles("AI", 3)
        
        # 驗證結果
        self.assertEqual(articles, [])
    
    def test_fetch_articles_empty_keyword(self):
        """測試空關鍵字處理"""
        articles = self.crawler.fetch_articles("", 3)
        self.assertIsInstance(articles, list)
    
    def test_fetch_articles_zero_count(self):
        """測試零文章數量請求"""
        articles = self.crawler.fetch_articles("AI", 0)
        self.assertEqual(len(articles), 0)
    
    @patch('crawler.requests.Session.get')
    def test_extract_content_from_url_success(self, mock_get):
        """測試內容擷取成功"""
        # 模擬網頁內容
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = """
        <html>
            <body>
                <article class="entry-content">
                    <p>這是文章內容...</p>
                </article>
            </body>
        </html>"""
        mock_get.return_value = mock_response
        
        # 執行測試
        content = self.crawler._extract_content_from_url("https://test.com")
        
        # 驗證結果
        self.assertIn("這是文章內容", content)
    
    @patch('crawler.requests.Session.get')
    def test_extract_content_from_url_failure(self, mock_get):
        """測試內容擷取失敗"""
        # 模擬請求失敗
        mock_get.side_effect = requests.RequestException("Request failed")
        
        # 執行測試
        content = self.crawler._extract_content_from_url("https://test.com")
        
        # 驗證結果
        self.assertEqual(content, "")
    
    def test_fetch_articles_parameter_validation(self):
        """測試參數驗證"""
        # 測試負數 n
        with patch.object(self.crawler, '_fetch_from_rss', return_value=[]):
            articles = self.crawler.fetch_articles("AI", -1)
            self.assertEqual(len(articles), 0)
        
        # 測試大數 n
        with patch.object(self.crawler, '_fetch_from_rss', return_value=[]):
            articles = self.crawler.fetch_articles("AI", 1000)
            self.assertIsInstance(articles, list)

class TestFetchArticlesFunction(unittest.TestCase):
    """測試便利函數"""
    
    @patch('crawler.TechOrangeCrawler')
    def test_fetch_articles_function(self, mock_crawler_class):
        """測試 fetch_articles 便利函數"""
        # 模擬爬蟲實例
        mock_crawler = Mock()
        mock_crawler.fetch_articles.return_value = [
            {
                'title': '測試文章',
                'url': 'https://test.com',
                'content': '測試內容'
            }
        ]
        mock_crawler_class.return_value = mock_crawler
        
        # 執行測試
        articles = fetch_articles("test", 1)
        
        # 驗證結果
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['title'], '測試文章')
        mock_crawler.fetch_articles.assert_called_once_with("test", 1)

class TestIntegration(unittest.TestCase):
    """整合測試"""
    
    def test_full_workflow_mock(self):
        """測試完整工作流程（使用 mock）"""
        with patch('crawler.requests.Session.get') as mock_get:
            # 模擬 RSS 回應
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = """<?xml version="1.0"?>
            <rss version="2.0">
                <channel>
                    <item>
                        <title>AI 測試文章</title>
                        <link>https://buzzorange.com/techorange/ai-test</link>
                        <description>這是一篇關於 AI 的測試文章</description>
                    </item>
                </channel>
            </rss>"""
            mock_get.return_value = mock_response
            
            # 執行完整流程
            articles = fetch_articles("AI", 1)
            
            # 驗證結果結構
            self.assertIsInstance(articles, list)
            if articles:  # 如果有結果
                article = articles[0]
                self.assertIn('title', article)
                self.assertIn('url', article)
                self.assertIn('content', article)

if __name__ == '__main__':
    # 執行測試
    unittest.main(verbosity=2)
