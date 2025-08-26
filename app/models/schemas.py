from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class UserProfile(BaseModel):
    uid: str
    role: Literal["teacher", "student", "guardian"]
    display_name: str
    email: str
    grade: Optional[int] = None
    class_ids: List[str] = []
    guardian_of: List[str] = []
    disabled: bool = False
    created_at: datetime

class CreateUserRequest(BaseModel):
    display_name: str
    email: str
    role: Literal["teacher", "student", "guardian"]
    grade: Optional[int] = None
    class_id: Optional[str] = None
    guardian_email: Optional[str] = None

class Class(BaseModel):
    id: str
    name: str
    teacher_uid: str
    grade: int
    student_uids: List[str] = []
    created_at: datetime

class CreateClassRequest(BaseModel):
    name: str
    grade: int

class QuestionSchema(BaseModel):
    type: Literal["mcq", "numeric", "short", "checkbox"]
    options: Optional[List[str]] = None
    answer: Any
    tolerance: Optional[float] = None
    keywords: Optional[List[str]] = None

class Assignment(BaseModel):
    id: str
    title: str
    class_id: str
    teacher_uid: str
    type: Literal["homework", "quiz"]
    question_files: List[Dict[str, str]] = []
    question_count: int
    answer_schema: Dict[str, QuestionSchema]
    due_at: Optional[datetime] = None
    results_visible_to_students: bool = True
    created_at: datetime

class CreateAssignmentRequest(BaseModel):
    title: str
    class_id: str
    type: Literal["homework", "quiz"]
    question_count: int
    answer_schema: Dict[str, QuestionSchema]
    due_at: Optional[datetime] = None
    results_visible_to_students: bool = True

class Submission(BaseModel):
    id: str
    assn_id: str
    student_uid: str
    answers: Dict[str, Any] = {}
    score: Optional[float] = None
    max_score: float
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    feedback: Optional[str] = None
    visible_to_student: bool = True

class SubmitAnswersRequest(BaseModel):
    answers: Dict[str, Any]
    submit: bool = False

class GameResult(BaseModel):
    game_name: str
    score: int
    max_score: int
    time_taken: int
    student_uid: str
    created_at: datetime

class AnalyticsData(BaseModel):
    student_uid: str
    scores_over_time: List[Dict[str, Any]]
    topic_mastery: Dict[str, float]
    completion_rate: float
    average_score: float