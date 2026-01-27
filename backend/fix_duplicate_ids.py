import uuid
from collections import Counter
from mongo_helpers import posts_col

def fix_duplicate_ids():
    print("Checking for duplicate comment IDs...")
    posts = list(posts_col.find({"comments": {"$exists": True, "$not": {"$size": 0}}}))
    
    total_fixed = 0
    for post in posts:
        comments = post.get('comments', [])
        ids = [c.get('id') for c in comments if 'id' in c]
        
        counts = Counter(ids)
        duplicates = [id for id, count in counts.items() if count > 1]
        
        if not duplicates:
            continue
            
        print(f"Post {post['id']} has duplicate comment IDs: {duplicates}")
        
        # Strategy: Keep first occurrence, re-generate ID for others
        # AND update any parentId references? That's hard if we don't know which one was intended.
        # Safest: Re-generate ID for duplicates, set their parentId to None (detach to root) to avoid loops.
        
        seen_ids = set()
        has_changes = False
        
        for c in comments:
            cid = c.get('id')
            if not cid: continue
            
            if cid in seen_ids:
                # This is a duplicate!
                new_id = str(uuid.uuid4())
                print(f"  Renaming duplicate {cid} -> {new_id}")
                c['id'] = new_id
                c['parentId'] = None # Detach to be safe
                has_changes = True
            else:
                seen_ids.add(cid)
                
        if has_changes:
            posts_col.update_one(
                {"id": post['id']},
                {"$set": {"comments": comments}}
            )
            total_fixed += 1
            
    print(f"Fixed duplicate IDs in {total_fixed} posts.")

if __name__ == "__main__":
    fix_duplicate_ids()
