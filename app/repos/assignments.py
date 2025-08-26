from typing import List, Optional
from google.cloud import firestore
from ..models.schemas import Assignment, CreateAssignmentRequest, Submission, SubmitAnswersRequest
from ..deps.firebase import get_db
from datetime import datetime

class AssignmentsRepository:
    def __init__(self):
        self.db = get_db()
        # Check if using mock database
        if hasattr(self.db, 'create_document'):
            # Mock database
            self.collection = None
        else:
            # Firebase
            self.assignments_collection = self.db.collection('assignments')
            self.submissions_collection = self.db.collection('submissions')
    
    async def create_assignment(self, assignment_data: CreateAssignmentRequest, teacher_uid: str) -> str:
        """Create a new assignment"""
        assignment_doc = {
            "title": assignment_data.title,
            "class_id": assignment_data.class_id,
            "teacher_uid": teacher_uid,
            "type": assignment_data.type,
            "question_files": [],
            "question_count": assignment_data.question_count,
            "answer_schema": assignment_data.answer_schema.dict(),
            "due_at": assignment_data.due_at,
            "results_visible_to_students": assignment_data.results_visible_to_students,
            "created_at": datetime.now().isoformat()
        }
        
        if hasattr(self.db, 'create_document'):
            # Mock database
            return self.db.create_document('assignments', assignment_doc)
        else:
            # Firebase
            doc_ref = self.assignments_collection.document()
            assignment_doc["created_at"] = firestore.SERVER_TIMESTAMP
            doc_ref.set(assignment_doc)
            return doc_ref.id
    
    async def get_assignment(self, assignment_id: str) -> Optional[Assignment]:
        """Get assignment by ID"""
        if hasattr(self.db, 'get_document'):
            # Mock database
            data = self.db.get_document('assignments', assignment_id)
            if data:
                data['id'] = assignment_id
                return Assignment(**data)
            return None
        else:
            # Firebase
            doc = self.assignments_collection.document(assignment_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = assignment_id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                if 'due_at' in data and data['due_at']:
                    data['due_at'] = data['due_at'].replace(tzinfo=None)
                return Assignment(**data)
            return None
    
    async def get_class_assignments(self, class_id: str) -> List[Assignment]:
        """Get all assignments for a class"""
        if hasattr(self.db, 'query_documents'):
            # Mock database
            assignments_data = self.db.query_documents('assignments', 'class_id', '==', class_id)
            assignments = []
            for data in assignments_data:
                data['id'] = data.get('id', '')
                assignments.append(Assignment(**data))
            return assignments
        else:
            # Firebase
            query = self.assignments_collection.where("class_id", "==", class_id)
            assignments = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                if 'due_at' in data and data['due_at']:
                    data['due_at'] = data['due_at'].replace(tzinfo=None)
                assignments.append(Assignment(**data))
            
            return assignments
    
    async def get_teacher_assignments(self, teacher_uid: str) -> List[Assignment]:
        """Get all assignments for a teacher"""
        if hasattr(self.db, 'query_documents'):
            # Mock database
            assignments_data = self.db.query_documents('assignments', 'teacher_uid', '==', teacher_uid)
            assignments = []
            for data in assignments_data:
                data['id'] = data.get('id', '')
                assignments.append(Assignment(**data))
            return assignments
        else:
            # Firebase
            query = self.assignments_collection.where("teacher_uid", "==", teacher_uid)
            assignments = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                if 'due_at' in data and data['due_at']:
                    data['due_at'] = data['due_at'].replace(tzinfo=None)
                assignments.append(Assignment(**data))
            
            return assignments
    
    async def update_assignment(self, assignment_id: str, updates: dict) -> bool:
        """Update assignment document"""
        try:
            self.assignments_collection.document(assignment_id).update(updates)
            return True
        except Exception:
            return False
    
    async def delete_assignment(self, assignment_id: str) -> bool:
        """Delete an assignment"""
        try:
            self.assignments_collection.document(assignment_id).delete()
            return True
        except Exception:
            return False
    
    async def save_student_answers(self, assignment_id: str, student_uid: str, 
                                 answers_data: SubmitAnswersRequest, max_score: float) -> str:
        """Save or submit student answers"""
        # Check if submission already exists
        existing_submission = await self.get_student_submission(assignment_id, student_uid)
        
        if existing_submission:
            # Update existing submission
            submission_id = existing_submission.id
            updates = {
                "answers": answers_data.answers,
                "max_score": max_score
            }
            
            if answers_data.submit:
                updates["submitted_at"] = firestore.SERVER_TIMESTAMP
            else:
                updates["started_at"] = firestore.SERVER_TIMESTAMP
            
            self.submissions_collection.document(submission_id).update(updates)
            return submission_id
        else:
            # Create new submission
            doc_ref = self.submissions_collection.document()
            
            submission_doc = {
                "assn_id": assignment_id,
                "student_uid": student_uid,
                "answers": answers_data.answers,
                "score": None,
                "max_score": max_score,
                "started_at": firestore.SERVER_TIMESTAMP,
                "submitted_at": firestore.SERVER_TIMESTAMP if answers_data.submit else None,
                "feedback": None,
                "visible_to_student": True
            }
            
            doc_ref.set(submission_doc)
            return doc_ref.id
    
    async def get_student_submission(self, assignment_id: str, student_uid: str) -> Optional[Submission]:
        """Get student's submission for an assignment"""
        query = self.submissions_collection.where("assn_id", "==", assignment_id).where("student_uid", "==", student_uid)
        
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            if 'started_at' in data and data['started_at']:
                data['started_at'] = data['started_at'].replace(tzinfo=None)
            if 'submitted_at' in data and data['submitted_at']:
                data['submitted_at'] = data['submitted_at'].replace(tzinfo=None)
            return Submission(**data)
        
        return None
    
    async def get_assignment_submissions(self, assignment_id: str) -> List[Submission]:
        """Get all submissions for an assignment"""
        query = self.submissions_collection.where("assn_id", "==", assignment_id)
        submissions = []
        
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            if 'started_at' in data and data['started_at']:
                data['started_at'] = data['started_at'].replace(tzinfo=None)
            if 'submitted_at' in data and data['submitted_at']:
                data['submitted_at'] = data['submitted_at'].replace(tzinfo=None)
            submissions.append(Submission(**data))
        
        return submissions
    
    async def update_submission_score(self, submission_id: str, score: float, feedback: str) -> bool:
        """Update submission with score and feedback"""
        try:
            self.submissions_collection.document(submission_id).update({
                "score": score,
                "feedback": feedback
            })
            return True
        except Exception:
            return False
    
    async def get_student_submissions(self, student_uid: str) -> List[Submission]:
        """Get all submissions for a student"""
        query = self.submissions_collection.where("student_uid", "==", student_uid)
        submissions = []
        
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            if 'started_at' in data and data['started_at']:
                data['started_at'] = data['started_at'].replace(tzinfo=None)
            if 'submitted_at' in data and data['submitted_at']:
                data['submitted_at'] = data['submitted_at'].replace(tzinfo=None)
            submissions.append(Submission(**data))
        
        return submissions