"""
自動取得 ngrok URL 的腳本
"""
import requests
import json
import time

def get_ngrok_url():
    """取得當前的 ngrok URL"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            for tunnel in tunnels:
                public_url = tunnel.get('public_url', '')
                if public_url.startswith('https://'):
                    return public_url
        return None
    except:
        return None

def main():
    print("🔍 取得 ngrok URL...")
    
    for i in range(10):
        url = get_ngrok_url()
        if url:
            print(f"✅ 找到 ngrok URL: {url}")
            print(f"📱 LINE Webhook URL: {url}/callback")
            print(f"🧪 健康檢查: {url}/health")
            return url
        
        print(f"⏳ 等待 ngrok 啟動... ({i+1}/10)")
        time.sleep(2)
    
    print("❌ 無法取得 ngrok URL")
    return None

if __name__ == "__main__":
    main()
