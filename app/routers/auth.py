from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import auth
from ..deps.firebase import verify_token
from ..models.schemas import UserProfile
from ..repos.users import UsersRepository
import jwt
import datetime

router = APIRouter()

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "96429642"
# Teacher credentials
TEACHER_USERNAME = "Selami"
TEACHER_PASSWORD = "96429642"
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable

@router.post("/bootstrap")
async def bootstrap_user(user: dict = Depends(verify_token)):
    """
    Bootstrap user session - verify token and return user profile
    """
    try:
        users_repo = UsersRepository()
        
        # Get user profile from Firestore
        user_profile = await users_repo.get_user(user['uid'])
        
        if not user_profile:
            # Check if this is a known teacher email
            teacher_emails = [
                "selami@system.com",  # Add known teacher emails here
                "selami.oktem@gmail.com",
                "selami.oktem@hotmail.com"
            ]
            
            # Determine role based on email
            user_email = user.get('email', '').lower()
            if user_email in teacher_emails or 'selami' in user_email:
                default_role = "teacher"
            else:
                default_role = "student"
            
            # Create basic profile if doesn't exist
            basic_profile = {
                "role": default_role,
                "display_name": user.get('name', user.get('email', 'User')),
                "email": user.get('email', ''),
                "grade": None,
                "class_ids": [],
                "guardian_of": [],
                "disabled": False
            }
            
            # Set custom claims for role-based access
            auth.set_custom_user_claims(user['uid'], {"role": default_role})
            
            return {
                "user": basic_profile,
                "token_valid": True
            }
        
        return {
            "user": user_profile.dict(),
            "token_valid": True
        }
    
    except Exception as e:
        # If Firebase is not available, return a default teacher profile
        print(f"Bootstrap error: {e}")
        return {
            "user": {
                "role": "teacher",
                "display_name": user.get('name', user.get('email', 'User')),
                "email": user.get('email', ''),
                "grade": None,
                "class_ids": [],
                "guardian_of": [],
                "disabled": False
            },
            "token_valid": True
        }

@router.post("/set-role/{user_uid}")
async def set_user_role(user_uid: str, role: str, admin_user: dict = Depends(verify_token)):
    """
    Set custom claims for a user (admin only)
    """
    # Check if admin user is teacher
    if admin_user.get('role') != 'teacher':
        raise HTTPException(status_code=403, detail="Only teachers can set user roles")
    
    try:
        # Set custom claims
        auth.set_custom_user_claims(user_uid, {"role": role})
        
        # Update user document
        users_repo = UsersRepository()
        await users_repo.update_user(user_uid, {"role": role})
        
        return {"message": f"Role set to {role} for user {user_uid}"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to set role: {str(e)}")

@router.post("/admin-login")
async def admin_login(username: str, password: str):
    """
    Admin login endpoint
    """
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Create JWT token for admin
        payload = {
            "username": username,
            "role": "admin",
            "uid": "admin",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        return {
            "token": token,
            "user": {
                "uid": "admin",
                "role": "admin",
                "display_name": "Admin",
                "email": "admin@system.com"
            },
            "message": "Admin girişi başarılı"
        }
    elif username == TEACHER_USERNAME and password == TEACHER_PASSWORD:
        # Create JWT token for teacher
        payload = {
            "username": username,
            "role": "teacher",
            "uid": "teacher_selami",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        return {
            "token": token,
            "user": {
                "uid": "teacher_selami",
                "role": "teacher",
                "display_name": "Selami ÖKTEM",
                "email": "selami@system.com"
            },
            "message": "Öğretmen girişi başarılı"
        }
    else:
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre")

@router.get("/admin-dashboard")
async def admin_dashboard():
    """
    Admin dashboard data endpoint
    """
    # Mock data for now - in real implementation, fetch from database
    stats = {
        "total_students": 150,
        "total_classes": 12,
        "total_assignments": 45,
        "active_teachers": 8
    }
    
    activities = [
        {
            "description": "Yeni öğrenci kaydı: Ahmet Yılmaz",
            "timestamp": datetime.datetime.now() - datetime.timedelta(minutes=30)
        },
        {
            "description": "Yeni ödev oluşturuldu: Kesirler Quiz 1",
            "timestamp": datetime.datetime.now() - datetime.timedelta(hours=2)
        },
        {
            "description": "Sınıf oluşturuldu: 6-A Matematik",
            "timestamp": datetime.datetime.now() - datetime.timedelta(hours=5)
        },
        {
            "description": "Öğretmen girişi: Ayşe Demir",
            "timestamp": datetime.datetime.now() - datetime.timedelta(hours=8)
        }
    ]
    
    return {
        "stats": stats,
        "recent_activities": activities
    }