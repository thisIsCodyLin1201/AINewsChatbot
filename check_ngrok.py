"""
持續檢查 ngrok 隧道狀態
"""
import requests
import json
import time

def check_ngrok_status():
    """檢查 ngrok 隧道狀態"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            if tunnels:
                print("🎉 ngrok 隧道已建立！")
                print("=" * 50)
                for tunnel in tunnels:
                    name = tunnel.get('name', 'unknown')
                    public_url = tunnel.get('public_url', 'unknown')
                    proto = tunnel.get('proto', 'unknown')
                    
                    print(f"隧道名稱: {name}")
                    print(f"公網 URL: {public_url}")
                    print(f"協定: {proto}")
                    
                    if public_url and public_url.startswith('https://'):
                        webhook_url = f"{public_url}/callback"
                        print(f"\n📱 LINE Webhook URL:")
                        print(f"   {webhook_url}")
                        print(f"\n🔧 設定步驟:")
                        print(f"   1. 前往 LINE Developers Console")
                        print(f"   2. 選擇你的 Channel (ID: 2008061586)")
                        print(f"   3. 點擊 Messaging API")
                        print(f"   4. 在 Webhook URL 欄位輸入:")
                        print(f"      {webhook_url}")
                        print(f"   5. 啟用 'Use webhook' 選項")
                        print(f"   6. 點擊 Verify 測試連線")
                
                return True
            else:
                print("⏳ 隧道正在建立中...")
                return False
        else:
            print(f"❌ API 回應錯誤: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"⏳ 等待 ngrok 啟動... ({str(e)[:50]})")
        return False

def main():
    """主函數"""
    print("🔍 檢查 ngrok 隧道狀態...")
    
    max_attempts = 20
    for attempt in range(1, max_attempts + 1):
        print(f"\n嘗試 {attempt}/{max_attempts}:")
        
        if check_ngrok_status():
            print("\n✅ ngrok 已就緒！")
            break
        
        if attempt < max_attempts:
            time.sleep(2)
    else:
        print("\n❌ 無法連接到 ngrok API")
        print("請確認:")
        print("1. ngrok 是否正在運行")
        print("2. ngrok Web 介面是否可在 http://localhost:4040 存取")

if __name__ == "__main__":
    main()
