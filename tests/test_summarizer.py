"""
Gemini 摘要模組單元測試
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
from summarizer import GeminiSummarizer, summarize_text

class TestGeminiSummarizer(unittest.TestCase):
    
    def setUp(self):
        """測試前準備"""
        # 設置測試用的 API Key
        self.test_api_key = "test_api_key_12345"
        
    def test_summarizer_initialization_with_api_key(self):
        """測試使用 API Key 初始化摘要器"""
        with patch('summarizer.genai.configure') as mock_configure:
            with patch('summarizer.genai.GenerativeModel') as mock_model_class:
                # 模擬成功的模型初始化
                mock_model = Mock()
                mock_model.generate_content.return_value.text = "測試"
                mock_model_class.return_value = mock_model
                
                summarizer = GeminiSummarizer(api_key=self.test_api_key)
                
                # 驗證 API 配置被調用
                mock_configure.assert_called_once_with(api_key=self.test_api_key)
                # 驗證嘗試初始化模型
                self.assertTrue(mock_model_class.called)
                self.assertEqual(summarizer.api_key, self.test_api_key)
                self.assertIsNotNone(summarizer.model_name)
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'env_api_key'})
    def test_summarizer_initialization_from_env(self):
        """測試從環境變數初始化摘要器"""
        with patch('summarizer.genai.configure') as mock_configure:
            with patch('summarizer.genai.GenerativeModel') as mock_model:
                summarizer = GeminiSummarizer()
                
                # 驗證使用環境變數的 API Key
                mock_configure.assert_called_once_with(api_key='env_api_key')
                self.assertEqual(summarizer.api_key, 'env_api_key')
    
    def test_summarizer_initialization_no_api_key(self):
        """測試沒有 API Key 時的錯誤處理"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                GeminiSummarizer()
            
            self.assertIn("Gemini API Key 未設置", str(context.exception))
    
    @patch('summarizer.genai.configure')
    @patch('summarizer.genai.GenerativeModel')
    def test_summarize_text_success(self, mock_model_class, mock_configure):
        """測試成功生成摘要"""
        # 模擬 Gemini 回應
        mock_response = Mock()
        mock_response.text = "這是一個測試摘要，內容簡潔明瞭。"
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # 創建摘要器
        summarizer = GeminiSummarizer(api_key=self.test_api_key)
        
        # 執行測試
        test_content = "這是一篇很長的文章內容，需要被摘要..."
        summary = summarizer.summarize_text(test_content, "測試標題")
        
        # 驗證結果
        self.assertEqual(summary, "這是一個測試摘要，內容簡潔明瞭。")
        mock_model.generate_content.assert_called_once()
    
    @patch('summarizer.genai.configure')
    @patch('summarizer.genai.GenerativeModel')
    def test_summarize_text_long_summary(self, mock_model_class, mock_configure):
        """測試過長摘要的截斷處理"""
        # 模擬過長的回應
        long_summary = "這是一個非常長的摘要" * 20  # 超過 100 字
        mock_response = Mock()
        mock_response.text = long_summary
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # 創建摘要器
        summarizer = GeminiSummarizer(api_key=self.test_api_key)
        
        # 執行測試
        summary = summarizer.summarize_text("測試內容", "測試標題")
        
        # 驗證結果長度不超過 100 字
        self.assertLessEqual(len(summary), 100)
        self.assertTrue(summary.endswith("..."))
    
    @patch('summarizer.genai.configure')
    @patch('summarizer.genai.GenerativeModel')
    def test_summarize_text_api_error(self, mock_model_class, mock_configure):
        """測試 API 錯誤處理"""
        # 模擬 API 錯誤
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model
        
        # 創建摘要器
        summarizer = GeminiSummarizer(api_key=self.test_api_key)
        
        # 執行測試
        summary = summarizer.summarize_text("測試內容", "測試標題")
        
        # 驗證使用後備摘要
        self.assertNotEqual(summary, "")
        self.assertNotIn("API Error", summary)
    
    @patch('summarizer.genai.configure')
    @patch('summarizer.genai.GenerativeModel')
    def test_summarize_text_empty_content(self, mock_model_class, mock_configure):
        """測試空內容處理"""
        # 創建摘要器
        summarizer = GeminiSummarizer(api_key=self.test_api_key)
        
        # 執行測試
        summary = summarizer.summarize_text("", "測試標題")
        
        # 驗證結果
        self.assertEqual(summary, "無法取得文章內容")
    
    @patch('summarizer.genai.configure')
    @patch('summarizer.genai.GenerativeModel')
    def test_summarize_text_empty_response(self, mock_model_class, mock_configure):
        """測試空回應處理"""
        # 模擬空回應
        mock_response = Mock()
        mock_response.text = None
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # 創建摘要器
        summarizer = GeminiSummarizer(api_key=self.test_api_key)
        
        # 執行測試
        summary = summarizer.summarize_text("測試內容", "測試標題")
        
        # 驗證結果
        self.assertEqual(summary, "無法生成摘要")
    
    def test_fallback_summary(self):
        """測試後備摘要功能"""
        with patch('summarizer.genai.configure'):
            with patch('summarizer.genai.GenerativeModel'):
                summarizer = GeminiSummarizer(api_key=self.test_api_key)
                
                # 測試正常文本
                test_content = "這是第一句話。這是第二句話。這是第三句話。"
                fallback = summarizer._fallback_summary(test_content, "測試")
                
                # 驗證結果
                self.assertIn("這是第一句話", fallback)
                self.assertLessEqual(len(fallback), 100)
    
    @patch('summarizer.genai.configure')
    @patch('summarizer.genai.GenerativeModel')
    def test_summarize_articles_batch(self, mock_model_class, mock_configure):
        """測試批量摘要功能"""
        # 模擬回應
        mock_response = Mock()
        mock_response.text = "測試摘要"
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # 創建摘要器
        summarizer = GeminiSummarizer(api_key=self.test_api_key)
        
        # 測試資料
        articles = [
            {
                'title': '文章1',
                'content': '內容1',
                'url': 'https://test1.com'
            },
            {
                'title': '文章2',
                'content': '內容2',
                'url': 'https://test2.com'
            }
        ]
        
        # 執行測試
        results = summarizer.summarize_articles(articles)
        
        # 驗證結果
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn('title', result)
            self.assertIn('summary', result)
            self.assertIn('url', result)
            self.assertIn('original_content', result)

class TestSummarizeTextFunction(unittest.TestCase):
    """測試便利函數"""
    
    @patch('summarizer.GeminiSummarizer')
    def test_summarize_text_function(self, mock_summarizer_class):
        """測試 summarize_text 便利函數"""
        # 模擬摘要器實例
        mock_summarizer = Mock()
        mock_summarizer.summarize_text.return_value = "測試摘要"
        mock_summarizer_class.return_value = mock_summarizer
        
        # 執行測試
        summary = summarize_text("測試內容", "測試標題")
        
        # 驗證結果
        self.assertEqual(summary, "測試摘要")
        mock_summarizer.summarize_text.assert_called_once_with("測試內容", "測試標題")

class TestPromptGeneration(unittest.TestCase):
    """測試提示詞生成"""
    
    @patch('summarizer.genai.configure')
    @patch('summarizer.genai.GenerativeModel')
    def test_prompt_contains_required_elements(self, mock_model_class, mock_configure):
        """測試提示詞包含必要元素"""
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        summarizer = GeminiSummarizer(api_key="test")
        
        # 模擬摘要調用以檢查提示詞
        def capture_prompt(prompt):
            self.assertIn("100 個字", prompt)
            self.assertIn("中文摘要", prompt)
            self.assertIn("測試標題", prompt)
            self.assertIn("測試內容", prompt)
            mock_response = Mock()
            mock_response.text = "測試摘要"
            return mock_response
        
        mock_model.generate_content.side_effect = capture_prompt
        
        # 執行測試
        summarizer.summarize_text("測試內容", "測試標題")

if __name__ == '__main__':
    # 執行測試
    unittest.main(verbosity=2)
