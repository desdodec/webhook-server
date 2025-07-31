from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Webhook received:", json.dumps(data, indent=2))
    return jsonify({"status": "received"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Webhook server running"

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
