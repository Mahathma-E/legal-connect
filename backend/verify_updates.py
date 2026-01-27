from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["legalconnect"]
collection = db["constitution_parts"]

def verify():
    # Check a few random articles from different parts
    check_ids = ["51A", "100", "243", "368", "395"]
    
    print("Verifying updates for sample articles:")
    for aid in check_ids:
        # Find the document containing this article
        result = collection.find_one(
            {"articles.id": aid},
            {"articles.$": 1} 
        )
        
        if result and 'articles' in result and len(result['articles']) > 0:
            article = result['articles'][0]
            content = article.get('content', '')
            print(f"\n[Article {aid}]")
            print(f"Content Preview: {content[:100]}...")
            if len(content) > 20: 
                print("✓ Status: Content Present")
            else:
                print("✗ Status: Content Missing or Too Short")
        else:
            print(f"\n[Article {aid}]")
            print("✗ Status: NOT FOUND in DB")

if __name__ == "__main__":
    verify()
