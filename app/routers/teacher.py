from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import List
import csv
import io
from ..deps.firebase import require_teacher
from ..models.schemas import (
    CreateUserRequest, CreateClassRequest, CreateAssignmentRequest, 
    UserProfile, Class, Assignment, Lesson, CreateLessonRequest,
    IndividualAssignment, CreateIndividualAssignmentRequest,
    StudentTeacherRelation, CreateStudentTeacherRelationRequest
)
from ..repos.users import UsersRepository
from ..repos.classes import ClassesRepository
from ..repos.assignments import AssignmentsRepository
from ..repos.lessons import LessonsRepository
from ..repos.individual_assignments import IndividualAssignmentsRepository
from ..repos.student_teacher_relations import StudentTeacherRelationsRepository
from ..services.scoring import ScoringService

router = APIRouter()

@router.post("/users", response_model=str)
async def create_user(user_data: CreateUserRequest, teacher: dict = Depends(require_teacher)):
    """Create a new student or guardian"""
    users_repo = UsersRepository()
    
    try:
        user_id = await users_repo.create_user(user_data)
        
        # If creating a student, add to class
        if user_data.role == "student" and user_data.class_id:
            classes_repo = ClassesRepository()
            await classes_repo.add_student_to_class(user_data.class_id, user_id)
        
        return user_id
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create user: {str(e)}")

@router.post("/users/bulk-import")
async def bulk_import_students(
    class_id: str = Form(...),
    file: UploadFile = File(...),
    teacher: dict = Depends(require_teacher)
):
    """Bulk import students from CSV"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")
    
    try:
        contents = await file.read()
        csv_data = contents.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        students_data = []
        
        for row in csv_reader:
            students_data.append({
                'name': row.get('name', row.get('Name', '')),
                'email': row.get('email', row.get('Email', '')),
                'grade': int(row.get('grade', row.get('Grade', 5)))
            })
        
        users_repo = UsersRepository()
        created_ids = await users_repo.bulk_create_students(students_data, class_id)
        
        # Update class with new students
        classes_repo = ClassesRepository()
        for student_id in created_ids:
            await classes_repo.add_student_to_class(class_id, student_id)
        
        return {
            "message": f"Successfully imported {len(created_ids)} students",
            "created_ids": created_ids
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

@router.post("/classes", response_model=str)
async def create_class(class_data: CreateClassRequest, teacher: dict = Depends(require_teacher)):
    """Create a new class"""
    classes_repo = ClassesRepository()
    
    try:
        class_id = await classes_repo.create_class(class_data, teacher['uid'])
        return class_id
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create class: {str(e)}")

@router.get("/classes", response_model=List[Class])
async def get_teacher_classes(teacher: dict = Depends(require_teacher)):
    """Get all classes for the teacher"""
    classes_repo = ClassesRepository()
    return await classes_repo.get_teacher_classes(teacher['uid'])

@router.get("/classes/{class_id}", response_model=Class)
async def get_class_detail(class_id: str, teacher: dict = Depends(require_teacher)):
    """Get class details"""
    classes_repo = ClassesRepository()
    class_data = await classes_repo.get_class(class_id)
    
    if not class_data:
        raise HTTPException(status_code=404, detail="Class not found")
    
    if class_data.teacher_uid != teacher['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Add student count
    users_repo = UsersRepository()
    students = await users_repo.get_students_in_class(class_id)
    class_data.student_count = len(students)
    
    return class_data

@router.get("/classes/{class_id}/students", response_model=List[UserProfile])
async def get_class_students(class_id: str, teacher: dict = Depends(require_teacher)):
    """Get all students in a class"""
    users_repo = UsersRepository()
    return await users_repo.get_students_in_class(class_id)

@router.get("/students/available", response_model=List[UserProfile])
async def get_available_students(teacher: dict = Depends(require_teacher)):
    """Get all available students (not in any class)"""
    users_repo = UsersRepository()
    return await users_repo.get_available_students()

@router.get("/students/all", response_model=List[UserProfile])
async def get_all_students(teacher: dict = Depends(require_teacher)):
    """Get all students regardless of class status"""
    users_repo = UsersRepository()
    return await users_repo.get_all_students()

@router.post("/classes/{class_id}/students/{student_uid}")
async def add_student_to_class(class_id: str, student_uid: str, teacher: dict = Depends(require_teacher)):
    """Add a student to a class"""
    classes_repo = ClassesRepository()
    users_repo = UsersRepository()
    
    success1 = await classes_repo.add_student_to_class(class_id, student_uid)
    success2 = await users_repo.add_student_to_class(student_uid, class_id)
    
    if success1 and success2:
        return {"message": "Student added to class successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to add student to class")

@router.delete("/classes/{class_id}/students/{student_uid}")
async def remove_student_from_class(class_id: str, student_uid: str, teacher: dict = Depends(require_teacher)):
    """Remove a student from a class"""
    classes_repo = ClassesRepository()
    users_repo = UsersRepository()
    
    success1 = await classes_repo.remove_student_from_class(class_id, student_uid)
    success2 = await users_repo.remove_student_from_class(student_uid, class_id)
    
    if success1 and success2:
        return {"message": "Student removed from class successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to remove student from class")

@router.post("/assignments", response_model=str)
async def create_assignment(assignment_data: CreateAssignmentRequest, teacher: dict = Depends(require_teacher)):
    """Create a new assignment"""
    assignments_repo = AssignmentsRepository()
    
    try:
        assignment_id = await assignments_repo.create_assignment(assignment_data, teacher['uid'])
        return assignment_id
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create assignment: {str(e)}")

@router.get("/assignments", response_model=List[Assignment])
async def get_teacher_assignments(teacher: dict = Depends(require_teacher)):
    """Get all assignments for the teacher"""
    assignments_repo = AssignmentsRepository()
    return await assignments_repo.get_teacher_assignments(teacher['uid'])

@router.get("/assignments/{assignment_id}/submissions")
async def get_assignment_submissions(assignment_id: str, teacher: dict = Depends(require_teacher)):
    """Get all submissions for an assignment"""
    assignments_repo = AssignmentsRepository()
    
    # Get assignment to verify teacher ownership
    assignment = await assignments_repo.get_assignment(assignment_id)
    if not assignment or assignment.teacher_uid != teacher['uid']:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    submissions = await assignments_repo.get_assignment_submissions(assignment_id)
    
    # Auto-score submissions that haven't been scored yet
    for submission in submissions:
        if submission.score is None and submission.submitted_at:
            score, breakdown = ScoringService.score_submission(
                submission.answers, 
                assignment.answer_schema
            )
            
            feedback = ScoringService.generate_feedback(breakdown, score, submission.max_score)
            
            await assignments_repo.update_submission_score(
                submission.id, 
                score, 
                feedback
            )
            submission.score = score
            submission.feedback = feedback
    
    return {
        "assignment": assignment.dict(),
        "submissions": [s.dict() for s in submissions]
    }

@router.patch("/submissions/{submission_id}")
async def update_submission(
    submission_id: str,
    score: float = None,
    feedback: str = None,
    visible_to_student: bool = None,
    teacher: dict = Depends(require_teacher)
):
    """Update submission score, feedback, or visibility"""
    assignments_repo = AssignmentsRepository()
    
    try:
        success = True
        if score is not None or feedback is not None:
            success = await assignments_repo.update_submission_score(submission_id, score, feedback)
        
        if visible_to_student is not None:
            success = success and await assignments_repo.toggle_submission_visibility(submission_id, visible_to_student)
        
        if success:
            return {"message": "Submission updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to update submission")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

@router.post("/assignments/{assignment_id}/files")
async def update_assignment_files(
    assignment_id: str,
    file_urls: List[dict],
    teacher: dict = Depends(require_teacher)
):
    """Update assignment with uploaded file URLs"""
    assignments_repo = AssignmentsRepository()
    
    success = await assignments_repo.update_assignment_files(assignment_id, file_urls)
    
    if success:
        return {"message": "Assignment files updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to update assignment files")

# Öğrenci İzleme Sistemi Endpoint'leri

@router.get("/students/my-students", response_model=List[UserProfile])
async def get_my_students(teacher: dict = Depends(require_teacher)):
    """Get all students who have accepted relations with the teacher"""
    relations_repo = StudentTeacherRelationsRepository()
    student_uids = await relations_repo.get_accepted_students_for_teacher(teacher['uid'])
    
    users_repo = UsersRepository()
    students = []
    for uid in student_uids:
        user = await users_repo.get_user(uid)
        if user:
            students.append(user)
    
    return students

@router.get("/students/pending-requests", response_model=List[StudentTeacherRelation])
async def get_pending_requests(teacher: dict = Depends(require_teacher)):
    """Get all pending student-teacher relation requests"""
    relations_repo = StudentTeacherRelationsRepository()
    relations = await relations_repo.get_teacher_relations(teacher['uid'])
    return [rel for rel in relations if rel.status == "pending"]

@router.post("/students/{student_uid}/accept")
async def accept_student_request(student_uid: str, teacher: dict = Depends(require_teacher)):
    """Accept a student's request to work with the teacher"""
    relations_repo = StudentTeacherRelationsRepository()
    relations = await relations_repo.get_teacher_relations(teacher['uid'])
    
    # Find the pending relation for this student
    pending_relation = None
    for rel in relations:
        if rel.student_uid == student_uid and rel.status == "pending":
            pending_relation = rel
            break
    
    if not pending_relation:
        raise HTTPException(status_code=404, detail="No pending request found for this student")
    
    success = await relations_repo.accept_relation(pending_relation.id)
    if success:
        return {"message": "Student request accepted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to accept student request")

@router.post("/students/{student_uid}/reject")
async def reject_student_request(student_uid: str, teacher: dict = Depends(require_teacher)):
    """Reject a student's request to work with the teacher"""
    relations_repo = StudentTeacherRelationsRepository()
    relations = await relations_repo.get_teacher_relations(teacher['uid'])
    
    # Find the pending relation for this student
    pending_relation = None
    for rel in relations:
        if rel.student_uid == student_uid and rel.status == "pending":
            pending_relation = rel
            break
    
    if not pending_relation:
        raise HTTPException(status_code=404, detail="No pending request found for this student")
    
    success = await relations_repo.reject_relation(pending_relation.id)
    if success:
        return {"message": "Student request rejected successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to reject student request")

# Ders Takip Sistemi

@router.post("/lessons", response_model=str)
async def create_lesson(lesson_data: CreateLessonRequest, teacher: dict = Depends(require_teacher)):
    """Create a new lesson record"""
    lessons_repo = LessonsRepository()
    
    try:
        lesson_id = await lessons_repo.create_lesson(lesson_data, teacher['uid'])
        return lesson_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create lesson: {str(e)}")

@router.get("/lessons", response_model=List[Lesson])
async def get_my_lessons(teacher: dict = Depends(require_teacher)):
    """Get all lessons for the teacher"""
    lessons_repo = LessonsRepository()
    return await lessons_repo.get_teacher_lessons(teacher['uid'])

@router.get("/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson_detail(lesson_id: str, teacher: dict = Depends(require_teacher)):
    """Get lesson details"""
    lessons_repo = LessonsRepository()
    lesson = await lessons_repo.get_lesson(lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    if lesson.teacher_uid != teacher['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return lesson

@router.put("/lessons/{lesson_id}")
async def update_lesson(
    lesson_id: str,
    updates: dict,
    teacher: dict = Depends(require_teacher)
):
    """Update lesson details"""
    lessons_repo = LessonsRepository()
    lesson = await lessons_repo.get_lesson(lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    if lesson.teacher_uid != teacher['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = await lessons_repo.update_lesson(lesson_id, updates)
    if success:
        return {"message": "Lesson updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to update lesson")

@router.delete("/lessons/{lesson_id}")
async def delete_lesson(lesson_id: str, teacher: dict = Depends(require_teacher)):
    """Delete a lesson"""
    lessons_repo = LessonsRepository()
    lesson = await lessons_repo.get_lesson(lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    if lesson.teacher_uid != teacher['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = await lessons_repo.delete_lesson(lesson_id)
    if success:
        return {"message": "Lesson deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to delete lesson")

# Bireysel Ödev Sistemi

@router.post("/individual-assignments", response_model=str)
async def create_individual_assignment(
    assignment_data: CreateIndividualAssignmentRequest,
    teacher: dict = Depends(require_teacher)
):
    """Create a new individual assignment for a student"""
    individual_assignments_repo = IndividualAssignmentsRepository()
    
    try:
        assignment_id = await individual_assignments_repo.create_assignment(assignment_data, teacher['uid'])
        return assignment_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create individual assignment: {str(e)}")

@router.get("/individual-assignments", response_model=List[IndividualAssignment])
async def get_my_individual_assignments(teacher: dict = Depends(require_teacher)):
    """Get all individual assignments created by the teacher"""
    individual_assignments_repo = IndividualAssignmentsRepository()
    return await individual_assignments_repo.get_teacher_assignments(teacher['uid'])

@router.get("/individual-assignments/{assignment_id}", response_model=IndividualAssignment)
async def get_individual_assignment_detail(assignment_id: str, teacher: dict = Depends(require_teacher)):
    """Get individual assignment details"""
    individual_assignments_repo = IndividualAssignmentsRepository()
    assignment = await individual_assignments_repo.get_assignment(assignment_id)
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Individual assignment not found")
    
    if assignment.teacher_uid != teacher['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return assignment

@router.post("/individual-assignments/{assignment_id}/submit")
async def submit_individual_assignment(
    assignment_id: str,
    score: float,
    feedback: str = None,
    teacher: dict = Depends(require_teacher)
):
    """Submit an individual assignment with score and feedback"""
    individual_assignments_repo = IndividualAssignmentsRepository()
    assignment = await individual_assignments_repo.get_assignment(assignment_id)
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Individual assignment not found")
    
    if assignment.teacher_uid != teacher['uid']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = await individual_assignments_repo.submit_assignment(assignment_id, score, feedback)
    if success:
        return {"message": "Individual assignment submitted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to submit individual assignment")