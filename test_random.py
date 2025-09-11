from crawler import TechOrangeCrawler

# 測試隨機文章功能
crawler = TechOrangeCrawler()

print("測試 1:")
articles1 = crawler.fetch_random_articles(3)
for i, article in enumerate(articles1, 1):
    print(f"{i}. {article['title']}")

print("\n測試 2:")
articles2 = crawler.fetch_random_articles(3)
for i, article in enumerate(articles2, 1):
    print(f"{i}. {article['title']}")

print("\n測試 3:")
articles3 = crawler.fetch_random_articles(3)
for i, article in enumerate(articles3, 1):
    print(f"{i}. {article['title']}")
