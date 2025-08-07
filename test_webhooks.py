import requests

url = "https://webhook-server-production-d665.up.railway.app/webhook/0Jujlm4azmNANRauhfzEL9J_yUuDR3jG"

payload = {
    "event": {
        "pulseId": 7284436494,
        "pulseName": "Karen Glossop",
        "boardId": 7112177547
    }
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print("Status:", response.status_code)
print("Response:", response.text)
