from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Handle Monday.com's challenge verification
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # Handle actual button click events
    print("Received webhook from Monday:")
    print(data)

    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Webhook server running"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
