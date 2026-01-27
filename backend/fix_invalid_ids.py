import uuid
from mongo_helpers import posts_col

def fix_invalid_ids():
    print("Checking for null/invalid comment IDs...")
    posts = list(posts_col.find({"comments": {"$exists": True, "$not": {"$size": 0}}}))
    
    total_fixed = 0
    for post in posts:
        has_changes = False
        updated_comments = []
        for c in post.get('comments', []):
            cid = c.get('id')
            
            # Check if ID is None, empty, or not a string
            if not cid or not isinstance(cid, str):
                new_id = str(uuid.uuid4())
                print(f"Fixing invalid ID '{cid}' -> '{new_id}' in post {post['id']}")
                c['id'] = new_id
                c['parentId'] = None # Reset parent to be safe
                has_changes = True
            
            updated_comments.append(c)
            
        if has_changes:
            posts_col.update_one(
                {"id": post['id']},
                {"$set": {"comments": updated_comments}}
            )
            total_fixed += 1
            
    print(f"Fixed invalid IDs in {total_fixed} posts.")

if __name__ == "__main__":
    fix_invalid_ids()
