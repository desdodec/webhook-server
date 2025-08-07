# test_webhook.py
import requests
import json

url = "https://2d596750fb3f.ngrok-free.app/process"

payload = {
    "pulseId": 123,
    "pulseName": "Test Item",
    "statusInfo": {
        "label": {
            "text": "Automate_Test"
        }
    }
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")