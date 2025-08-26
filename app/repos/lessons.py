from typing import List, Optional
from google.cloud import firestore
from ..models.schemas import Lesson, CreateLessonRequest
from ..deps.firebase import get_db
from datetime import datetime

class LessonsRepository:
    def __init__(self):
        self.db = get_db()
        # Check if it's mock database
        if hasattr(self.db, 'create_document'):
            self.collection = None  # Mock database doesn't need collection
        else:
            self.collection = self.db.collection('lessons')
    
    async def create_lesson(self, lesson_data: CreateLessonRequest, teacher_uid: str) -> str:
        """Create a new lesson"""
        lesson_doc = {
            "student_uid": lesson_data.student_uid,
            "teacher_uid": teacher_uid,
            "lesson_date": lesson_data.lesson_date,
            "duration_minutes": lesson_data.duration_minutes,
            "topic": lesson_data.topic,
            "content_covered": lesson_data.content_covered,
            "notes": lesson_data.notes,
            "homework_assigned": lesson_data.homework_assigned,
            "student_performance": lesson_data.student_performance
        }
        
        if hasattr(self.db, 'create_document'):
            # Mock database
            return self.db.create_document('lessons', lesson_doc)
        else:
            # Firebase
            doc_ref = self.collection.document()
            lesson_doc["created_at"] = firestore.SERVER_TIMESTAMP
            doc_ref.set(lesson_doc)
            return doc_ref.id
    
    async def get_lesson(self, lesson_id: str) -> Optional[Lesson]:
        """Get lesson by ID"""
        if hasattr(self.db, 'get_document'):
            # Mock database
            data = self.db.get_document('lessons', lesson_id)
            if data:
                data['id'] = lesson_id
                data['created_at'] = datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                return Lesson(**data)
            return None
        else:
            # Firebase
            doc = self.collection.document(lesson_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = lesson_id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                return Lesson(**data)
            return None
    
    async def get_teacher_lessons(self, teacher_uid: str) -> List[Lesson]:
        """Get all lessons for a teacher"""
        if hasattr(self.db, 'get_all_documents'):
            # Mock database
            all_lessons = self.db.get_all_documents('lessons')
            lessons = []
            for data in all_lessons:
                if data.get('teacher_uid') == teacher_uid:
                    data['id'] = data.get('id', '')
                    data['created_at'] = datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                    lessons.append(Lesson(**data))
            return lessons
        else:
            # Firebase
            query = self.collection.where("teacher_uid", "==", teacher_uid).order_by("lesson_date", direction=firestore.Query.DESCENDING)
            lessons = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                lessons.append(Lesson(**data))
            
            return lessons
    
    async def get_student_lessons(self, student_uid: str) -> List[Lesson]:
        """Get all lessons for a student"""
        if hasattr(self.db, 'get_all_documents'):
            # Mock database
            all_lessons = self.db.get_all_documents('lessons')
            lessons = []
            for data in all_lessons:
                if data.get('student_uid') == student_uid:
                    data['id'] = data.get('id', '')
                    data['created_at'] = datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                    lessons.append(Lesson(**data))
            return lessons
        else:
            # Firebase
            query = self.collection.where("student_uid", "==", student_uid).order_by("lesson_date", direction=firestore.Query.DESCENDING)
            lessons = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                lessons.append(Lesson(**data))
            
            return lessons
    
    async def update_lesson(self, lesson_id: str, updates: dict) -> bool:
        """Update lesson"""
        if hasattr(self.db, 'update_document'):
            # Mock database
            try:
                self.db.update_document('lessons', lesson_id, updates)
                return True
            except Exception:
                return False
        else:
            # Firebase
            try:
                self.collection.document(lesson_id).update(updates)
                return True
            except Exception:
                return False
    
    async def delete_lesson(self, lesson_id: str) -> bool:
        """Delete lesson"""
        if hasattr(self.db, 'delete_document'):
            # Mock database
            try:
                self.db.delete_document('lessons', lesson_id)
                return True
            except Exception:
                return False
        else:
            # Firebase
            try:
                self.collection.document(lesson_id).delete()
                return True
            except Exception:
                return False
