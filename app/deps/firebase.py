import os
import json
import base64
from typing import Optional
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Global Firebase app instance
_firebase_app = None
_db = None
_storage_client = None

def initialize_firebase():
    global _firebase_app, _db, _storage_client
    
    if _firebase_app is not None:
        return _firebase_app
    
    try:
        # Try to get service account from environment
        service_account_b64 = os.getenv("FIREBASE_SERVICE_ACCOUNT_B64")
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        
        if service_account_b64:
            # Decode base64 service account
            service_account_json = base64.b64decode(service_account_b64).decode('utf-8')
            service_account_dict = json.loads(service_account_json)
            cred = credentials.Certificate(service_account_dict)
            
            _firebase_app = firebase_admin.initialize_app(cred, {
                'projectId': project_id or 'your-project-id',
                'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET", f"{project_id}.appspot.com")
            })
        else:
            # Try to use default credentials (for local development)
            try:
                _firebase_app = firebase_admin.initialize_app()
                print("Firebase initialized with default credentials.")
            except Exception as default_error:
                print(f"Default credentials failed: {default_error}")
                print("Firebase credentials not found. Please set FIREBASE_SERVICE_ACCOUNT_B64 environment variable.")
                _firebase_app = None
                _db = None
                _storage_client = None
                return None
        
        _db = firestore.client()
        _storage_client = storage.bucket()
        
        return _firebase_app
    
    except Exception as e:
        print(f"Firebase initialization failed: {e}")
        print("Running in development mode without Firebase.")
        _firebase_app = None
        _db = None
        _storage_client = None
        return None

def get_db():
    if _db is None:
        initialize_firebase()
    if _db is None:
        # Use mock database for development
        from .mock_db import mock_db
        return mock_db
    return _db

def get_storage():
    if _storage_client is None:
        initialize_firebase()
    if _storage_client is None:
        raise Exception("Firebase not initialized. Please set up Firebase credentials.")
    return _storage_client

# Security dependency
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        # For development, accept any token or return mock user
        if _firebase_app is None:
            # Mock user for development
            return {
                "uid": "mock_teacher_1",
                "email": "teacher@example.com",
                "role": "teacher",
                "name": "Selami ÖKTEM"
            }
        else:
            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(credentials.credentials)
            return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

async def require_teacher(user: dict = Depends(verify_token)) -> dict:
    if user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Teacher access required")
    return user

async def require_student(user: dict = Depends(verify_token)) -> dict:
    if user.get("role") != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    return user