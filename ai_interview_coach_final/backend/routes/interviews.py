from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.models.interview import Interview
from backend.models.question import InterviewQuestion
from backend.models.answer import CandidateAnswer
from backend.models.evaluation import AnswerEvaluation
from backend.models.feedback import InterviewFeedback
from backend.schemas.interview import InterviewCreate, InterviewOut
from backend.schemas.question import QuestionOut, AnswerCreate, AnswerSubmissionResponse
from backend.schemas.evaluation import AnswerEvaluationOut, FeedbackOut
from backend.services.interview_service import interview_service
from backend.utils.security import get_current_user

router = APIRouter(prefix="/api/interviews", tags=["Interviews"])

@router.post("", response_model=InterviewOut, status_code=status.HTTP_201_CREATED)
def create_interview(
    config: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configures and creates a new mock interview session."""
    interview = interview_service.create_interview(
        db=db,
        user_id=current_user.id,
        target_role=config.target_role,
        interview_type=config.interview_type,
        difficulty=config.difficulty,
        total_questions=config.total_questions
    )
    return interview

@router.get("", response_model=List[InterviewOut])
def list_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all mock interview sessions conducted by the candidate."""
    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(Interview.created_at.desc()).all()
    return interviews

@router.get("/{interview_id}", response_model=InterviewOut)
def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches details of a specific interview session."""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")
    return interview

@router.post("/{interview_id}/start", response_model=QuestionOut)
def start_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Starts the interview session and generates Question 1 dynamically using GenAI."""
    return interview_service.start_interview(db, interview_id, current_user.id)

@router.get("/{interview_id}/questions/current", response_model=QuestionOut)
def get_current_question(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches the current active question for an ongoing interview session."""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    latest_q = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview_id
    ).order_by(InterviewQuestion.id.desc()).first()

    if not latest_q:
        # Start if not started yet
        return interview_service.start_interview(db, interview_id, current_user.id)
    return latest_q

@router.post("/{interview_id}/answer", response_model=AnswerSubmissionResponse)
def submit_answer(
    interview_id: int,
    answer_data: AnswerCreate,
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submits candidate answer for a question, triggers AI evaluation & follow-up check."""
    return interview_service.submit_answer(
        db=db,
        interview_id=interview_id,
        user_id=current_user.id,
        question_id=question_id,
        answer_text=answer_data.answer_text
    )

@router.post("/{interview_id}/complete", response_model=InterviewOut)
def complete_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Finalizes an interview session, calculates weighted scores, and generates AI feedback."""
    return interview_service.complete_interview(db, interview_id, current_user.id)

@router.get("/{interview_id}/evaluation", response_model=List[AnswerEvaluationOut])
def get_interview_evaluations(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all question evaluations for an interview session."""
    evaluations = db.query(AnswerEvaluation).join(CandidateAnswer).join(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).all()
    return evaluations

@router.get("/{interview_id}/feedback", response_model=FeedbackOut)
def get_interview_feedback(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves aggregate AI feedback for a completed interview."""
    fb = db.query(InterviewFeedback).filter(InterviewFeedback.interview_id == interview_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Interview feedback not generated yet.")
    return fb
