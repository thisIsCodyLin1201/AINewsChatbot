"""
TechOrange 爬蟲模組
負責從 TechOrange 網站擷取最新相關文章
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
import time

# 設置日誌
logger = logging.getLogger(__name__)

class TechOrangeCrawler:
    """
    TechOrange 網站爬蟲類別
    
    功能：
    - 從 RSS feed 擷取最新文章
    - 根據關鍵字搜尋相關文章
    - 擷取文章完整內容
    """
    
    def __init__(self):
        """初始化爬蟲"""
        self.base_url = "https://buzzorange.com/techorange"
        self.rss_url = "https://buzzorange.com/techorange/feed/"
        self.search_url = "https://buzzorange.com/techorange/"
        
        # 設置 User-Agent 避免被封鎖
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_articles(self, keyword: str, n: int = 3) -> List[Dict[str, str]]:
        """
        從 TechOrange 擷取包含關鍵字的最新文章
        
        Args:
            keyword: 搜尋關鍵字
            n: 返回文章數量，預設 3 篇
            
        Returns:
            List of Dict containing {title, url, content}
        """
        try:
            logger.info(f"開始爬取 TechOrange 文章，關鍵字: {keyword}, 數量: {n}")
            
            # 首先嘗試使用 RSS feed
            articles = self._fetch_from_rss(keyword, n)
            
            # 如果 RSS 結果不足，嘗試網頁搜尋
            if len(articles) < n:
                additional_articles = self._fetch_from_search(keyword, n - len(articles))
                articles.extend(additional_articles)
            
            # 確保不超過請求數量
            articles = articles[:n]
            
            logger.info(f"成功擷取 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            logger.error(f"爬取文章時發生錯誤: {str(e)}")
            return []
    
    def _fetch_from_rss(self, keyword: str, n: int) -> List[Dict[str, str]]:
        """
        從 RSS feed 擷取文章
        
        Args:
            keyword: 搜尋關鍵字
            n: 最大文章數量
            
        Returns:
            List of Dict containing {title, url, content}
        """
        try:
            logger.info("從 RSS feed 擷取文章...")
            
            # 發送 RSS 請求
            response = requests.get(self.rss_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 解析 RSS
            feed = feedparser.parse(response.content)
            
            articles = []
            keyword_lower = keyword.lower()
            
            for entry in feed.entries:
                if len(articles) >= n:
                    break
                    
                title = entry.get('title', '').strip()
                link = entry.get('link', '').strip()
                
                # 檢查標題是否包含關鍵字
                if keyword_lower in title.lower():
                    # 擷取文章內容
                    content = self._extract_article_content(link)
                    
                    if content:
                        articles.append({
                            'title': title,
                            'url': link,
                            'content': content
                        })
                        
                        # 避免過於頻繁的請求
                        time.sleep(0.5)
            
            logger.info(f"從 RSS 找到 {len(articles)} 篇相關文章")
            return articles
            
        except Exception as e:
            logger.warning(f"RSS 擷取失敗: {str(e)}")
            return []
    
    def _fetch_from_search(self, keyword: str, n: int) -> List[Dict[str, str]]:
        """
        從網站搜尋擷取文章
        
        Args:
            keyword: 搜尋關鍵字
            n: 最大文章數量
            
        Returns:
            List of Dict containing {title, url, content}
        """
        try:
            logger.info("從網站搜尋擷取文章...")
            
            # 構建搜尋 URL
            search_params = {
                's': keyword,
                'post_type': 'post'
            }
            
            response = requests.get(self.search_url, params=search_params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # 查找文章連結
            article_links = soup.find_all('a', href=True)
            
            for link in article_links:
                if len(articles) >= n:
                    break
                    
                href = link.get('href', '')
                
                # 確保是 TechOrange 文章連結
                if self.base_url in href and '/20' in href:  # 包含年份的文章
                    title = link.get_text().strip()
                    
                    if title and len(title) > 10:  # 過濾太短的標題
                        # 擷取文章內容
                        content = self._extract_article_content(href)
                        
                        if content:
                            articles.append({
                                'title': title,
                                'url': href,
                                'content': content
                            })
                            
                            # 避免過於頻繁的請求
                            time.sleep(0.5)
            
            logger.info(f"從搜尋找到 {len(articles)} 篇相關文章")
            return articles
            
        except Exception as e:
            logger.warning(f"搜尋擷取失敗: {str(e)}")
            return []
    
    def _extract_article_content(self, url: str) -> str:
        """
        從文章 URL 擷取內容
        
        Args:
            url: 文章 URL
            
        Returns:
            文章內容摘要
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找文章內容區域
            content_selectors = [
                '.post-content p',
                '.entry-content p',
                '.content p',
                'article p'
            ]
            
            content_parts = []
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements[:3]:  # 只取前 3 段
                        text = element.get_text().strip()
                        if text and len(text) > 20:  # 過濾太短的段落
                            content_parts.append(text)
                    break
            
            if not content_parts:
                # 嘗試其他方法擷取內容
                paragraphs = soup.find_all('p')
                for p in paragraphs[:5]:
                    text = p.get_text().strip()
                    if text and len(text) > 20:
                        content_parts.append(text)
            
            content = ' '.join(content_parts)
            
            # 限制內容長度
            if len(content) > 500:
                content = content[:500] + '...'
            
            return content if content else "無法擷取內容摘要"
            
        except Exception as e:
            logger.warning(f"擷取文章內容失敗 ({url}): {str(e)}")
            return "無法擷取內容摘要"

# 便利函數
def fetch_articles(keyword: str, n: int = 3) -> List[Dict[str, str]]:
    """
    便利函數：擷取 TechOrange 文章
    
    Args:
        keyword: 搜尋關鍵字
        n: 文章數量
        
    Returns:
        List of Dict containing {title, url, content}
    """
    crawler = TechOrangeCrawler()
    return crawler.fetch_articles(keyword, n)

if __name__ == "__main__":
    # 測試用例
    test_keyword = "AI"
    articles = fetch_articles(test_keyword, 3)
    
    print(f"找到 {len(articles)} 篇文章：")
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. 標題: {article['title']}")
        print(f"   連結: {article['url']}")
        print(f"   內容預覽: {article['content'][:100]}...")
    def __init__(self):
        # 支援的科技新聞來源
        self.sources = {
            'techorange': {
                'name': '科技報橘',
                'base_url': 'https://buzzorange.com/techorange',
                'rss_url': 'https://buzzorange.com/techorange/feed/',
                'search_url': 'https://buzzorange.com/techorange/?s={keyword}',
                'content_selectors': ['.entry-content', '.post-content', '.article-content']
            },
            'ithome': {
                'name': 'iThome',
                'base_url': 'https://www.ithome.com.tw',
                'rss_url': 'https://feeds.feedburner.com/ithomeOnline',
                'search_url': 'https://www.ithome.com.tw/search?keyword={keyword}',
                'content_selectors': ['.field-item', '.content', '.article-content']
            },
            'technews': {
                'name': '科技新報',
                'base_url': 'https://technews.tw',
                'rss_url': 'https://technews.tw/feed/',
                'search_url': 'https://technews.tw/?s={keyword}',
                'content_selectors': ['.entry-content', '.post-content', '.article-body']
            },
            'inside': {
                'name': 'Inside 硬塞的網路趨勢觀察',
                'base_url': 'https://www.inside.com.tw',
                'rss_url': 'https://www.inside.com.tw/feed',
                'search_url': 'https://www.inside.com.tw/?s={keyword}',
                'content_selectors': ['.entry-content', '.post-content', '.article-content']
            }
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_articles(self, keyword: str, n: int = 3) -> List[Dict[str, str]]:
        """
        從多個科技新聞來源擷取包含關鍵字的最新文章
        
        Args:
            keyword: 搜尋關鍵字
            n: 返回文章數量，預設 3 篇
            
        Returns:
            List of Dict containing {title, url, content, source}
        """
        try:
            logger.info(f"開始從多個來源爬取文章，關鍵字: {keyword}, 數量: {n}")
            
            all_articles = []
            sources_tried = []
            
            # 隨機打亂來源順序，平衡各網站的使用
            source_names = list(self.sources.keys())
            random.shuffle(source_names)
            
            for source_name in source_names:
                try:
                    source_info = self.sources[source_name]
                    sources_tried.append(source_info['name'])
                    
                    logger.info(f"正在從 {source_info['name']} 爬取文章...")
                    
                    # 嘗試從 RSS 擷取
                    articles = self._fetch_from_source_rss(source_name, keyword, n - len(all_articles))
                    
                    if articles:
                        all_articles.extend(articles)
                        logger.info(f"從 {source_info['name']} 成功獲得 {len(articles)} 篇文章")
                    
                    # 如果已經有足夠文章就停止
                    if len(all_articles) >= n:
                        break
                        
                except Exception as e:
                    logger.warning(f"從 {source_info['name']} 爬取失敗: {str(e)}")
                    continue
            
            # 限制返回數量
            result_articles = all_articles[:n]
            
            logger.info(f"總共成功擷取 {len(result_articles)} 篇文章，嘗試來源: {', '.join(sources_tried)}")
            return result_articles
            
        except Exception as e:
            logger.error(f"爬取文章時發生錯誤: {str(e)}")
            return []
    
    def _fetch_from_source_rss(self, source_name: str, keyword: str, max_articles: int) -> List[Dict[str, str]]:
        """
        從指定來源的 RSS 擷取包含關鍵字的文章
        
        Args:
            source_name: 來源名稱 
            keyword: 搜尋關鍵字
            max_articles: 最大文章數量
            
        Returns:
            List of Dict containing {title, url, content, source}
        """
        try:
            source_info = self.sources[source_name]
            
            # 擷取 RSS feed
            response = requests.get(source_info['rss'], headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 解析 RSS
            feed = feedparser.parse(response.content)
            
            articles = []
            keyword_lower = keyword.lower()
            
            for entry in feed.entries:
                if len(articles) >= max_articles:
                    break
                    
                title = entry.get('title', '').strip()
                link = entry.get('link', '').strip()
                
                # 檢查標題是否包含關鍵字
                if keyword_lower in title.lower():
                    # 擷取文章內容
                    content = self._extract_content_from_url(link, source_name)
                    
                    if content:
                        articles.append({
                            'title': title,
                            'url': link,
                            'content': content,
                            'source': source_info['name']
                        })
                        
                        # 避免過於頻繁的請求
                        time.sleep(0.5)
            
            return articles
            
        except Exception as e:
            logger.warning(f"從 {source_name} RSS 擷取失敗: {str(e)}")
            return []
    
    def _extract_content_from_url(self, url: str, source_name: str) -> str:
        """
        從文章 URL 擷取內容
        
        Args:
            url: 文章網址
            source_name: 來源名稱
            
        Returns:
            文章內容摘要
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 根據不同來源使用不同的內容選擇器
            content_selectors = {
                'techorange': '.post-content p, .entry-content p',
                'ithome': '.field-item p, .content p', 
                'technews': '.entry-content p, .post-content p',
                'inside': '.post-content p, .entry-content p'
            }
            
            selector = content_selectors.get(source_name, 'p')
            content_elements = soup.select(selector)
            
            # 提取文字內容
            content_parts = []
            for element in content_elements[:3]:  # 只取前 3 段
                text = element.get_text().strip()
                if text and len(text) > 20:  # 過濾太短的段落
                    content_parts.append(text)
            
            content = ' '.join(content_parts)
            
            # 限制內容長度
            if len(content) > 500:
                content = content[:500] + '...'
            
            return content if content else "無法擷取內容摘要"
            
        except Exception as e:
            logger.warning(f"從 {url} 擷取內容失敗: {str(e)}")
            return "無法擷取內容摘要"

    def _fetch_from_rss(self, keyword: str, n: int) -> List[Dict[str, str]]:
        """從 RSS feed 擷取文章"""
        try:
            response = self.session.get(self.rss_url, timeout=10)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            articles = []
            
            for entry in feed.entries:
                # 檢查標題或摘要是否包含關鍵字
                if (keyword.lower() in entry.title.lower() or 
                    keyword.lower() in entry.summary.lower()):
                    
                    # 獲取文章內容
                    content = self._extract_content_from_url(entry.link)
                    
                    article = {
                        'title': entry.title,
                        'url': entry.link,
                        'content': content[:500] if content else entry.summary[:500]  # 限制內容長度
                    }
                    articles.append(article)
                    
                    if len(articles) >= n:
                        break
                        
            return articles
            
        except Exception as e:
            logger.error(f"RSS 爬取失敗: {str(e)}")
            return []

    def _fetch_from_search(self, keyword: str, n: int) -> List[Dict[str, str]]:
        """從搜尋頁面擷取文章"""
        try:
            search_url = f"{self.base_url}/?s={keyword}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # 查找文章連結 (根據 TechOrange 的實際 HTML 結構調整)
            article_links = soup.find_all('a', class_='post-title') or soup.find_all('h2', class_='entry-title')
            
            for link_element in article_links[:n]:
                try:
                    if link_element.name == 'a':
                        title = link_element.get_text(strip=True)
                        url = link_element.get('href')
                    else:  # h2 case
                        a_tag = link_element.find('a')
                        if a_tag:
                            title = a_tag.get_text(strip=True)
                            url = a_tag.get('href')
                        else:
                            continue
                    
                    if url and title:
                        # 獲取文章內容
                        content = self._extract_content_from_url(url)
                        
                        article = {
                            'title': title,
                            'url': url,
                            'content': content[:500] if content else ""
                        }
                        articles.append(article)
                        
                        if len(articles) >= n:
                            break
                            
                except Exception as e:
                    logger.warning(f"解析單篇文章失敗: {str(e)}")
                    continue
                    
            return articles
            
        except Exception as e:
            logger.error(f"搜尋頁面爬取失敗: {str(e)}")
            return []

    def _extract_content_from_url(self, url: str) -> str:
        """從文章 URL 擷取內容"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 嘗試多種可能的內容選擇器
            content_selectors = [
                '.entry-content',
                '.post-content', 
                '.article-content',
                '.content',
                'article',
                '.post'
            ]
            
            content = ""
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    # 移除不需要的元素
                    for unwanted in content_element.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        unwanted.decompose()
                    
                    content = content_element.get_text(strip=True)
                    break
            
            # 如果還是沒有內容，嘗試取得 meta description
            if not content:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    content = meta_desc.get('content', '')
            
            return content
            
        except Exception as e:
            logger.warning(f"擷取文章內容失敗 {url}: {str(e)}")
            return ""

# 便利函數
def fetch_articles(keyword: str, n: int = 3) -> List[Dict[str, str]]:
    """
    便利函數：使用多來源爬蟲擷取科技新聞文章
    
    Args:
        keyword: 搜尋關鍵字
        n: 文章數量
        
    Returns:
        List of Dict containing {title, url, content, source}
    """
    crawler = MultiSourceTechCrawler()
    return crawler.fetch_articles(keyword, n)

if __name__ == "__main__":
    # 測試用例
    test_keyword = "AI"
    articles = fetch_articles(test_keyword, 3)
    
    print(f"找到 {len(articles)} 篇文章：")
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. 標題: {article['title']}")
        print(f"   連結: {article['url']}")
        print(f"   內容預覽: {article['content'][:100]}...")
