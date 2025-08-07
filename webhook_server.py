from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Webhook endpoint that works with Monday.com
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # Handle Monday.com's initial challenge verification
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # Optional: verify a secret value inside the payload
    if os.environ.get("REQUIRE_WEBHOOK_SECRET") == "1":
        secret_received = data.get("secret")
        expected_secret = os.environ.get("MONDAY_WEBHOOK_SECRET")
        print(f"🔐 Received secret: {secret_received}")
        print(f"🔐 Expected secret: {expected_secret}")
        if secret_received != expected_secret:
            return jsonify({"error": "unauthorized"}), 403

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
