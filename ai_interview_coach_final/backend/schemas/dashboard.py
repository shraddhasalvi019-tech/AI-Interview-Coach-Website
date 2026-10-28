from typing import List, Optional
from pydantic import BaseModel
from backend.schemas.interview import InterviewOut

class DashboardMetrics(BaseModel):
    candidate_name: str
    target_role: str
    interviews_completed: int
    average_score: float
    best_score: float
    latest_score: Optional[float] = 0.0
    technical_avg: float
    communication_avg: float
    problem_solving_avg: float
    strongest_skill: str
    skill_to_improve: str
    recent_interviews: List[InterviewOut] = []
