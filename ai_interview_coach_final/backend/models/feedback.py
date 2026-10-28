from datetime import datetime
from sqlalchemy import Column, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class InterviewFeedback(Base):
    __tablename__ = "interview_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), unique=True, nullable=False)

    overall_summary = Column(Text, nullable=False)
    strengths = Column(JSON, default=list)                  # ["Strong Java OOP", "Clear communication"]
    weaknesses = Column(JSON, default=list)                 # ["Missed thread synchronization details"]
    technical_gaps = Column(JSON, default=list)             # ["Java Concurrency API", "REST Status codes"]
    communication_issues = Column(JSON, default=list)       # ["Could use structured examples like STAR technique"]
    recommended_topics = Column(JSON, default=list)         # ["Java Collections", "Spring Boot"]
    practice_areas = Column(JSON, default=list)             # ["System Design", "Mock coding"]
    tips = Column(JSON, default=list)                       # ["Be specific when discussing complexity"]
    sample_answer_improvements = Column(JSON, default=list)# [{question: "...", improved_answer: "..."}]

    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    interview = relationship("Interview", back_populates="feedback")
