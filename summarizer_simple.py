"""
文章摘要模組 (無 AI 版本)
提供基本的文章摘要功能，不依賴外部 AI API
"""

import os
from typing import Optional
import logging
import re

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiSummarizer:
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化摘要器 (無 AI 版本)
        
        Args:
            api_key: 保留參數以維持介面相容性
        """
        logger.info("摘要器初始化為無 AI 版本，將使用基本文字處理方法")
        
    def summarize_text(self, article_text: str, title: str = "") -> str:
        """
        使用基本文字處理產生文章摘要
        
        Args:
            article_text: 文章內容
            title: 文章標題（可選）
            
        Returns:
            簡單的文章摘要
        """
        try:
            if not article_text.strip():
                return "無法取得文章內容"
            
            # 清理文本
            clean_text = self._clean_text(article_text)
            
            # 如果文章很短，直接返回
            if len(clean_text) <= 200:
                return clean_text
            
            # 簡單的摘要策略：取前幾句話
            sentences = self._split_sentences(clean_text)
            
            # 選擇前 2-3 句作為摘要
            summary_sentences = []
            total_length = 0
            max_length = 150
            
            for sentence in sentences[:5]:  # 只考慮前5句
                if total_length + len(sentence) <= max_length:
                    summary_sentences.append(sentence)
                    total_length += len(sentence)
                else:
                    break
            
            if summary_sentences:
                summary = ''.join(summary_sentences)
            else:
                # 如果沒有合適的句子，截取前150字
                summary = clean_text[:150] + "..."
            
            # 確保不超過200字
            if len(summary) > 200:
                summary = summary[:197] + "..."
                
            logger.info(f"成功產生摘要，長度: {len(summary)} 字")
            return summary
            
        except Exception as e:
            logger.error(f"摘要產生失敗: {str(e)}")
            # 回退策略：簡單截取
            try:
                fallback = article_text[:100] + "..." if len(article_text) > 100 else article_text
                return fallback
            except:
                return "摘要產生失敗"
    
    def _clean_text(self, text: str) -> str:
        """清理文本，移除多餘的空白和特殊字符"""
        # 移除多餘的空白
        text = re.sub(r'\s+', ' ', text)
        
        # 移除HTML標籤
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除特殊符號（保留中文標點）
        text = re.sub(r'[^\w\s\u4e00-\u9fff。，！？；：「」『』（）【】]', '', text)
        
        return text.strip()
    
    def _split_sentences(self, text: str) -> list:
        """將文本分割成句子"""
        # 使用中文標點符號分割句子
        sentences = re.split(r'[。！？；]', text)
        
        # 清理空句子並加回標點
        result = []
        for i, sentence in enumerate(sentences[:-1]):  # 最後一個通常是空的
            if sentence.strip():
                # 重新加入標點
                if i < len(sentences) - 1:
                    # 找出原始的標點符號
                    original_pos = text.find(sentence) + len(sentence)
                    if original_pos < len(text):
                        punct = text[original_pos]
                        result.append(sentence.strip() + punct)
                    else:
                        result.append(sentence.strip() + '。')
                else:
                    result.append(sentence.strip())
        
        return result

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
