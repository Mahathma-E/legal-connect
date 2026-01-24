"""
Complete MongoDB Migration Script for LegalConnect
Migrates ALL data from JSON files to MongoDB collections
Run this ONCE to populate the database
"""

from pymongo import MongoClient
import json
import os
from datetime import datetime

# MongoDB connection
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["legalconnect"]

# Collections
constitution_col = db["constitution_parts"]
users_col = db["users"]
posts_col = db["posts"]
conversations_col = db["conversations"]
notifications_col = db["notifications"]
reports_col = db["reports"]
verification_requests_col = db["verification_requests"]

# Get the directory where this script is located
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def migrate_constitution():
    """Migrate constitution data"""
    print("\n📜 Migrating Constitution Data...")
    try:
        constitution_col.delete_many({})
        
        json_path = os.path.join(DATA_DIR, 'constitution.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'parts' in data and len(data['parts']) > 0:
            result = constitution_col.insert_many(data['parts'])
            constitution_col.create_index("articles.id")
            constitution_col.create_index("id")
            print(f"   ✓ Migrated {len(result.inserted_ids)} constitution parts")
            return True
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def migrate_users():
    """Migrate users data"""
    print("\n👥 Migrating Users Data...")
    try:
        users_col.delete_many({})
        
        json_path = os.path.join(DATA_DIR, 'users.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert from {email: userData} to list of user documents
        users_list = []
        for email, user_data in data.items():
            # Add email as a field if not present
            if 'email' not in user_data:
                user_data['email'] = email
            users_list.append(user_data)
        
        if users_list:
            result = users_col.insert_many(users_list)
            # Create indexes for faster queries
            users_col.create_index("id", unique=True)
            users_col.create_index("email", unique=True)
            users_col.create_index("bar_code")
            print(f"   ✓ Migrated {len(result.inserted_ids)} users")
            return True
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def migrate_posts():
    """Migrate posts data"""
    print("\n📝 Migrating Posts Data...")
    try:
        posts_col.delete_many({})
        
        json_path = os.path.join(DATA_DIR, 'posts.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data and len(data) > 0:
            result = posts_col.insert_many(data)
            # Create indexes
            posts_col.create_index("id", unique=True)
            posts_col.create_index("userId")
            posts_col.create_index("timestamp")
            print(f"   ✓ Migrated {len(result.inserted_ids)} posts")
            return True
        else:
            print("   ℹ No posts to migrate")
            return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def migrate_conversations():
    """Migrate conversations data"""
    print("\n💬 Migrating Conversations Data...")
    try:
        conversations_col.delete_many({})
        
        json_path = os.path.join(DATA_DIR, 'conversations.json')
        if not os.path.exists(json_path):
            print("   ℹ No conversations.json found, skipping")
            return True
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data and len(data) > 0:
            result = conversations_col.insert_many(data)
            conversations_col.create_index("id", unique=True)
            conversations_col.create_index("users")
            print(f"   ✓ Migrated {len(result.inserted_ids)} conversations")
            return True
        else:
            print("   ℹ No conversations to migrate")
            return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def migrate_notifications():
    """Migrate notifications data"""
    print("\n🔔 Migrating Notifications Data...")
    try:
        notifications_col.delete_many({})
        
        json_path = os.path.join(DATA_DIR, 'notifications.json')
        if not os.path.exists(json_path):
            print("   ℹ No notifications.json found, skipping")
            return True
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert from {userId: [notifications]} to list of documents
        notif_list = []
        for user_id, notifications in data.items():
            for notif in notifications:
                notif_doc = {
                    'userId': user_id,
                    **notif
                }
                notif_list.append(notif_doc)
        
        if notif_list:
            result = notifications_col.insert_many(notif_list)
            notifications_col.create_index("userId")
            print(f"   ✓ Migrated {len(result.inserted_ids)} notifications")
            return True
        else:
            print("   ℹ No notifications to migrate")
            return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def migrate_reports():
    """Migrate reports data"""
    print("\n🚨 Migrating Reports Data...")
    try:
        reports_col.delete_many({})
        
        json_path = os.path.join(DATA_DIR, 'reports.json')
        if not os.path.exists(json_path):
            print("   ℹ No reports.json found, skipping")
            return True
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data and len(data) > 0:
            result = reports_col.insert_many(data)
            reports_col.create_index("postId")
            print(f"   ✓ Migrated {len(result.inserted_ids)} reports")
            return True
        else:
            print("   ℹ No reports to migrate")
            return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def migrate_verification_requests():
    """Migrate verification requests data"""
    print("\n✅ Migrating Verification Requests Data...")
    try:
        verification_requests_col.delete_many({})
        
        json_path = os.path.join(DATA_DIR, 'verification_requests.json')
        if not os.path.exists(json_path):
            print("   ℹ No verification_requests.json found, skipping")
            return True
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data and len(data) > 0:
            result = verification_requests_col.insert_many(data)
            verification_requests_col.create_index("userId")
            print(f"   ✓ Migrated {len(result.inserted_ids)} verification requests")
            return True
        else:
            print("   ℹ No verification requests to migrate")
            return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def verify_migration():
    """Verify all data was migrated successfully"""
    print("\n🔍 Verifying Migration...")
    print(f"   Constitution parts: {constitution_col.count_documents({})}")
    print(f"   Users: {users_col.count_documents({})}")
    print(f"   Posts: {posts_col.count_documents({})}")
    print(f"   Conversations: {conversations_col.count_documents({})}")
    print(f"   Notifications: {notifications_col.count_documents({})}")
    print(f"   Reports: {reports_col.count_documents({})}")
    print(f"   Verification Requests: {verification_requests_col.count_documents({})}")

if __name__ == "__main__":
    print("=" * 70)
    print("  LegalConnect - Complete MongoDB Migration")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    results.append(("Constitution", migrate_constitution()))
    results.append(("Users", migrate_users()))
    results.append(("Posts", migrate_posts()))
    results.append(("Conversations", migrate_conversations()))
    results.append(("Notifications", migrate_notifications()))
    results.append(("Reports", migrate_reports()))
    results.append(("Verification Requests", migrate_verification_requests()))
    
    verify_migration()
    
    print("\n" + "=" * 70)
    print("  Migration Summary")
    print("=" * 70)
    
    all_success = all(result[1] for result in results)
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"   {status} {name}")
    
    if all_success:
        print("\n✅ All data migrated successfully!")
        print("   MongoDB is now the single source of truth.")
        print("   JSON files are no longer needed at runtime.")
    else:
        print("\n⚠️  Some migrations failed. Please check errors above.")
    
    print("=" * 70)
