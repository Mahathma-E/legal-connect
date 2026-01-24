"""
MongoDB Migration Script for Constitution Data
This script loads constitution.json data into MongoDB
Run this once to populate the database
"""

from pymongo import MongoClient
import json
import os

# MongoDB connection
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["legalconnect"]
constitution_col = db["constitution_parts"]

# Get the directory where this script is located
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def migrate_constitution_data():
    """
    Migrate constitution data from JSON file to MongoDB
    """
    try:
        # Clear existing data to avoid duplicates
        print("Clearing existing constitution data...")
        constitution_col.delete_many({})
        
        # Read constitution.json with UTF-8 encoding
        json_path = os.path.join(DATA_DIR, 'constitution.json')
        print(f"Reading constitution data from: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Insert constitution parts into MongoDB
        if 'parts' in data and len(data['parts']) > 0:
            print(f"Inserting {len(data['parts'])} constitution parts...")
            result = constitution_col.insert_many(data['parts'])
            print(f"✓ Successfully inserted {len(result.inserted_ids)} documents")
            
            # Create index on article IDs for faster queries
            print("Creating indexes...")
            constitution_col.create_index("articles.id")
            constitution_col.create_index("id")
            print("✓ Indexes created")
            
            return True
        else:
            print("✗ No constitution parts found in JSON file")
            return False
            
    except FileNotFoundError:
        print(f"✗ Error: constitution.json not found at {json_path}")
        return False
    except Exception as e:
        print(f"✗ Error during migration: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Constitution Data Migration to MongoDB")
    print("=" * 50)
    
    success = migrate_constitution_data()
    
    if success:
        # Verify the data
        count = constitution_col.count_documents({})
        print(f"\n✓ Migration completed successfully!")
        print(f"Total documents in database: {count}")
        
        # Show sample article
        sample = constitution_col.find_one({"articles.id": "23"})
        if sample:
            print(f"\nSample verification - Found Part: {sample.get('title', 'Unknown')}")
            for article in sample.get('articles', []):
                if article.get('id') == '23':
                    print(f"Article 23: {article.get('title', 'No title')}")
    else:
        print("\n✗ Migration failed. Please check the errors above.")
    
    print("=" * 50)
