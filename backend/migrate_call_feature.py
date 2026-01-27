"""
Database Migration Script for Paid Calling Feature
Initializes call_settings collection and adds wallet fields to users
"""
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["legalconnect"]

def migrate_call_feature():
    print("=" * 60)
    print("Migrating Paid Calling Feature to MongoDB")
    print("=" * 60)
    
    # 1. Create call_settings collection with default values
    print("\n1. Creating call_settings collection...")
    call_settings_col = db["call_settings"]
    
    # Check if settings already exist
    existing_settings = call_settings_col.find_one()
    if existing_settings:
        print("   ⚠️  Call settings already exist. Skipping...")
    else:
        default_settings = {
            "call_price": 20,              # ₹20 per call
            "call_duration": 10,            # 10 minutes
            "feature_enabled": True,        # Feature is enabled
            "updated_at": datetime.now(),
            "updated_by": "system"
        }
        call_settings_col.insert_one(default_settings)
        print("   ✅ Call settings created with defaults:")
        print(f"      - Price: ₹{default_settings['call_price']}")
        print(f"      - Duration: {default_settings['call_duration']} minutes")
    
    # 2. Create call_history collection (empty, will be populated on calls)
    print("\n2. Creating call_history collection...")
    call_history_col = db["call_history"]
    
    # Create indexes for efficient queries
    call_history_col.create_index("caller_id")
    call_history_col.create_index("receiver_id")
    call_history_col.create_index("started_at")
    print("   ✅ Call history collection created with indexes")
    
    # 3. Add wallet fields to existing users
    print("\n3. Adding wallet fields to users...")
    users_col = db["users"]
    
    # Update users who don't have wallet_balance
    result = users_col.update_many(
        {"wallet_balance": {"$exists": False}},
        {"$set": {
            "wallet_balance": 100,          # Initial demo balance ₹100
            "total_calls_made": 0,
            "total_calls_received": 0
        }}
    )
    
    print(f"   ✅ Updated {result.modified_count} users with wallet fields")
    print(f"      - Initial balance: ₹100")
    
    # 4. Summary
    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60)
    print("\nCollections created:")
    print("  - call_settings")
    print("  - call_history")
    print("\nUsers updated with:")
    print("  - wallet_balance: 100")
    print("  - total_calls_made: 0")
    print("  - total_calls_received: 0")
    print("\n✅ Paid calling feature database ready!")

if __name__ == "__main__":
    try:
        migrate_call_feature()
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
