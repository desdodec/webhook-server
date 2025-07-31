from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Webhook endpoint with secret token in the URL path
@app.route('/webhook/<secret>', methods=['POST'])
def webhook(secret):
    expected_secret = os.environ.get("MONDAY_WEBHOOK_SECRET")
    print(f"🔐 Received secret: {secret}")
    print(f"🔐 Expected secret: {expected_secret}")
    if secret != expected_secret:
        return jsonify({"error": "unauthorized"}), 403

    data = request.json

    # Handle Monday.com's initial challenge verification
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # Log the incoming webhook data
    print("✅ Received webhook payload:")
    print(data)

    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Webhook server running"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
