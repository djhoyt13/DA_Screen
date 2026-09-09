"""SQLAlchemy models for quiz submissions and per-question answers."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    recruiter_email = Column(String, nullable=False)
    score_percentage = Column(Float, nullable=False)
    correct_count = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    email_sent = Column(Boolean, default=False, nullable=False)
    assessment = Column(String, default="ds", nullable=False)
    # Client-reported telemetry (ISO timestamps from the browser)
    opened_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)

    answers = relationship("Answer", back_populates="submission")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_key = Column(String, nullable=False)
    user_answer = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, nullable=True)

    submission = relationship("Submission", back_populates="answers")
