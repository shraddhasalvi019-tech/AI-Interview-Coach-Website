from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from backend.schemas.interview import InterviewOut
from backend.schemas.evaluation import FeedbackOut

class QuestionEvaluationReport(BaseModel):
    question_order: int
    question_text: str
    category: str
    targeted_skill: Optional[str] = None
    difficulty: str
    is_follow_up: bool
    candidate_answer: Optional[str] = None
    score: float
    correctness: float
    relevance: float
    completeness: float
    technical_understanding: float
    communication: float
    strengths: List[str] = []
    improvements: List[str] = []
    feedback_text: Optional[str] = None

class DetailedReportOut(BaseModel):
    candidate_name: str
    candidate_email: str
    candidate_education: Optional[str] = None
    candidate_experience: str
    interview_info: InterviewOut
    overall_score: float
    dimension_scores: Dict[str, float]
    category_scores: Dict[str, float]
    questions_evaluations: List[QuestionEvaluationReport]
    ai_feedback: Optional[FeedbackOut] = None
    skill_gap: Optional[Dict[str, Any]] = None
