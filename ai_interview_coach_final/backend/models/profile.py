from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    education = Column(String, nullable=True)
    skills = Column(JSON, default=list)  # List of strings e.g. ["Java", "SQL", "Python"]
    programming_languages = Column(JSON, default=list)  # List of strings e.g. ["Java", "Python"]
    experience_level = Column(String, nullable=False, default="Fresher")  # Fresher, Junior, Mid-Level, Senior
    target_role = Column(String, nullable=False, default="Software Developer")
    preferred_interview_type = Column(String, nullable=False, default="Technical")
    preferred_difficulty = Column(String, nullable=False, default="Medium")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")
    skill_assessments = relationship("SkillAssessment", back_populates="profile", cascade="all, delete-orphan")
