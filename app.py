"""
LINE TechOrange NewsBot 主應用程序
Flask 伺服器，處理 LINE webhook 和協調各模組
"""

import os
import threading
import time
from flask import Flask, request, abort
from dotenv import load_dotenv
import logging

# 載入環境變數
load_dotenv()

# 匯入自定義模組
from line_handler import LINENewsBot
from crawler import TechOrangeCrawler
from summarizer import GeminiSummarizer

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 Flask 應用
app = Flask(__name__)

# 全域變數
line_bot = None
crawler = None
summarizer = None

def initialize_components():
    """初始化所有組件"""
    global line_bot, crawler, summarizer
    
    try:
        # 初始化 LINE Bot
        line_bot = LINENewsBot()
        logger.info("LINE Bot 初始化成功")
        
        # 初始化爬蟲
        crawler = TechOrangeCrawler()
        logger.info("TechOrange 爬蟲初始化成功")
        
        # 初始化摘要器
        summarizer = GeminiSummarizer()
        logger.info("Gemini 摘要器初始化成功")
        
        return True
        
    except Exception as e:
        logger.error(f"組件初始化失敗: {str(e)}")
        return False

@app.route("/callback", methods=['POST'])
def callback():
    """LINE webhook 回調端點"""
    
    # 獲取 X-Line-Signature header 值
    signature = request.headers['X-Line-Signature']
    
    # 獲取請求內容
    body = request.get_data(as_text=True)
    logger.info(f"收到 webhook 請求: {body}")
    
    # 驗證簽名
    try:
        line_bot.handle_webhook(body, signature)
    except Exception as e:
        logger.error(f"處理 webhook 失敗: {str(e)}")
        abort(400)
    
    return 'OK'

@app.route("/health", methods=['GET'])
def health_check():
    """健康檢查端點"""
    return {
        'status': 'healthy',
        'components': {
            'line_bot': line_bot is not None,
            'crawler': crawler is not None,
            'summarizer': summarizer is not None
        }
    }

@app.route("/", methods=['GET'])
def index():
    """首頁"""
    return """
    <h1>LINE TechOrange NewsBot</h1>
    <p>狀態: 正常運行</p>
    <p>功能: 搜尋 TechOrange 文章並產生 AI 摘要</p>
    <p>使用方式: 在 LINE 中輸入關鍵字即可</p>
    """

class NewsBot:
    """新聞機器人主要邏輯類別"""
    
    def __init__(self):
        self.max_articles = int(os.getenv('MAX_ARTICLES', 3))
        
    def process_user_query(self, user_id: str, keyword: str):
        """
        處理用戶查詢請求（在背景執行）
        
        Args:
            user_id: LINE 用戶 ID
            keyword: 搜尋關鍵字
        """
        try:
            logger.info(f"開始處理用戶查詢: 用戶ID={user_id}, 關鍵字={keyword}")
            
            # 1. 爬取文章
            logger.info(f"正在爬取 TechOrange 文章...")
            articles = crawler.fetch_articles(keyword, self.max_articles)
            
            if not articles:
                line_bot.send_article_results(user_id, [], keyword)
                return
            
            logger.info(f"成功爬取 {len(articles)} 篇文章")
            
            # 2. 生成摘要
            logger.info("正在生成文章摘要...")
            summarized_articles = summarizer.summarize_articles(articles)
            
            if not summarized_articles:
                logger.warning("摘要生成失敗")
                line_bot.send_article_results(user_id, [], keyword)
                return
            
            logger.info(f"成功生成 {len(summarized_articles)} 篇摘要")
            
            # 3. 發送結果
            line_bot.send_article_results(user_id, summarized_articles, keyword)
            
            logger.info(f"用戶查詢處理完成: {keyword}")
            
        except Exception as e:
            logger.error(f"處理用戶查詢時發生錯誤: {str(e)}")
            try:
                # 嘗試發送錯誤訊息
                error_articles = [{
                    'title': '處理錯誤',
                    'summary': '抱歉，處理您的請求時發生錯誤，請稍後再試。',
                    'url': '#'
                }]
                line_bot.send_article_results(user_id, error_articles, keyword)
            except Exception as send_error:
                logger.error(f"發送錯誤訊息失敗: {str(send_error)}")
    
    def process_random_push(self, user_id: str):
        """
        處理隨機推送請求（在背景執行）
        
        Args:
            user_id: LINE 用戶 ID
        """
        try:
            logger.info(f"開始處理隨機推送: 用戶ID={user_id}")
            
            # 1. 隨機爬取文章
            logger.info(f"正在隨機擷取 TechOrange 文章...")
            articles = crawler.fetch_random_articles(self.max_articles)
            
            if not articles:
                # 發送無文章的訊息
                error_articles = [{
                    'title': '無法取得文章',
                    'summary': '抱歉，目前無法擷取文章，請稍後再試。',
                    'url': '#'
                }]
                line_bot.send_random_results(user_id, error_articles)
                return
            
            logger.info(f"成功隨機擷取 {len(articles)} 篇文章")
            
            # 2. 生成摘要
            logger.info("正在生成文章摘要...")
            summarized_articles = summarizer.summarize_articles(articles)
            
            if not summarized_articles:
                logger.warning("摘要生成失敗")
                error_articles = [{
                    'title': '摘要生成失敗',
                    'summary': '抱歉，無法生成文章摘要，請稍後再試。',
                    'url': '#'
                }]
                line_bot.send_random_results(user_id, error_articles)
                return
            
            logger.info(f"成功生成 {len(summarized_articles)} 篇摘要")
            
            # 3. 發送結果
            line_bot.send_random_results(user_id, summarized_articles)
            
            logger.info("隨機推送處理完成")
            
        except Exception as e:
            logger.error(f"處理隨機推送時發生錯誤: {str(e)}")
            try:
                # 嘗試發送錯誤訊息
                error_articles = [{
                    'title': '處理錯誤',
                    'summary': '抱歉，處理隨機推送時發生錯誤，請稍後再試。',
                    'url': '#'
                }]
                line_bot.send_random_results(user_id, error_articles)
            except Exception as send_error:
                logger.error(f"發送錯誤訊息失敗: {str(send_error)}")

# 創建新聞機器人實例
news_bot = NewsBot()

# 覆寫 LINE Bot 的訊息處理方法
def custom_process_keyword_query(event, keyword: str):
    """自定義關鍵字查詢處理"""
    try:
        user_id = event.source.user_id
        
        # 在背景執行處理程序，避免 LINE 超時
        threading.Thread(
            target=news_bot.process_user_query,
            args=(user_id, keyword),
            daemon=True
        ).start()
        
    except Exception as e:
        logger.error(f"啟動背景處理時發生錯誤: {str(e)}")

def custom_process_random_push(event):
    """自定義隨機推送處理"""
    try:
        user_id = event.source.user_id
        
        # 在背景執行隨機推送，避免 LINE 超時
        threading.Thread(
            target=news_bot.process_random_push,
            args=(user_id,),
            daemon=True
        ).start()
        
    except Exception as e:
        logger.error(f"啟動隨機推送時發生錯誤: {str(e)}")

# 測試端點（僅開發環境使用）
@app.route("/test/<keyword>", methods=['GET'])
def test_query(keyword):
    """測試查詢端點（開發用）"""
    try:
        # 模擬處理流程
        articles = crawler.fetch_articles(keyword, 2)
        summarized_articles = summarizer.summarize_articles(articles)
        
        return {
            'keyword': keyword,
            'articles_found': len(articles),
            'summaries_generated': len(summarized_articles),
            'results': summarized_articles
        }
        
    except Exception as e:
        return {
            'error': str(e)
        }, 500

@app.route("/test-random", methods=['GET'])
def test_random():
    """測試隨機推送端點（開發用）"""
    try:
        # 模擬隨機推送流程
        articles = crawler.fetch_random_articles(3)
        summarized_articles = summarizer.summarize_articles(articles)
        
        return {
            'type': 'random_push',
            'articles_found': len(articles),
            'summaries_generated': len(summarized_articles),
            'results': summarized_articles
        }
        
    except Exception as e:
        return {
            'error': str(e)
        }, 500

def setup_line_bot():
    """設定 LINE Bot 的自定義處理邏輯"""
    if line_bot:
        # 替換原本的處理方法
        line_bot.process_keyword_query = custom_process_keyword_query
        line_bot.process_random_push = custom_process_random_push

if __name__ == "__main__":
    # 初始化組件
    if not initialize_components():
        logger.error("組件初始化失敗，無法啟動服務")
        exit(1)
    
    # 設定 LINE Bot
    setup_line_bot()
    
    # 取得配置
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '127.0.0.1')
    
    logger.info(f"啟動 Flask 伺服器: http://{host}:{port}")
    logger.info(f"Debug 模式: {debug_mode}")
    logger.info("LINE TechOrange NewsBot 已啟動，等待用戶查詢...")
    
    # 啟動 Flask 應用
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )
