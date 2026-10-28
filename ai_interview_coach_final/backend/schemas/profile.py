from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, example="Demo Candidate")
    education: Optional[str] = Field(None, example="B.Tech in Computer Science")
    skills: Optional[List[str]] = Field(default=[], example=["Java", "SQL", "Python", "HTML", "CSS"])
    programming_languages: Optional[List[str]] = Field(default=[], example=["Java", "Python"])
    experience_level: Optional[str] = Field("Fresher", example="Fresher")  # Fresher, Junior, Mid-Level, Senior
    target_role: Optional[str] = Field("Java Developer", example="Java Developer")
    preferred_interview_type: Optional[str] = Field("Technical", example="Technical")
    preferred_difficulty: Optional[str] = Field("Medium", example="Medium")

class ProfileOut(BaseModel):
    id: int
    user_id: int
    full_name: str
    education: Optional[str] = None
    skills: List[str] = []
    programming_languages: List[str] = []
    experience_level: str
    target_role: str
    preferred_interview_type: str
    preferred_difficulty: str
    updated_at: datetime

    class Config:
        from_attributes = True

class SkillGapOut(BaseModel):
    target_role: str
    candidate_skills: List[str]
    expected_skills: List[str]
    strong_skills: List[str]
    skills_to_improve: List[str]
    recommended_learning_areas: List[str]
