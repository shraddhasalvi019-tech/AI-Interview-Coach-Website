from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class InterviewCreate(BaseModel):
    target_role: Optional[str] = Field(None, example="Java Developer")
    interview_type: str = Field("Technical", example="Technical") # Technical, HR, Behavioral, Mixed
    difficulty: str = Field("Medium", example="Medium")            # Easy, Medium, Hard
    total_questions: int = Field(5, ge=1, le=20, example=5)

class InterviewOut(BaseModel):
    id: int
    user_id: int
    target_role: str
    interview_type: str
    difficulty: str
    total_questions: int
    status: str
    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    relevance_score: Optional[float] = None
    correctness_score: Optional[float] = None
    completeness_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
