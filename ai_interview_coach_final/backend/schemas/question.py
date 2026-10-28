from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class QuestionOut(BaseModel):
    id: int
    interview_id: int
    question_order: int
    question_text: str
    category: str
    targeted_skill: Optional[str] = None
    difficulty: str
    is_follow_up: bool
    parent_question_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AnswerCreate(BaseModel):
    answer_text: str = Field(..., min_length=1, example="ArrayList uses a dynamic array internally, whereas LinkedList uses a doubly linked list structure.")

class AnswerOut(BaseModel):
    id: int
    interview_id: int
    question_id: int
    answer_text: str
    submitted_at: datetime

    class Config:
        from_attributes = True

class AnswerSubmissionResponse(BaseModel):
    answer_id: int
    evaluation: Optional[dict] = None
    has_follow_up: bool = False
    follow_up_question: Optional[QuestionOut] = None
    is_interview_completed: bool = False
    next_question: Optional[QuestionOut] = None
