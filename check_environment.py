#!/usr/bin/env python3
"""
環境變數診斷腳本
檢查部署環境的環境變數設置
"""

import requests
import json

def check_render_deployment():
    """檢查 Render 部署的環境變數狀態"""
    base_url = "https://ainewschatbot.onrender.com"
    
    print("🔍 檢查 Render 部署環境變數狀態")
    print("=" * 50)
    
    try:
        # 檢查健康狀態
        print("📊 獲取健康檢查報告...")
        response = requests.get(f"{base_url}/health", timeout=15)
        
        if response.status_code == 200:
            health_data = response.json()
            
            print(f"整體狀態: {health_data.get('status', '未知')}")
            print("\n🔧 組件狀態:")
            components = health_data.get('components', {})
            for component, status in components.items():
                emoji = "✅" if status else "❌"
                print(f"  {emoji} {component}: {status}")
            
            print("\n🔑 環境變數狀態:")
            env_vars = health_data.get('environment_variables', {})
            for var_name, status in env_vars.items():
                emoji = "✅" if status else "❌"
                print(f"  {emoji} {var_name}: {'已設置' if status else '未設置'}")
            
            # 顯示建議
            if 'suggestions' in health_data:
                print("\n💡 建議:")
                for suggestion in health_data['suggestions']:
                    print(f"  - {suggestion}")
            
            # 根據狀態給出具體的解決方案
            status = health_data.get('status')
            if status == 'unhealthy':
                print("\n🚨 嚴重問題 - LINE Bot 無法正常運作")
                print("解決步驟:")
                print("1. 登入 Render Dashboard")
                print("2. 進入服務設定 → Environment")
                print("3. 確認設置以下環境變數:")
                print("   - LINE_CHANNEL_ACCESS_TOKEN")
                print("   - LINE_CHANNEL_SECRET")
                print("   - GEMINI_API_KEY")
                print("4. 重新部署服務")
                
            elif status == 'degraded':
                print("\n⚠️ 部分功能異常")
                print("LINE Bot 基礎功能應該可用，但部分組件可能有問題")
                
            else:
                print("\n🎉 一切正常！")
                
        else:
            print(f"❌ 健康檢查失敗: HTTP {response.status_code}")
            print(f"回應: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ 無法連接到服務: {e}")
        print("可能原因:")
        print("1. 服務尚未完全啟動")
        print("2. 部署失敗")
        print("3. 網路連接問題")
    
    except Exception as e:
        print(f"❌ 未預期的錯誤: {e}")

def test_callback_endpoint():
    """測試 callback 端點"""
    base_url = "https://ainewschatbot.onrender.com"
    
    print("\n" + "=" * 50)
    print("🧪 測試 Callback 端點")
    
    try:
        # 模擬 LINE webhook 請求
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'LineBotWebhook/2.0',
            'X-Line-Signature': 'test_signature'
        }
        
        test_payload = {
            "events": [],
            "destination": "test"
        }
        
        response = requests.post(
            f"{base_url}/callback",
            headers=headers,
            json=test_payload,
            timeout=10
        )
        
        print(f"Callback 測試結果: HTTP {response.status_code}")
        print(f"回應: {response.text}")
        
        if response.status_code == 200:
            print("✅ Callback 端點運作正常")
        else:
            print("❌ Callback 端點有問題")
            
    except Exception as e:
        print(f"❌ Callback 測試失敗: {e}")

if __name__ == "__main__":
    check_render_deployment()
    test_callback_endpoint()
    
    print("\n" + "=" * 50)
    print("📋 下一步:")
    print("1. 如果環境變數未設置，請在 Render Dashboard 中設定")
    print("2. 檢查 Render 的即時日誌 (Logs 頁面)")
    print("3. 確認部署已完成且服務正在運行")
    print("4. 重新在 LINE Developers Console 測試 webhook")