"""
Migration script to add email verification fields to existing users
Auto-verifies existing users so they can continue logging in
"""

import json
import os

def migrate_users():
    """Add email verification fields to existing users and auto-verify them"""
    
    # Path to users.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    users_file = os.path.join(script_dir, 'users.json')
    
    if not os.path.exists(users_file):
        print("users.json not found. No migration needed.")
        return
    
    # Load existing users
    with open(users_file, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    # Track changes
    updated_count = 0
    
    # Update each user
    for email, user_data in users.items():
        # Check if user already has email verification fields
        if 'emailVerified' not in user_data:
            # Auto-verify existing users
            user_data['emailVerified'] = True
            user_data['emailVerificationToken'] = None
            user_data['emailVerificationExpiry'] = None
            user_data['passwordResetToken'] = None
            user_data['passwordResetExpiry'] = None
            
            updated_count += 1
            print(f"✅ Auto-verified existing user: {email}")
    
    # Save updated users
    if updated_count > 0:
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Migration complete! Updated {updated_count} users.")
        print("All existing users have been auto-verified and can log in immediately.")
        print("New users will need to verify their email addresses.")
    else:
        print("No users needed migration. All users already have email verification fields.")

if __name__ == '__main__':
    migrate_users()
