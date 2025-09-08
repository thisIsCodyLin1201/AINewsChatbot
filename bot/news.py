"""
新聞抓取模組
負責從 TechOrange RSS 抓取最新文章
"""
import feedparser
import requests
from datetime import datetime


def get_news_articles(count=3):
    """
    從 TechOrange RSS 抓取最新文章
    
    Args:
        count (int): 要抓取的文章數量，預設 3 篇
        
    Returns:
        list: 文章資料列表，每個元素包含 title, link, summary, published
    """
    rss_url = "https://buzzorange.com/techorange/feed/"
    
    try:
        # 設定請求標頭
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 抓取 RSS
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析 RSS
        feed = feedparser.parse(response.content)
        
        if not feed.entries:
            print("No articles found in RSS feed")
            return []
        
        articles = []
        for entry in feed.entries[:count]:
            article = {
                'title': entry.get('title', '無標題'),
                'link': entry.get('link', ''),
                'summary': entry.get('summary', ''),
                'published': entry.get('published', ''),
                'published_parsed': entry.get('published_parsed', None)
            }
            
            # 清理摘要（移除 HTML 標籤）
            if article['summary']:
                article['summary'] = clean_html(article['summary'])
            
            articles.append(article)
        
        print(f"Successfully fetched {len(articles)} articles from TechOrange")
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS: {e}")
        return []
    except Exception as e:
        print(f"Error parsing RSS: {e}")
        return []


def clean_html(text):
    """
    清理 HTML 標籤和多餘空白
    
    Args:
        text (str): 原始文字
        
    Returns:
        str: 清理後的文字
    """
    import re
    
    # 移除 HTML 標籤
    text = re.sub(r'<[^>]+>', '', text)
    
    # 移除多餘空白和換行
    text = re.sub(r'\s+', ' ', text)
    
    # 移除首尾空白
    text = text.strip()
    
    return text


def test_rss_fetch():
    """
    測試 RSS 抓取功能
    """
    print("Testing TechOrange RSS fetch...")
    articles = get_news_articles(3)
    
    if articles:
        print(f"Found {len(articles)} articles:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Link: {article['link']}")
            print(f"   Summary: {article['summary'][:100]}...")
    else:
        print("No articles found")


if __name__ == "__main__":
    test_rss_fetch()
