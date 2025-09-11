"""
測試 Gemini 2.0 Flash 模型連接
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def test_gemini_models():
    """測試不同的 Gemini 模型名稱"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 未設置")
        return
    
    genai.configure(api_key=api_key)
    
    # 嘗試不同的模型名稱
    model_names = [
        'gemini-2.0-flash-exp',
        'gemini-2.0-flash',
        'gemini-pro',
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]
    
    test_prompt = "請用中文簡短回答：什麼是人工智慧？"
    
    for model_name in model_names:
        try:
            print(f"\n🧪 測試模型: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(test_prompt)
            
            if response.text:
                print(f"✅ 成功! 回應: {response.text[:50]}...")
                print(f"   模型 {model_name} 可正常使用")
                break
            else:
                print(f"❌ 無回應內容")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
    
    # 測試列出可用模型
    try:
        print(f"\n📋 查詢可用模型:")
        models = genai.list_models()
        gemini_models = [m for m in models if 'gemini' in m.name.lower()]
        for model in gemini_models[:5]:  # 只顯示前5個
            print(f"   - {model.name}")
    except Exception as e:
        print(f"❌ 無法列出模型: {str(e)}")

if __name__ == "__main__":
    test_gemini_models()
