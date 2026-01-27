"""
Script to delete all posts from MongoDB
"""
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['legalconnect']
posts_col = db['posts']

# Count posts before deletion
count_before = posts_col.count_documents({})
print(f"📊 Total posts before deletion: {count_before}")

if count_before == 0:
    print("✅ No posts to delete!")
else:
    # Confirm deletion
    print(f"\n⚠️  About to delete {count_before} posts from MongoDB")
    confirm = input("Type 'YES' to confirm deletion: ")
    
    if confirm == 'YES':
        # Delete all posts
        result = posts_col.delete_many({})
        print(f"\n✅ Successfully deleted {result.deleted_count} posts!")
        
        # Verify deletion
        count_after = posts_col.count_documents({})
        print(f"📊 Total posts after deletion: {count_after}")
    else:
        print("\n❌ Deletion cancelled")

client.close()
