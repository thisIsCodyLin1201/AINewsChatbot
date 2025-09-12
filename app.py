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
from linebot.models import TextSendMessage

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
        # 檢查環境變數
        line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        line_secret = os.getenv('LINE_CHANNEL_SECRET') 
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        logger.info("檢查環境變數...")
        logger.info(f"LINE_CHANNEL_ACCESS_TOKEN: {'設置' if line_token else '未設置'}")
        logger.info(f"LINE_CHANNEL_SECRET: {'設置' if line_secret else '未設置'}")
        logger.info(f"GEMINI_API_KEY: {'設置' if gemini_key else '未設置'}")
        
        if not line_token or not line_secret:
            logger.error("LINE 環境變數未設置，無法初始化 LINE Bot")
            return False
        
        # 初始化 LINE Bot
        logger.info("正在初始化 LINE Bot...")
        line_bot = LINENewsBot()
        logger.info("LINE Bot 初始化成功")
        
        # 初始化爬蟲
        logger.info("正在初始化 TechOrange 爬蟲...")
        crawler = TechOrangeCrawler()
        logger.info("TechOrange 爬蟲初始化成功")
        
        # 初始化摘要器
        if gemini_key:
            logger.info("正在初始化 Gemini 摘要器...")
            summarizer = GeminiSummarizer()
            logger.info("Gemini 摘要器初始化成功")
        else:
            logger.warning("GEMINI_API_KEY 未設置，摘要功能將不可用")
            summarizer = None
        
        return True
        
    except Exception as e:
        logger.error(f"組件初始化失敗: {str(e)}")
        return False

@app.route("/callback", methods=['POST'])
def callback():
    """LINE webhook 回調端點"""
    
    logger.info(f"收到 callback 請求: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        # 獲取 X-Line-Signature header 值
        signature = request.headers.get('X-Line-Signature')
        
        # 獲取請求內容
        body = request.get_data(as_text=True)
        logger.info(f"請求體長度: {len(body)}")
        
        # LINE webhook 驗證請求通常沒有簽名或空請求體
        if not signature:
            logger.info("收到無簽名的請求（可能是驗證請求）")
            return 'OK', 200
        
        if not body or body.strip() == '':
            logger.info("收到空請求體（可能是驗證請求）")
            return 'OK', 200
        
        # 確保 LINE Bot 已初始化
        if not line_bot:
            logger.error("LINE Bot 尚未初始化，嘗試重新初始化...")
            # 嘗試重新初始化組件
            if initialize_components():
                logger.info("重新初始化成功")
                # 重新設置自定義處理邏輯
                setup_line_bot()
            else:
                logger.error("重新初始化失敗")
                return 'OK', 200
        
        # 處理正常的 webhook 事件
        logger.info("處理 LINE webhook 事件")
        line_bot.handle_webhook(body, signature)
        logger.info("Webhook 事件處理完成")
        
    except Exception as e:
        logger.error(f"處理 webhook 失敗: {str(e)}")
        logger.error(f"錯誤類型: {type(e).__name__}")
        import traceback
        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        # 即使出錯也返回 200，避免 LINE 重複發送請求
    
    return 'OK', 200

@app.route("/health", methods=['GET'])
def health_check():
    """健康檢查端點"""
    try:
        # 檢查組件狀態
        components_status = {
            'line_bot': line_bot is not None,
            'crawler': crawler is not None,
            'summarizer': summarizer is not None
        }
        
        # 檢查關鍵環境變數
        env_vars = {
            'LINE_CHANNEL_ACCESS_TOKEN': bool(os.getenv('LINE_CHANNEL_ACCESS_TOKEN')),
            'LINE_CHANNEL_SECRET': bool(os.getenv('LINE_CHANNEL_SECRET')),
            'GEMINI_API_KEY': bool(os.getenv('GEMINI_API_KEY'))
        }
        
        # 判斷整體狀態
        all_components_ok = all(components_status.values())
        required_env_ok = env_vars['LINE_CHANNEL_ACCESS_TOKEN'] and env_vars['LINE_CHANNEL_SECRET']
        
        if all_components_ok and required_env_ok:
            overall_status = 'healthy'
        elif required_env_ok:
            overall_status = 'degraded'  # 環境變數 OK 但組件有問題
        else:
            overall_status = 'unhealthy'  # 缺少必要環境變數
        
        status = {
            'status': overall_status,
            'timestamp': time.time(),
            'components': components_status,
            'environment_variables': env_vars
        }
        
        # 如果有問題，添加建議
        if overall_status != 'healthy':
            suggestions = []
            if not required_env_ok:
                suggestions.append("檢查 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_CHANNEL_SECRET 環境變數")
            if not all_components_ok:
                suggestions.append("組件初始化失敗，檢查日誌詳情")
            status['suggestions'] = suggestions
        
        return status
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }, 500

@app.route("/", methods=['GET'])
def index():
    """首頁"""
    return """
    <h1>LINE TechOrange NewsBot</h1>
    <p>狀態: 正常運行</p>
    <p>功能: 搜尋 TechOrange 文章並產生 AI 摘要</p>
    <p>使用方式: 在 LINE 中輸入關鍵字即可</p>
    <br>
    <a href="/health">健康檢查</a>
    """

@app.route("/test", methods=['GET', 'POST'])
def test_endpoint():
    """測試端點 - 用於調試"""
    return {
        'method': request.method,
        'headers': dict(request.headers),
        'body': request.get_data(as_text=True),
        'status': 'OK'
    }

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
            
            # 檢查組件是否初始化
            if not crawler:
                logger.error("Crawler 未初始化")
                error_articles = [{
                    'title': '系統錯誤',
                    'summary': '抱歉，爬蟲系統尚未初始化，請稍後再試。',
                    'url': '#'
                }]
                line_bot.send_random_results(user_id, error_articles)
                return
                
            if not summarizer:
                logger.warning("Summarizer 未初始化，將不提供摘要")
            
            # 1. 隨機爬取文章
            logger.info(f"正在隨機擷取 TechOrange 文章...")
            try:
                articles = crawler.fetch_random_articles(self.max_articles)
                logger.info(f"爬蟲返回結果: {len(articles) if articles else 0} 篇文章")
            except Exception as e:
                logger.error(f"爬取文章失敗: {str(e)}")
                error_articles = [{
                    'title': '爬取失敗',
                    'summary': f'抱歉，無法取得文章: {str(e)}',
                    'url': '#'
                }]
                line_bot.send_random_results(user_id, error_articles)
                return
            
            if not articles:
                logger.warning("爬蟲返回空結果")
                error_articles = [{
                    'title': '無法取得文章',
                    'summary': '抱歉，目前無法擷取文章，請稍後再試。',
                    'url': '#'
                }]
                line_bot.send_random_results(user_id, error_articles)
                return

            logger.info(f"成功隨機擷取 {len(articles)} 篇文章")
            
            # 2. 生成摘要
            if summarizer:
                logger.info("正在生成文章摘要...")
                try:
                    summarized_articles = summarizer.summarize_articles(articles)
                    logger.info(f"摘要器返回結果: {len(summarized_articles) if summarized_articles else 0} 篇摘要")
                except Exception as e:
                    logger.error(f"摘要生成失敗: {str(e)}")
                    # 使用原始文章內容，不包含摘要
                    summarized_articles = articles
                    for article in summarized_articles:
                        article['summary'] = article.get('description', '摘要生成失敗')[:100] + "..."
            else:
                logger.info("使用原始文章內容（無摘要功能）")
                summarized_articles = articles
                for article in summarized_articles:
                    article['summary'] = article.get('description', '無摘要')[:100] + "..."

            if not summarized_articles:
                logger.error("最終文章列表為空")
                error_articles = [{
                    'title': '處理失敗',
                    'summary': '抱歉，文章處理失敗，請稍後再試。',
                    'url': '#'
                }]
                line_bot.send_random_results(user_id, error_articles)
                return

            logger.info(f"準備發送 {len(summarized_articles)} 篇文章給用戶")
            
            # 3. 發送結果
            line_bot.send_random_results(user_id, summarized_articles)
            logger.info("隨機推送處理完成")
            
        except Exception as e:
            logger.error(f"隨機推送處理失敗: {str(e)}")
            import traceback
            logger.error(f"詳細錯誤: {traceback.format_exc()}")
            try:
                error_articles = [{
                    'title': '系統錯誤',
                    'summary': f'處理請求時發生錯誤: {str(e)}',
                    'url': '#'
                }]
                line_bot.send_random_results(user_id, error_articles)
            except Exception as send_error:
                logger.error(f"發送錯誤訊息也失敗: {str(send_error)}")
            
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

def safe_background_random_push(user_id: str):
    """
    安全的背景隨機推送處理，包含完整錯誤捕捉
    
    Args:
        user_id: LINE 用戶 ID
    """
    try:
        logger.info(f"[背景任務] 開始處理隨機推送: user_id={user_id}")
        
        # 檢查全域組件
        if not crawler:
            logger.error("[背景任務] Crawler 未初始化")
            if line_bot:
                error_msg = "抱歉，文章爬蟲系統尚未準備好，請稍後再試。"
                line_bot.line_bot_api.push_message(user_id, TextSendMessage(text=error_msg))
            return
            
        if not line_bot:
            logger.error("[背景任務] LINE Bot 未初始化")
            return
        
        # 1. 爬取隨機文章
        logger.info("[背景任務] 開始爬取隨機文章...")
        try:
            articles = crawler.fetch_random_articles(3)
            logger.info(f"[背景任務] 爬蟲返回: {len(articles) if articles else 0} 篇文章")
            
            if not articles:
                logger.warning("[背景任務] 未取得任何文章")
                error_msg = "抱歉，目前無法取得文章，請稍後再試。"
                line_bot.line_bot_api.push_message(user_id, TextSendMessage(text=error_msg))
                return
                
        except Exception as e:
            logger.error(f"[背景任務] 爬蟲失敗: {str(e)}")
            import traceback
            logger.error(f"[背景任務] 爬蟲錯誤詳情: {traceback.format_exc()}")
            error_msg = f"抱歉，文章爬取失敗: {str(e)}"
            line_bot.line_bot_api.push_message(user_id, TextSendMessage(text=error_msg))
            return
        
        # 2. 生成摘要
        logger.info("[背景任務] 開始生成摘要...")
        try:
            if summarizer:
                summarized_articles = summarizer.summarize_articles(articles)
                logger.info(f"[背景任務] 摘要生成完成: {len(summarized_articles) if summarized_articles else 0} 篇")
            else:
                logger.warning("[背景任務] Summarizer 未初始化，使用原始內容")
                summarized_articles = articles
                for article in summarized_articles:
                    article['summary'] = article.get('description', '無摘要')[:150] + "..."
                    
        except Exception as e:
            logger.error(f"[背景任務] 摘要生成失敗: {str(e)}")
            import traceback
            logger.error(f"[背景任務] 摘要錯誤詳情: {traceback.format_exc()}")
            # 使用原始文章內容作為備案
            summarized_articles = articles
            for article in summarized_articles:
                article['summary'] = article.get('description', '摘要生成失敗')[:150] + "..."
        
        # 3. 發送結果
        logger.info("[背景任務] 準備發送文章結果...")
        try:
            line_bot.send_random_results(user_id, summarized_articles)
            logger.info("[背景任務] 隨機推送完成！")
            
        except Exception as e:
            logger.error(f"[背景任務] 發送結果失敗: {str(e)}")
            import traceback
            logger.error(f"[背景任務] 發送錯誤詳情: {traceback.format_exc()}")
            error_msg = "文章處理完成，但發送時發生錯誤，請重新嘗試。"
            line_bot.line_bot_api.push_message(user_id, TextSendMessage(text=error_msg))
            
    except Exception as e:
        logger.error(f"[背景任務] 整體處理失敗: {str(e)}")
        import traceback
        logger.error(f"[背景任務] 整體錯誤詳情: {traceback.format_exc()}")
        try:
            if line_bot:
                error_msg = f"處理隨機推送時發生未預期的錯誤，請聯絡開發者。"
                line_bot.line_bot_api.push_message(user_id, TextSendMessage(text=error_msg))
        except:
            pass

def custom_process_random_push(event):
    """自定義隨機推送處理"""
    try:
        user_id = event.source.user_id
        logger.info(f"啟動隨機推送背景任務: user_id={user_id}")
        
        # 在背景執行安全的隨機推送處理
        threading.Thread(
            target=safe_background_random_push,
            args=(user_id,),
            daemon=True
        ).start()
        
        logger.info("隨機推送背景任務已啟動")
        
    except Exception as e:
        logger.error(f"啟動隨機推送時發生錯誤: {str(e)}")
        import traceback
        logger.error(f"錯誤詳情: {traceback.format_exc()}")

# 測試端點
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
        logger.info("設置 LINE Bot 自定義處理器")
        # 設置自定義處理函數為屬性
        line_bot._custom_random_handler = custom_process_random_push
        line_bot._custom_keyword_handler = custom_process_keyword_query
        logger.info("LINE Bot 自定義處理器設置完成")

if __name__ == "__main__":
    # 初始化組件
    if not initialize_components():
        logger.error("組件初始化失敗，無法啟動服務")
        exit(1)
    
    # 設定 LINE Bot
    setup_line_bot()
    
    # 生產環境配置
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')  # 生產環境綁定所有界面
    flask_env = os.getenv('FLASK_ENV', 'development')
    
    # 生產環境設定
    if flask_env == 'production':
        debug_mode = False
        logger.info("生產環境模式啟動")
    
    logger.info(f"環境: {flask_env}")
    logger.info(f"啟動 Flask 伺服器: http://{host}:{port}")
    logger.info(f"Debug 模式: {debug_mode}")
    logger.info("LINE TechOrange NewsBot 已啟動，等待用戶查詢...")
    
    # 啟動 Flask 應用
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True  # 支援多執行緒處理請求
    )
