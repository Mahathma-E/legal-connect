from pymongo import MongoClient
import json
import os

client = MongoClient("mongodb://localhost:27017/")
db = client["legalconnect"]
collection = db["constitution_parts"]

def update_all_articles():
    print("Loading data from civic_tech_coi.json...")
    try:
        with open('civic_tech_coi.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Loaded {len(data)} items. Starting update...")
        
        updated_count = 0
        not_found_count = 0
        
        for item in data:
            article_id = str(item.get('article'))
            content = item.get('description', '')
            title = item.get('title', '')
            
            # Skip Preamble if it's article 0 (we handled it separately, but updating again is harmless if ID matches)
            # My Preamble ID might be "PREAMBLE" not "0".
            if article_id == "0":
                article_id = "PREAMBLE"
            
            # Clean content slightly if needed (optional)
            # content = content.replace('\u00a0', ' ') 
            
            result = collection.update_one(
                {"articles.id": article_id},
                {"$set": {
                    "articles.$[elem].content": content,
                    # Optionally update title too if it's better
                    # "articles.$[elem].title": title 
                }},
                array_filters=[{"elem.id": article_id}]
            )
            
            if result.modified_count > 0:
                print(f"✓ Updated Article {article_id}")
                updated_count += 1
            elif result.matched_count > 0:
                # print(f"- Article {article_id} already up to date")
                pass
            else:
                print(f"✗ Article {article_id} NOT FOUND in DB (Title: {title})")
                not_found_count += 1
                
        print("\n" + "="*50)
        print(f"Update Complete.")
        print(f"Total processed: {len(data)}")
        print(f"Successfully updated: {updated_count}")
        print(f"Not found in DB Structure: {not_found_count}")
        print("="*50)
        
    except FileNotFoundError:
        print("Error: civic_tech_coi.json not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_all_articles()
