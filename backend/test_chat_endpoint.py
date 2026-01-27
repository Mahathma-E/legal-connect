import requests
import time

url = "http://localhost:5000/chat"
payload = {"message": "What is Article 21?"}

print(f"Sending POST request to {url}...")
try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print(f"Request failed: {e}")
