from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.models.profile import CandidateProfile
from backend.models.interview import Interview
from backend.schemas.dashboard import DashboardMetrics
from backend.utils.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Candidate Dashboard"])

@router.get("", response_model=DashboardMetrics)
def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculates overall candidate analytics, average performance scores, and recent interviews."""
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    target_role = profile.target_role if profile else "Software Developer"
    candidate_name = current_user.name

    completed_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == "completed"
    ).order_by(Interview.completed_at.desc()).all()

    count = len(completed_interviews)
    if count == 0:
        return {
            "candidate_name": candidate_name,
            "target_role": target_role,
            "interviews_completed": 0,
            "average_score": 0.0,
            "best_score": 0.0,
            "latest_score": 0.0,
            "technical_avg": 0.0,
            "communication_avg": 0.0,
            "problem_solving_avg": 0.0,
            "strongest_skill": profile.skills[0] if (profile and profile.skills) else "Java",
            "skill_to_improve": "Multithreading & System Design",
            "recent_interviews": []
        }

    scores = [i.overall_score for i in completed_interviews if i.overall_score is not None]
    tech_scores = [i.technical_score for i in completed_interviews if i.technical_score is not None]
    comm_scores = [i.communication_score for i in completed_interviews if i.communication_score is not None]
    prob_scores = [i.correctness_score for i in completed_interviews if i.correctness_score is not None]

    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    best_score = round(max(scores), 1) if scores else 0.0
    latest_score = round(scores[0], 1) if scores else 0.0

    tech_avg = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else 0.0
    comm_avg = round(sum(comm_scores) / len(comm_scores), 1) if comm_scores else 0.0
    prob_avg = round(sum(prob_scores) / len(prob_scores), 1) if prob_scores else 0.0

    strongest = profile.skills[0] if (profile and profile.skills) else "Core CS Principles"
    if tech_avg > comm_avg:
        skill_improve = "Communication & Storytelling (STAR Method)"
    else:
        skill_improve = "System Architecture & Memory Management"

    all_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(Interview.created_at.desc()).limit(5).all()

    return {
        "candidate_name": candidate_name,
        "target_role": target_role,
        "interviews_completed": count,
        "average_score": avg_score,
        "best_score": best_score,
        "latest_score": latest_score,
        "technical_avg": tech_avg,
        "communication_avg": comm_avg,
        "problem_solving_avg": prob_avg,
        "strongest_skill": strongest,
        "skill_to_improve": skill_improve,
        "recent_interviews": all_interviews
    }
