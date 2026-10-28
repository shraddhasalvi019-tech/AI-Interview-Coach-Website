from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.models.profile import CandidateProfile
from backend.schemas.profile import ProfileUpdate, ProfileOut, SkillGapOut
from backend.utils.security import get_current_user
from backend.services.skill_service import skill_service

router = APIRouter(prefix="/api/profile", tags=["Candidate Profile"])

@router.get("", response_model=ProfileOut)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches candidate profile details for the authenticated user."""
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        # Create fallback profile
        profile = CandidateProfile(
            user_id=current_user.id,
            full_name=current_user.name,
            education="B.Tech in Computer Science",
            skills=["Java", "SQL", "Python"],
            programming_languages=["Java", "Python"],
            experience_level="Fresher",
            target_role="Software Developer"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("", response_model=ProfileOut)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates candidate profile information."""
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id, full_name=current_user.name)
        db.add(profile)

    if profile_data.full_name is not None:
        profile.full_name = profile_data.full_name
    if profile_data.education is not None:
        profile.education = profile_data.education
    if profile_data.skills is not None:
        profile.skills = profile_data.skills
    if profile_data.programming_languages is not None:
        profile.programming_languages = profile_data.programming_languages
    if profile_data.experience_level is not None:
        profile.experience_level = profile_data.experience_level
    if profile_data.target_role is not None:
        profile.target_role = profile_data.target_role
    if profile_data.preferred_interview_type is not None:
        profile.preferred_interview_type = profile_data.preferred_interview_type
    if profile_data.preferred_difficulty is not None:
        profile.preferred_difficulty = profile_data.preferred_difficulty

    db.commit()
    db.refresh(profile)
    return profile

@router.get("/skill-gap", response_model=SkillGapOut)
def get_skill_gap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Executes AI skill-gap analysis comparing candidate skills against expected role benchmarks."""
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete your candidate profile before performing a skill gap analysis."
        )

    analysis = skill_service.get_skill_gap_analysis(profile)
    return {
        "target_role": analysis.get("target_role", profile.target_role),
        "candidate_skills": profile.skills or [],
        "expected_skills": analysis.get("expected_skills", []),
        "strong_skills": analysis.get("strong_skills", []),
        "skills_to_improve": analysis.get("skills_to_improve", []),
        "recommended_learning_areas": analysis.get("recommended_learning_areas", [])
    }
