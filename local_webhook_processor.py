# local_webhook_processor.py
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

def process_sap_ariba_automation(pulse_id, pulse_name, status_info):
    """Your SAP/Ariba processing function"""
    print(f"🔄 Processing pulse: {pulse_id}")
    print(f"📝 Pulse name: {pulse_name}")
    print(f"📊 New status: {status_info.get('label', {}).get('text', 'Unknown')}")
    
    # Add your SAP/Ariba automation logic here
    # Example:
    if status_info.get('label', {}).get('text') == 'Automate_Test':
        print("✅ Triggering SAP/Ariba form automation...")
        # Your actual automation code here
        return True
    
    print("⏭️ Status not matching automation trigger")
    return False

@app.route('/process', methods=['POST'])
def process_webhook():
    try:
        print("📨 Received webhook from Railway server")
        data = request.json
        print(f"📄 Data received: {json.dumps(data, indent=2)}")
        
        pulse_id = data.get('pulseId')
        pulse_name = data.get('pulseName')
        status_info = data.get('statusInfo', {})
        
        if not pulse_id:
            return jsonify({'status': 'error', 'message': 'Missing pulseId'}), 400
        
        success = process_sap_ariba_automation(pulse_id, pulse_name, status_info)
        
        if success:
            return jsonify({'status': 'processed', 'pulseId': pulse_id}), 200
        else:
            return jsonify({'status': 'skipped', 'pulseId': pulse_id}), 200
            
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Local processor running'}), 200

if __name__ == '__main__':
    print("🚀 Starting local webhook processor...")
    print("📍 Server will run on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)