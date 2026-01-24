"""
Test script for MongoDB endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoints():
    print("=" * 60)
    print("Testing MongoDB Integration Endpoints")
    print("=" * 60)
    
    # Test 1: MongoDB connection test
    print("\n1. Testing MongoDB connection (/api/test-db)...")
    try:
        response = requests.get(f"{BASE_URL}/api/test-db")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Fetch Article 23
    print("\n2. Testing Article Fetch (/api/constitution/article/23)...")
    try:
        response = requests.get(f"{BASE_URL}/api/constitution/article/23")
        print(f"   Status Code: {response.status_code}")
        data = response.json()
        if response.status_code == 200:
            print(f"   ✓ Article ID: {data.get('article', {}).get('id')}")
            print(f"   ✓ Article Title: {data.get('article', {}).get('title')}")
            print(f"   ✓ Part Title: {data.get('partTitle')}")
        else:
            print(f"   Response: {data}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Fetch all constitution data
    print("\n3. Testing Constitution Endpoint (/constitution)...")
    try:
        response = requests.get(f"{BASE_URL}/constitution")
        print(f"   Status Code: {response.status_code}")
        data = response.json()
        if response.status_code == 200:
            parts_count = len(data.get('parts', []))
            print(f"   ✓ Successfully fetched {parts_count} constitution parts")
        else:
            print(f"   Response: {data}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_endpoints()
