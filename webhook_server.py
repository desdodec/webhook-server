from flask import Flask, request, jsonify
import os
import requests
import json

app = Flask(__name__)

# Get the local development URL from environment variable
LOCAL_SERVER_URL = os.environ.get("LOCAL_DEV_URL", "")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
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
        print("✅ Received webhook payload from Monday.com:")
        print(json.dumps(data, indent=2))
        
        # Check if LOCAL_DEV_URL is configured
        if not LOCAL_SERVER_URL:
            print("⚠️ LOCAL_DEV_URL environment variable not set - skipping forwarding")
            print("📋 To enable forwarding, set LOCAL_DEV_URL in Railway dashboard")
            return jsonify({"status": "ok", "message": "No local dev URL configured"}), 200
        
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
                    timeout=30,  # Increased timeout for automation
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"✅ Local server response status: {response.status_code}")
                print(f"📄 Local server response: {response.text}")
                
                if response.status_code == 200:
                    print("🎉 Successfully processed by local server")
                else:
                    print(f"⚠️ Local server returned non-200 status: {response.status_code}")
                
            except requests.exceptions.Timeout:
                print("⏰ Timeout connecting to local server (automation may still be running)")
            except requests.exceptions.ConnectionError:
                print("🔌 Connection error - is local server running and ngrok active?")
                print(f"💡 Current LOCAL_DEV_URL: {LOCAL_SERVER_URL}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to forward to local server: {e}")
        else:
            print("📝 No event data found in webhook - might be a test webhook")
        
        # Always return success to Monday.com so webhook doesn't get disabled
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"❌ Webhook processing error: {e}")
        # Even if there's an error, return 200 to Monday so webhook doesn't get disabled
        return jsonify({"status": "error", "message": str(e)}), 200

@app.route('/', methods=['GET'])
def home():
    local_url_status = "configured" if LOCAL_SERVER_URL else "not configured"
    return f"Webhook server running - local forwarding: {local_url_status}"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "local_server": LOCAL_SERVER_URL if LOCAL_SERVER_URL else "not configured",
        "forwarding": "enabled" if LOCAL_SERVER_URL else "disabled"
    })

@app.route('/config', methods=['GET'])
def config():
    """Show current configuration (useful for debugging)"""
    return jsonify({
        "LOCAL_DEV_URL_configured": bool(LOCAL_SERVER_URL),
        "LOCAL_DEV_URL_value": LOCAL_SERVER_URL[:50] + "..." if len(LOCAL_SERVER_URL) > 50 else LOCAL_SERVER_URL,
        "REQUIRE_WEBHOOK_SECRET": os.environ.get("REQUIRE_WEBHOOK_SECRET", "not set"),
        "environment_vars": list(os.environ.keys())
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Railway webhook server on port {port}")
    
    if LOCAL_SERVER_URL:
        print(f"📡 Local development forwarding enabled: {LOCAL_SERVER_URL}")
    else:
        print("⚠️ LOCAL_DEV_URL not set - local forwarding disabled")
        print("💡 Set LOCAL_DEV_URL in Railway dashboard to enable forwarding")
    
    app.run(host='0.0.0.0', port=port)