"""
Script to refill wallet balance for demo accounts
"""
import json
import os

# Load users
users_file = 'users.json'
with open(users_file, 'r') as f:
    users = json.load(f)

# Demo account IDs
JOHN_ID = "69b41f73-2bbb-40ed-8899-8a098835594e"
SARAH_ID = "f5c161c5-88c3-4672-bde4-ad0eba9874f9"

# Find and update wallet balances
updated = False
for email, user_data in users.items():
    if user_data.get('id') == JOHN_ID:
        user_data['wallet_balance'] = 500  # Refill to 500
        print(f"✅ Refilled John Public's wallet: ₹500")
        updated = True
    elif user_data.get('id') == SARAH_ID:
        user_data['wallet_balance'] = 500  # Refill to 500
        print(f"✅ Refilled Sarah Advocate's wallet: ₹500")
        updated = True

if updated:
    # Save updated users
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)
    print("\n✅ Wallet balances updated successfully!")
else:
    print("❌ Demo accounts not found in users.json")
    print("Please run: python create_demo_accounts.py first")
