"""
Demo Account Setup Script for Paid Calling Feature
Creates two test accounts (Public + Advocate) with mutual following
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def create_demo_accounts():
    print("\n" + "="*60)
    print("CREATING DEMO ACCOUNTS FOR CALLING FEATURE")
    print("="*60)
    
    # Account 1: Public User
    public_user = {
        "name": "John Public",
        "email": "john.public@demo.com",
        "password": "demo123",
        "role": "Public"
    }
    
    # Account 2: Advocate User
    advocate_user = {
        "name": "Sarah Advocate",
        "email": "sarah.advocate@demo.com",
        "password": "demo123",
        "role": "Advocate",
        "bar_code": "BAR12345"
    }
    
    print("\n1️⃣  Creating Public User Account...")
    print(f"   Email: {public_user['email']}")
    print(f"   Password: {public_user['password']}")
    
    response = requests.post(f"{BASE_URL}/register", json=public_user)
    if response.status_code == 200:
        public_data = response.json()
        print(f"   ✅ Created! User ID: {public_data.get('id')}")
        public_id = public_data.get('id')
    else:
        print(f"   ⚠️  Response: {response.json()}")
        # User might already exist, try to login
        login_response = requests.post(f"{BASE_URL}/login", json={
            "email": public_user['email'],
            "password": public_user['password']
        })
        if login_response.status_code == 200:
            public_data = login_response.json()
            public_id = public_data.get('id')
            print(f"   ℹ️  User already exists. ID: {public_id}")
        else:
            print(f"   ❌ Failed to create/login public user")
            return
    
    print("\n2️⃣  Creating Advocate User Account...")
    print(f"   Email: {advocate_user['email']}")
    print(f"   Password: {advocate_user['password']}")
    print(f"   Bar Code: {advocate_user['bar_code']}")
    
    response = requests.post(f"{BASE_URL}/register", json=advocate_user)
    if response.status_code == 200:
        advocate_data = response.json()
        print(f"   ✅ Created! User ID: {advocate_data.get('id')}")
        advocate_id = advocate_data.get('id')
    else:
        print(f"   ⚠️  Response: {response.json()}")
        # User might already exist, try to login
        login_response = requests.post(f"{BASE_URL}/login", json={
            "email": advocate_user['email'],
            "password": advocate_user['password']
        })
        if login_response.status_code == 200:
            advocate_data = login_response.json()
            advocate_id = advocate_data.get('id')
            print(f"   ℹ️  User already exists. ID: {advocate_id}")
        else:
            print(f"   ❌ Failed to create/login advocate user")
            return
    
    print("\n3️⃣  Setting up Mutual Following...")
    print(f"   {public_user['name']} → follows → {advocate_user['name']}")
    print(f"   {advocate_user['name']} → follows → {public_user['name']}")
    
    # Note: You'll need to implement follow endpoints or manually add to database
    # For now, we'll show the manual database update
    print("\n   ⚠️  Manual Step Required:")
    print("   Run the following in MongoDB shell or Compass:")
    print(f"""
   // Update Public user to follow Advocate
   db.users.updateOne(
     {{ "id": "{public_id}" }},
     {{ $addToSet: {{ following: "{advocate_id}" }} }}
   )
   
   // Update Advocate to follow Public user
   db.users.updateOne(
     {{ "id": "{advocate_id}" }},
     {{ $addToSet: {{ following: "{public_id}" }} }}
   )
   
   // Update followers count
   db.users.updateOne(
     {{ "id": "{public_id}" }},
     {{ $addToSet: {{ followers: "{advocate_id}" }} }}
   )
   
   db.users.updateOne(
     {{ "id": "{advocate_id}" }},
     {{ $addToSet: {{ followers: "{public_id}" }} }}
   )
   """)
    
    print("\n4️⃣  Verifying Advocate Account...")
    print("   ⚠️  Manual Step Required:")
    print("   Run the following in MongoDB shell or Compass:")
    print(f"""
   db.users.updateOne(
     {{ "id": "{advocate_id}" }},
     {{ $set: {{ isVerified: true }} }}
   )
   """)
    
    print("\n5️⃣  Checking Wallet Balances...")
    print("   Both users should have ₹100 initial balance")
    print("   (Set by migration script)")
    
    print("\n" + "="*60)
    print("DEMO ACCOUNTS SUMMARY")
    print("="*60)
    
    print("\n📋 Account Details:")
    print("\n🙋 Public User:")
    print(f"   Name: {public_user['name']}")
    print(f"   Email: {public_user['email']}")
    print(f"   Password: {public_user['password']}")
    print(f"   User ID: {public_id}")
    print(f"   Wallet: ₹100")
    
    print("\n⚖️  Advocate User:")
    print(f"   Name: {advocate_user['name']}")
    print(f"   Email: {advocate_user['email']}")
    print(f"   Password: {advocate_user['password']}")
    print(f"   User ID: {advocate_id}")
    print(f"   Bar Code: {advocate_user['bar_code']}")
    print(f"   Wallet: ₹100")
    print(f"   Verified: ✅ (after manual step)")
    
    print("\n🔗 Mutual Following:")
    print(f"   {public_user['name']} ↔️ {advocate_user['name']}")
    
    print("\n📞 Testing Call Eligibility:")
    print(f"\n   Testing if {public_user['name']} can call {advocate_user['name']}...")
    
    eligibility_response = requests.post(
        f"{BASE_URL}/api/call/check-eligibility",
        json={
            "caller_id": public_id,
            "receiver_id": advocate_id
        }
    )
    
    if eligibility_response.status_code == 200:
        eligibility = eligibility_response.json()
        if eligibility.get('eligible'):
            print("   ✅ ELIGIBLE TO CALL!")
            print(f"   💰 Call Price: ₹{eligibility.get('call_price')}")
            print(f"   ⏱️  Duration: {eligibility.get('call_duration')} minutes")
            print(f"   💵 Wallet Balance: ₹{eligibility.get('wallet_balance')}")
        else:
            print(f"   ❌ NOT ELIGIBLE")
            print(f"   Reason: {eligibility.get('reason')}")
    else:
        print(f"   ⚠️  Error checking eligibility: {eligibility_response.text}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("\n1. Complete the manual MongoDB updates above")
    print("2. Login to the application:")
    print(f"   - Go to http://localhost:3000")
    print(f"   - Login as: {public_user['email']}")
    print(f"   - Password: {public_user['password']}")
    print("3. Navigate to Advocate's profile")
    print("4. You should see the [📞 Call] button enabled!")
    print("5. Click it to test the calling feature")
    
    print("\n✅ Demo accounts created successfully!")
    print("="*60 + "\n")
    
    # Save account info to file for reference
    demo_info = {
        "public_user": {
            "name": public_user['name'],
            "email": public_user['email'],
            "password": public_user['password'],
            "id": public_id
        },
        "advocate_user": {
            "name": advocate_user['name'],
            "email": advocate_user['email'],
            "password": advocate_user['password'],
            "id": advocate_id,
            "bar_code": advocate_user['bar_code']
        }
    }
    
    with open('demo_accounts.json', 'w') as f:
        json.dump(demo_info, f, indent=2)
    
    print("💾 Account details saved to: demo_accounts.json\n")

if __name__ == "__main__":
    try:
        create_demo_accounts()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend server")
        print("   Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
