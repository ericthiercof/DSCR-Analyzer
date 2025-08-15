import os
import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    """Initialize Firebase with appropriate credentials"""
    if not firebase_admin._apps:
        try:
            # Try to use firebase_key.json if it exists
            if os.path.exists("firebase_key.json"):
                cred = credentials.Certificate("firebase_key.json")
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized with firebase_key.json")
            else:
                # Use default credentials (this will work in many cloud environments)
                firebase_admin.initialize_app()
                print("✅ Firebase initialized with default credentials")
            return True
        except Exception as e:
            print(f"⚠️ Firebase initialization failed: {e}")
            print("📝 Note: Some features requiring Firebase will not work")
            return False
    return True

def get_firestore_client():
    """Get Firestore client or None if unavailable"""
    try:
        initialize_firebase()
        db = firestore.client()
        print("✅ Firestore client initialized")
        return db
    except Exception as e:
        print(f"⚠️ Firestore client initialization failed: {e}")
        return None