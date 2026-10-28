from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = Column(String, nullable=False)
    interview_type = Column(String, nullable=False)  # Technical, HR, Behavioral, Mixed
    difficulty = Column(String, nullable=False)      # Easy, Medium, Hard
    total_questions = Column(Integer, default=5)
    status = Column(String, default="configured")    # configured, in_progress, completed

    # Dimension Scores (0.0 to 100.0 or 0.0 to 10.0 scale)
    overall_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    correctness_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan", order_by="InterviewQuestion.question_order")
    answers = relationship("CandidateAnswer", back_populates="interview", cascade="all, delete-orphan")
    feedback = relationship("InterviewFeedback", back_populates="interview", uselist=False, cascade="all, delete-orphan")
