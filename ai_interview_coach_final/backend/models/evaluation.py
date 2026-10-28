from datetime import datetime
from sqlalchemy import Column, Integer, Float, JSON, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("candidate_answers.id", ondelete="CASCADE"), unique=True, nullable=False)

    # 0 to 10 ratings
    correctness = Column(Float, nullable=False, default=0.0)
    relevance = Column(Float, nullable=False, default=0.0)
    completeness = Column(Float, nullable=False, default=0.0)
    technical_understanding = Column(Float, nullable=False, default=0.0)
    communication = Column(Float, nullable=False, default=0.0)
    overall_score = Column(Float, nullable=False, default=0.0)

    strengths = Column(JSON, default=list)       # List of strength strings
    improvements = Column(JSON, default=list)    # List of improvement strings
    feedback_text = Column(Text, nullable=True)  # Detailed feedback text
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    answer = relationship("CandidateAnswer", back_populates="evaluation")
