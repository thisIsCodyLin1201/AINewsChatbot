"""
Google Gemini API 摘要模組
負責使用 Gemini API 產生文章摘要
"""

import os
import google.generativeai as genai
from typing import Optional
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiSummarizer:
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Gemini 摘要器
        
        Args:
            api_key: Gemini API 金鑰，如果不提供則從環境變數讀取
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API Key 未設置！請設置 GEMINI_API_KEY 環境變數")
        
        # 配置 Gemini API
        genai.configure(api_key=self.api_key)
        
        # 嘗試初始化不同的模型（優先使用 flash 避免配額問題）
        model_candidates = [
            'gemini-1.5-flash',      # 優先使用 flash，配額較寬鬆
            'gemini-1.5-pro',
            'gemini-pro',
            'gemini-1.0-pro'
        ]
        
        self.model = None
        self.model_name = None
        
        for model_name in model_candidates:
            try:
                self.model = genai.GenerativeModel(model_name)
                # 測試模型是否可用
                test_response = self.model.generate_content("測試")
                self.model_name = model_name
                logger.info(f"成功初始化 Gemini 模型: {model_name}")
                break
            except Exception as e:
                logger.warning(f"模型 {model_name} 初始化失敗: {str(e)}")
                continue
        
        if not self.model:
            raise ValueError("無法初始化任何 Gemini 模型！請檢查 API Key 或網路連線")
        
        # 摘要提示詞模板
        self.summary_prompt = """
請為以下文章內容產生一個簡潔的中文摘要，要求：
1. 摘要盡量控制在 100-200 個字之間
2. 抓住文章的核心重點和關鍵資訊
3. 語言簡潔易懂，條理清晰
4. 適合快速閱讀，突出重要內容

文章標題：{title}

文章內容：
{content}

請提供摘要：
"""

    def summarize_text(self, article_text: str, title: str = "") -> str:
        """
        使用 Gemini API 產生文章摘要
        
        Args:
            article_text: 文章內容
            title: 文章標題（可選）
            
        Returns:
            不超過 100 字的中文摘要
        """
        try:
            if not article_text.strip():
                return "無法取得文章內容"
            
            # 限制輸入文本長度以避免 API 限制
            max_input_length = 8000
            if len(article_text) > max_input_length:
                article_text = article_text[:max_input_length] + "..."
            
            # 構建提示詞
            prompt = self.summary_prompt.format(
                title=title or "未提供標題",
                content=article_text
            )
            
            # 產生摘要
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                summary = response.text.strip()
                
                # 確保不超過指定長度
                if len(summary) > 200:
                    summary = summary[:197] + "..."
                
                logger.info(f"成功產生摘要，長度: {len(summary)} 字")
                return summary
            else:
                logger.warning("Gemini API 沒有返回有效回應")
                return "摘要產生失敗"
                
        except Exception as e:
            logger.error(f"摘要產生失敗: {str(e)}")
            # 回退策略：簡單截取前100字
            try:
                fallback = article_text[:100] + "..." if len(article_text) > 100 else article_text
                return fallback
            except:
                return "摘要產生失敗"

    def summarize_articles(self, articles: list) -> list:
        """
        批量處理文章摘要
        
        Args:
            articles: 文章列表，每個文章應包含 'content' 和可選的 'title' 欄位
            
        Returns:
            包含摘要的文章列表
        """
        summarized_articles = []
        
        for article in articles:
            try:
                content = article.get('content', '')
                title = article.get('title', '')
                
                summary = self.summarize_text(content, title)
                
                # 複製原文章資訊並添加摘要
                summarized_article = article.copy()
                summarized_article['summary'] = summary
                
                summarized_articles.append(summarized_article)
                
            except Exception as e:
                logger.error(f"處理文章摘要時發生錯誤: {str(e)}")
                # 即使摘要失敗，也保留原文章
                summarized_article = article.copy()
                summarized_article['summary'] = "摘要生成失敗"
                summarized_articles.append(summarized_article)
        
        return summarized_articles
