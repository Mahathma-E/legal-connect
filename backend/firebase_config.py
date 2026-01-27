"""
Firebase Admin SDK configuration for LegalConnect backend
Handles Firebase authentication token verification
"""

import firebase_admin
from firebase_admin import credentials, auth
import os

# Initialize Firebase Admin SDK
cred_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
cred = credentials.Certificate(cred_path)

# Check if already initialized to prevent errors on reload
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

def verify_firebase_token(id_token):
    """
    Verify Firebase ID token
    
    Args:
        id_token: Firebase ID token from client
        
    Returns:
        tuple: (decoded_token_dict, error_message_str)
        If valid: (token_dict, None)
        If invalid: (None, error_message)
    """
    try:
        # Allow 5 seconds of clock skew to prevent "Token used too early" errors
        decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=5)
        return decoded_token, None
    except Exception as e:
        error_msg = str(e)
        print(f"[FIREBASE] Token verification failed: {error_msg}", flush=True)
        return None, error_msg

def get_user_by_email(email):
    """
    Get Firebase user by email
    
    Args:
        email: User's email address
        
    Returns:
        Firebase user record if found, None otherwise
    """
    try:
        user = auth.get_user_by_email(email)
        return user
    except Exception as e:
        print(f"[FIREBASE] User not found: {e}")
        return None

def get_user_by_uid(uid):
    """
    Get Firebase user by UID
    
    Args:
        uid: Firebase user UID
        
    Returns:
        Firebase user record if found, None otherwise
    """
    try:
        user = auth.get_user(uid)
        return user
    except Exception as e:
        print(f"[FIREBASE] User not found: {e}")
        return None

def set_custom_claims(uid, claims):
    """
    Set custom claims for a user (for roles)
    
    Args:
        uid: Firebase user UID
        claims: Dict of custom claims (e.g., {'role': 'lawyer', 'verified': True})
    """
    try:
        auth.set_custom_user_claims(uid, claims)
        print(f"[FIREBASE] Custom claims set for user {uid}: {claims}")
        return True
    except Exception as e:
        print(f"[FIREBASE] Failed to set custom claims: {e}")
        return False
