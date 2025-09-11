"""
TechOrange 爬蟲模組
負責從 TechOrange 網站擷取最新相關文章
使用 Gemini AI 進行智能模糊搜尋
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
import time
import re
import os
import google.generativeai as genai
import json

# 設置日誌
logger = logging.getLogger(__name__)

class TechOrangeCrawler:
    """
    TechOrange 網站爬蟲類別
    
    功能：
    - 從 RSS feed 擷取最新文章
    - 根據關鍵字搜尋相關文章
    - 擷取文章完整內容
    - 隨機推送最新文章
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
        
        # 初始化 Gemini AI (如果有 API Key)
        self.gemini_model = None
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("Gemini AI 模糊搜尋功能已啟用")
            else:
                logger.warning("未找到 GEMINI_API_KEY，將使用傳統模糊搜尋")
        except Exception as e:
            logger.warning(f"Gemini AI 初始化失敗，將使用傳統模糊搜尋: {str(e)}")
            self.gemini_model = None
    
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
            logger.error(f"擷取文章時發生錯誤: {str(e)}")
            return []
    
    def fetch_random_articles(self, n: int = 3) -> List[Dict[str, str]]:
        """
        隨機擷取最新文章（不需要關鍵字）
        
        Args:
            n: 返回文章數量，預設 3 篇
            
        Returns:
            List of Dict containing {title, url, content}
        """
        try:
            logger.info(f"開始隨機擷取 TechOrange 文章，數量: {n}")
            
            # 從 RSS feed 獲取最新文章
            response = requests.get(self.rss_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 解析 RSS
            feed = feedparser.parse(response.content)
            
            # 先收集所有可用的文章
            all_articles = []
            for entry in feed.entries:
                title = entry.get('title', '').strip()
                link = entry.get('link', '').strip()
                
                if title and link:
                    all_articles.append({
                        'title': title,
                        'url': link,
                        'entry': entry
                    })
            
            # 隨機選擇文章
            import random
            if len(all_articles) > n:
                selected_articles = random.sample(all_articles, n)
            else:
                selected_articles = all_articles
            
            # 擷取選中文章的內容
            final_articles = []
            for article_info in selected_articles:
                content = self._extract_article_content(article_info['url'])
                
                if content:
                    final_articles.append({
                        'title': article_info['title'],
                        'url': article_info['url'],
                        'content': content
                    })
                    
                    if len(final_articles) >= n:
                        break
            
            logger.info(f"成功隨機擷取 {len(final_articles)} 篇文章")
            return final_articles
            
        except Exception as e:
            logger.error(f"隨機擷取文章時發生錯誤: {str(e)}")
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
                        
                        # 如果已經找到足夠的文章，停止搜尋
                        if len(exact_matches) + len(fuzzy_matches) >= n * 2:
                            break
            
            # 排序：精確匹配優先，然後按分數排序
            exact_matches.sort(key=lambda x: x['match_score'], reverse=True)
            fuzzy_matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            # 合併結果，優先返回精確匹配
            final_articles = exact_matches + fuzzy_matches
            final_articles = final_articles[:n]
            
            # 移除 match_score，只保留必要欄位
            for article in final_articles:
                article.pop('match_score', None)
            
            exact_count = len([a for a in final_articles if a in exact_matches])
            fuzzy_count = len(final_articles) - exact_count
            
            logger.info(f"從 RSS 找到 {len(final_articles)} 篇相關文章 (精確匹配: {exact_count}, 模糊匹配: {fuzzy_count})")
            return final_articles
            
        except Exception as e:
            logger.error(f"從 RSS 擷取文章時發生錯誤: {str(e)}")
            return []

    def _fetch_from_search(self, keyword: str, n: int) -> List[Dict[str, str]]:
        """
        從網站搜尋功能擷取文章
        
        Args:
            keyword: 搜尋關鍵字
            n: 最大文章數量
            
        Returns:
            List of Dict containing {title, url, content}
        """
        try:
            logger.info("從網站搜尋擷取文章...")
            
            # 生成搜尋關鍵字
            fuzzy_keywords = self._generate_fuzzy_keywords(keyword.lower())
            search_terms = [keyword] + fuzzy_keywords[:3]  # 限制搜尋詞數量
            
            articles = []
            processed_urls = set()
            
            for search_term in search_terms:
                if len(articles) >= n:
                    break
                    
                # 構建搜尋 URL
                search_params = {
                    's': search_term,
                    'post_type': 'post'
                }
                
                try:
                    response = requests.get(
                        self.search_url,
                        params=search_params,
                        headers=self.headers,
                        timeout=10
                    )
                    response.raise_for_status()
                    
                    # 解析搜尋結果頁面
                    try:
                        soup = BeautifulSoup(response.content, 'lxml')
                    except:
                        try:
                            soup = BeautifulSoup(response.content, 'html5lib')
                        except:
                            soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 尋找文章連結
                    article_links = self._extract_article_links_from_search(soup)
                    
                    for link in article_links:
                        if len(articles) >= n or link in processed_urls:
                            break
                            
                        processed_urls.add(link)
                        
                        # 擷取文章內容
                        content = self._extract_article_content(link)
                        if content:
                            # 從連結擷取標題
                            title = self._extract_title_from_url(link)
                            
                            articles.append({
                                'title': title,
                                'url': link,
                                'content': content
                            })
                
                except Exception as search_error:
                    logger.warning(f"搜尋詞 '{search_term}' 失敗: {str(search_error)}")
                    continue
                
                # 避免過於頻繁的請求
                time.sleep(1)
            
            logger.info(f"從搜尋找到 {len(articles)} 篇相關文章")
            return articles
            
        except Exception as e:
            logger.error(f"從搜尋擷取文章時發生錯誤: {str(e)}")
            return []

    def _generate_fuzzy_keywords(self, keyword: str) -> List[str]:
        """
        使用 Gemini AI 生成模糊搜尋關鍵字，如果失敗則使用傳統方法
        
        Args:
            keyword: 原始關鍵字
            
        Returns:
            List of fuzzy keywords
        """
        # 嘗試使用 Gemini AI
        if self.gemini_model:
            try:
                prompt = f"""
針對科技新聞網站搜尋，為關鍵字「{keyword}」生成相關的搜尋詞。

請提供 8 個相關的搜尋關鍵字，包括：
1. 英文翻譯
2. 同義詞
3. 相關技術術語
4. 產業相關詞彙

請以 JSON 陣列格式回答，例如：["keyword1", "keyword2", ...]

只回答 JSON 陣列，不要其他說明。
"""
                
                response = self.gemini_model.generate_content(prompt)
                result_text = response.text.strip()
                
                # 解析 JSON 回應
                if result_text.startswith('[') and result_text.endswith(']'):
                    fuzzy_keywords = json.loads(result_text)
                    if isinstance(fuzzy_keywords, list):
                        logger.info(f"Gemini AI 生成關鍵字: {fuzzy_keywords}")
                        return fuzzy_keywords
                
            except Exception as e:
                logger.warning(f"Gemini AI 生成關鍵字失敗: {str(e)}")
        
        # 回退到傳統方法
        return self._generate_traditional_fuzzy_keywords(keyword)

    def _generate_traditional_fuzzy_keywords(self, keyword: str) -> List[str]:
        """
        傳統模糊搜尋關鍵字生成（備用方法）
        
        Args:
            keyword: 原始關鍵字
            
        Returns:
            List of fuzzy keywords
        """
        fuzzy_keywords = []
        
        # 預設的科技相關詞彙映射
        tech_mapping = {
            'ai': ['人工智慧', '機器學習', '深度學習', 'artificial intelligence', 'machine learning'],
            '人工智慧': ['ai', 'artificial intelligence', '機器學習', '深度學習', 'neural network'],
            'blockchain': ['區塊鏈', '加密貨幣', 'cryptocurrency', 'bitcoin', '數位貨幣'],
            '區塊鏈': ['blockchain', '加密貨幣', 'cryptocurrency', 'bitcoin'],
            'startup': ['新創', '創業', '新創公司', 'venture capital', '創新'],
            '新創': ['startup', '創業', '新創公司', 'venture capital'],
            'fintech': ['金融科技', '數位金融', '支付', 'payment', '投資科技'],
            '金融科技': ['fintech', '數位金融', '支付', 'payment'],
            '5g': ['第五代行動通訊', '5G網路', '行動網路', 'mobile network'],
            'iot': ['物聯網', 'internet of things', '智慧家庭', 'smart home'],
            '物聯網': ['iot', 'internet of things', '智慧家庭', 'smart home'],
            'cloud': ['雲端', '雲端運算', 'cloud computing', 'aws', 'azure'],
            '雲端': ['cloud', '雲端運算', 'cloud computing'],
            '電商': ['e-commerce', '網路購物', 'online shopping', '電子商務'],
            'e-commerce': ['電商', '網路購物', 'online shopping', '電子商務']
        }
        
        keyword_lower = keyword.lower()
        
        # 檢查是否有預設映射
        if keyword_lower in tech_mapping:
            fuzzy_keywords.extend(tech_mapping[keyword_lower])
        
        # 添加常見變化
        if len(keyword) > 2:
            # 移除常見字尾
            for suffix in ['公司', '科技', '技術', 'tech', 'technology']:
                if keyword.endswith(suffix):
                    base_word = keyword[:-len(suffix)]
                    if len(base_word) > 1:
                        fuzzy_keywords.append(base_word)
        
        # 添加組合關鍵字
        tech_suffixes = ['科技', '技術', '應用', '發展', '創新', 'tech', 'technology']
        for suffix in tech_suffixes:
            if suffix not in keyword.lower():
                fuzzy_keywords.append(f"{keyword} {suffix}")
        
        # 移除重複並限制數量
        fuzzy_keywords = list(dict.fromkeys(fuzzy_keywords))[:8]
        
        logger.info(f"傳統方法生成關鍵字: {fuzzy_keywords}")
        return fuzzy_keywords

    def _calculate_match_score(self, title: str, keyword: str, fuzzy_keywords: List[str]) -> int:
        """
        計算標題與關鍵字的匹配分數
        
        Args:
            title: 文章標題（小寫）
            keyword: 主要關鍵字（小寫）
            fuzzy_keywords: 模糊關鍵字列表
            
        Returns:
            匹配分數 (0-100)
        """
        score = 0
        
        # 精確匹配主要關鍵字
        if keyword in title:
            score = 100
            return score
        
        # AI 生成的第一個關鍵字優先級較高
        for i, fuzzy_keyword in enumerate(fuzzy_keywords[:3]):
            if fuzzy_keyword.lower() in title:
                if i == 0:  # 第一個 AI 關鍵字
                    score = 95
                elif i <= 2:  # 前三個關鍵字
                    score = 85
                else:
                    score = 70
                break
        
        # 其他模糊關鍵字匹配
        if score == 0:
            for fuzzy_keyword in fuzzy_keywords[3:]:
                if fuzzy_keyword.lower() in title:
                    score = 70
                    break
        
        # 部分匹配檢查
        if score == 0:
            # 檢查關鍵字的部分匹配
            if len(keyword) > 3:
                keyword_parts = keyword.split()
                for part in keyword_parts:
                    if len(part) > 2 and part in title:
                        score = max(score, 50)
        
        # 多個關鍵字匹配，額外加分
        matched_count = sum(1 for kw in [keyword] + fuzzy_keywords if kw.lower() in title)
        if matched_count > 1:
            score = min(100, score + matched_count * 2)
        
        return score

    def _extract_article_content(self, url: str) -> Optional[str]:
        """
        從文章 URL 擷取完整內容
        
        Args:
            url: 文章 URL
            
        Returns:
            文章內容文字，失敗則返回 None
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # 嘗試使用不同的解析器
            try:
                soup = BeautifulSoup(response.content, 'lxml')
            except:
                try:
                    soup = BeautifulSoup(response.content, 'html5lib')
                except:
                    soup = BeautifulSoup(response.content, 'html.parser')
            
            # 移除不需要的元素
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # 尋找文章內容區域
            content_selectors = [
                'div.entry-content',
                'article .content',
                'div.post-content',
                'div.article-content',
                'main article',
                'div.single-content'
            ]
            
            content = None
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    content = content_div.get_text(strip=True)
                    break
            
            # 如果找不到特定選擇器，嘗試一般方法
            if not content:
                article_tag = soup.find('article')
                if article_tag:
                    content = article_tag.get_text(strip=True)
                else:
                    # 最後手段：取得 body 內容
                    body_tag = soup.find('body')
                    if body_tag:
                        content = body_tag.get_text(strip=True)
            
            if content and len(content) > 100:
                return content[:2000]  # 限制內容長度
            
            return None
            
        except Exception as e:
            logger.warning(f"擷取文章內容失敗 ({url}): {str(e)}")
            return None

    def _extract_article_links_from_search(self, soup: BeautifulSoup) -> List[str]:
        """
        從搜尋結果頁面擷取文章連結
        
        Args:
            soup: BeautifulSoup 物件
            
        Returns:
            文章連結列表
        """
        links = []
        
        # 常見的文章連結選擇器
        link_selectors = [
            'h2.entry-title a',
            'h3.entry-title a',
            'h1.entry-title a',
            '.post-title a',
            '.entry-title a',
            'article h2 a',
            'article h3 a'
        ]
        
        for selector in link_selectors:
            link_elements = soup.select(selector)
            for link_element in link_elements:
                href = link_element.get('href')
                if href and href.startswith('http'):
                    links.append(href)
                    if len(links) >= 10:  # 限制連結數量
                        break
            if links:
                break
        
        return links

    def _extract_title_from_url(self, url: str) -> str:
        """
        從 URL 中擷取文章標題
        
        Args:
            url: 文章 URL
            
        Returns:
            文章標題
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            try:
                soup = BeautifulSoup(response.content, 'lxml')
            except:
                try:
                    soup = BeautifulSoup(response.content, 'html5lib')
                except:
                    soup = BeautifulSoup(response.content, 'html.parser')
            
            # 尋找標題
            title_selectors = [
                'h1.entry-title',
                'h1.post-title',
                'h1.article-title',
                'title',
                'h1'
            ]
            
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = title_element.get_text(strip=True)
                    if title and len(title) > 5:
                        return title
            
            # 如果找不到標題，從 URL 推測
            return url.split('/')[-1].replace('-', ' ').replace('.html', '').title()
            
        except Exception as e:
            logger.warning(f"擷取標題失敗 ({url}): {str(e)}")
            return "標題擷取失敗"

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

def fetch_random_articles(n: int = 3) -> List[Dict[str, str]]:
    """
    便利函數：隨機擷取 TechOrange 文章
    
    Args:
        n: 文章數量
        
    Returns:
        List of Dict containing {title, url, content}
    """
    crawler = TechOrangeCrawler()
    return crawler.fetch_random_articles(n)

if __name__ == "__main__":
    # 測試用例
    print("測試關鍵字搜尋:")
    test_keyword = "AI"
    articles = fetch_articles(test_keyword, 2)
    
    print(f"找到 {len(articles)} 篇文章：")
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. 標題: {article['title']}")
        print(f"   連結: {article['url']}")
        print(f"   內容預覽: {article['content'][:100]}...")
    
    print("\n" + "="*50)
    print("測試隨機推送:")
    random_articles = fetch_random_articles(2)
    
    print(f"隨機找到 {len(random_articles)} 篇文章：")
    for i, article in enumerate(random_articles, 1):
        print(f"\n{i}. 標題: {article['title']}")
        print(f"   連結: {article['url']}")
        print(f"   內容預覽: {article['content'][:100]}...")
