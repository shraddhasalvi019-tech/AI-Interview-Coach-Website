from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class AnswerEvaluationOut(BaseModel):
    id: int
    answer_id: int
    correctness: float = Field(..., ge=0.0, le=10.0)
    relevance: float = Field(..., ge=0.0, le=10.0)
    completeness: float = Field(..., ge=0.0, le=10.0)
    technical_understanding: float = Field(..., ge=0.0, le=10.0)
    communication: float = Field(..., ge=0.0, le=10.0)
    overall_score: float = Field(..., ge=0.0, le=10.0)
    strengths: List[str] = []
    improvements: List[str] = []
    feedback_text: Optional[str] = None
    evaluated_at: datetime

    class Config:
        from_attributes = True

class FeedbackOut(BaseModel):
    id: int
    interview_id: int
    overall_summary: str
    strengths: List[str] = []
    weaknesses: List[str] = []
    technical_gaps: List[str] = []
    communication_issues: List[str] = []
    recommended_topics: List[str] = []
    practice_areas: List[str] = []
    tips: List[str] = []
    sample_answer_improvements: List[dict] = []
    generated_at: datetime

    class Config:
        from_attributes = True
