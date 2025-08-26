from typing import List, Optional
from google.cloud import firestore
from ..models.schemas import Class, CreateClassRequest
from ..deps.firebase import get_db
from datetime import datetime

class ClassesRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.collection('classes')
    
    async def create_class(self, class_data: CreateClassRequest, teacher_uid: str) -> str:
        """Create a new class"""
        doc_ref = self.collection.document()
        
        class_doc = {
            "name": class_data.name,
            "teacher_uid": teacher_uid,
            "grade": class_data.grade,
            "student_uids": [],
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.set(class_doc)
        return doc_ref.id
    
    async def get_class(self, class_id: str) -> Optional[Class]:
        """Get class by ID"""
        doc = self.collection.document(class_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = class_id
            if 'created_at' in data:
                data['created_at'] = data['created_at'].replace(tzinfo=None)
            return Class(**data)
        return None
    
    async def get_teacher_classes(self, teacher_uid: str) -> List[Class]:
        """Get all classes for a teacher"""
        query = self.collection.where("teacher_uid", "==", teacher_uid)
        classes = []
        
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            if 'created_at' in data:
                data['created_at'] = data['created_at'].replace(tzinfo=None)
            classes.append(Class(**data))
        
        return classes
    
    async def get_student_classes(self, student_uid: str) -> List[Class]:
        """Get all classes for a student"""
        query = self.collection.where("student_uids", "array_contains", student_uid)
        classes = []
        
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            if 'created_at' in data:
                data['created_at'] = data['created_at'].replace(tzinfo=None)
            classes.append(Class(**data))
        
        return classes
    
    async def add_student_to_class(self, class_id: str, student_uid: str) -> bool:
        """Add student to a class"""
        try:
            class_ref = self.collection.document(class_id)
            class_ref.update({
                "student_uids": firestore.ArrayUnion([student_uid])
            })
            return True
        except Exception:
            return False
    
    async def remove_student_from_class(self, class_id: str, student_uid: str) -> bool:
        """Remove student from a class"""
        try:
            class_ref = self.collection.document(class_id)
            class_ref.update({
                "student_uids": firestore.ArrayRemove([student_uid])
            })
            return True
        except Exception:
            return False
    
    async def update_class(self, class_id: str, updates: dict) -> bool:
        """Update class document"""
        try:
            self.collection.document(class_id).update(updates)
            return True
        except Exception:
            return False
    
    async def delete_class(self, class_id: str) -> bool:
        """Delete a class"""
        try:
            self.collection.document(class_id).delete()
            return True
        except Exception:
            return False