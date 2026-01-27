"""
Quick test to check if backend is working
"""
import requests

BASE_URL = "http://localhost:5000"

print("Testing LegalConnect Backend...")
print("=" * 60)

# Test 1: Posts endpoint
print("\n1. Testing /posts endpoint...")
try:
    response = requests.get(f"{BASE_URL}/posts?userId=test123")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Posts endpoint working! Found {len(data)} posts")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: User search endpoint
print("\n2. Testing /users/search endpoint...")
try:
    response = requests.get(f"{BASE_URL}/users/search?q=sarah")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Search endpoint working! Found {len(data)} users")
        for user in data:
            print(f"      - {user.get('name')} ({user.get('role')})")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Call settings endpoint
print("\n3. Testing /api/admin/call-settings endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/admin/call-settings")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Call settings working!")
        print(f"      Price: ₹{data.get('call_price')}")
        print(f"      Duration: {data.get('call_duration')} minutes")
    else:
        print(f"   ❌ Error: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("Backend test complete!")
