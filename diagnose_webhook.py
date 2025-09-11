#!/usr/bin/env python3
"""
遠端診斷腳本 - 檢查部署的應用狀態
"""

import requests
import json

def test_webhook_endpoint():
    """測試 webhook 端點"""
    base_url = "https://ainewschatbot.onrender.com"
    
    print("🔍 診斷 LINE TechOrange NewsBot 部署狀態")
    print("=" * 50)
    
    # 測試健康檢查
    print("1. 測試健康檢查端點...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   狀態碼: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   健康狀態: {health_data.get('status', '未知')}")
            print(f"   組件狀態: {health_data.get('components', {})}")
        else:
            print(f"   錯誤: {response.text}")
    except Exception as e:
        print(f"   錯誤: {e}")
    
    # 測試首頁
    print("\n2. 測試首頁...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   狀態碼: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 首頁正常")
        else:
            print(f"   ❌ 首頁錯誤: {response.text}")
    except Exception as e:
        print(f"   錯誤: {e}")
    
    # 測試 callback 端點（GET 請求 - 不應該有內容但應該回應）
    print("\n3. 測試 callback 端點（GET 請求）...")
    try:
        response = requests.get(f"{base_url}/callback", timeout=10)
        print(f"   狀態碼: {response.status_code}")
        # callback 只接受 POST，所以 GET 會返回 405
        if response.status_code == 405:
            print("   ✅ 正確拒絕 GET 請求（返回 405）")
        else:
            print(f"   狀態: {response.text}")
    except Exception as e:
        print(f"   錯誤: {e}")
    
    # 測試 callback 端點（POST 請求 - 模擬 LINE 驗證）
    print("\n4. 測試 callback 端點（POST 請求）...")
    try:
        # 模擬 LINE 驗證請求（通常沒有簽名或空內容）
        response = requests.post(f"{base_url}/callback", timeout=10)
        print(f"   狀態碼: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ POST 請求正常回應")
            print(f"   回應內容: {response.text}")
        else:
            print(f"   ❌ POST 請求錯誤: {response.text}")
    except Exception as e:
        print(f"   錯誤: {e}")
    
    # 測試帶有 header 的 POST 請求
    print("\n5. 測試帶有 LINE header 的 POST 請求...")
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'LineBotWebhook/2.0',
        }
        response = requests.post(f"{base_url}/callback", 
                               headers=headers, 
                               json={}, 
                               timeout=10)
        print(f"   狀態碼: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 帶 header 的 POST 請求正常")
        else:
            print(f"   狀態: {response.text}")
    except Exception as e:
        print(f"   錯誤: {e}")
    
    print("\n" + "=" * 50)
    print("📋 診斷建議:")
    print("- 如果第 4 項測試返回 200，那麼 LINE webhook 驗證應該能通過")
    print("- 如果仍然失敗，請檢查 Render 的實時日誌")
    print("- 確保環境變數已正確設定")

if __name__ == "__main__":
    test_webhook_endpoint()
