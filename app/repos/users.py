from typing import List, Optional
from google.cloud import firestore
from ..models.schemas import UserProfile, CreateUserRequest
from ..deps.firebase import get_db
from datetime import datetime

class UsersRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection('users')
    
    async def create_user(self, user_data: CreateUserRequest) -> str:
        """Create a new user in Firestore"""
        doc_ref = self.collection.document()
        
        user_doc = {
            "role": user_data.role,
            "display_name": user_data.display_name,
            "email": user_data.email,
            "grade": user_data.grade,
            "class_ids": [user_data.class_id] if user_data.class_id else [],
            "guardian_of": [],
            "disabled": False,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.set(user_doc)
        return doc_ref.id
    
    async def get_user(self, uid: str) -> Optional[UserProfile]:
        """Get user by UID"""
        doc = self.collection.document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            data['uid'] = uid
            # Convert Firestore timestamp to datetime
            if 'created_at' in data:
                data['created_at'] = data['created_at'].replace(tzinfo=None)
            return UserProfile(**data)
        return None
    
    async def update_user(self, uid: str, updates: dict) -> bool:
        """Update user document"""
        try:
            self.collection.document(uid).update(updates)
            return True
        except Exception:
            return False
    
    async def get_students_in_class(self, class_id: str) -> List[UserProfile]:
        """Get all students in a specific class"""
        query = self.collection.where("role", "==", "student").where("class_ids", "array_contains", class_id)
        students = []
        
        for doc in query.stream():
            data = doc.to_dict()
            data['uid'] = doc.id
            if 'created_at' in data:
                data['created_at'] = data['created_at'].replace(tzinfo=None)
            students.append(UserProfile(**data))
        
        return students
    
    async def add_student_to_class(self, student_uid: str, class_id: str) -> bool:
        """Add student to a class"""
        try:
            student_ref = self.collection.document(student_uid)
            student_ref.update({
                "class_ids": firestore.ArrayUnion([class_id])
            })
            return True
        except Exception:
            return False
    
    async def remove_student_from_class(self, student_uid: str, class_id: str) -> bool:
        """Remove student from a class"""
        try:
            student_ref = self.collection.document(student_uid)
            student_ref.update({
                "class_ids": firestore.ArrayRemove([class_id])
            })
            return True
        except Exception:
            return False
    
    async def bulk_create_students(self, students_data: List[dict], class_id: str) -> List[str]:
        """Bulk create students from CSV data"""
        created_uids = []
        batch = self.db.batch()
        
        for student_data in students_data:
            doc_ref = self.collection.document()
            user_doc = {
                "role": "student",
                "display_name": student_data.get("name", ""),
                "email": student_data.get("email", ""),
                "grade": int(student_data.get("grade", 5)),
                "class_ids": [class_id],
                "guardian_of": [],
                "disabled": False,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            batch.set(doc_ref, user_doc)
            created_uids.append(doc_ref.id)
        
        batch.commit()
        return created_uids