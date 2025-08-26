from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..deps.firebase import require_student
from ..models.schemas import Assignment, Submission, SubmitAnswersRequest
from ..repos.assignments import AssignmentsRepository
from ..repos.classes import ClassesRepository
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