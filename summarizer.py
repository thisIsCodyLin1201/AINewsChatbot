"""
Google Gemini API 摘要模組
支援智能模型切換，當某個模型配額用盡時自動切換到下一個可用模型
"""

import os
import google.generativeai as genai
from typing import Optional, List, Dict
import logging
import time

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiSummarizer:
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Gemini 摘要器，支援智能模型切換
        
        Args:
            api_key: Gemini API 金鑰，如果不提供則從環境變數讀取
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API Key 未設置！請設置 GEMINI_API_KEY 環境變數")
        
        # 配置 Gemini API
        genai.configure(api_key=self.api_key)
        
        # 按優先順序排列的模型列表（基於配額限制和效能）
        self.model_candidates = [
            # 免費層級配額較高的模型優先
            {
                'name': 'gemini-2.0-flash-lite',
                'rpm_limit': 30,  # 免費層級最高
                'description': '成本效益最佳，低延遲'
            },
            {
                'name': 'gemini-2.5-flash-lite', 
                'rpm_limit': 15,
                'description': '成本效益最佳，高吞吐量'
            },
            {
                'name': 'gemini-2.0-flash',
                'rpm_limit': 15,
                'description': '次世代功能，速度快'
            },
            {
                'name': 'gemini-1.5-flash',
                'rpm_limit': 15,
                'description': '快速且多功能'
            },
            {
                'name': 'gemini-2.5-flash',
                'rpm_limit': 10,
                'description': '價效比最佳，適應性思考'
            },
            {
                'name': 'gemini-1.5-flash-8b',
                'rpm_limit': 15,
                'description': '高量低智慧任務'
            },
            {
                'name': 'gemini-2.5-pro',
                'rpm_limit': 5,
                'description': '最強推理能力'
            },
            {
                'name': 'gemini-1.5-pro',
                'rpm_limit': 5,  # 估計值
                'description': '複雜推理任務'
            }
        ]
        
        self.model = None
        self.current_model_info = None
        self.failed_models = set()  # 記錄失敗的模型
        
        # 初始化模型
        self._initialize_model()
    
    def _initialize_model(self):
        """
        智能初始化模型，自動選擇可用的模型
        """
        logger.info("開始智能模型選擇...")
        
        for model_info in self.model_candidates:
            model_name = model_info['name']
            
            # 跳過已知失敗的模型
            if model_name in self.failed_models:
                continue
                
            try:
                logger.info(f"嘗試初始化模型: {model_name} ({model_info['description']})")
                
                # 建立模型實例
                self.model = genai.GenerativeModel(model_name)
                
                # 測試模型可用性
                test_response = self._test_model()
                
                if test_response:
                    self.current_model_info = model_info
                    logger.info(f"✅ 成功初始化模型: {model_name}")
                    logger.info(f"   - 描述: {model_info['description']}")
                    logger.info(f"   - 免費層級限制: {model_info['rpm_limit']} RPM")
                    return True
                else:
                    logger.warning(f"❌ 模型 {model_name} 測試失敗")
                    self.failed_models.add(model_name)
                    
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"❌ 模型 {model_name} 初始化失敗: {error_msg}")
                
                # 檢查是否是配額錯誤
                if '429' in error_msg or 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
                    logger.info(f"   → 配額用盡，將此模型標記為不可用")
                    self.failed_models.add(model_name)
                
                continue
        
        # 如果所有模型都失敗
        logger.error("❌ 所有 Gemini 模型都無法使用！")
        raise RuntimeError("無法初始化任何 Gemini 模型，請檢查 API 金鑰和配額")
    
    def _test_model(self) -> bool:
        """
        測試模型是否可用
        
        Returns:
            bool: 模型是否可用
        """
        try:
            response = self.model.generate_content("Hello")
            return response and response.text
        except Exception as e:
            logger.warning(f"模型測試失敗: {str(e)}")
            return False
    
    def _switch_to_next_model(self) -> bool:
        """
        切換到下一個可用的模型
        
        Returns:
            bool: 是否成功切換
        """
        if self.current_model_info:
            current_model = self.current_model_info['name']
            logger.warning(f"🔄 模型 {current_model} 配額用盡，嘗試切換到下一個模型...")
            self.failed_models.add(current_model)
        
        # 重新初始化
        try:
            self._initialize_model()
            return True
        except Exception as e:
            logger.error(f"無法切換到其他模型: {str(e)}")
            return False
    
    def _generate_content_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        智能重試機制，包含模型切換
        
        Args:
            prompt: 輸入提示
            max_retries: 最大重試次數
            
        Returns:
            生成的內容或 None
        """
        for attempt in range(max_retries):
            try:
                if not self.model:
                    logger.error("沒有可用的模型")
                    return None
                
                logger.info(f"使用模型 {self.current_model_info['name']} 生成內容 (嘗試 {attempt + 1}/{max_retries})")
                
                response = self.model.generate_content(prompt)
                
                if response and response.text:
                    return response.text.strip()
                else:
                    logger.warning("模型返回空回應")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"生成內容失敗 (嘗試 {attempt + 1}): {error_msg}")
                
                # 檢查是否是配額錯誤
                if '429' in error_msg or 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
                    logger.warning("⚠️ 檢測到配額限制錯誤，嘗試切換模型...")
                    
                    if self._switch_to_next_model():
                        logger.info("✅ 成功切換到新模型，繼續重試...")
                        continue
                    else:
                        logger.error("❌ 無法切換到其他模型")
                        return None
                        
                # 其他錯誤，等待後重試
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.info(f"等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
        
        logger.error(f"重試 {max_retries} 次後仍然失敗")
        return None
    
    def summarize_article(self, title: str, content: str) -> str:
        """
        生成文章摘要
        
        Args:
            title: 文章標題
            content: 文章內容
            
        Returns:
            摘要文字
        """
        try:
            # 建構提示詞
            prompt = f"""
            請針對以下科技新聞文章提供一個簡潔的中文摘要（大約100-150字）：

            標題：{title}
            
            內容：{content}
            
            摘要要求：
            1. 用繁體中文撰寫
            2. 突出重點資訊
            3. 保持客觀中性
            4. 約100-150字
            5. 適合LINE訊息閱讀
            """
            
            logger.info(f"開始生成摘要，使用模型: {self.current_model_info['name']}")
            
            # 使用智能重試機制生成摘要
            summary = self._generate_content_with_retry(prompt)
            
            if summary:
                logger.info(f"✅ 摘要生成成功，長度: {len(summary)} 字")
                return summary
            else:
                logger.error("❌ 摘要生成失敗")
                return "抱歉，目前無法生成摘要，請稍後再試。"
                
        except Exception as e:
            logger.error(f"摘要生成過程發生錯誤: {str(e)}")
            return "抱歉，摘要生成發生錯誤，請稍後再試。"
    
    def summarize_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        批量生成多篇文章摘要
        
        Args:
            articles: 文章列表，每個元素為包含 title, content 的字典
            
        Returns:
            包含摘要的文章列表
        """
        try:
            logger.info(f"開始批量生成 {len(articles)} 篇文章摘要...")
            summarized_articles = []
            
            for i, article in enumerate(articles):
                try:
                    title = article.get('title', '無標題')
                    content = article.get('content', '')
                    url = article.get('url', '')
                    
                    if not content:
                        logger.warning(f"文章 {i+1} 內容為空，跳過摘要生成")
                        # 保持原始文章結構，但添加默認摘要
                        article_copy = article.copy()
                        article_copy['summary'] = "抱歉，無法獲取文章內容進行摘要。"
                        summarized_articles.append(article_copy)
                        continue
                    
                    logger.info(f"正在處理第 {i+1}/{len(articles)} 篇文章: {title[:50]}...")
                    
                    # 生成摘要
                    summary = self.summarize_article(title, content)
                    
                    # 創建包含摘要的文章副本
                    article_copy = article.copy()
                    article_copy['summary'] = summary
                    summarized_articles.append(article_copy)
                    
                    logger.info(f"✅ 第 {i+1} 篇文章摘要完成")
                    
                    # 添加小延遲以避免過度頻繁的 API 調用
                    if i < len(articles) - 1:  # 不是最後一篇
                        time.sleep(1)
                        
                except Exception as e:
                    logger.error(f"處理第 {i+1} 篇文章時發生錯誤: {str(e)}")
                    # 即使個別文章處理失敗，也要保持原始文章結構
                    article_copy = article.copy()
                    article_copy['summary'] = "抱歉，摘要生成失敗，請稍後再試。"
                    summarized_articles.append(article_copy)
                    continue
            
            logger.info(f"✅ 批量摘要生成完成，成功處理 {len(summarized_articles)} 篇文章")
            return summarized_articles
            
        except Exception as e:
            logger.error(f"批量摘要生成過程發生錯誤: {str(e)}")
            # 返回原始文章列表，添加錯誤摘要
            error_articles = []
            for article in articles:
                article_copy = article.copy()
                article_copy['summary'] = "抱歉，摘要服務暫時不可用。"
                error_articles.append(article_copy)
            return error_articles
    
    def get_model_status(self) -> Dict:
        """
        取得當前模型狀態資訊
        
        Returns:
            包含模型狀態的字典
        """
        return {
            'current_model': self.current_model_info['name'] if self.current_model_info else None,
            'current_model_info': self.current_model_info,
            'failed_models': list(self.failed_models),
            'available_models': [
                model for model in self.model_candidates 
                if model['name'] not in self.failed_models
            ]
        }
    
    def reset_failed_models(self):
        """
        重置失敗模型記錄（可能在一段時間後配額重置）
        """
        logger.info("重置失敗模型記錄...")
        self.failed_models.clear()
        self._initialize_model()


# 創建全域實例
_summarizer_instance = None

def get_summarizer() -> GeminiSummarizer:
    """
    取得 GeminiSummarizer 單例實例
    
    Returns:
        GeminiSummarizer 實例
    """
    global _summarizer_instance
    
    if _summarizer_instance is None:
        try:
            _summarizer_instance = GeminiSummarizer()
        except Exception as e:
            logger.error(f"初始化 GeminiSummarizer 失敗: {str(e)}")
            raise
    
    return _summarizer_instance

def summarize_article(title: str, content: str) -> str:
    """
    便利函數：生成文章摘要
    
    Args:
        title: 文章標題
        content: 文章內容
        
    Returns:
        摘要文字
    """
    try:
        summarizer = get_summarizer()
        return summarizer.summarize_article(title, content)
    except Exception as e:
        logger.error(f"摘要生成失敗: {str(e)}")
        return "抱歉，目前無法生成摘要，請稍後再試。"