from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ..deps.firebase import require_teacher, require_student
from ..repos.assignments import AssignmentsRepository
from ..repos.classes import ClassesRepository
from ..repos.users import UsersRepository
from ..services.scoring import ScoringService

router = APIRouter()

@router.get("/teacher/overview")
async def get_teacher_analytics(teacher: dict = Depends(require_teacher)):
    """Get overview analytics for teacher"""
    classes_repo = ClassesRepository()
    assignments_repo = AssignmentsRepository()
    
    # Get teacher's classes
    classes = await classes_repo.get_teacher_classes(teacher['uid'])
    
    total_students = 0
    total_assignments = 0
    total_submissions = 0
    average_score = 0
    
    for class_obj in classes:
        # Count students in class
        students = await classes_repo.get_class_students(class_obj.id)
        total_students += len(students)
        
        # Count assignments in class
        assignments = await assignments_repo.get_class_assignments(class_obj.id)
        total_assignments += len(assignments)
        
        # Count submissions and calculate scores
        for assignment in assignments:
            submissions = await assignments_repo.get_assignment_submissions(assignment.id)
            total_submissions += len(submissions)
            
            if submissions:
                scores = [s.score for s in submissions if s.score is not None]
                if scores:
                    average_score += sum(scores)
    
    if total_submissions > 0:
        average_score = average_score / total_submissions
    
    return {
        "total_classes": len(classes),
        "total_students": total_students,
        "total_assignments": total_assignments,
        "total_submissions": total_submissions,
        "average_score": round(average_score, 2)
    }

@router.get("/teacher/class/{class_id}")
async def get_class_analytics(class_id: str, teacher: dict = Depends(require_teacher)):
    """Get analytics for a specific class"""
    classes_repo = ClassesRepository()
    assignments_repo = AssignmentsRepository()
    
    # Verify teacher owns this class
    class_obj = await classes_repo.get_class(class_id)
    if not class_obj or class_obj.teacher_uid != teacher['uid']:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Get students in class
    students = await classes_repo.get_class_students(class_id)
    
    # Get assignments in class
    assignments = await assignments_repo.get_class_assignments(class_id)
    
    # Calculate analytics
    assignment_analytics = []
    for assignment in assignments:
        submissions = await assignments_repo.get_assignment_submissions(assignment.id)
        
        if submissions:
            scores = [s.score for s in submissions if s.score is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            completion_rate = len(submissions) / len(students) if students else 0
            
            assignment_analytics.append({
                "assignment_id": assignment.id,
                "title": assignment.title,
                "total_students": len(students),
                "submitted": len(submissions),
                "completion_rate": round(completion_rate * 100, 1),
                "average_score": round(avg_score, 2),
                "max_score": assignment.question_count
            })
    
    return {
        "class_id": class_id,
        "class_name": class_obj.name,
        "total_students": len(students),
        "total_assignments": len(assignments),
        "assignment_analytics": assignment_analytics
    }

@router.get("/student/{student_uid}")
async def get_student_analytics(student_uid: str, teacher: dict = Depends(require_teacher)):
    """Get analytics for a specific student"""
    assignments_repo = AssignmentsRepository()
    users_repo = UsersRepository()
    
    # Get student profile
    student = await users_repo.get_user(student_uid)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get student's submissions
    submissions = await assignments_repo.get_student_submissions(student_uid)
    
    # Calculate analytics
    total_assignments = len(submissions)
    completed_assignments = len([s for s in submissions if s.submitted_at])
    
    scores = [s.score for s in submissions if s.score is not None]
    average_score = sum(scores) / len(scores) if scores else 0
    
    # Calculate scores over time
    scores_over_time = []
    for submission in submissions:
        if submission.score is not None and submission.submitted_at:
            scores_over_time.append({
                "date": submission.submitted_at.isoformat(),
                "score": submission.score,
                "max_score": submission.max_score,
                "percentage": ScoringService.calculate_percentage(submission.score, submission.max_score)
            })
    
    # Sort by date
    scores_over_time.sort(key=lambda x: x["date"])
    
    return {
        "student_uid": student_uid,
        "student_name": student.display_name,
        "grade": student.grade,
        "total_assignments": total_assignments,
        "completed_assignments": completed_assignments,
        "completion_rate": round((completed_assignments / total_assignments * 100) if total_assignments > 0 else 0, 1),
        "average_score": round(average_score, 2),
        "scores_over_time": scores_over_time
    }

@router.get("/student/my-progress")
async def get_my_progress(student: dict = Depends(require_student)):
    """Get analytics for the current student"""
    assignments_repo = AssignmentsRepository()
    
    # Get student's submissions
    submissions = await assignments_repo.get_student_submissions(student['uid'])
    
    # Calculate analytics
    total_assignments = len(submissions)
    completed_assignments = len([s for s in submissions if s.submitted_at])
    
    scores = [s.score for s in submissions if s.score is not None]
    average_score = sum(scores) / len(scores) if scores else 0
    
    # Calculate scores over time
    scores_over_time = []
    for submission in submissions:
        if submission.score is not None and submission.submitted_at:
            scores_over_time.append({
                "date": submission.submitted_at.isoformat(),
                "score": submission.score,
                "max_score": submission.max_score,
                "percentage": ScoringService.calculate_percentage(submission.score, submission.max_score)
            })
    
    # Sort by date
    scores_over_time.sort(key=lambda x: x["date"])
    
    # Get recent performance (last 5 assignments)
    recent_scores = scores[-5:] if len(scores) >= 5 else scores
    recent_average = sum(recent_scores) / len(recent_scores) if recent_scores else 0
    
    return {
        "total_assignments": total_assignments,
        "completed_assignments": completed_assignments,
        "completion_rate": round((completed_assignments / total_assignments * 100) if total_assignments > 0 else 0, 1),
        "average_score": round(average_score, 2),
        "recent_average": round(recent_average, 2),
        "scores_over_time": scores_over_time,
        "grade_level": ScoringService.get_grade_level(ScoringService.calculate_percentage(average_score, 1))
    }