"""
LINE Messaging API 處理模組
負責處理 LINE webhook 事件和回傳訊息
"""

import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    CarouselTemplate, CarouselColumn, TemplateSendMessage,
    URIAction, MessageAction, PostbackAction
)
from typing import List, Dict, Optional
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LINENewsBot:
    def __init__(self, channel_access_token: Optional[str] = None, 
                 channel_secret: Optional[str] = None):
        """
        初始化 LINE Bot
        
        Args:
            channel_access_token: LINE Channel Access Token
            channel_secret: LINE Channel Secret
        """
        self.channel_access_token = channel_access_token or os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.channel_secret = channel_secret or os.getenv('LINE_CHANNEL_SECRET')
        
        if not self.channel_access_token or not self.channel_secret:
            raise ValueError("LINE Channel Access Token 和 Channel Secret 未設置！")
        
        # 初始化 LINE Bot API
        self.line_bot_api = LineBotApi(self.channel_access_token)
        self.handler = WebhookHandler(self.channel_secret)
        
        # 註冊訊息處理器
        self._register_handlers()

    def _register_handlers(self):
        """註冊 LINE Bot 事件處理器"""
        
        @self.handler.add(MessageEvent, message=TextMessage)
        def handle_text_message(event):
            self.handle_text_message_event(event)

    def handle_text_message_event(self, event):
        """
        處理用戶文字訊息事件
        
        Args:
            event: LINE MessageEvent 物件
        """
        try:
            user_message = event.message.text.strip()
            user_id = event.source.user_id
            
            logger.info(f"收到用戶訊息: {user_message} (用戶ID: {user_id})")
            
            # 檢查是否為有效的關鍵字查詢
            if len(user_message) < 1:
                reply_message = TextSendMessage(text="請輸入關鍵字來搜尋 TechOrange 文章！")
                self.line_bot_api.reply_message(event.reply_token, reply_message)
                return
            
            # 處理關鍵字查詢
            self.process_keyword_query(event, user_message)
            
        except Exception as e:
            logger.error(f"處理文字訊息時發生錯誤: {str(e)}")
            error_message = TextSendMessage(text="抱歉，處理您的請求時發生錯誤，請稍後再試。")
            try:
                self.line_bot_api.reply_message(event.reply_token, error_message)
            except LineBotApiError as api_error:
                logger.error(f"回傳錯誤訊息失敗: {str(api_error)}")

    def process_keyword_query(self, event, keyword: str):
        """
        處理關鍵字查詢請求
        
        Args:
            event: LINE MessageEvent 物件
            keyword: 用戶輸入的關鍵字
        """
        try:
            # 先回覆正在處理的訊息
            processing_message = TextSendMessage(text=f"正在搜尋「{keyword}」相關的 TechOrange 文章，請稍候...")
            self.line_bot_api.reply_message(event.reply_token, processing_message)
            
            # 這裡會由主應用程序調用爬蟲和摘要功能
            # 然後推送結果訊息給用戶
            
        except LineBotApiError as e:
            logger.error(f"回傳處理中訊息失敗: {str(e)}")

    def send_article_results(self, user_id: str, articles: List[Dict], keyword: str):
        """
        發送文章搜尋結果給用戶
        
        Args:
            user_id: LINE 用戶 ID
            articles: 包含摘要的文章列表
            keyword: 搜尋關鍵字
        """
        try:
            if not articles:
                no_result_message = TextSendMessage(
                    text=f"抱歉，沒有找到與「{keyword}」相關的 TechOrange 文章。請嘗試其他關鍵字。"
                )
                self.line_bot_api.push_message(user_id, no_result_message)
                return
            
            # 先發送總結訊息
            summary_message = TextSendMessage(
                text=f"📰 找到 {len(articles)} 篇與「{keyword}」相關的 TechOrange 文章："
            )
            self.line_bot_api.push_message(user_id, summary_message)
            
            # 分別發送每篇文章，避免內容被截斷
            for i, article in enumerate(articles, 1):
                try:
                    article_message = self._create_single_article_message(article, i)
                    self.line_bot_api.push_message(user_id, article_message)
                    
                    # 在多篇文章間稍作延遲，避免發送過快
                    if i < len(articles):
                        import time
                        time.sleep(0.5)
                        
                except Exception as e:
                    logger.error(f"發送第 {i} 篇文章失敗: {str(e)}")
                    continue
            
            logger.info(f"成功發送 {len(articles)} 篇文章結果給用戶 {user_id}")
            
        except LineBotApiError as e:
            logger.error(f"發送文章結果失敗: {str(e)}")
            # 嘗試發送錯誤訊息
            try:
                error_message = TextSendMessage(text="發送搜尋結果時發生錯誤，請稍後再試。")
                self.line_bot_api.push_message(user_id, error_message)
            except LineBotApiError:
                pass

    def _create_carousel_message(self, articles: List[Dict], keyword: str):
        """
        創建輪播格式訊息
        
        Args:
            articles: 文章列表
            keyword: 搜尋關鍵字
            
        Returns:
            TemplateSendMessage 物件
        """
        columns = []
        
        for i, article in enumerate(articles[:10]):  # LINE 輪播最多 10 個
            title = article.get('title', '無標題')
            summary = article.get('summary', '無摘要')
            url = article.get('url', '')
            
            # 確保標題不超過 40 字符（LINE 限制）
            if len(title) > 40:
                title = title[:37] + "..."
            
            # 確保摘要不超過 60 字符（LINE 限制）
            if len(summary) > 60:
                summary = summary[:57] + "..."
            
            column = CarouselColumn(
                thumbnail_image_url="https://buzzorange.com/wp-content/uploads/2019/08/TechOrange_logo.png",  # TechOrange Logo
                title=title,
                text=summary,
                actions=[
                    URIAction(
                        label="閱讀全文",
                        uri=url
                    )
                ]
            )
            columns.append(column)
        
        carousel_template = CarouselTemplate(columns=columns)
        return TemplateSendMessage(
            alt_text=f"找到 {len(articles)} 篇與「{keyword}」相關的文章",
            template=carousel_template
        )

    def _create_text_message(self, articles: List[Dict], keyword: str):
        """
        創建文字格式訊息
        
        Args:
            articles: 文章列表
            keyword: 搜尋關鍵字
            
        Returns:
            TextSendMessage 物件
        """
        message_text = f"📰 找到 {len(articles)} 篇與「{keyword}」相關的 TechOrange 文章：\n\n"
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', '無標題')
            summary = article.get('summary', '無摘要')
            url = article.get('url', '')
            
            message_text += f"{i}. {title}\n"
            message_text += f"📝 {summary}\n"
            message_text += f"🔗 {url}\n\n"
        
        # 確保訊息不超過 LINE 限制（5000 字符）
        if len(message_text) > 4900:
            message_text = message_text[:4900] + "\n...(內容過長，已截斷)"
        
        return TextSendMessage(text=message_text)

    def _create_single_article_message(self, article: Dict, index: int):
        """
        創建單篇文章訊息
        
        Args:
            article: 文章資料
            index: 文章編號
            
        Returns:
            TextSendMessage 物件
        """
        title = article.get('title', '無標題')
        summary = article.get('summary', '無摘要')
        url = article.get('url', '')
        
        # 構建訊息文字，充分展示完整摘要
        message_text = f"📰 文章 {index}\n\n"
        message_text += f"📝 標題：{title}\n\n"
        message_text += f"🤖 AI 摘要：\n{summary}\n\n"
        message_text += f"🔗 閱讀全文：{url}"
        
        # 確保訊息不超過 LINE 限制（5000 字符）
        if len(message_text) > 4900:
            # 如果超長，優先保留標題和連結，縮短摘要
            max_summary_length = 4900 - len(f"📰 文章 {index}\n\n📝 標題：{title}\n\n🤖 AI 摘要：\n\n\n🔗 閱讀全文：{url}")
            if max_summary_length > 100:
                truncated_summary = summary[:max_summary_length-3] + "..."
                message_text = f"📰 文章 {index}\n\n"
                message_text += f"📝 標題：{title}\n\n"
                message_text += f"🤖 AI 摘要：\n{truncated_summary}\n\n"
                message_text += f"🔗 閱讀全文：{url}"
        
        return TextSendMessage(text=message_text)

    def verify_signature(self, body: str, signature: str) -> bool:
        """
        驗證 LINE webhook 簽名
        
        Args:
            body: 請求內容
            signature: LINE 簽名
            
        Returns:
            驗證結果
        """
        try:
            self.handler.handle(body, signature)
            return True
        except InvalidSignatureError:
            logger.error("Invalid signature")
            return False

    def handle_webhook(self, body: str, signature: str):
        """
        處理 LINE webhook 請求
        
        Args:
            body: 請求內容
            signature: LINE 簽名
        """
        try:
            self.handler.handle(body, signature)
        except InvalidSignatureError:
            logger.error("Invalid signature")
            raise
        except Exception as e:
            logger.error(f"處理 webhook 時發生錯誤: {str(e)}")
            raise

# 便利函數和全域變數
_bot_instance = None

def get_line_bot() -> LINENewsBot:
    """取得 LINE Bot 實例（單例模式）"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = LINENewsBot()
    return _bot_instance

def send_article_results(user_id: str, articles: List[Dict], keyword: str):
    """便利函數：發送文章結果"""
    bot = get_line_bot()
    bot.send_article_results(user_id, articles, keyword)

if __name__ == "__main__":
    # 測試用例
    print("LINE Bot 模組載入成功")
    
    # 模擬文章資料
    test_articles = [
        {
            'title': 'AI 技術的最新發展',
            'summary': '人工智慧技術持續進步，在各領域都有重大突破，未來將改變我們的生活方式。',
            'url': 'https://buzzorange.com/techorange/test1'
        },
        {
            'title': '機器學習在醫療領域的應用',
            'summary': '機器學習幫助醫生更準確診斷疾病，提高治療效果，為醫療行業帶來革新。',
            'url': 'https://buzzorange.com/techorange/test2'
        }
    ]
    
    print(f"測試資料：{len(test_articles)} 篇文章")
