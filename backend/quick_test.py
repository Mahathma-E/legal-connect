"""
Quick test for chatbot endpoint
"""
import requests

try:
    print("Testing chatbot endpoint...")
    response = requests.post(
        "http://localhost:5000/chat",
        json={"message": "hello", "document": ""},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
