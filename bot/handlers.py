"""
LINE Bot 指令處理器
負責分派用戶指令並格式化回覆訊息
"""
import re
from .news import get_news_articles
from .summarize import summarize_article


def handle_message(event):
    """
    處理用戶訊息
    
    Args:
        event: LINE Bot 事件物件
        
    Returns:
        str: 回覆訊息文字
    """
    user_text = event.message.text.strip()
    
    # 解析 /news 指令
    news_match = re.match(r'^(/news|新聞)\s*(\d*)$', user_text, re.IGNORECASE)
    
    if news_match:
        # 取得要抓取的文章數量
        count_str = news_match.group(2)
        count = int(count_str) if count_str else 3
        
        # 限制數量範圍
        count = max(1, min(count, 10))
        
        try:
            # 抓取新聞
            articles = get_news_articles(count)
            
            if not articles:
                return "抱歉，目前抓不到新聞，稍後再試"
            
            # 格式化回覆
            reply_text = format_news_reply(articles)
            return reply_text
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return "抱歉，目前抓不到新聞，稍後再試"
    
    # 預設回覆
    return "請輸入 '/news' 或 '/news N' 來取得最新新聞摘要\n例如：/news 5"


def format_news_reply(articles):
    """
    格式化新聞回覆訊息
    
    Args:
        articles: 新聞文章列表
        
    Returns:
        str: 格式化後的回覆文字
    """
    reply_lines = ["📰 最新新聞摘要\n"]
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', '無標題')
        summary = article.get('summary', '無摘要')
        link = article.get('link', '')
        
        # 限制摘要長度
        if len(summary) > 100:
            summary = summary[:100] + "..."
        
        article_text = f"{i}. {title}\n{summary}"
        if link:
            article_text += f"\n🔗 {link}"
        
        reply_lines.append(article_text)
        reply_lines.append("")  # 空行分隔
    
    # 移除最後的空行
    if reply_lines[-1] == "":
        reply_lines.pop()
    
    return "\n".join(reply_lines)
