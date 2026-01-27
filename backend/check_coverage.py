from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["legalconnect"]
collection = db["constitution_parts"]

def check_coverage():
    print("Checking Article Content Coverage...")
    
    # Aggregation to unwind articles and count
    pipeline = [
        {"$unwind": "$articles"},
        {"$project": {
            "id": "$articles.id",
            "has_content": {"$gt": [{"$strLenCP": {"$ifNull": ["$articles.content", ""]}}, 0]}
        }},
        {"$group": {
            "_id": None,
            "total_articles": {"$sum": 1},
            "filled_articles": {"$sum": {"$cond": ["$has_content", 1, 0]}}
        }}
    ]
    
    result = list(collection.aggregate(pipeline))

    with open('coverage_report.txt', 'w', encoding='utf-8') as f:
        if result:
            stats = result[0]
            total = stats['total_articles']
            filled = stats['filled_articles']
            percent = (filled / total) * 100 if total > 0 else 0
            
            f.write(f"Total Articles in DB: {total}\n")
            f.write(f"Articles with Content: {filled}\n")
            f.write(f"Coverage: {percent:.2f}%\n")
            
            if filled < total:
                f.write("\nMissing Content for Articles:\n")
                # Find which ones are empty
                empty_pipeline = [
                    {"$unwind": "$articles"},
                    {"$match": {"articles.content": {"$exists": True, "$eq": ""}}},
                    {"$limit": 50},
                    {"$project": {"_id": 0, "id": "$articles.id", "title": "$articles.title"}}
                ]
                empty = list(collection.aggregate(empty_pipeline))
                for e in empty:
                    f.write(f"- Article {e.get('id')}: {e.get('title')}\n")
        else:
            f.write("No articles found in database.\n")
            
    print("Report written to coverage_report.txt")

if __name__ == "__main__":
    check_coverage()
