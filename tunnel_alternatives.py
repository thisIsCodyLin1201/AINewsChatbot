"""
公網隧道替代方案
使用 localtunnel 或其他服務作為 ngrok 的替代
"""

# 方案 1: 使用 localtunnel (需要 Node.js)
# npm install -g localtunnel
# lt --port 5000 --subdomain your-bot-name

# 方案 2: 使用 serveo.net (免費，無需註冊)
# ssh -R 80:localhost:5000 serveo.net

# 方案 3: 使用 Cloudflare Tunnel (免費，需註冊)
# cloudflared tunnel --url http://localhost:5000

print("LINE Bot 公網隧道替代方案")
print("=" * 40)
print()
print("1. localtunnel (需要 Node.js):")
print("   npm install -g localtunnel")
print("   lt --port 5000")
print()
print("2. serveo.net (免費，無需註冊):")
print("   ssh -R 80:localhost:5000 serveo.net")
print()
print("3. Cloudflare Tunnel:")
print("   cloudflared tunnel --url http://localhost:5000")
print()
print("4. 或者註冊 ngrok 免費帳戶:")
print("   https://dashboard.ngrok.com/signup")
