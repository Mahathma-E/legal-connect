"""
Complete Demo Setup - Adds Mutual Following and Verification
Run this after create_demo_accounts.py
"""
import json
from pymongo import MongoClient
from datetime import datetime

# Load demo account info
with open('demo_accounts.json', 'r') as f:
    demo_data = json.load(f)

public_id = demo_data['public_user']['id']
advocate_id = demo_data['advocate_user']['id']

print("\n" + "="*60)
print("COMPLETING DEMO SETUP")
print("="*60)

# Connect to MongoDB
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["legalconnect"]

# Load users from JSON file (your app uses JSON files)
with open('users.json', 'r') as f:
    users = json.load(f)

print("\n1️⃣  Setting up Mutual Following...")

# Find users by ID
public_email = None
advocate_email = None

for email, user in users.items():
    if user['id'] == public_id:
        public_email = email
    if user['id'] == advocate_id:
        advocate_email = email

if not public_email or not advocate_email:
    print("   ❌ Could not find users in database")
    exit(1)

# Add mutual following
if advocate_id not in users[public_email].get('following', []):
    users[public_email].setdefault('following', []).append(advocate_id)
    print(f"   ✅ {demo_data['public_user']['name']} now follows {demo_data['advocate_user']['name']}")
else:
    print(f"   ℹ️  {demo_data['public_user']['name']} already follows {demo_data['advocate_user']['name']}")

if public_id not in users[advocate_email].get('following', []):
    users[advocate_email].setdefault('following', []).append(public_id)
    print(f"   ✅ {demo_data['advocate_user']['name']} now follows {demo_data['public_user']['name']}")
else:
    print(f"   ℹ️  {demo_data['advocate_user']['name']} already follows {demo_data['public_user']['name']}")

# Add mutual followers
if advocate_id not in users[public_email].get('followers', []):
    users[public_email].setdefault('followers', []).append(advocate_id)

if public_id not in users[advocate_email].get('followers', []):
    users[advocate_email].setdefault('followers', []).append(public_id)

print("\n2️⃣  Verifying Advocate Account...")
users[advocate_email]['isVerified'] = True
print(f"   ✅ {demo_data['advocate_user']['name']} is now verified")

print("\n3️⃣  Ensuring Wallet Balances...")
if 'wallet_balance' not in users[public_email]:
    users[public_email]['wallet_balance'] = 100
    print(f"   ✅ Added ₹100 to {demo_data['public_user']['name']}'s wallet")
else:
    print(f"   ℹ️  {demo_data['public_user']['name']} wallet: ₹{users[public_email]['wallet_balance']}")

if 'wallet_balance' not in users[advocate_email]:
    users[advocate_email]['wallet_balance'] = 100
    print(f"   ✅ Added ₹100 to {demo_data['advocate_user']['name']}'s wallet")
else:
    print(f"   ℹ️  {demo_data['advocate_user']['name']} wallet: ₹{users[advocate_email]['wallet_balance']}")

# Initialize call counters
users[public_email].setdefault('total_calls_made', 0)
users[public_email].setdefault('total_calls_received', 0)
users[advocate_email].setdefault('total_calls_made', 0)
users[advocate_email].setdefault('total_calls_received', 0)

# Save updated users
with open('users.json', 'w') as f:
    json.dump(users, f, indent=2)

print("\n4️⃣  Saving changes to database...")
print("   ✅ users.json updated successfully")

print("\n" + "="*60)
print("DEMO SETUP COMPLETE!")
print("="*60)

print("\n✅ Configuration Summary:")
print(f"\n🙋 Public User: {demo_data['public_user']['name']}")
print(f"   Email: {demo_data['public_user']['email']}")
print(f"   Password: {demo_data['public_user']['password']}")
print(f"   Wallet: ₹{users[public_email]['wallet_balance']}")
print(f"   Following: {len(users[public_email].get('following', []))} users")

print(f"\n⚖️  Advocate User: {demo_data['advocate_user']['name']}")
print(f"   Email: {demo_data['advocate_user']['email']}")
print(f"   Password: {demo_data['advocate_user']['password']}")
print(f"   Wallet: ₹{users[advocate_email]['wallet_balance']}")
print(f"   Verified: ✅ YES")
print(f"   Following: {len(users[advocate_email].get('following', []))} users")

print(f"\n🔗 Mutual Following: ✅ ENABLED")
print(f"   {demo_data['public_user']['name']} ↔️ {demo_data['advocate_user']['name']}")

print("\n📞 Call Feature Status:")
print("   ✅ Both users can now call each other")
print("   ✅ Call price: ₹20 for 10 minutes")
print("   ✅ Sufficient wallet balance")

print("\n" + "="*60)
print("HOW TO TEST")
print("="*60)
print("\n1. Open browser: http://localhost:3000")
print(f"\n2. Login as Public User:")
print(f"   Email: {demo_data['public_user']['email']}")
print(f"   Password: {demo_data['public_user']['password']}")
print("\n3. Navigate to Advocate's profile")
print("\n4. You should see:")
print("   - [📞 Call] button (ENABLED - green)")
print("   - Wallet balance: ₹100")
print("\n5. Click [📞 Call] to test:")
print("   - Payment modal will appear")
print("   - Confirm payment")
print("   - Call interface will start")
print("   - Timer will count down from 10:00")
print("\n6. After call:")
print("   - Check call history in dashboard")
print("   - Wallet balance will be ₹80")
print("\n✅ Demo accounts ready for testing!")
print("="*60 + "\n")
