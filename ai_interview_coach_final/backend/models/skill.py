from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class SkillAssessment(Base):
    __tablename__ = "skill_assessments"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    target_role = Column(String, nullable=False)

    strong_skills = Column(JSON, default=list)             # Candidate skills that match role requirements
    skills_to_improve = Column(JSON, default=list)         # Expected role skills candidate lacks or scores low in
    recommended_learning_areas = Column(JSON, default=list)# Learning modules / topics to study
    assessed_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    profile = relationship("CandidateProfile", back_populates="skill_assessments")
