from typing import List, Optional
from google.cloud import firestore
from ..models.schemas import UserProfile, CreateUserRequest
from ..deps.firebase import get_db
from datetime import datetime

class UsersRepository:
    def __init__(self):
        self.db = get_db()
        # Check if it's mock database
        if hasattr(self.db, 'create_document'):
            self.collection = None  # Mock database doesn't need collection
        else:
            self.collection = self.db.collection('users')
    
    async def create_user(self, user_data: CreateUserRequest) -> str:
        """Create a new user in Firestore"""
        user_doc = {
            "role": user_data.role,
            "display_name": user_data.display_name,
            "email": user_data.email,
            "grade": user_data.grade,
            "class_ids": [user_data.class_id] if user_data.class_id else [],
            "guardian_of": [],
            "disabled": False
        }
        
        if hasattr(self.db, 'create_document'):
            # Mock database
            return self.db.create_document('users', user_doc)
        else:
            # Firebase
            doc_ref = self.collection.document()
            user_doc["created_at"] = firestore.SERVER_TIMESTAMP
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
        if hasattr(self.db, 'query_documents'):
            # Mock database - get all students first, then filter
            all_users = self.db.get_all_documents('users')
            students = []
            for data in all_users:
                if (data.get('role') == 'student' and 
                    'class_ids' in data and 
                    class_id in data.get('class_ids', [])):
                    # Convert mock database format to UserProfile format
                    student_data = {
                        'uid': data.get('id', ''),
                        'display_name': data.get('display_name', ''),
                        'email': data.get('email', ''),
                        'grade': data.get('grade', 5),
                        'role': data.get('role', 'student'),
                        'class_ids': data.get('class_ids', []),
                        'guardian_of': data.get('guardian_of', []),
                        'disabled': data.get('disabled', False),
                        'created_at': datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                    }
                    students.append(UserProfile(**student_data))
            return students
        else:
            # Firebase
            query = self.collection.where("role", "==", "student").where("class_ids", "array_contains", class_id)
            students = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['uid'] = doc.id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                students.append(UserProfile(**data))
            
            return students
    
    async def get_available_students(self) -> List[UserProfile]:
        """Get all available students (not in any class)"""
        if hasattr(self.db, 'get_all_documents'):
            # Mock database - get all students first, then filter
            all_users = self.db.get_all_documents('users')
            students = []
            for data in all_users:
                if (data.get('role') == 'student' and 
                    (not data.get('class_ids') or len(data.get('class_ids', [])) == 0)):
                    # Convert mock database format to UserProfile format
                    student_data = {
                        'uid': data.get('id', ''),
                        'display_name': data.get('display_name', ''),
                        'email': data.get('email', ''),
                        'grade': data.get('grade', 5),
                        'role': data.get('role', 'student'),
                        'class_ids': data.get('class_ids', []),
                        'guardian_of': data.get('guardian_of', []),
                        'disabled': data.get('disabled', False),
                        'created_at': datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                    }
                    students.append(UserProfile(**student_data))
            return students
        else:
            # Firebase - get all students, then filter those not in any class
            query = self.collection.where("role", "==", "student")
            students = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['uid'] = doc.id
                # Only include students not in any class
                if not data.get('class_ids') or len(data.get('class_ids', [])) == 0:
                    if 'created_at' in data:
                        data['created_at'] = data['created_at'].replace(tzinfo=None)
                    students.append(UserProfile(**data))
            
            return students
    
    async def add_student_to_class(self, student_uid: str, class_id: str) -> bool:
        """Add student to a class"""
        if hasattr(self.db, 'update_document'):
            # Mock database
            try:
                student_data = self.db.get_document('users', student_uid)
                if student_data:
                    current_class_ids = student_data.get('class_ids', [])
                    if class_id not in current_class_ids:
                        current_class_ids.append(class_id)
                        self.db.update_document('users', student_uid, {'class_ids': current_class_ids})
                    return True
                return False
            except Exception:
                return False
        else:
            # Firebase
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
        if hasattr(self.db, 'update_document'):
            # Mock database
            try:
                student_data = self.db.get_document('users', student_uid)
                if student_data:
                    current_class_ids = student_data.get('class_ids', [])
                    if class_id in current_class_ids:
                        current_class_ids.remove(class_id)
                        self.db.update_document('users', student_uid, {'class_ids': current_class_ids})
                    return True
                return False
            except Exception:
                return False
        else:
            # Firebase
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

    async def get_all_teachers(self) -> List[dict]:
        """Get all teachers with basic information"""
        if hasattr(self.db, 'get_all_documents'):
            # Mock database
            all_users = self.db.get_all_documents('users')
            teachers = []
            for data in all_users:
                if data.get('role') == 'teacher':
                    teachers.append({
                        'uid': data.get('id', ''),
                        'display_name': data.get('display_name', ''),
                        'email': data.get('email', ''),
                        'student_count': len(data.get('student_relations', [])),
                        'experience_years': data.get('experience_years', 'Belirtilmemiş')
                    })
            return teachers
        else:
            # Firebase
            query = self.collection.where("role", "==", "teacher")
            teachers = []
            
            for doc in query.stream():
                data = doc.to_dict()
                teachers.append({
                    'uid': doc.id,
                    'display_name': data.get('display_name', ''),
                    'email': data.get('email', ''),
                    'student_count': 0,  # This would need to be calculated from relations
                    'experience_years': data.get('experience_years', 'Belirtilmemiş')
                })
            
            return teachers

    async def get_all_students(self) -> List[UserProfile]:
        """Get all students regardless of class status"""
        if hasattr(self.db, 'get_all_documents'):
            # Mock database - get all students
            all_users = self.db.get_all_documents('users')
            students = []
            for data in all_users:
                if data.get('role') == 'student':
                    # Convert mock database format to UserProfile format
                    student_data = {
                        'uid': data.get('id', ''),
                        'display_name': data.get('display_name', ''),
                        'email': data.get('email', ''),
                        'grade': data.get('grade', 5),
                        'role': data.get('role', 'student'),
                        'class_ids': data.get('class_ids', []),
                        'guardian_of': data.get('guardian_of', []),
                        'disabled': data.get('disabled', False),
                        'selected_teacher_uid': data.get('selected_teacher_uid'),
                        'level': data.get('level'),
                        'total_points': data.get('total_points', 0),
                        'created_at': datetime.fromisoformat(data.get('created_at', '').replace('Z', '+00:00'))
                    }
                    students.append(UserProfile(**student_data))
            return students
        else:
            # Firebase - get all students
            query = self.collection.where("role", "==", "student")
            students = []
            
            for doc in query.stream():
                data = doc.to_dict()
                data['uid'] = doc.id
                if 'created_at' in data:
                    data['created_at'] = data['created_at'].replace(tzinfo=None)
                students.append(UserProfile(**data))
            
            return students