from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_order = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    category = Column(String, nullable=False, default="Technical")
    targeted_skill = Column(String, nullable=True)
    difficulty = Column(String, nullable=False, default="Medium")
    is_follow_up = Column(Boolean, default=False)
    parent_question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answer = relationship("CandidateAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")
    parent_question = relationship("InterviewQuestion", remote_side=[id], backref="follow_ups")
