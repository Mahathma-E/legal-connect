import firebase_admin
from firebase_admin import credentials, auth
from pymongo import MongoClient
import os
import uuid
from datetime import datetime
import bcrypt

# Setup Firebase
cred_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
cred = credentials.Certificate(cred_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Setup Mongo
client = MongoClient("mongodb://localhost:27017/")
db = client["legalconnect"]
users_col = db["users"]

TARGET_EMAIL = "vkmmahathma@gmail.com"
TARGET_PASSWORD = "admin123"
TARGET_NAME = "Admin User"

def create_admin():
    print(f"--- Processing Admin: {TARGET_EMAIL} ---")
    
    firebase_uid = None
    
    # 1. Handle Firebase User
    try:
        try:
            user_record = auth.get_user_by_email(TARGET_EMAIL)
            print(f"Firebase user found: {user_record.uid}")
            firebase_uid = user_record.uid
            
            # Update password
            auth.update_user(firebase_uid, password=TARGET_PASSWORD)
            print("Password updated in Firebase.")
            
        except auth.UserNotFoundError:
            print("Creating new Firebase user...")
            user_record = auth.create_user(
                email=TARGET_EMAIL,
                password=TARGET_PASSWORD,
                email_verified=True,
                display_name=TARGET_NAME
            )
            firebase_uid = user_record.uid
            print(f"Firebase user created: {firebase_uid}")
            
        # Set Admin Claims
        start_claims = {'role': 'admin', 'admin': True}
        auth.set_custom_user_claims(firebase_uid, start_claims)
        print("Firebase Custom Claims set to admin.")
        
    except Exception as e:
        print(f"Error handling Firebase: {e}")
        return

    # 2. Handle MongoDB User
    mongo_user = users_col.find_one({"email": TARGET_EMAIL})
    
    if mongo_user:
        print("Updating existing MongoDB user to Admin...")
        users_col.update_one(
            {"email": TARGET_EMAIL},
            {"$set": {
                "role": "admin",
                "firebaseUid": firebase_uid,
                "isVerified": True
            }}
        )
    else:
        print("Creating new MongoDB user...")
        # Hash password for legacy support (good practice even if using Firebase)
        hashed = bcrypt.hashpw(TARGET_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        new_user = {
            'id': str(uuid.uuid4()),
            'firebaseUid': firebase_uid,
            'name': TARGET_NAME,
            'email': TARGET_EMAIL,
            'password': hashed, # Legacy field
            'role': 'admin',
            'avatar': '/default-avatar.png',
            'bio': 'System Administrator',
            'followers': [],
            'following': [],
            'isVerified': True,
            'emailVerified': True,
            'createdAt': datetime.now().isoformat()
        }
        users_col.insert_one(new_user)
        print("MongoDB user created.")

    # 3. Demote other admins
    print("\n--- Updating Previous Admins ---")
    other_admins = users_col.find({"role": "admin", "email": {"$ne": TARGET_EMAIL}})
    
    count = 0
    for admin in other_admins:
        print(f"Demoting: {admin.get('email')}")
        users_col.update_one(
            {"_id": admin["_id"]},
            {"$set": {"role": "public"}} # Demote to public
        )
        
        # Also remove Firebase claim if possible (need UID)
        if admin.get('firebaseUid'):
            try:
                auth.set_custom_user_claims(admin['firebaseUid'], {'role': 'public', 'admin': False})
                print(f"Removed Firebase admin claim for {admin.get('email')}")
            except Exception as e:
                print(f"Failed to update claims for {admin.get('email')}: {e}")
        count += 1
        
    if count == 0:
        print("No previous admins to demote.")
    else:
        print(f"Demoted {count} previous admin(s).")
    
    print("\nSUCCESS: Admin transfer complete.")

if __name__ == "__main__":
    create_admin()
