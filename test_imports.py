# 測試新版本套件相容性

# 測試核心套件導入
print("測試套件導入...")

try:
    import flask
    print(f"✅ Flask {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask: {e}")

try:
    import requests
    print(f"✅ Requests {requests.__version__}")
except ImportError as e:
    print(f"❌ Requests: {e}")

try:
    import aiohttp
    print(f"✅ aiohttp {aiohttp.__version__}")
except ImportError as e:
    print(f"❌ aiohttp: {e}")

try:
    from linebot import LineBotApi
    import linebot
    print(f"✅ line-bot-sdk {linebot.__version__}")
except ImportError as e:
    print(f"❌ line-bot-sdk: {e}")

try:
    import google.generativeai as genai
    print(f"✅ google-generativeai 已導入")
except ImportError as e:
    print(f"❌ google-generativeai: {e}")

try:
    from bs4 import BeautifulSoup
    print("✅ BeautifulSoup 已導入")
except ImportError as e:
    print(f"❌ BeautifulSoup: {e}")

try:
    import lxml
    print("✅ lxml 已導入")
except ImportError as e:
    print(f"❌ lxml: {e}")

print("\n測試完成！")
