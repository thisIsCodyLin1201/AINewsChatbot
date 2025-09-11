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
import re

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
        從 RSS feed 擷取文章 - 支援模糊搜尋和精確匹配優先
        
        Args:
            keyword: 搜尋關鍵字
            n: 最大文章數量
            
        Returns:
            List of Dict containing {title, url, content, match_score}
        """
        try:
            logger.info("從 RSS feed 擷取文章...")
            
            # 發送 RSS 請求
            response = requests.get(self.rss_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 解析 RSS
            feed = feedparser.parse(response.content)
            
            exact_matches = []  # 精確匹配
            fuzzy_matches = []  # 模糊匹配
            keyword_lower = keyword.lower()
            
            # 準備模糊搜尋的關鍵字變體
            fuzzy_keywords = self._generate_fuzzy_keywords(keyword_lower)
            
            for entry in feed.entries:
                title = entry.get('title', '').strip()
                link = entry.get('link', '').strip()
                title_lower = title.lower()
                
                match_score = self._calculate_match_score(title_lower, keyword_lower, fuzzy_keywords)
                
                if match_score > 0:
                    # 擷取文章內容
                    content = self._extract_article_content(link)
                    
                    if content:
                        article_data = {
                            'title': title,
                            'url': link,
                            'content': content,
                            'match_score': match_score
                        }
                        
                        # 根據匹配分數分類
                        if match_score >= 100:  # 精確匹配
                            exact_matches.append(article_data)
                        else:  # 模糊匹配
                            fuzzy_matches.append(article_data)
                        
                        # 避免過於頻繁的請求
                        time.sleep(0.5)
                        
                        # 如果已經有足夠的精確匹配，可以早期停止
                        if len(exact_matches) >= n:
                            break
            
            # 排序：精確匹配優先，然後按分數排序
            exact_matches.sort(key=lambda x: x['match_score'], reverse=True)
            fuzzy_matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            # 合併結果，精確匹配在前
            all_articles = exact_matches + fuzzy_matches
            articles = all_articles[:n]
            
            # 移除 match_score 欄位，不傳給後續處理
            for article in articles:
                del article['match_score']
            
            logger.info(f"從 RSS 找到 {len(articles)} 篇相關文章 (精確匹配: {len(exact_matches)}, 模糊匹配: {len(fuzzy_matches)})")
            return articles
            
        except Exception as e:
            logger.warning(f"RSS 擷取失敗: {str(e)}")
            return []
    
    def _fetch_from_search(self, keyword: str, n: int) -> List[Dict[str, str]]:
        """
        從網站搜尋擷取文章 - 支援多關鍵字搜尋
        
        Args:
            keyword: 搜尋關鍵字
            n: 最大文章數量
            
        Returns:
            List of Dict containing {title, url, content}
        """
        try:
            logger.info("從網站搜尋擷取文章...")
            
            # 準備搜尋關鍵字（包含模糊搜尋）
            keyword_lower = keyword.lower()
            fuzzy_keywords = self._generate_fuzzy_keywords(keyword_lower)
            
            all_articles = []
            searched_urls = set()  # 避免重複文章
            
            # 搜尋原始關鍵字和主要同義詞
            search_terms = [keyword] + fuzzy_keywords[:3]  # 限制搜尋次數
            
            for search_term in search_terms:
                if len(all_articles) >= n * 2:  # 取得足夠的候選文章
                    break
                    
                # 構建搜尋 URL
                search_params = {
                    's': search_term,
                    'post_type': 'post'
                }
                
                try:
                    response = requests.get(self.search_url, params=search_params, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 查找文章連結
                    article_links = soup.find_all('a', href=True)
                    
                    for link in article_links:
                        if len(all_articles) >= n * 2:
                            break
                            
                        href = link.get('href', '')
                        
                        # 確保是 TechOrange 文章連結且未重複
                        if (self.base_url in href and '/20' in href and 
                            href not in searched_urls):
                            
                            searched_urls.add(href)
                            title = link.get_text().strip()
                            
                            if title and len(title) > 10:  # 過濾太短的標題
                                # 計算匹配分數
                                match_score = self._calculate_match_score(title.lower(), keyword_lower, fuzzy_keywords)
                                
                                if match_score > 0:  # 只要有匹配就收集
                                    # 擷取文章內容
                                    content = self._extract_article_content(href)
                                    
                                    if content:
                                        all_articles.append({
                                            'title': title,
                                            'url': href,
                                            'content': content,
                                            'match_score': match_score
                                        })
                                        
                                        # 避免過於頻繁的請求
                                        time.sleep(0.3)
                    
                    # 搜尋間隔
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"搜尋關鍵字 '{search_term}' 失敗: {str(e)}")
                    continue
            
            # 按匹配分數排序並取前 n 篇
            all_articles.sort(key=lambda x: x['match_score'], reverse=True)
            articles = all_articles[:n]
            
            # 移除 match_score 欄位
            for article in articles:
                del article['match_score']
            
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
    
    def _generate_fuzzy_keywords(self, keyword: str) -> List[str]:
        """
        產生模糊搜尋的關鍵字變體
        
        Args:
            keyword: 原始關鍵字
            
        Returns:
            關鍵字變體列表
        """
        fuzzy_keywords = [keyword]
        
        # 常見的科技術語映射
        tech_synonyms = {
            'ai': ['人工智慧', '機器學習', 'machine learning', 'artificial intelligence', '深度學習'],
            '人工智慧': ['ai', 'artificial intelligence', '機器學習', '深度學習'],
            'blockchain': ['區塊鏈', '比特幣', 'bitcoin', '加密貨幣'],
            '區塊鏈': ['blockchain', '比特幣', 'bitcoin', '加密貨幣'],
            '5g': ['第五代', '5G網路', '行動通訊'],
            'iot': ['物聯網', 'internet of things', '智慧家居'],
            '物聯網': ['iot', 'internet of things', '智慧家居'],
            'vr': ['虛擬實境', 'virtual reality', 'ar', '擴增實境'],
            '虛擬實境': ['vr', 'virtual reality', 'ar', '擴增實境'],
            'ar': ['擴增實境', 'augmented reality', 'vr', '虛擬實境'],
            '擴增實境': ['ar', 'augmented reality', 'vr', '虛擬實境'],
            'fintech': ['金融科技', '數位金融', '行動支付'],
            '金融科技': ['fintech', '數位金融', '行動支付'],
            'startup': ['新創', '創業', '新創公司'],
            '新創': ['startup', '創業', '新創公司'],
            'ecommerce': ['電商', '電子商務', '網購'],
            '電商': ['ecommerce', '電子商務', '網購'],
            'cloud': ['雲端', '雲計算', '雲服務'],
            '雲端': ['cloud', '雲計算', '雲服務']
        }
        
        # 添加同義詞
        if keyword in tech_synonyms:
            fuzzy_keywords.extend(tech_synonyms[keyword])
        
        # 添加部分匹配的詞彙
        if len(keyword) >= 3:
            # 移除常見的後綴
            base_word = keyword.replace('技術', '').replace('產業', '').replace('公司', '')
            if base_word != keyword and len(base_word) >= 2:
                fuzzy_keywords.append(base_word)
        
        return list(set(fuzzy_keywords))  # 去重
    
    def _calculate_match_score(self, title: str, keyword: str, fuzzy_keywords: List[str]) -> int:
        """
        計算標題與關鍵字的匹配分數
        
        Args:
            title: 文章標題 (小寫)
            keyword: 原始關鍵字 (小寫)
            fuzzy_keywords: 模糊搜尋關鍵字列表
            
        Returns:
            匹配分數 (0-100)，0表示無匹配，100表示精確匹配
        """
        if not title or not keyword:
            return 0
        
        score = 0
        
        # 精確匹配 - 最高分
        if keyword in title:
            score = 100
        else:
            # 模糊匹配檢查
            for fuzzy_keyword in fuzzy_keywords:
                if fuzzy_keyword in title:
                    # 根據匹配的關鍵字長度給分
                    if len(fuzzy_keyword) >= 3:
                        score = max(score, 80)  # 同義詞匹配
                    else:
                        score = max(score, 60)  # 短詞匹配
        
        # 關鍵字在標題開頭，加分
        if any(title.startswith(kw) for kw in [keyword] + fuzzy_keywords):
            score = min(100, score + 10)
        
        # 完整詞匹配（被空格或標點包圍），加分
        import re
        for kw in [keyword] + fuzzy_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', title):
                score = min(100, score + 5)
                break
        
        return score

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
