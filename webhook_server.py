from flask import Flask, request, jsonify
import os
import requests
import json

app = Flask(__name__)

# Your ngrok URL - update this when ngrok restarts
LOCAL_SERVER_URL = "https://2d596750fb3f.ngrok-free.app"  # Replace with your actual ngrok URL

# Webhook endpoint that works with Monday.com
@app.route('/webhook', methods=['POST'])
def webhook():
    print("🚨 WEBHOOK ENDPOINT HIT!")  # This should show up immediately
    print(f"📥 Request method: {request.method}")
    print(f"📥 Request headers: {dict(request.headers)}")
    
    try:
        data = request.json
        print("📄 Successfully parsed JSON data")
    except Exception as e:
        print(f"❌ Error parsing JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400
    
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
    print("✅ Received webhook payload from Monday.com:")
    print(json.dumps(data, indent=2))
    
    # Extract event data for forwarding
    event = data.get('event', {})
    if event:
        # Prepare payload for local server
        webhook_payload = {
            'pulseId': event.get('pulseId'),
            'pulseName': event.get('pulseName'),
            'statusInfo': event.get('value', {}),
            'previousStatus': event.get('previousValue', {}),
            'boardId': event.get('boardId'),
            'columnId': event.get('columnId'),
            'columnTitle': event.get('columnTitle'),
            'triggerTime': event.get('triggerTime'),
            'userId': event.get('userId')
        }
        
        print(f"📤 Forwarding to local development server: {LOCAL_SERVER_URL}/process")
        print(f"📋 Payload: {json.dumps(webhook_payload, indent=2)}")
        
        # Forward to your local development server
        try:
            response = requests.post(
                f"{LOCAL_SERVER_URL}/process",
                json=webhook_payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"✅ Local server response status: {response.status_code}")
            print(f"📄 Local server response: {response.text}")
            
            if response.status_code == 200:
                print("🎉 Successfully processed by local server")
            else:
                print(f"⚠️ Local server returned non-200 status: {response.status_code}")
            
        except requests.exceptions.Timeout:
            print("⏰ Timeout connecting to local server")
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error - is local server running?")
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to forward to local server: {e}")
    else:
        print("📝 No event data found in webhook - might be a test webhook")
    
    # Always return success to Monday.com so webhook doesn't get disabled
    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def home():
    return "Webhook server running - forwarding to local development"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "local_server": LOCAL_SERVER_URL,
        "forwarding": "enabled"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)