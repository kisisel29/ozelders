from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..deps.firebase import require_student
from ..models.schemas import (
    Assignment, Submission, SubmitAnswersRequest, Lesson, 
    IndividualAssignment, StudentTeacherRelation, CreateStudentTeacherRelationRequest
)
from ..repos.assignments import AssignmentsRepository
from ..repos.classes import ClassesRepository
from ..repos.lessons import LessonsRepository
from ..repos.individual_assignments import IndividualAssignmentsRepository
from ..repos.student_teacher_relations import StudentTeacherRelationsRepository
from ..repos.users import UsersRepository
from ..services.scoring import ScoringService

router = APIRouter()

@router.get("/assignments", response_model=List[Assignment])
async def get_student_assignments(student: dict = Depends(require_student)):
    """Get all assignments for the student's classes"""
    classes_repo = ClassesRepository()
    assignments_repo = AssignmentsRepository()
    
    # Get student's classes
    student_classes = await classes_repo.get_student_classes(student['uid'])
    
    all_assignments = []
    for class_obj in student_classes:
        class_assignments = await assignments_repo.get_class_assignments(class_obj.id)
        all_assignments.extend(class_assignments)
    
    return all_assignments

@router.get("/assignments/{assignment_id}")
async def get_assignment_detail(assignment_id: str, student: dict = Depends(require_student)):
    """Get assignment detail with student's submission status"""
    assignments_repo = AssignmentsRepository()
    
    assignment = await assignments_repo.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Get student's submission if it exists
    submission = await assignments_repo.get_student_submission(assignment_id, student['uid'])
    
    return {
        "assignment": assignment.dict(),
        "submission": submission.dict() if submission else None
    }

@router.post("/assignments/{assignment_id}/submit")
async def submit_assignment_answers(
    assignment_id: str,
    answers_data: SubmitAnswersRequest,
    student: dict = Depends(require_student)
):
    """Save or submit student answers"""
    assignments_repo = AssignmentsRepository()
    
    # Get assignment to validate and get answer schema
    assignment = await assignments_repo.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    try:
        # Calculate max score
        max_score = float(len(assignment.answer_schema))
        
        # Save answers
        submission_id = await assignments_repo.save_student_answers(
            assignment_id, 
            student['uid'], 
            answers_data,
            max_score
        )
        
        # If submitting (not just saving), calculate score
        score = None
        feedback = None
        
        if answers_data.submit:
            score, breakdown = ScoringService.score_submission(
                answers_data.answers, 
                assignment.answer_schema
            )
            
            feedback = ScoringService.generate_feedback(breakdown, score, max_score)
            
            # Update submission with score and feedback
            await assignments_repo.update_submission_score(submission_id, score, feedback)
        
        return {
            "message": "Cevaplar kaydedildi!" if not answers_data.submit else "Ödev teslim edildi!",
            "submission_id": submission_id,
            "score": score,
            "feedback": feedback if assignment.results_visible_to_students else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to submit answers: {str(e)}")

@router.get("/submissions")
async def get_student_submissions(student: dict = Depends(require_student)):
    """Get all submissions for the student"""
    # This would require a more complex query or different data structure
    # For now, we'll get assignments and check for submissions
    assignments_repo = AssignmentsRepository()
    classes_repo = ClassesRepository()
    
    # Get student's classes
    student_classes = await classes_repo.get_student_classes(student['uid'])
    
    all_submissions = []
    for class_obj in student_classes:
        class_assignments = await assignments_repo.get_class_assignments(class_obj.id)
        
        for assignment in class_assignments:
            submission = await assignments_repo.get_student_submission(assignment.id, student['uid'])
            if submission and submission.visible_to_student:
                all_submissions.append({
                    "assignment": assignment.dict(),
                    "submission": submission.dict()
                })
    
    return all_submissions

# Öğrenci İzleme Sistemi Endpoint'leri

@router.get("/teachers/available", response_model=List[dict])
async def get_available_teachers(student: dict = Depends(require_student)):
    """Get all available teachers for the student to choose from"""
    users_repo = UsersRepository()
    teachers = await users_repo.get_all_teachers()
    return teachers

@router.post("/teachers/{teacher_uid}/request")
async def request_teacher(teacher_uid: str, student: dict = Depends(require_student)):
    """Request to work with a specific teacher and update student's selected teacher"""
    relations_repo = StudentTeacherRelationsRepository()
    users_repo = UsersRepository()
    
    # Check if relation already exists
    existing_relations = await relations_repo.get_student_relations(student['uid'])
    for rel in existing_relations:
        if rel.teacher_uid == teacher_uid:
            raise HTTPException(status_code=400, detail="Request already exists for this teacher")
    
    # Create new relation request
    relation_data = CreateStudentTeacherRelationRequest(teacher_uid=teacher_uid)
    relation_id = await relations_repo.create_relation(relation_data, student['uid'])
    
    # Update student's selected_teacher_uid
    await users_repo.update_user(student['uid'], {'selected_teacher_uid': teacher_uid})
    
    return {"message": "Teacher request sent successfully", "relation_id": relation_id}

@router.get("/teachers/my-teachers", response_model=List[dict])
async def get_my_teachers(student: dict = Depends(require_student)):
    """Get all teachers who have accepted relations with the student"""
    relations_repo = StudentTeacherRelationsRepository()
    teacher_uids = await relations_repo.get_accepted_teachers_for_student(student['uid'])
    
    users_repo = UsersRepository()
    teachers = []
    for uid in teacher_uids:
        user = await users_repo.get_user(uid)
        if user:
            teachers.append({
                'uid': user.uid,
                'display_name': user.display_name,
                'email': user.email
            })
    
    return teachers

@router.get("/teachers/pending-requests", response_model=List[StudentTeacherRelation])
async def get_pending_requests(student: dict = Depends(require_student)):
    """Get all pending teacher requests for the student"""
    relations_repo = StudentTeacherRelationsRepository()
    relations = await relations_repo.get_student_relations(student['uid'])
    return [rel for rel in relations if rel.status == "pending"]

# Ders Takip Sistemi

@router.get("/lessons", response_model=List[Lesson])
async def get_my_lessons(student: dict = Depends(require_student)):
    """Get all lessons for the student"""
    lessons_repo = LessonsRepository()
    return await lessons_repo.get_student_lessons(student['uid'])

@router.get("/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson_detail(lesson_id: str, student: dict = Depends(require_student)):
    """Get lesson details"""
    lessons_repo = LessonsRepository()
    lesson = await lessons_repo.get_lesson(lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    if lesson.student_uid != student['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return lesson

# Bireysel Ödev Sistemi

@router.get("/individual-assignments", response_model=List[IndividualAssignment])
async def get_my_individual_assignments(student: dict = Depends(require_student)):
    """Get all individual assignments for the student"""
    individual_assignments_repo = IndividualAssignmentsRepository()
    return await individual_assignments_repo.get_student_assignments(student['uid'])

@router.get("/individual-assignments/{assignment_id}", response_model=IndividualAssignment)
async def get_individual_assignment_detail(assignment_id: str, student: dict = Depends(require_student)):
    """Get individual assignment details"""
    individual_assignments_repo = IndividualAssignmentsRepository()
    assignment = await individual_assignments_repo.get_assignment(assignment_id)
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Individual assignment not found")
    
    if assignment.student_uid != student['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return assignment