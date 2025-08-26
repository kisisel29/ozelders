from typing import List, Optional
from google.cloud import firestore
from ..models.schemas import StudentTeacherRelation, CreateStudentTeacherRelationRequest
from ..deps.firebase import get_db
from datetime import datetime

class StudentTeacherRelationsRepository:
    def __init__(self):
        self.db = get_db()
        # Check if it's mock database
        if hasattr(self.db, 'create_document'):
            self.collection = None  # Mock database doesn't need collection
        else:
            self.collection = self.db.collection('student_teacher_relations')
    
    async def create_relation(self, relation_data: CreateStudentTeacherRelationRequest, student_uid: str) -> str:
        """Create a new student-teacher relation request"""
        relation_doc = {
            "student_uid": student_uid,
            "teacher_uid": relation_data.teacher_uid,
            "status": "pending"
        }
        
        if hasattr(self.db, 'create_document'):
            # Mock database
            return self.db.create_document('student_teacher_relations', relation_doc)
        else:
            # Firebase
            doc_ref = self.collection.document()
            relation_doc["created_at"] = firestore.SERVER_TIMESTAMP
            doc_ref.set(relation_doc)
            return doc_ref.id
    
    async def get_relation(self, relation_id: str) -> Optional[StudentTeacherRelation]:
        """Get relation by ID"""
        if hasattr(self.db, 'get_document'):
            # Mock database
            data = self.db.get_document('student_teacher_relations', relation_id)
            if data:
                data['id'] = relation_id
                data['created_at'] = datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                return StudentTeacherRelation(**data)
            return None
        else:
            # Firebase
            doc = self.collection.document(relation_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = relation_id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                return StudentTeacherRelation(**data)
            return None
    
    async def get_student_relations(self, student_uid: str) -> List[StudentTeacherRelation]:
        """Get all relations for a student"""
        if hasattr(self.db, 'get_all_documents'):
            # Mock database
            all_relations = self.db.get_all_documents('student_teacher_relations')
            relations = []
            for data in all_relations:
                if data.get('student_uid') == student_uid:
                    data['id'] = data.get('id', '')
                    data['created_at'] = datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                    relations.append(StudentTeacherRelation(**data))
            return relations
        else:
            # Firebase
            query = self.collection.where("student_uid", "==", student_uid)
            relations = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                relations.append(StudentTeacherRelation(**data))
            
            return relations
    
    async def get_teacher_relations(self, teacher_uid: str) -> List[StudentTeacherRelation]:
        """Get all relations for a teacher"""
        if hasattr(self.db, 'get_all_documents'):
            # Mock database
            all_relations = self.db.get_all_documents('student_teacher_relations')
            relations = []
            for data in all_relations:
                if data.get('teacher_uid') == teacher_uid:
                    data['id'] = data.get('id', '')
                    data['created_at'] = datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                    relations.append(StudentTeacherRelation(**data))
            return relations
        else:
            # Firebase
            query = self.collection.where("teacher_uid", "==", teacher_uid)
            relations = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                relations.append(StudentTeacherRelation(**data))
            
            return relations
    
    async def update_relation(self, relation_id: str, updates: dict) -> bool:
        """Update relation"""
        if hasattr(self.db, 'update_document'):
            # Mock database
            try:
                self.db.update_document('student_teacher_relations', relation_id, updates)
                return True
            except Exception:
                return False
        else:
            # Firebase
            try:
                self.collection.document(relation_id).update(updates)
                return True
            except Exception:
                return False
    
    async def accept_relation(self, relation_id: str) -> bool:
        """Accept a relation request"""
        updates = {
            "status": "accepted",
            "accepted_at": datetime.now()
        }
        return await self.update_relation(relation_id, updates)
    
    async def reject_relation(self, relation_id: str) -> bool:
        """Reject a relation request"""
        updates = {
            "status": "rejected"
        }
        return await self.update_relation(relation_id, updates)
    
    async def get_accepted_students_for_teacher(self, teacher_uid: str) -> List[str]:
        """Get list of student UIDs who have accepted relations with the teacher"""
        relations = await self.get_teacher_relations(teacher_uid)
        return [rel.student_uid for rel in relations if rel.status == "accepted"]
    
    async def get_accepted_teachers_for_student(self, student_uid: str) -> List[str]:
        """Get list of teacher UIDs who have accepted relations with the student"""
        relations = await self.get_student_relations(student_uid)
        return [rel.teacher_uid for rel in relations if rel.status == "accepted"]
