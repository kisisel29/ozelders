from typing import List, Optional
from google.cloud import firestore
from ..models.schemas import IndividualAssignment, CreateIndividualAssignmentRequest
from ..deps.firebase import get_db
from datetime import datetime

class IndividualAssignmentsRepository:
    def __init__(self):
        self.db = get_db()
        # Check if it's mock database
        if hasattr(self.db, 'create_document'):
            self.collection = None  # Mock database doesn't need collection
        else:
            self.collection = self.db.collection('individual_assignments')
    
    async def create_assignment(self, assignment_data: CreateIndividualAssignmentRequest, teacher_uid: str) -> str:
        """Create a new individual assignment"""
        assignment_doc = {
            "title": assignment_data.title,
            "student_uid": assignment_data.student_uid,
            "teacher_uid": teacher_uid,
            "description": assignment_data.description,
            "due_date": assignment_data.due_date,
            "status": "assigned",
            "max_score": assignment_data.max_score
        }
        
        if hasattr(self.db, 'create_document'):
            # Mock database
            return self.db.create_document('individual_assignments', assignment_doc)
        else:
            # Firebase
            doc_ref = self.collection.document()
            assignment_doc["created_at"] = firestore.SERVER_TIMESTAMP
            doc_ref.set(assignment_doc)
            return doc_ref.id
    
    async def get_assignment(self, assignment_id: str) -> Optional[IndividualAssignment]:
        """Get assignment by ID"""
        if hasattr(self.db, 'get_document'):
            # Mock database
            data = self.db.get_document('individual_assignments', assignment_id)
            if data:
                data['id'] = assignment_id
                data['created_at'] = datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                return IndividualAssignment(**data)
            return None
        else:
            # Firebase
            doc = self.collection.document(assignment_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = assignment_id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                return IndividualAssignment(**data)
            return None
    
    async def get_teacher_assignments(self, teacher_uid: str) -> List[IndividualAssignment]:
        """Get all assignments created by a teacher"""
        if hasattr(self.db, 'get_all_documents'):
            # Mock database
            all_assignments = self.db.get_all_documents('individual_assignments')
            assignments = []
            for data in all_assignments:
                if data.get('teacher_uid') == teacher_uid:
                    data['id'] = data.get('id', '')
                    data['created_at'] = datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                    assignments.append(IndividualAssignment(**data))
            return assignments
        else:
            # Firebase
            query = self.collection.where("teacher_uid", "==", teacher_uid).order_by("created_at", direction=firestore.Query.DESCENDING)
            assignments = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                assignments.append(IndividualAssignment(**data))
            
            return assignments
    
    async def get_student_assignments(self, student_uid: str) -> List[IndividualAssignment]:
        """Get all assignments for a student"""
        if hasattr(self.db, 'get_all_documents'):
            # Mock database
            all_assignments = self.db.get_all_documents('individual_assignments')
            assignments = []
            for data in all_assignments:
                if data.get('student_uid') == student_uid:
                    data['id'] = data.get('id', '')
                    data['created_at'] = datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                    assignments.append(IndividualAssignment(**data))
            return assignments
        else:
            # Firebase
            query = self.collection.where("student_uid", "==", student_uid).order_by("created_at", direction=firestore.Query.DESCENDING)
            assignments = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                assignments.append(IndividualAssignment(**data))
            
            return assignments
    
    async def update_assignment(self, assignment_id: str, updates: dict) -> bool:
        """Update assignment"""
        if hasattr(self.db, 'update_document'):
            # Mock database
            try:
                self.db.update_document('individual_assignments', assignment_id, updates)
                return True
            except Exception:
                return False
        else:
            # Firebase
            try:
                self.collection.document(assignment_id).update(updates)
                return True
            except Exception:
                return False
    
    async def delete_assignment(self, assignment_id: str) -> bool:
        """Delete assignment"""
        if hasattr(self.db, 'delete_document'):
            # Mock database
            try:
                self.db.delete_document('individual_assignments', assignment_id)
                return True
            except Exception:
                return False
        else:
            # Firebase
            try:
                self.collection.document(assignment_id).delete()
                return True
            except Exception:
                return False
    
    async def submit_assignment(self, assignment_id: str, score: float, feedback: Optional[str] = None) -> bool:
        """Submit assignment with score and feedback"""
        updates = {
            "status": "completed",
            "score": score,
            "feedback": feedback,
            "completed_at": datetime.now()
        }
        return await self.update_assignment(assignment_id, updates)
