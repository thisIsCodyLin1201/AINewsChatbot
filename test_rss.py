import requests
import feedparser

# 測試 RSS feed
response = requests.get('https://buzzorange.com/techorange/feed/')
feed = feedparser.parse(response.content)

print(f'RSS feed 中有 {len(feed.entries)} 篇文章')
print('前 10 篇文章標題:')
for i, entry in enumerate(feed.entries[:10]):
    print(f'{i+1}. {entry.title}')

# 測試隨機選擇
import random
if len(feed.entries) > 3:
    selected = random.sample(feed.entries, 3)
    print('\n隨機選擇的 3 篇:')
    for i, entry in enumerate(selected):
        print(f'{i+1}. {entry.title}')
else:
    print(f'\nRSS feed 只有 {len(feed.entries)} 篇文章，無法隨機選擇')
