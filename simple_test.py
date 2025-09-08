"""
簡化的 LINE Bot 測試服務
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return "LINE Bot Test Server is running!"

@app.route("/health", methods=['GET'])
def health():
    return {"status": "ok", "message": "Health check passed"}

@app.route("/callback", methods=['GET', 'POST'])
def callback():
    if request.method == 'GET':
        return {"status": "ok", "method": "GET", "message": "Callback endpoint is working"}
    
    if request.method == 'POST':
        # 記錄請求內容
        headers = dict(request.headers)
        body = request.get_data(as_text=True)
        
        print(f"收到 POST 請求:")
        print(f"Headers: {headers}")
        print(f"Body: {body}")
        
        return "OK", 200

if __name__ == "__main__":
    print("🤖 啟動簡化測試服務...")
    print("📱 健康檢查: http://localhost:5000/health")
    print("🔗 回調端點: http://localhost:5000/callback")
    app.run(host='0.0.0.0', port=5000, debug=True)
