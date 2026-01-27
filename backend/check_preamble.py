from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient("mongodb://localhost:27017/")
db = client["legalconnect"]

def check_preamble():
    collection = db['constitution_parts']
    
    # Try to find Preamble
    # Based on frontend code: article.id === 'PREAMBLE'
    # It seems parts contain articles. 
    # Let's search for a part that contains an article with id 'PREAMBLE'
    
    pipeline = [
        {"$unwind": "$articles"},
        {"$match": {"articles.id": "PREAMBLE"}}
    ]
    
    results = list(collection.aggregate(pipeline))
    
    if results:
        print("Found Preamble:")
        print(results[0]['articles']['content'])
    else:
        print("Preamble not found via aggregation.")
        
        # List all parts to see structure
        print("\nListing Parts:")
        for part in collection.find({}, {'title': 1, 'id': 1}):
            print(f"- {part.get('title')} (ID: {part.get('id')})")

if __name__ == "__main__":
    check_preamble()
