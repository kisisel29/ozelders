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
    # Yeni alanlar
    selected_teacher_uid: Optional[str] = None  # Öğrenci seçtiği öğretmen
    level: Optional[str] = None  # Öğrenci seviyesi (başlangıç, orta, ileri)
    total_points: int = 0  # Toplam puan (rekabet için)

class CreateUserRequest(BaseModel):
    display_name: str
    email: str
    role: Literal["teacher", "student", "guardian"]
    grade: Optional[int] = None
    class_id: Optional[str] = None
    guardian_email: Optional[str] = None
    selected_teacher_uid: Optional[str] = None
    level: Optional[str] = None

# Öğrenci-Öğretmen İlişkisi
class StudentTeacherRelation(BaseModel):
    id: str
    student_uid: str
    teacher_uid: str
    status: Literal["pending", "accepted", "rejected"] = "pending"
    created_at: datetime
    accepted_at: Optional[datetime] = None

class CreateStudentTeacherRelationRequest(BaseModel):
    teacher_uid: str

# Ders Takip Sistemi
class Lesson(BaseModel):
    id: str
    student_uid: str
    teacher_uid: str
    lesson_date: datetime
    duration_minutes: int
    topic: str
    content_covered: str
    notes: Optional[str] = None
    homework_assigned: Optional[str] = None
    student_performance: Optional[Literal["excellent", "good", "average", "needs_improvement"]] = None
    created_at: datetime

class CreateLessonRequest(BaseModel):
    student_uid: str
    lesson_date: datetime
    duration_minutes: int
    topic: str
    content_covered: str
    notes: Optional[str] = None
    homework_assigned: Optional[str] = None
    student_performance: Optional[Literal["excellent", "good", "average", "needs_improvement"]] = None

# Bireysel Ödev Sistemi
class IndividualAssignment(BaseModel):
    id: str
    title: str
    student_uid: str
    teacher_uid: str
    description: str
    due_date: Optional[datetime] = None
    status: Literal["assigned", "in_progress", "completed", "overdue"] = "assigned"
    score: Optional[float] = None
    max_score: float = 100
    feedback: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class CreateIndividualAssignmentRequest(BaseModel):
    student_uid: str
    title: str
    description: str
    due_date: Optional[datetime] = None
    max_score: float = 100

# Rekabet Sistemi
class Competition(BaseModel):
    id: str
    title: str
    description: str
    grade: int
    level: str  # başlangıç, orta, ileri
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int] = None
    prize_description: Optional[str] = None
    created_by: str  # teacher_uid
    status: Literal["upcoming", "active", "completed"] = "upcoming"
    created_at: datetime

class CreateCompetitionRequest(BaseModel):
    title: str
    description: str
    grade: int
    level: str
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int] = None
    prize_description: Optional[str] = None

class CompetitionParticipant(BaseModel):
    id: str
    competition_id: str
    student_uid: str
    points: int = 0
    rank: Optional[int] = None
    joined_at: datetime

# Mevcut şemalar devam ediyor...
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