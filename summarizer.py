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
        
        # 嘗試初始化不同的模型（優先使用 Gemini 2.0 Flash）
        model_candidates = [
            'gemini-2.0-flash-exp',
            'gemini-2.0-flash', 
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro'
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
            
            logger.info(f"開始生成摘要，文章標題: {title}")
            
            # 生成摘要
            response = self.model.generate_content(prompt)
            
            logger.info(f"Gemini API 回應狀態: {hasattr(response, 'text')}")
            if hasattr(response, 'prompt_feedback'):
                logger.info(f"Prompt feedback: {response.prompt_feedback}")
            
            if response.text:
                summary = response.text.strip()
                
                # 摘要長度控制：如果超過 250 字才截斷（給 200 字目標一些彈性）
                if len(summary) > 250:
                    # 嘗試在句號處截斷以保持完整性
                    sentences = summary[:247].split('。')
                    if len(sentences) > 1:
                        summary = '。'.join(sentences[:-1]) + '。'
                    else:
                        summary = summary[:247] + "..."
                
                logger.info(f"摘要生成成功，長度: {len(summary)} 字")
                return summary
            else:
                logger.warning("Gemini API 返回空結果")
                return "無法生成摘要"
                
        except Exception as e:
            logger.error(f"摘要生成失敗: {str(e)}")
            logger.error(f"錯誤類型: {type(e).__name__}")
            # 返回簡化版摘要作為後備方案
            return self._fallback_summary(article_text, title)

    def _fallback_summary(self, article_text: str, title: str = "") -> str:
        """
        後備摘要方案：當 API 調用失敗時使用
        
        Args:
            article_text: 文章內容
            title: 文章標題
            
        Returns:
            簡化版摘要
        """
        try:
            # 取文章前幾句作為摘要
            sentences = article_text.split('。')
            summary_sentences = []
            char_count = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if char_count + len(sentence) <= 180:  # 調整為接近 200 字的限制
                    summary_sentences.append(sentence)
                    char_count += len(sentence) + 1  # +1 for the period
                else:
                    break
            
            if summary_sentences:
                return '。'.join(summary_sentences) + '。'
            else:
                # 如果沒有合適的句子，直接截取前 190 個字符
                return article_text[:190] + "..." if len(article_text) > 190 else article_text
                
        except Exception as e:
            logger.error(f"後備摘要生成失敗: {str(e)}")
            return "摘要生成失敗"

    def summarize_articles(self, articles: list) -> list:
        """
        批量生成多篇文章的摘要
        
        Args:
            articles: 文章列表，每個元素應包含 title, content, url
            
        Returns:
            包含摘要的文章列表
        """
        summarized_articles = []
        
        for article in articles:
            try:
                title = article.get('title', '')
                content = article.get('content', '')
                url = article.get('url', '')
                
                summary = self.summarize_text(content, title)
                
                summarized_article = {
                    'title': title,
                    'summary': summary,
                    'url': url,
                    'original_content': content
                }
                
                summarized_articles.append(summarized_article)
                
            except Exception as e:
                logger.error(f"處理文章摘要時發生錯誤: {str(e)}")
                # 即使單篇文章失敗，也繼續處理其他文章
                continue
        
        return summarized_articles

# 便利函數
def summarize_text(article_text: str, title: str = "") -> str:
    """
    便利函數：生成文章摘要
    
    Args:
        article_text: 文章內容
        title: 文章標題
        
    Returns:
        文章摘要
    """
    summarizer = GeminiSummarizer()
    return summarizer.summarize_text(article_text, title)

if __name__ == "__main__":
    # 測試用例
    test_title = "人工智慧的未來發展"
    test_content = """
    人工智慧（AI）技術正在快速發展，從機器學習到深度學習，再到生成式AI，
    每一個階段都帶來了革命性的變化。目前，ChatGPT等大語言模型的出現，
    讓AI技術更貼近普通用戶的日常生活。未來，AI將在更多領域發揮重要作用，
    包括醫療、教育、交通、金融等。然而，AI的發展也帶來了一些挑戰，
    如就業影響、隱私保護、倫理問題等，需要社會各界共同關注和解決。
    """
    
    try:
        summary = summarize_text(test_content, test_title)
        print(f"標題: {test_title}")
        print(f"摘要: {summary}")
        print(f"摘要長度: {len(summary)} 字")
    except Exception as e:
        print(f"測試失敗: {str(e)}")
        print("請確保已設置 GEMINI_API_KEY 環境變數")
