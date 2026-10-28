from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.models.profile import CandidateProfile
from backend.models.interview import Interview
from backend.models.question import InterviewQuestion
from backend.models.answer import CandidateAnswer
from backend.models.evaluation import AnswerEvaluation
from backend.models.feedback import InterviewFeedback
from backend.schemas.report import DetailedReportOut, QuestionEvaluationReport
from backend.utils.security import get_current_user
from backend.services.skill_service import skill_service

router = APIRouter(prefix="/api/reports", tags=["Interview Reports"])

@router.get("/{interview_id}", response_model=DetailedReportOut)
def get_detailed_report(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates a complete 12-section detailed candidate assessment report."""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    
    # Gather question evaluations
    qa_list = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview_id
    ).order_by(InterviewQuestion.question_order.asc()).all()

    q_eval_reports = []
    category_totals = {}
    category_counts = {}

    for q in qa_list:
        ans = db.query(CandidateAnswer).filter(CandidateAnswer.question_id == q.id).first()
        ev = db.query(AnswerEvaluation).filter(AnswerEvaluation.answer_id == ans.id).first() if ans else None

        score = ev.overall_score if ev else 0.0
        q_report = QuestionEvaluationReport(
            question_order=q.question_order,
            question_text=q.question_text,
            category=q.category,
            targeted_skill=q.targeted_skill,
            difficulty=q.difficulty,
            is_follow_up=q.is_follow_up,
            candidate_answer=ans.answer_text if ans else "No answer submitted",
            score=score,
            correctness=ev.correctness if ev else 0.0,
            relevance=ev.relevance if ev else 0.0,
            completeness=ev.completeness if ev else 0.0,
            technical_understanding=ev.technical_understanding if ev else 0.0,
            communication=ev.communication if ev else 0.0,
            strengths=ev.strengths if ev else [],
            improvements=ev.improvements if ev else [],
            feedback_text=ev.feedback_text if ev else "Not evaluated"
        )
        q_eval_reports.append(q_report)

        # Track category scores
        cat = q.category or "Technical"
        category_totals[cat] = category_totals.get(cat, 0.0) + (score * 10.0)
        category_counts[cat] = category_counts.get(cat, 0) + 1

    category_scores = {cat: round(category_totals[cat] / category_counts[cat], 1) for cat in category_totals}

    # Retrieve aggregate feedback
    fb = db.query(InterviewFeedback).filter(InterviewFeedback.interview_id == interview_id).first()
    
    # Skill gap analysis
    skill_gap_data = skill_service.get_skill_gap_analysis(profile) if profile else None

    dimension_scores = {
        "Technical Score": interview.technical_score or 0.0,
        "Communication Score": interview.communication_score or 0.0,
        "Relevance Score": interview.relevance_score or 0.0,
        "Correctness Score": interview.correctness_score or 0.0,
        "Completeness Score": interview.completeness_score or 0.0
    }

    return {
        "candidate_name": current_user.name,
        "candidate_email": current_user.email,
        "candidate_education": profile.education if profile else "B.Tech",
        "candidate_experience": profile.experience_level if profile else "Fresher",
        "interview_info": interview,
        "overall_score": interview.overall_score or 0.0,
        "dimension_scores": dimension_scores,
        "category_scores": category_scores,
        "questions_evaluations": q_eval_reports,
        "ai_feedback": fb,
        "skill_gap": skill_gap_data
    }
