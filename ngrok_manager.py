"""
自動化 ngrok 管理腳本
處理 ngrok 重新啟動和 URL 獲取
"""
import requests
import time
import subprocess
import os

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

def warm_up_ngrok_url(url):
    """預熱 ngrok URL 來跳過警告頁面"""
    endpoints = ['/', '/health', '/callback']
    
    print(f"🔥 預熱 ngrok URL: {url}")
    
    for endpoint in endpoints:
        try:
            full_url = url + endpoint
            print(f"   訪問: {full_url}")
            response = requests.get(full_url, timeout=10, allow_redirects=True)
            print(f"   回應: {response.status_code}")
        except Exception as e:
            print(f"   錯誤: {e}")
        time.sleep(1)

def main():
    print("🚀 ngrok 自動化管理")
    print("=" * 50)
    
    # 等待 ngrok 啟動
    print("\n⏳ 等待 ngrok 啟動...")
    for i in range(20):
        url = get_ngrok_url()
        if url:
            print(f"\n✅ 取得 ngrok URL: {url}")
            
            # 預熱 URL
            warm_up_ngrok_url(url)
            
            print(f"\n📱 LINE Webhook URL:")
            print(f"   {url}/callback")
            
            print(f"\n🧪 測試端點:")
            print(f"   健康檢查: {url}/health")
            print(f"   首頁: {url}")
            print(f"   回調: {url}/callback")
            
            return url
        
        print(f"   嘗試 {i+1}/20...")
        time.sleep(2)
    
    print("\n❌ 無法取得 ngrok URL")
    return None

if __name__ == "__main__":
    main()
