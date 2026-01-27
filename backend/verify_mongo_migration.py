import requests
import uuid

BASE_URL = "http://localhost:5000"

def test_flow():
    email = f"mongo_test_{uuid.uuid4().hex[:8]}@example.com"
    name = "Mongo Test User"
    
    print(f"Testing with email: {email}")
    
    # 1. Register
    payload = {
        "firebaseUid": f"fb_{uuid.uuid4().hex}",
        "email": email,
        "name": name,
        "role": "public"
    }
    print("1. Registering...")
    res = requests.post(f"{BASE_URL}/register", json=payload)
    print(f"   Status: {res.status_code}")
    if res.status_code != 201:
        print(f"   Response: {res.text}")
        return
        
    user_id = res.json()['user']['id']
    print(f"   User ID: {user_id}")
    
    # 2. Login (Stubbed logic since we need firebase token, but we can verify user exists via search)
    print("2. Verifying user exists via Search...")
    res = requests.get(f"{BASE_URL}/users/search?q={email}")
    print(f"   Status: {res.status_code}")
    users = res.json()
    if len(users) > 0 and users[0]['email'] == email:
        print("   SUCCESS: User found in search (from MongoDB)")
    else:
        print(f"   FAILURE: User not found. Response: {users}")
        
    # 3. Create Post
    print("3. Creating Post...")
    post_payload = {
        "userId": user_id,
        "content": "Hello MongoDB World!",
        "timestamp": None
    }
    res = requests.post(f"{BASE_URL}/posts", json=post_payload)
    print(f"   Status: {res.status_code}")
    if res.status_code == 201:
         print("   SUCCESS: Post created in MongoDB")
    else:
         print(f"   FAILURE: {res.text}")

if __name__ == "__main__":
    try:
        test_flow()
    except Exception as e:
        print(f"Error: {e}")
