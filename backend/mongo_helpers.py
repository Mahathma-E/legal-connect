# MongoDB Helper Functions to replace JSON operations

def get_user_by_email(email):
    """Get user by email from MongoDB"""
    return users_col.find_one({"email": email}, {'_id': 0})

def get_user_by_id(user_id):
    """Get user by ID from MongoDB"""
    return users_col.find_one({"id": user_id}, {'_id': 0})

def get_user_by_email_or_barcode(email_or_bar):
    """Get user by email or bar code"""
    return users_col.find_one({
        "$or": [
            {"email": email_or_bar},
            {"bar_code": email_or_bar}
        ]
    }, {'_id': 0})

def create_user(user_data):
    """Create a new user in MongoDB"""
    users_col.insert_one(user_data)
    return user_data

def update_user(user_id, update_data):
    """Update user in MongoDB"""
    users_col.update_one(
        {"id": user_id},
        {"$set": update_data}
    )

def delete_user(user_id):
    """Delete user from MongoDB"""
    users_col.delete_one({"id": user_id})

def get_all_users():
    """Get all users from MongoDB"""
    return list(users_col.find({}, {'_id': 0}))

# Posts helpers
def get_all_posts():
    """Get all posts from MongoDB"""
    return list(posts_col.find({}, {'_id': 0}).sort("timestamp", -1))

def get_post_by_id(post_id):
    """Get post by ID"""
    return posts_col.find_one({"id": post_id}, {'_id': 0})

def create_post(post_data):
    """Create new post"""
    posts_col.insert_one(post_data)
    return post_data

def update_post(post_id, update_data):
    """Update post"""
    posts_col.update_one(
        {"id": post_id},
        {"$set": update_data}
    )

def delete_post(post_id):
    """Delete post"""
    posts_col.delete_one({"id": post_id})

def add_like_to_post(post_id, user_id):
    """Add or remove like from post"""
    post = get_post_by_id(post_id)
    if not post:
        return None
    
    if user_id in post.get('likes', []):
        posts_col.update_one(
            {"id": post_id},
            {"$pull": {"likes": user_id}}
        )
        return {"action": "unliked"}
    else:
        posts_col.update_one(
            {"id": post_id},
            {"$push": {"likes": user_id}}
        )
        return {"action": "liked"}

def add_comment_to_post(post_id, comment_data):
    """Add comment to post"""
    posts_col.update_one(
        {"id": post_id},
        {"$push": {"comments": comment_data}}
    )

def delete_comment_from_post(post_id, comment_index):
    """Delete comment from post"""
    post = get_post_by_id(post_id)
    if post and 'comments' in post and 0 <= comment_index < len(post['comments']):
        post['comments'].pop(comment_index)
        posts_col.update_one(
            {"id": post_id},
            {"$set": {"comments": post['comments']}}
        )
        return True
    return False

# Conversations helpers
def get_conversations_for_user(user_id):
    """Get all conversations for a user"""
    return list(conversations_col.find(
        {"users": user_id},
        {'_id': 0}
    ))

def get_conversation_by_id(conv_id):
    """Get conversation by ID"""
    return conversations_col.find_one({"id": conv_id}, {'_id': 0})

def create_conversation(conv_data):
    """Create new conversation"""
    conversations_col.insert_one(conv_data)
    return conv_data

def update_conversation(conv_id, update_data):
    """Update conversation"""
    conversations_col.update_one(
        {"id": conv_id},
        {"$set": update_data}
    )

def add_message_to_conversation(conv_id, message_data):
    """Add message to conversation"""
    conversations_col.update_one(
        {"id": conv_id},
        {"$push": {"messages": message_data}}
    )

# Notifications helpers
def get_notifications_for_user(user_id):
    """Get all notifications for a user"""
    return list(notifications_col.find(
        {"userId": user_id},
        {'_id': 0}
    ))

def add_notification(user_id, notif_data):
    """Add notification for a user"""
    notif_doc = {
        'userId': user_id,
        **notif_data
    }
    notifications_col.insert_one(notif_doc)

def clear_notifications_for_user(user_id):
    """Clear all notifications for a user"""
    notifications_col.delete_many({"userId": user_id})

# Reports helpers
def create_report(report_data):
    """Create a new report"""
    reports_col.insert_one(report_data)

def get_all_reports():
    """Get all reports"""
    return list(reports_col.find({}, {'_id': 0}))
