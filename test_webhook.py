"""
測試 LINE Webhook 連線
"""
import requests
import json

def test_ngrok_endpoints():
    """測試 ngrok 端點"""
    base_url = "https://e910a8b0e709.ngrok-free.app"
    
    endpoints = [
        "/health",
        "/test", 
        "/callback"
    ]
    
    print("🧪 測試 ngrok 端點連線...")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\n測試: {url}")
        
        try:
            # 測試 GET 請求
            response = requests.get(url, timeout=10)
            print(f"  GET: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"  GET 錯誤: {e}")
        
        # 對 callback 端點測試 POST
        if endpoint == "/callback":
            try:
                # 模擬 LINE Webhook 請求
                test_data = {
                    "destination": "test",
                    "events": []
                }
                headers = {
                    'Content-Type': 'application/json',
                    'X-Line-Signature': 'test_signature'
                }
                response = requests.post(url, json=test_data, headers=headers, timeout=10)
                print(f"  POST: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                print(f"  POST 錯誤: {e}")

def test_local_endpoints():
    """測試本地端點"""
    base_url = "http://localhost:5000"
    
    endpoints = ["/health", "/test", "/callback"]
    
    print("\n🏠 測試本地端點連線...")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\n測試: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"  狀態: {response.status_code}")
            print(f"  回應: {response.text[:100]}")
        except Exception as e:
            print(f"  錯誤: {e}")

if __name__ == "__main__":
    test_local_endpoints()
    test_ngrok_endpoints()
